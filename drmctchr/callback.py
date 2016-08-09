#!C:\Python27\python.exe
import os
import time
import urllib2
import threading
from core import *

# Calls back to a single server that will recieve the callback requests.
class HTTPCallbackThread(threading.Thread):
	serverAddr = ""
	clientID = ""

	def __init__(self, serverAddr, clientID):
		threading.Thread.__init__(self) # calling super method
		self.serverAddr = serverAddr
		self.clientID = clientID

	# Run it in another thread
	def run(self):
		try:
			callbackURL = "http://%s/callback.php?id=%s" % (self.serverAddr, self.clientID)
			debug("callback", "Calling back to: %s" % callbackURL)
			urllib2.urlopen(callbackURL)
		except Exception as e:
			debug("callback", "Error connecting to %s -> %s" % (self.serverAddr, str(e)))
