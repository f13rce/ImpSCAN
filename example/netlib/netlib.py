'''
	Python3 Network Library Example
'''

import socket
import sys
from threading import Thread, Lock
import time
import os

pid = os.getpid()

# Globals
ip = "127.0.0.1"
port = 1313
buffer_size = 4096
reconnectTimeout = 3 # seconds

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Warning 1: No IPv6 implementation

def Initialize(aIsClient, aRecvCallbackFunc):
	if (aIsClient):
		# Try to connect
		while not Connect():
			print("Retrying in {} seconds...".format(reconnectTimeout))
			time.sleep(reconnectTimeout)

	# Set up receive and send threads 
	try:
		rcv = Thread(target=Receive, args=(aRecvCallbackFunc,))
		rcv.start()

		netlibMain = Thread(target=NetlibMain)
		netlibMain.start()

	# Stop application on exception
	except:
		Exit(s)

def NetlibMain():
	while s != None:
		# Keep application alive
		time.sleep(1)

# Funcs
def Connect():
	try:
		s.connect((ip, port))
		return True
	except Exception as ex:
		print("Failed to connect. {}\n".format(ex))
		return False

def Exit(aSocket = None):
	print("\nGoodbye.")
	if aSocket != None:
		aSocket.close()
	global s
	s.close()
	sys.exit()
	os.system("kill -9 {}".format(pid))

def Send(aMessage):
	try:
			str_send = aMessage.encode('utf-8')
			#str_send = str_send[:64] # This must fix mistake #1
			#str_send = "test" # This also fixes mistake #1
			#someVar = "potato"
			s.send(str_send)
	except Exception as ex:
		print("Socket is goofed: {}".format(ex))
		Exit(s)

def Receive(aRecvCallbackFunc):
	while True:
		if (s != None):
			str_recv = s.recv(buffer_size)
			if (len(str_recv) > 0):
				aRecvCallbackFunc(str_recv.decode('utf-8'))
			else:
				break
		else:
			break
	Exit(s)