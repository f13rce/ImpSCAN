import sys
import netlib

def OnReceive(aMessage):
	sys.stdout.write("\r{}".format(aMessage)) # Already includes a \n
	sys.stdout.write("Say: ")
	sys.stdout.flush()

netlib.Initialize(True, OnReceive)

try:
	while True:
		sys.stdout.write("Say: ")
		sys.stdout.flush()
		str_send = sys.stdin.readline() # Mistake 1: Potential for unlimited bandwidth
		netlib.Send(str_send)
except:
	netlib.Exit()