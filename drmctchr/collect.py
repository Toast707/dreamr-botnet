import os
import time
import urllib2
import threading

from ftplib import FTP
from core import *

class Collect(threading.Thread):
	sourcePath = ""
	sourceName = ""
	serverAddr = ""

	def __init__(self, sourcePath, sourceName, serverAddr):
		threading.Thread.__init__(self)
		debug("collect", "Uploading the file to remote server.")
		self.sourcePath = sourcePath
		self.sourceName = sourceName
		self.serverAddr = serverAddr

	def run(self):
		os.chdir(self.sourcePath) # because of the initial move
		print("Uploading: %s" % self.sourceName)
		# Try downloading the file from another server
		try:
			ftp = FTP()
			ftp.connect("%s" % self.serverAddr, "8080")
			ftp.login("lucid", "dreamr")
			with open("%s%s" % (self.sourcePath, self.sourceName), 'rb') as handle:
				ftp.storbinary("STOR %s" % self.sourceName, handle)
		except Exception as e:
			debug("collect", "Upload file failed. -> %s" % str(e))
