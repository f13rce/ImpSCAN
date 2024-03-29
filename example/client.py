'''
	Python3 Chat Client
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

runApp = True

# Funcs
def Connect():
	try:
		s.connect((ip, port))
		return True
	except Exception as ex:
		print("Failed to connect. {}\n".format(ex))
		return False

def Exit(socket):
	print("\nGoodbye.")
	socket.close()
	sys.exit()
	os.system("kill -9 {}".format(pid))

def Send():
	try:
		while True: # Warning 2: This allows spamming of data
			# While(test=NameConstant(value=True)
			sys.stdout.write("Say: ")
			sys.stdout.flush()
			str_send = sys.stdin.readline() # Mistake 1: Potential for unlimited bandwidth
			str_send = str_send.encode('utf-8')
			#str_send = str_send[:64] # This must fix mistake #1
			#str_send = "test" # This also fixes mistake #1
			#someVar = "potato"
			#str_send = someVar # This could fix mistake #1, depending on the size of this string
			str_send = str_send # This should be ignored
			s.send(str_send)
	except Exception as ex:
		print("Socket is goofed: {}".format(ex))
	Exit(s)

def Receive():
	while True:
		if (s != None):
			str_recv = s.recv(buffer_size)
			if (len(str_recv) > 0):
				sys.stdout.write("\r{}".format(str_recv.decode('utf-8'))) # Already includes a \n
				sys.stdout.write("Say: ")
				sys.stdout.flush()
			else:
				break
		else:
			break
	Exit(s)

# "Main"

# Try to connect
while not Connect():
	print("Retrying in {} seconds...".format(reconnectTimeout))
	time.sleep(reconnectTimeout)

# Set up receive and send threads 
try:
	snd = Thread(target=Send)
	rcv = Thread(target=Receive)

	snd.start()
	rcv.start()

	while True:
		# Keep application alive
		time.sleep(1)

# Stop application on exception
except:
	Exit(s)