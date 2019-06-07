'''
	Python3 Chat Server
'''

''' This is another comment using a multiline '''

import socket
import threading
import sys
import random
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = "127.0.0.1"
port = 1313
buffer_size = 4096

s.bind((ip, port))

s.listen(5)
flag = 0

clientConnections = []

def GetRandomName():
	random.seed(int(time.time()))
	names = ["Bob", "Alice", "Eve", "Trudy", "Pjotr", "Anon"]
	number = random.randint(1000,9999)

	name = random.choice(names) + str(number)
	return name

def BroadcastMessage(aMessage):
	socketsToRemove = []

	for sock in clientConnections:
		try:
			#print("\tSending message to {}".format(sock[1]))
			sock[0].sendto(aMessage.encode('utf-8'), sock[1])
		except Exception as ex:
			print("Failed to broadcast to client: {}".format(ex))
			socketsToRemove.append(sock[2])
			sock[0].close()
			clientConnections.remove(sock)
			continue
	
	for sock in socketsToRemove:
		BroadcastMessage("{} has left the chat.\n".format(name))

def ListenToClient(cliSocket, name):

	while True:
		try:
			str_recv = cliSocket.recv(buffer_size)
			
			if (len(str_recv) > 0):
				str_return = "{}: {}".format(name, str_recv.decode('utf-8'))
				sys.stdout.write(str_return)
				BroadcastMessage(str_return)
			else:
				raise Exception("Connection seems to be terminated.")
		except Exception as ex:
			print("Client disconnected: {}".format(ex))

			# Find connection to destroy
			toDelete = None
			for connection in clientConnections:
				if (connection[0] == cliSocket):
					toDelete = connection
					break
			if (toDelete != None):
				clientConnections.remove(toDelete)
			
			BroadcastMessage("{} has left the chat.\n".format(name))
			break

version = "1.0.0 ALPHA"

print("Successfully started the server on {}:{}!".format(ip, port))
print("\tRunning version: {}".format(version))

try:
	while True:
		connect, addr = s.accept()
		print("Connection incoming from {}".format(str(addr)))

		name = GetRandomName()
		welcomeMessage = "[SERVER] Welcome to the chat server, {}.\n\tServer version: {}\n\tPeople online: {}\n\n".format(name, version, len(clientConnections) + 1)
		connect.sendto(bytes(welcomeMessage, 'utf-8'), addr)

		BroadcastMessage("{} has joined the chat.\n".format(name))

		clientConnections.append([connect, addr, name])

		cliThread = threading.Thread(target=ListenToClient, args=(clientConnections[-1][0], clientConnections[-1][2]))
		cliThread.start()

except Exception as ex:
	print("Exception: {}".format(ex))
	s.close()
	for sock in clientConnections:
		sock.first.close()