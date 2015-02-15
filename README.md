Evernote Notes Backup Plugin
----------------------------

This is a python driven evernote Notes Backup script for the Seagate Wireless or LaCie drive.
The intention is to be able to run this on a Seagate Wireless Drive and have it pull down all
notebooks in the authenticated account and back it up into ENML and HTML format.

Resources are also downloaded and extracted to be named alongside the notes.

These scripts has not been tested on anything else.

Requirements
------------
The drive would have to be modded with the improvements from http://hackseagatesatellite.com

Setup
----
Download and extract the files into the root of your drive.
If you are copying them over USB, it would be in
> /plugins/evernote

If you are copying over FTP, the files should be located in
> /static/Data/1/plugins/evernote

Once done, you should boot up your drive (if not already booted) and telnet into it. Run the following.
> * cd /static/Data/1/plugins/evernote
> * ./setup.sh

This would create a set of folders to hold the backup content of evernote and also create a *evernote* folder within your *Data* directory. This would allow you to browse to the folder within the GUI.

A custom script is also copied to allow you to run the backup from the GUI.

**BEFORE YOU BEGIN** You would have to obtain a valid copy of oauth_one.py and oauth_two.py containing the production information of this app (Assuming evernote approves) by emailing me at sulph68 at gmail dot com. Otherwise, you would have to edit these two files to include your own consumer secret and key. You might also need to change the code a little to also handle the sandbox environment.

You then need to complete the authorization to perform a backup from Evernote by pointing your browser to http://yourhostname.local/plugins/evernote/index.py and follow the instructions. If everything went well, you should see the list of your notebooks appear.

For example, http://fuel.local/plugins/evernote/index.py

File Structure
--------------
These folders created to STORE the notes
* cache - the actual downloaded notes and attached resources. ENML files are also converted to HTML for easy viewing
* files - contains the links to cache with the notes and resources named based on titles
* contentHash - contains the content MD5 to help detect changes based on GUID of the content

Every notebook is created as its own folder. 

**Take Note** The script DOES NOT remove any notes from your evernote account! It also does not do any match between Evernote and the local copies. It will only pull down what is available in Evernote and keep a copy locally.

While it is likely to contain everything that's in Evernote, you should do a check if there is anything critical in there.

Running the Notes Backup
------------------------
Telnet into the device and run
> * cd /static/Data/1/plugins/evernote
> * ./run_evernote_sync.sh

OR

Go to the Settings page in your GUI
> * Click on Services
> * Scroll to Custom Scripts
> * Click on "Run"

A copy of the log is available at /plugins/evernote-sync.log

Cleanup or Re-sync
------------------
To cleanup all the backups, simply delete the folders
* files
* cache
* contentHash

Delete the following file
* authToken

Re-run setup.sh as stated above and revisit index.py to re-authorize the account you want to download from.
