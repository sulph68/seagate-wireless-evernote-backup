Evernote Notes Backup Plugin
----------------------------

This is a python driven evernote Notes Backup script for the Seagate
Wireless or LaCie drive.
The intention is to be able to run this on a Seagate Wireless Drive and
have it pull down all
notebooks in the authenticated account and back it up into ENML and HTML
format.

Resources are also downloaded and extracted to be named alongside the
notes.

These scripts has not been tested on anything else.

Requirements
------------
The drive would have to be modded with the improvements from
http://hackseagatesatellite.com

Setup
----
Download and extract the files into the root of your drive.
If you are copying them over USB, it would be in
> /plugins/evernote
> /
If you are copying over FTP, the files should be located in
> /static/Data/1/plugins/evernote
> /
Once done, you should boot up your drive (if not already booted) and
telnet into it. Run the following.
> * cd /static/Data/1/plugins/evernote
> * ./setup.sh
> 
This would create a set of folders to hold the backup content of
evernote and also create a *evernote* folder within your *Data*
directory. This would allow you to browse to the folder within the GUI.

A custom script is also copied to allow you to run the backup from the
GUI.

**BEFORE YOU BEGIN** You would have to obtain a valid developer token
for your evernote account. This can be obtained at https://www.evernote.com/api/DeveloperToken.action

Note this taken from the evernote developer site

> Please save this token in a safe spot. After you leave this page, if you forget or lose your token you will have to generate a new one.
> **Developer tokens**
> If you are using the API to access only your Evernote account for personal use, you don't need to go through the OAuth authorization process. Instead, you can get a developer token that will allow you to access your account through the API.
> Your developer token grants full access to your Evernote account, so don't share it with anybody else! If you suspect that your developer token has been stolen, you can revoke it by visiting the developer token page 

Once you have obtained a Developer Auth token for your account, you would need to put that information into the */static/Data/1/plugins/evernote/authToken* file.

It would look something like this.
> S=d18:U=5e234e:E=7567456fxf5sdad:C=sdf5456svdsds42:P=3rf:A=en-devtoken:V=2:H=7ce0b0091024477090dfd1414ebce982

Make sure that the file only contain the one line.

File Structure
--------------
These folders created to STORE the notes
* cache - the actual downloaded notes and attached resources. ENML files
are also converted to HTML for easy viewing
* files - contains the links to cache with the notes and resources named
based on titles
* contentHash - contains the content MD5 to help detect changes based on
GUID of the content

Every notebook is created as its own folder. 

**Take Note** The script DOES NOT remove any notes from your evernote
account! It also does not do any match between Evernote and the local
copies. It will only pull down what is available in Evernote and keep a
copy locally.

While it is likely to contain everything that's in Evernote, you should
do a check if there is anything critical in there.

Running the Notes Backup
------------------------
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

Cleanup or Re-sync
------------------
To cleanup all the backups, simply delete the folders
* files
* cache
* contentHash

Re-run setup.sh as stated above and revisit index.py to re-authorize the
account you want to download from.
