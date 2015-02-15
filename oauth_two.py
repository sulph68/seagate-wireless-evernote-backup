#!/usr/bin/python
# We use the code from python OAuth example as the basis to authenticate
# https://gist.github.com/inkedmn/5041037

import os
import sys
sys.path.append("/static/Data/1/plugins/evernote/lib")

# Python OAuth example

import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient

plugin_name = "evernote"                                  
plugin_dir = "/static/Data/1/plugins"                      
                                                                       
plugin_path = plugin_dir + "/" + plugin_name                           
plugin_file_path = plugin_path + "/files"                                                                         
plugin_cache_path = plugin_path + "/cache"                                                                        
plugin_contentHash_path = plugin_path + "/contentHash"

##
# Helper function to turn query string parameters into a 
# Python dictionary
##
def parse_query_string(authorize_url):
    uargs = authorize_url.split('?')
    vals = {}
    if len(uargs) == 1:
        raise Exception('Invalid Authorization URL')
    for pair in uargs[1].split('&'):
        key, value = pair.split('=', 1)
        vals[key] = value
    return vals

##
# Create an instance of EvernoteClient using your API
# key (consumer key and consumer secret)
##
client = EvernoteClient(
            consumer_key = 'sulph68',
            consumer_secret = '45ca10219801d5a5',
            sandbox = True
        )

##
# Parse the URL to get the OAuth verifier
##
authurl = os.environ.get("QUERY_STRING", "NOQS")
if authurl == "NOQS":
	print "Content-type: text/html\n\n"
	print "<html><body>Error: No Query String</body></html>"
	exit()

print "Content-type: text/html\n\n"               
print "<html><body><pre>"
# print "Query String: " + authurl

vals = parse_query_string("http://localhost/?" + authurl)

if not 'oauth_verifier' in vals:
        print "Error: No OAuth Verifier</body></html>"
        exit()

# print "OAuth: " + vals['oauth_verifier']

# Read the token secrets
token_secret = plugin_path + "/token_secret"
f = open(token_secret, "r")
oauth_token_secret = f.readline()
f.close()
oauth_token_secret.rstrip()

auth_token = client.get_access_token(
            vals['oauth_token'],
            oauth_token_secret,
            vals['oauth_verifier']
        )

# Save the auth token to a file
auth_token_file = plugin_path + "/authToken" 
f = open(auth_token_file, "w")
f.write(auth_token)
f.close()

# delete token_secret file
os.remove(token_secret)

##
# Create a new EvernoteClient instance with our auth
# token.
##
client = EvernoteClient(token=auth_token, sandbox=True)

##
# Test the auth token...
##
userStore = client.get_user_store()
user = userStore.getUser()

# Print successful output in form
print "Notes Backup"
print "-------------"
print "Authentication successful"
print "Your username is: ", user.username

note_store = client.get_note_store()

# List all of the notebooks in the user's account
notebooks = note_store.listNotebooks()

print "Found ", len(notebooks), " notebooks:"
for notebook in notebooks:
    print "  * ", notebook.name

print "To backup your evernote into the drive, telnet into your drive and run ./evernote-sync.py in the evernote plugin directory"
print "Alternatively you can run the 'Custom Script' action in the Settings of the drive"
print "</pre></body></html>"
