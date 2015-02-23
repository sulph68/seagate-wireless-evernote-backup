#!/usr/bin/python
import sys
sys.path.append("/static/Data/1/plugins/evernote/lib")

import os
import shutil
import re
import time
import ConfigParser

import hashlib
import binascii
import ENML2HTML as enml

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec

plugin_name = "evernote"
plugin_dir = "/static/Data/1/plugins"

plugin_path = plugin_dir + "/" + plugin_name
plugin_file_path = plugin_path + "/files"
plugin_cache_path = plugin_path + "/cache"
plugin_contentHash_path = plugin_path + "/contentHash"

# configuration file to store values between runs
config_file = plugin_path + "/config.cfg"

# throttle delay between query
rate_limit = 2
# force refresh all content if 1, normally should be 0
refresh_all = 0
# sync only this notebook. if empty, ("") will sync all
sync_notebook = ""

def checkAuthToken():
	# print "Checking auth token"
	token_file = plugin_path + "/authToken"
	if os.path.exists(token_file):
		f = open(token_file, "r")
		token = f.readline()
		f.close()
		# print "Token is: ", token
		return token.rstrip()
	else:
		return ""

# function to write contentHash file
def writeContentHash(guid, hash):
	# print "Updating hash"
	filename = plugin_contentHash_path + "/" + guid
	if os.path.exists(filename):
		os.remove(filename)
		file = open(filename, "w")
		file.write(binascii.b2a_base64(hash))
		file.close()

# function to compare contentHash file
def compareContentHash(guid, hash):
	filename = plugin_contentHash_path + "/" + guid
	if os.path.exists(filename):
		file = open(filename, "r")
		h = file.readline()
		file.close()
		if str(h) == str(binascii.b2a_base64(hash)):
			# print "No change in content"
			if refresh_all == 1:
				return False
			else:
				return True
		else:
			# print "Content changed"
			return False
	else:
		# print "Content changed"
		return False

# Configuration file handlers
def ReadCheckpoint(notebook):
	config = ConfigParser.ConfigParser()
	# if config file doesn't exist, create it
	if not os.path.exists(config_file):
		file = open(config_file, "w")
		config.add_section("Checkpoint")
		config.write(file)
		file.close()
	config.read(config_file)
	try:
		count = config.get("Checkpoint", notebook)
		print "   * Checkpoint found! Starting from ", count
	except:
		print "   * No checkpoint found! Starting from 0"
		WriteCheckpoint(notebook, 0)
		count = 0
	return int(count)

def WriteCheckpoint(notebook, count):
	config = ConfigParser.ConfigParser()
	config.read(config_file)
	for name,value in config.items("Checkpoint"):
		if name == notebook:
			continue
		else:
			config.set("Checkpoint", name, value)
	config.set("Checkpoint", notebook, count)
	file = open(config_file,"w")
	config.write(file)
	file.close()
	
# Main
auth_token = checkAuthToken()
# print "Got token: ", auth_token
if auth_token == "":
	print "Application authentication token not found."
	print "Please authenticate before use."
	exit(1)

client = EvernoteClient(token=auth_token, sandbox=False)

now = time.strftime("%c")
print "Authenticated..."

# do a loop if rate limit is reached. automatically sleep for duration and retry
rate_test = 0
while (rate_test == 0): 
	try:
		note_store = client.get_note_store()
		syncState = note_store.getSyncState()
		user_store = client.get_user_store()
		rate_test = 1
	except Errors.EDAMSystemException, e:
		rate_test = 0
		if e.errorCode == Errors.EDAMErrorCode.RATE_LIMIT_REACHED:
			print "**", time.strftime("%c")
			print "** Rate limit reached"
			print "** Retrying your request in %d seconds" % e.rateLimitDuration
			time.sleep(e.rateLimitDuration)
			

# user = user_store.getUser()
# print "User: ", user.username
# print "NoteStore URL: ", user_store.getNoteStoreUrl()

version_ok = user_store.checkVersion(
	"Evernote EDAMTest (Python)",
	UserStoreConstants.EDAM_VERSION_MAJOR,
	UserStoreConstants.EDAM_VERSION_MINOR
)

if not version_ok:
	print "Evernote client out of date."
	print ""
	exit(1)

# List all of the notebooks in the user's account
notebooks = note_store.listNotebooks()

# Manipulate sync_notebook for "\"
sync_notebook = sync_notebook.replace("/","|")

print "Found ", len(notebooks), " notebooks:"
for notebook in notebooks:
	# we replace all "/" with "|" to prevent filesystem errors
	notebook_name = notebook.name.replace("/", "|")
	
	if sync_notebook == "":
		print "  * ", notebook_name, " (", notebook.guid, ")"
	else:
		if notebook_name == sync_notebook:
			print "  * ", notebook_name, " (", notebook.guid, ") - Syncing"
		else:
			print "  * ", notebook_name, " (", notebook.guid, ") - Skipping"
			continue
			
	# slight delay to prevent rate limitation issues
	time.sleep(rate_limit)
	
	# Create mapping cache path and file path
	notebook_cache_path = plugin_cache_path + "/" + notebook.guid
	notebook_file_path = plugin_file_path + "/" + notebook_name
	if not(os.path.exists(notebook_cache_path)):
		os.mkdir(notebook_cache_path)
	if not(os.path.exists(notebook_file_path)):  
		os.mkdir(notebook_file_path) 

	# Get relavent filter and get number of notes
	filter = NoteStore.NoteFilter(notebookGuid=notebook.guid)
	# print "Auth token: " + auth_token
	
	# iterative loop to get all notes starts here
	# Retrieve checkpoint of notebook
	complete_notes = ReadCheckpoint(notebook_name)
	notebook_complete = 0
	
	while (notebook_complete == 0):
		# do a loop if rate limit is reached. automatically sleep for duration and retry
		rate_test = 0
		while (rate_test == 0): 
			try:
				note_counts = note_store.findNoteCounts(auth_token, filter, False)
				print "   - ", note_counts.notebookCounts[notebook.guid], " notes"
				# Fetch all notes within the notebooks
				result_spec = NoteStore.NotesMetadataResultSpec(includeTitle=True)
				note_list = note_store.findNotesMetadata(auth_token, filter, complete_notes, 20000, result_spec)
				print "   -- Retrieved note list count from ", complete_notes, " to ", (complete_notes + len(note_list.notes)), " of ", note_list.totalNotes
				complete_notes = complete_notes + len(note_list.notes)
				if (complete_notes >= note_list.totalNotes):
					notebook_complete = 1
				rate_test = 1
			except Errors.EDAMSystemException, e:
				rate_test = 0
				if e.errorCode == Errors.EDAMErrorCode.RATE_LIMIT_REACHED:
					print "**", time.strftime("%c")
					print "** Rate limit reached"
					print "** Retrying your request in %d seconds" % e.rateLimitDuration
					time.sleep(e.rateLimitDuration)
				
		# Iteration within note
		count_index = 0
		for note in note_list.notes:
			# we replace all "/" with "|" to prevent filesystem errors
			note_title = note.title.replace("/","|")
			curr_note = (complete_notes - len(note_list.notes) + count_index)
			print "   ", curr_note,"> ", note_title, "(", note.guid, ")"
			
			# update count of notes in current iteration
			count_index = count_index + 1
			
			# slight delay to prevent rate limitation issues
			time.sleep(rate_limit)
		
			# do a loop if rate limit is reached. automatically sleep for duration and retry
			rate_test = 0
			while (rate_test == 0): 
				try:
					note_detail = note_store.getNote(auth_token, note.guid, True, False, False, False)
					rate_test = 1
				except Errors.EDAMSystemException, e:
					rate_test = 0
					if e.errorCode == Errors.EDAMErrorCode.RATE_LIMIT_REACHED:
						print "**", time.strftime("%c")
						print "** Rate limit reached"
						print "** Retrying your request in %d seconds" % e.rateLimitDuration
						time.sleep(e.rateLimitDuration)
			# print note_detail
		
			# Compare contentHash file
			if compareContentHash(note.guid, note_detail.contentHash):
				# Write checkpoint information for recovery if no change
				# print "notebook name:", notebook_name
				if curr_note >= (note_list.totalNotes - 1):
					WriteCheckpoint(notebook_name, 0)
				else:
					WriteCheckpoint(notebook_name, curr_note)
				continue
			
			# Content changed. Fetch everything
			# do a loop if rate limit is reached. automatically sleep for duration and retry
			rate_test = 0
			while (rate_test == 0): 
				try:
					note_detail = note_store.getNote(auth_token, note.guid, True, True, True, True) 
					rate_test = 1
				except Errors.EDAMSystemException, e:
					rate_test = 0
					if e.errorCode == Errors.EDAMErrorCode.RATE_LIMIT_REACHED:
						print "**", time.strftime("%c")
						print "** Rate limit reached"
						print "** Retrying your request in %d seconds" % e.rateLimitDuration
						time.sleep(e.rateLimitDuration)	
					
			print "    -> Updating Note"
			# Write ENML file and link
			filename = notebook_cache_path + "/" +  note.guid + ".enml"
			file = open(filename, "w")
			file.write(note_detail.content)
			file.close()
			linkname = notebook_file_path + "/" + note_title + ".enml"
			if os.path.exists(linkname):
				os.remove(linkname)
			os.symlink(filename, linkname) 
		
			# Convert ENML to HTML so its viewable on the web
			note_html = enml.ENMLToHTML(note_detail.content)
			filename = notebook_cache_path + "/" +  note.guid + ".html"
			file = open(filename, "w")
			file.write(note_html)
			file.close()
			linkname = notebook_file_path + "/" + note_title + ".html"
	
			if os.path.exists(linkname):
				os.remove(linkname)		
			os.symlink(filename, linkname)
		
			# Update contentHash file
			writeContentHash(note.guid, note_detail.contentHash)
		
			# Get all resources of the note and save as file separately
			if note_detail.resources:
				for res in note_detail.resources:
					# slight delay to prevent rate limitation issues
					time.sleep(rate_limit)
					# check to see if file has changed through Hash
					if compareContentHash(res.guid, res.data.bodyHash):
						continue
					# print res.mime
					e = re.search("^\w+/(.+)$",res.mime)
					ext = e.group(1)
				
					if res.attributes.fileName:
						# we replace all "/" with "|" to prevent filesystem errors
						resource_filename = res.attributes.fileName.replace("/","|")
					else:
						resource_filename = res.guid + "." + ext
					
					# Always base caches on the GUID
					resource_name = notebook_cache_path + "/" + res.guid + "." + ext
					file = open(resource_name, "w")
					file.write(res.data.body)
					file.close()
					linkname = notebook_file_path + "/" + note_title + "-" + resource_filename
					if os.path.exists(linkname):
						os.remove(linkname)		
					os.symlink(resource_name, linkname)
					print "     -> ", resource_filename, " (Updated)"
				
					# Update contentHash of resource
					writeContentHash(res.guid, res.data.bodyHash)
			
			# Write checkpoint information for recovery
			# print "notebook name:", notebook_name
			if curr_note >= (note_list.totalNotes - 1):
				WriteCheckpoint(notebook_name, 0)
			else:
				WriteCheckpoint(notebook_name, curr_note)


