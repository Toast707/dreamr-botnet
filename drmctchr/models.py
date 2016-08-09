class PeerMessage():
	msgId           = ""
	msgType         = 0
	msgTime         = 0
	msgReturn       = ""
	msgSender       = ""
	msgSenderPublic = ""
	msgData         = ""

	def __init__(self, msgId, msgType, msgTime, msgReturn, msgSender, msgSenderPublic, msgData):
		self.msgId           = msgId
		self.msgType         = msgType
		self.msgTime         = msgTime
		self.msgReturn       = msgReturn
		self.msgSender       = msgSender
		self.msgSenderPublic = msgSenderPublic
		self.msgData         = msgData

class UserCreds():
	contentUser = ""
	contentPass = ""
	contentComment = "" # site name/login for
	def __init__(self, contentUser, contentPass, contentComment):
		self.contentUser = contentUser
		self.contentPass = contentPass
		self.contentComment = contentComment

# Might need to be a class in the future. Not sure yet, easy change
class ContentKey():
	contentID  = "" # ID of the content which should match the header
	contentName = "" # name of file if a file
	contentTime = 0 # timestamp for the file matching the message timestamp
	contentKey = "" # AES key
	def __init__(self, contentID, contentName, contentTime, contentKey):
		self.contentID = contentID
		self.contentName = contentName
		self.contentTime = contentTime
		self.contentKey = contentKey

# Class to handle the storing of lists of hosts, their public keys, and LAST TIME WE SAW THEM
class NetworkHost():
	hostAddr = ""
	hostID = ""
	isServer = False
	publicKey = ""
	lastSeen = 0
	def __init__(self, hostAddr, isServer, publicKey, lastSeen):
		self.hostAddr = hostAddr
		self.isServer = isServer
		self.publicKey = publicKey
		self.lastSeen = lastSeen
