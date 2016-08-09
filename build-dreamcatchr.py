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
	key = "drm-%10f" % (int(time.time()) - 4388635)

	# Execute the CMD
	cmd = "pyinstaller \"%s\drmctchr\dreamcatchr.py\" -F -n drm-%s --distpath \"%s\dist\" --specpath \"spec\" --key \"%s\" --clean\n" % (cwd, buildVersion, cwd, key)
	os.system(cmd)

	# Pause
	sys.exit(0)
except Exception as e:
	print "Error: " + str(e)
	sys.exit(0)
