#!C:\Python27\python.exe
import os
import time
import string
import urllib2
import threading

from core import *
from Context import Dreamr

class HTTPBootstrapThread(threading.Thread):
	serverAddr = ""

	def __init__(self, serverAddr):
		threading.Thread.__init__(self) # calling super method
		self.serverAddr = serverAddr

	def run(self):
		try:
			callbackURL = "http://%s/callback.php?hosts=please" % (self.serverAddr)
			debug("callback", "Looking for hosts on: %s" % callbackURL)
			response = urllib2.urlopen(callbackURL).read()
			hostlist = string.split(response, ":")
			for host in hostlist:
				if (host):
					if (int(time.time()) % 3 == 0):
						Dreamr.keystore.addPendingHost(host)
		except Exception as e:
			debug("callback", "Error connecting to %s -> %s" % (self.serverAddr, str(e)))