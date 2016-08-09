import os
import time
import threading

from core import *

class Garbage(threading.Thread):
	fileLocation = ""
	countdown = 0

	def __init__(self, fileLocation, countdown=420):
		threading.Thread.__init__(self)
		debug("garbage", "Garbage Init - The file will be deleted in 420 seconds.")
		self.fileLocation = fileLocation
		self.countdown = countdown

	# Run everything in a whole nother thread for <3 and the happy times.
	def run(self):
		try:
			# delete happens later
			time.sleep(self.countdown)
			unhideFile(self.fileLocation)
			#execute("attrib", ["-R", "-A", "-S", "-H", self.fileLocation], False)

			# Windows will say perm denied until NTFS
			time.sleep(2)

			# Write junk all over the files
			with open(self.fileLocation, "r+b") as handle:
				handle.seek(0, 2)
				size = handle.tell()
				handle.seek(0, 0)
				i = 0
				while (i < size):
					handle.write('\0')
					i += 1
		except Exception as e:
			pass

		# remove the file pointer
		os.remove(self.fileLocation)