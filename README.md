# Evernote Notes Backup Plugin

This is a python driven evernote Notes Backup script for the Seagate
Wireless or LaCie drive.
The intention is to be able to run this on a Seagate Wireless Drive and
have it pull down all
notebooks in the authenticated account and back it up into ENML and HTML
format.

Resources are also downloaded and extracted to be named alongside the
notes.

These scripts has not been tested on anything else.

## Features

Here are some features of this script

* Fetches all notes in Evernote ENML format and converts them into HTML formats (thanks to some python libraries)
* Fetches all corresponding resources of the notes
* Stores every note uniquely as Evernote does but links to readable title names. Also for their corresponding resources
* Ability to sync all notebooks or just one named notebook by setting the sync_notebook variable in the evernote-sync.py script
* Automatically recover form last known sync point if interrupted via a Checkpoint
* Able to force a refresh of all notes by setting the refresh_all variable to 1 or 0
* Delays between each contact to Evernote to handle rate limitations and automatically delay and resumes is the rate limit is hit

## Requirements

The drive would have to be modded with the improvements from
<http://hackseagatesatellite.com>

## Setup

Download and extract the files into the root of your drive.
If you are copying them over USB, it would be in

* /plugins/evernote

If you are copying over FTP, the files should be located in

* /static/Data/1/plugins/evernote

Once done, you should boot up your drive (if not already booted) and
telnet into it. Run the following.
> * cd /static/Data/1/plugins/evernote
> * ./setup.sh
 
This would create a set of folders to hold the backup content of
evernote and also create a *evernote* folder within your *Data*
directory. This would allow you to browse to the folder within the GUI.

A custom script is also copied to allow you to run the backup from the
GUI.

### BEFORE YOU BEGIN
You would have to obtain a valid developer token *OR* authorize your evernote account. You also need a live internet connection in order to sync.

#### Authorise your evernote account
You can make use of this script by authorising your account against it. After installing the script, simply run (if you are on SSL - if not, use http:// instead). e.g.

* <https://fuel.local/plugins/evernote/oauth_one.py>

This will bring you to the Evernote website and ask you to login and authorise the script. Once done, it would automatically redirect you back to your Seagate wireless drive and show you your list of notebooks available. If you can see that, the authorisation is successful.

 
####Developer tokens

Developer tokens can be obtained at <https://www.evernote.com/api/DeveloperToken.action>

This is taken from the evernote developer site.
> Please save this token in a safe spot. After you leave this page, if you forget or lose your token you will have to generate a new one.
> 
> If you are using the API to access only your Evernote account for personal use, you don't need to go through the OAuth authorization process. Instead, you can get a developer token that will allow you to access your account through the API.
> Your developer token grants full access to your Evernote account, so don't share it with anybody else! If you suspect that your developer token has been stolen, you can revoke it by visiting the developer token page 

Once you have obtained a Developer Auth token for your account, you would need to put that information into the */static/Data/1/plugins/evernote/authToken* file.

> It would look something like this.
> S=d18:U=5e234e:E=7567456fxf5sdad:C=sdf5456svdsds42:P=3rf:A=en-devtoken:V=2:H=7ce0b0091024477090dfd1414ebce982

> Make sure that the file only contain the one line.

##File Structure

These folders created to STORE the notes

* cache - the actual downloaded notes and attached resources. ENML files
are also converted to HTML for easy viewing
* files - contains the links to cache with the notes and resources named
based on titles
* contentHash - contains the content MD5 to help detect changes based on
GUID of the content

#### These files and folders store information that makes the script run
* lib - All required libraries to make this work
* oauth_[one|two].py - authorisation scripts
* authToken - This is the all important file that keeps your authorisation token
* config.cfg - This contains the checkpoint of the sync to allow the script to pick up where it left off if the script is interrupted 

Every notebook is created as its own folder. 

**Take Note** The script DOES NOT remove any notes from your evernote
account! It also does not do any match between Evernote and the local
copies. It will only pull down what is available in Evernote and keep a
copy locally.

While it is likely to contain everything that's in Evernote, you should
do a check if there is anything critical in there.

## Running the Notes Backup

Telnet into the device and run
> * cd /static/Data/1/plugins/evernote
> * ./run_evernote_sync.sh
> 
OR

Go to the Settings page in your GUI
> * Click on Services
> * Scroll to Custom Scripts
> * Click on "Run"
> 
A copy of the log is available at /plugins/evernote-sync.log

## Cleanup or Re-sync

To cleanup all the backups, simply delete the folders
* files
* cache
* contentHash

Re-run setup.sh as stated above and revisit index.py to re-authorize the
account you want to download from.

## Known Issues and notes
* Note titles are unescaped. This can lead to some weird behaviour when the links are viewed from a browser. However, the links are still correctly created and the files exists.
* While only tested frequently on the Seagate drive, this should work with any system that runs python when coupled with a developer token

## Disclaimer and license
This script is provided as is and i would not be held liable if your notes is to go missing. That said, as is, the script does not delete anything from your Evernote store and only downloads. 

I am no lawyer. But i would like to release this under [GPL](http://www.gnu.org/copyleft/gpl.html). A short copy of the license is available in the LICENSE file. All rights to libraries i used in this software also belongs to their respective owners. So please respect that. Some codes were based on available sample codes on the internet. Kudos goes to them for without which, this script wouldn't have been possible.

An important note is that you DO NOT share or re-use the registered Evernote Tokens for the sake of all other users and integrity of the intent of this software. If notified, i would be forced to remove them and we would all have to only rely on developer tokens to move forward.

#### Footnotes
If you like this script or find it useful, i'd appreciate a quick note of thanks at sulp68 <at> gmail dot com, send me a [small token of appreciation] (https://sulph68.wordpress.com/kudos-and-thanks/") or visit some of my other works at <https://sulph68.wordpress.com>
