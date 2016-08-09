import os
import time
import pickle

from config import *
from core import *

class SeenUnseen():
	seenMessages = []

	def __init__(self):
		self.loadSeen()
		return

	# Have we seen this message before?
	# True = seen before
	def seen(self, msgID):
		try:
			for seenID in self.seenMessages:
				if (seenID == msgID):
					print("dropped seen msg")
					return True
			# None on the entries matched, so it's unique.
			self.seenMessages.append(msgID)
			with open(SeenLocation, "wb") as handle:
				pickle.dump(self.seenMessages, handle)
			print("keeping msg")
			return False
		except Exception as e:
			print("seen error -> %s" % str(e))
		print("keeping msg")
		return False

	# Load seen list from pickle encoded storage
	def loadSeen(self):
		try:
			if (os.path.isfile(SeenLocation)):
				with open(SeenLocation, "rb") as handle:
					self.seenMessages = pickle.load(handle)
		except:
			pass
 		return False