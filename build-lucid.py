import os
import time
import sys
import shutil

try:
	# Get the build version from ver.txt
	cwd = os.getcwd()
	file = open("version.txt", "r")
	buildVersion = file.readline()
	file.close()

	# Add extra obfuscation
	key = "lucid-dreamr-%10f" % (int(time.time()) - 22535235)	
	cmd = "pyinstaller \"%s\drmctchr\lucid-dreamr.py\" -F --clean -n lucid-dreamr-%s --distpath \"%s\dist\" --specpath \"spec\" --key \"%s\"\n" % (cwd, buildVersion, cwd, key)
	os.system(cmd)

	# Pause
	sys.exit(0)
except Exception as e:
	print "Error: " + str(e)
	sys.exit(0)
