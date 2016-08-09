import os
import time
import urllib2
import threading

from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer

from core import *

# FTP server will drop files in the bot's web directory for easy access.
class FTPServer(threading.Thread):
	path = ""
	# The constructor for the ftp server
	def __init__(self, path):
		threading.Thread.__init__(self)
		debug("ftp", "The ftp server turns on.")
		self.path = path

	def run(self):
		global FTP_PORT
		while (True):
			try:
				time.sleep(15)
				os.chdir(self.path)
				address = ("0.0.0.0", FTP_PORT)
				authorizer = DummyAuthorizer() ## Yeah the guy called it that
				authorizer.add_user('lucid', 'dreamr', self.path, perm='elradfmw')
				handler = FTPHandler
				handler.authorizer = authorizer
				server = servers.FTPServer(address, handler)
				server.serve_forever()
			except Exception as e:
				debug("ftp", "Error -> %s" % str(e))
			time.sleep(3)