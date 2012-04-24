'''
This is an empty module
Since GPylint application is written in Gtk3 and pylint actually executes
source code, I need to create empty module with name gtk.py so I prevent pylint
from importing both gtk3 and gtk2. Otherwise we'd get SIGSEV while checking Gtk2
application
'''
