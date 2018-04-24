Attendance Tracker Readme
=========================

Bin
---
the official release for the dbbackup django module is bugged and does not allow for excluding tables, although it is partially implemented. This version of the tool works as intented (by adding a DBBACKUP\_EXCLUDED list to settings.py)


## Setup
## (Updated May 2018)
How to setup the checkin system 
Begin by opening the folder named setup
Follow the Ubuntu Env Setup.txt document
If you are not using the git (or the git account is no longer available you can skip that section)

Once the Ubuntu environment is set up you can open the CreateDatabase.txt file. 
	This file will set up the database with the correct tables as well as some beginning dummy data 
		A semester, a super user, and a course are created in this example. 

OPTIONAL:
You can open the Ubuntu Env Bash Alias.txt 
	this is to add some additional functionality to your bash that speeds up some terminal commands



Scripts OLD SETUP 
-------
All scripts contain within the scripts directory should be executed from the project root (ie. where manage.py is located)

- install.sh: this script should be run to install all of the applications necessary dependancies. Should likely be followed by a call to dbPopulate.sh
- dbPopulate.sh: populate the database with test data. Any test data should be added through this script, so that everyone has the same data to work with
- migrate\_brutal.sh: if dbPopulate.sh fails due to migration issues (which is likely to happend because development is happening on different machines), execute this script. It will wipe the entire database, but it will work
- fixPermissions.sh: ensure that all files/folders have the correct permissions and ownership
- runServer.sh: executes the server on port 18000, making it accessible outside of localhost
- backup.sh: backups up the db and stores it in the backups folder
- restore\_latest.sh: restores the most recent backup found in the backups folder
------- end old setup environment

