#!/bin/python3

import ast

##################################################################################

src = ""
with open("example/client.py", "r") as file:
	src = file.read()

##################################################################################
##################################################################################

class SocketReference:
	"""Every time a known socket gets referenced, it'll be listed here"""
	def __init__(self):
		self.method = ""
		self.attribute = ""

		self.node = None
		self.parentNode = None
		self.childNode = None

##################################################################################

class Socket:
	"""Sockets that have been discovered"""
	def __init__(self):
		self.aliases = []
		self.references = []

		self.node = None
		self.parentNode = None
		self.childNode = None

	def AddReference(self, aRef):
		self.references.append(aRef)

##################################################################################
##################################################################################

sockets = []

def ExtractVariables(node):
	print("\t\tExtracting variables:")
	for field, value in ast.iter_fields(node):
		if isinstance(node, ast.AST):
			fields = [(name, str_node(node, None)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
			if (node.__class__.__name__ == "Name"):
				#for field in fields:
				print("\t\tVariable name? {}".format("")) #field[1]


def str_node(node, parentNode):
	if isinstance(node, ast.AST):
		fields = [(name, str_node(val, parentNode)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
		# Call(func=Name(id='Exit', ctx=Load()), args=[<_ast.Name object at 0x7fb03dbe89e8>], keywords=[])
		# Call = node.__class__.__name__
		# func=Name = field in fields
		rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields)) + ')'

		if (node.__class__.__name__ == "Assign"):
			for field in fields:
				if (field[0] == "value") and ("id='socket'" in field[1]):
					sock = Socket()
					sock.aliases.append("???")
					sock.childNode = None
					sock.parentNode = parentNode
					sock.node = node
					sockets.append(sock)
					print("Found a socket: {}".format(repr(sock)))
					#print(type(field))
					#print(field)
		
		elif (node.__class__.__name__ == "Call"):
			#for sock in sockets:
			for field in fields:
				if ("func" in field[0]) and ("attr='connect'" in field[1]):
					print("Connect found for socket? {}\n\tfield[0]: {}".format(field[1], field[0]))
					#ExtractVariables(node)
				if ("func" in field[0]) and ("attr='send'" in field[1]):
					print("Send found for socket? {}\n\tfield[0]: {}".format(field[1], field[0]))
				if ("func" in field[0]) and ("attr='recv'" in field[1]):
					print("Recv found for socket? {}\n\tfield[0]: {}".format(field[1], field[0]))

		return rv
	else:
		return repr(node)

##################################################################################

def ast_visit(node, parentNode, level=0):
	#with open("out.txt", 'a') as f:
	#	f.write('  ' * level + str_node(node) + '\n')
	#	print('  ' * level + str_node(node))
	str_node(node, parentNode)
	for field, value in ast.iter_fields(node):
		if (type(value) == ast.Call):
			print("CALL FOUND")
		#print("F: {}\nV:{}\n".format(field, value))
		
		if isinstance(value, list):
			for item in value:
				if (type(item) == ast.Assign):
					print("ASSIGN FOUND")
				if isinstance(item, ast.AST):
					ast_visit(item, node, level=level+1)
		elif isinstance(value, ast.AST):
			ast_visit(value, node, level=level+1)

##################################################################################
##################################################################################

#Strat:
#	Check for Asssign, where:
#		Call = Socket, where Child or Child of children:
#			Attribute = "AF_INET"

startNode = ast.parse(src)

ast_visit(startNode, None)