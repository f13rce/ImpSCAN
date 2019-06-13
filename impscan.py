#!/bin/python3

import ast

functionKeywords = ["socket", "connect", "send", "recv"]
functionNames = []

## Funcs
def PrintNode(aNode):
	if isinstance(aNode, ast.AST):
		fields = [(name, PrintNode(val)) for name, val in ast.iter_fields(aNode) if name not in ('left', 'right')]
		# Call(func=Name(id='Exit', ctx=Load()), args=[<_ast.Name object at 0x7fb03dbe89e8>], keywords=[])
		# Call = node.__class__.__name__
		# func=Name = field in fields
		rv = '%s(%s' % (aNode.__class__.__name__, ', '.join('%s=%s' % field for field in fields)) + ')'

		return rv
	else:
		return repr(aNode)

def HandleNode(aNode, aNodePath, aState):
	PrintNode(aNode)

	fields = [(name, PrintNode(val)) for name, val in ast.iter_fields(aNode) if name not in ('left', 'right')]

	if (aState == 1): # and (isinstance(aNode, ast.AST)):
		for field in fields:
			if field[0] != "value" and field[0] != "func":
				continue
			#print(repr(field))
			#id='variable_name'
			#attr=function, e.g.:
			if aState == 1:
				for funcName in functionNames:
					if funcName in field[0] or funcName in field[1]:
						print("got something maybe {}:\n\t{}".format(funcName, repr(field)))


	elif (aState == 0) and (isinstance(aNode, ast.Call)):
		for field in fields:
			if (field[0] == "func"):
				for keyword in functionKeywords:
					if ("attr='{}'".format(keyword) in field[1]):
						#print("##########################################################################")
						print("Found call: {}\t{}".format(keyword, repr(field)))
						# Find function it was called from
						foundFunc = False
						for path in reversed(aNodePath):
							pathName = PrintNode(path)
							if ("FunctionDef" in pathName[:len("FunctionDef")]):
								#print(pathName)
								funcName = pathName.split("'")[1]
								print("It's coming from function named {}".format(funcName))
								functionNames.append(funcName)
								foundFunc = True
								break
						if not foundFunc:
							print("This call is not called from inside a function")
						#
						#i = 0
						#for path in aNodePath:
						#	i += 1
						#	print("\t{}:\t{}".format(i, PrintNode(path)))
						#print("\n")

def IterateThroughNodes(aNode, aNodePath, aState):
	aNodePath.append(aNode)
	HandleNode(aNode, aNodePath, aState)

	for field, value in ast.iter_fields(aNode):
		if isinstance(value, list):
			for item in value:
				if isinstance(item, ast.AST):
					IterateThroughNodes(item, aNodePath, aState)
		elif isinstance(value, ast.AST):
			IterateThroughNodes(value, aNodePath, aState)

## "Main"
src = ""
with open("example/client.py", "r") as file:
	src = file.read()

nodePath = []

startNode = ast.parse(src)
nodePath.append(startNode)

#HandleNode(startNode, nodePath)
state = 0
IterateThroughNodes(startNode, nodePath, state)

print("#################################################")
print("Done finding funcs - finding func references now")
print("Found funcs: {}".format(repr(functionNames)))
print("#################################################")


state = 1
IterateThroughNodes(startNode, nodePath, state)
