#!/usr/bin/python
import sys
sys.path.append("/static/Data/1/plugins/evernote/lib")

import os
import shutil
import re

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
                        return True            
                else:                            
                        # print "Content changed"                        
                        return False                                       
        else:                                                                 
                # print "Content changed"
                return False              


# Main
auth_token = checkAuthToken()
# print "Got token: ", auth_token
if auth_token == "":
    print "Application authentication token not found."
    print "Please authenticate before use."
    exit(1)

print "Authenticated..."

# include sandbox=True if operating in sandbox environment
client = EvernoteClient(token=auth_token)

user_store = client.get_user_store()

version_ok = user_store.checkVersion(
    "Evernote EDAMTest (Python)",
    UserStoreConstants.EDAM_VERSION_MAJOR,
    UserStoreConstants.EDAM_VERSION_MINOR
)

if not version_ok:
    print "Evernote client out of date."
    print ""
    exit(1)

# user = user_store.getUser()
# print "User: ", user.username
# print "NoteStore URL: ", user_store.getNoteStoreUrl()

note_store = client.get_note_store()

# List all of the notebooks in the user's account
notebooks = note_store.listNotebooks()

print "Found ", len(notebooks), " notebooks:"
for notebook in notebooks:
    print "  * ", notebook.name
    
    # Create mapping cache path and file path
    notebook_cache_path = plugin_cache_path + "/" + notebook.guid
    notebook_file_path = plugin_file_path + "/" + notebook.name
    if not(os.path.exists(notebook_cache_path)):
	os.mkdir(notebook_cache_path)
    if not(os.path.exists(notebook_file_path)):  
        os.mkdir(notebook_file_path) 

    # Get relavent filter and get number of notes
    filter = NoteStore.NoteFilter(notebookGuid=notebook.guid)
    # print "Auth token: " + auth_token
    note_counts = note_store.findNoteCounts(auth_token, filter, False)
    print "   - ", note_counts.notebookCounts[notebook.guid], " notes"

    # Fetch all notes within the notebooks
    result_spec = NoteStore.NotesMetadataResultSpec(includeTitle=True)
    note_list = note_store.findNotesMetadata(auth_token, filter, 0, 10, result_spec)
    for note in note_list.notes:
        print "    > ", note.title, "(", note.guid, ")"
	note_detail = note_store.getNote(auth_token, note.guid, True, False, False, False)
	# print note_detail

	# Compare contentHash file
	if compareContentHash(note.guid, note_detail.contentHash):
		continue

	# Content changed. Fetch everything
	note_detail = note_store.getNote(auth_token, note.guid, True, True, True, True)
	print "    -> Updating Note"

	# Write ENML file and link
	filename = notebook_cache_path + "/" +  note.guid + ".enml"
        file = open(filename, "w")
        file.write(note_detail.content)             
        file.close()                                            
        linkname = notebook_file_path + "/" + note.title + ".enml"
        if os.path.exists(linkname):                                                         
                os.remove(linkname)                                                          
        os.symlink(filename, linkname) 

	# Convert ENML to HTML so its viewable on the web
	note_html = enml.ENMLToHTML(note_detail.content)
        filename = notebook_cache_path + "/" +  note.guid + ".html"
        file = open(filename, "w")
        file.write(note_html)
        file.close()
	linkname = notebook_file_path + "/" + note.title + ".html"
   	if os.path.exists(linkname):
		os.remove(linkname)		
	os.symlink(filename, linkname)

	# Update contentHash file
	writeContentHash(note.guid, note_detail.contentHash)	

	# Get all resources of the note and save as file separately
	if note_detail.resources:
		for res in note_detail.resources:
			# check to see if file has changed through Hash
			if compareContentHash(res.guid, res.data.bodyHash):
				continue
			# print res.mime
			e = re.search("^\w+/(.+)$",res.mime)
			ext = e.group(1)
			if res.attributes.fileName:
				resource_filename = res.attributes.fileName
			else:
				resource_filename = res.guid + "." + ext
			# Always base caches on the GUID
			resource_name = notebook_cache_path + "/" + res.guid + "." + ext
		        file = open(resource_name, "w")
			file.write(res.data.body)
			file.close()
			linkname = notebook_file_path + "/" + note.title + "-" + resource_filename
		   	if os.path.exists(linkname):
				os.remove(linkname)		
			os.symlink(resource_name, linkname)
			print "     -> ", resource_filename, " (Updated)"

			# Update contentHash of resource
			writeContentHash(res.guid, res.data.bodyHash)

