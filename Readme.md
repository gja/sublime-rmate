Open things via rmate that will open in local sublime.

Installation:
-------------
* Install this via sublime package control (OR just checkout this git repo into your packages directory)
* Start sublime rmate server from the cmd-shift-p menu
* Port forward 52698 from the remote server to localhost (ssh -R 52698:localhost:52698 user@server)
* Download the rmate executable there
* rmate filename

Based On:
--------
Scroll down to the rmate section here: http://blog.macromates.com/2011/mate-and-rmate/

Known Issues:
-------------
* File titles are not correct
* If you save a file as something else, it will not disconnect from the server
* Temporary files are not deleted
