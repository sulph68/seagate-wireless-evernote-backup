#!/usr/bin/python
# We use the code from python OAuth example as the basis to authenticate
# https://gist.github.com/inkedmn/5041037

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

http_loc = "https://fuel.local/plugins/evernote/oauth_two.py"

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
# Provide the URL where the Evernote Cloud API should 
# redirect the user after the request token has been
# generated. In this example, localhost is used; note
# that in this example, we're copying the URLs manually
# and that, in production, this URL will need to 
# automatically parse the response and send the user
# to the next step in the flow.
##
request_token = client.get_request_token(http_loc)

token_secret = plugin_path + "/token_secret"
f = open(token_secret, "w")
f.write(request_token['oauth_token_secret'])
f.close()

##
# Prompt the user to open the request URL in their browser
##
print "Content-type: text/html\n\n" 
print "<html><body>"
print "<script>window.location='" + client.get_authorize_url(request_token) + "';</script>"
print "Evernote OAuth"
print "</body></html>"
