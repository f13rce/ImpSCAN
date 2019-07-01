import ast
from math import inf
import sys

import os
from os import listdir
from os.path import isfile, join

functionKeywords = ["socket", "connect", "send", "recv"]
functionNames = []

usesIPV4 = False
usesIPV6 = False

warnings = []
errors = []

maxBytesSent = 4096
writeNodesToFile = True

### Nodes to handle:
# Unlimited bandwidth: Assign(targets=[<_ast.Name object at 0x0000022A5D7F4710>], value=Call(func=Attribute(value=Attribute(value=Name(id='sys', ctx=Load()), attr='stdin', ctx=Load()), attr='readline', ctx=Load()), args=[], keywords=[]))
# 

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

def HandleNode(aNode, aNodePath):
	name = PrintNode(aNode)

	if writeNodesToFile:
		with open("out_{}.txt".format(sys.argv[1].replace('/', '_')), "a") as f:
			f.write("{}\n".format(name))

	fields = [(name, PrintNode(val)) for name, val in ast.iter_fields(aNode) if name not in ('left', 'right')]	

	if (isinstance(aNode, ast.Call)):
			for field in fields:
				# Find socket functionality
				#print(repr(field))
				#id='variable_name'
				#attr=function, e.g.: attr='send'
				if (field[0] == "func"):
					for keyword in functionKeywords:
						if ("attr='{}'".format(keyword) in field[1]):
							#print("##########################################################################")
							# Find socket's variable name
							socketVarName = field[1].split("'")[1]

							print("Found call: {}.{}\t{}".format(socketVarName, keyword, repr(field)))

							# Find related child nodes, such as variable names
							childNodes = []
							for field, value in ast.iter_fields(aNode):
								if isinstance(value, list):
									for item in value:
										if isinstance(item, ast.AST):
											childNodes.append(PrintNode(item))
											#print("\tCHILD: {}".format(PrintNode(item)))
								elif isinstance(value, ast.AST):
									childNodes.append(PrintNode(value))
									#print("\tCHILD: {}".format(PrintNode(value)))

							# Find function it was called from
							foundFunc = False
							for path in reversed(aNodePath):
								pathName = PrintNode(path)
								if ("FunctionDef" in pathName[:len("FunctionDef")]):
									#print(pathName)
									funcName = pathName.split("'")[1]
									print("It's coming from function named {}".format(funcName))
									foundFunc = True
									break
							if not foundFunc:
								print("This call is not called from inside a function")

							# Analyze child nodes
							variableNames = []
							for childNode in childNodes:
								if ("Name(id=" in childNode):
									varName = childNode.split("'")[1]
									if (varName != socketVarName):
										print("\t{}.{} is using a variable named {}".format(socketVarName, keyword, varName))
										variableNames.append(varName)
								# Find IPv4 / IPv6 connectivity
								if (keyword == functionKeywords[0]):
									try:
										if "AF_INET6" in childNode:
											global usesIPV6
											usesIPV6 = True
										elif "AF_INET" in childNode:
											global usesIPV4
											usesIPV4 = True
									except:
										pass

							for varName in variableNames:
								assignMethods = []

								for path in aNodePath:
									nodeText = PrintNode(path)
									subNodes = []
									if ("Assign(" in nodeText):
										
										# Parse child nodes
										for field, value in ast.iter_fields(path):
											if isinstance(value, list):
												for item in value:
													if isinstance(item, ast.AST):
														#print("\tAdding subnode: {}".format(PrintNode(item)))
														subNodes.append(PrintNode(item))
											elif isinstance(value, ast.AST):
												#print("\tAdding subnode: {}".format(PrintNode(value)))
												subNodes.append(PrintNode(value))

										# Does it have the keyword we're looking for?
										hasKeyword = False;
										for subNode in subNodes:
											if varName in subNode:
												hasKeyword = True
												break

										# Check what assigns this variable
										if (hasKeyword):
											searchComponents = ["id", "attr", "slice", "s"]
											for subNode in subNodes:
												searchStrings = ["Call", "Subscript", "Str", "Name"]
												for searchString in searchStrings:
													if ("{}(".format(searchString) in subNode[:len(searchString)+1]):
														#print("\tAnalyzing call node: {}".format(subNode))
														searchOutput = ""
														for component in searchComponents:
															if (component == searchComponents[0]) and (searchString == searchStrings[3]):
																if ("ctx=Load()" in subNode):
																	try:
																		searchStr = "id='"
																		foundName = subNode.split(searchStr)[1].split("'")[0]

																		# Ignore self assignments (E.g.: a = a)
																		if (foundName == varName):
																			continue

																		# TODO: Find length of string size
																		searchOutput = "= {}".format(varName, foundName)
																		assignMethods.append(searchOutput)
																		searchOutput = ""
																	except:
																		pass
															elif (component == searchComponents[0]) or (component == searchComponents[1]):
																try:
																	cutText = subNode
																	while True:
																		index = cutText.index("{}=".format(component))
																		cutText = cutText[index:]
																		foundName = cutText.split("'")[1]

																		if (component == searchComponents[0]):
																			if (searchOutput != varName):
																				searchOutput = "{}".format(foundName)
																			break

																		#print("\tCall {}: {}".format(component, foundName))
																		cutText = cutText[(cutText.index(foundName) + len(foundName)):]

																		if (searchOutput != varName):
																			if (searchOutput != ""):
																				searchOutput += "."
																			searchOutput += "{}".format(foundName)

																except Exception as ex:
																	if (searchOutput != "") and (searchOutput != varName):
																		assignMethods.append("= {}".format(searchOutput))

															elif component == searchComponents[2]:
																try:
																	searchStr = "upper=Num(n="
																	foundName = subNode.split(searchStr)[1][:len(searchStr)].split(")")[0]
																	searchOutput = "resize {}".format(foundName)
																	assignMethods.append(searchOutput)
																	searchOutput = ""
																except:
																	pass

															elif component == searchComponents[3]:
																try:
																	searchStr = "s='"
																	foundName = subNode.split(searchStr)[1][:len(searchStr) + 1].split("'")[0]
																	searchOutput = "resize {}".format(len(foundName) + 1) # Include null terminator
																	assignMethods.append(searchOutput)
																	searchOutput = ""
																except:
																	pass

								# Find unnecessary load and print results
								if assignMethods:
									print("\tAssignment order of {}:".format(varName))
									if (keyword == "send"):
										sentBytesCount = 0
										reason = ""

									for assignMethod in assignMethods:
										# Find unnecessary load
										if (keyword == "send"):
											method = assignMethod.split(" ")[0]
											value = assignMethod.split(" ")[1]
											if (method == "="):
												if (value == "sys.stdin.realine"):
													sentBytesCount = inf
													reason = value
												else:
													sentBytesCount = inf # TODO find out how big this var is
													reason = value
											elif (method == "resize"):
												sentBytesCount = int(value)

										# Print
										print("\t\t{}".format(assignMethod))

									if (keyword == "send"):
										global errors
										if (sentBytesCount == inf):	
											errors.append("Socket {} could be sending infinite amount of bytes because of: {}".format(socketVarName, reason))
										elif (sentBytesCount > maxBytesSent):
											errors.append("Socket {} is sending more than {} bytes in a resize, which could be bad for performance.".format(socketVarName, maxBytesSent))

							#i = 0
							#for path in aNodePath:
							#	i += 1
							#	print("\t{}:\t{}".format(i, PrintNode(path)))
							#print("\n")
	#for field, value in ast.iter_fields(aNode):
	#	print("{}, {}".format(field, value))

def IterateThroughNodes(aNode, aNodePath):
	aNodePath.append(aNode)
	HandleNode(aNode, aNodePath)

	for field, value in ast.iter_fields(aNode):
		if isinstance(value, list):
			for item in value:
				if isinstance(item, ast.AST):
					IterateThroughNodes(item, aNodePath)
		elif isinstance(value, ast.AST):
			IterateThroughNodes(value, aNodePath)

## "Main"
print("### Debug ###")
src = ""

if len(sys.argv) >= 2:
	imports = []

	with open(sys.argv[1], "r") as file:
		src = file.read()
		src += "\n"

	# TODO: Make this clean using the alias below from the AST:
	#	Import(names=[<_ast.alias object at 0x0000020C212CFB70>])
	#	alias(name='netlib', asname=None)
	lines = src.split("\n")
	for line in lines:
		if ("import " in line):
			imports.append(line.split(" ")[1])

	if imports:
		currentDir = "{}/".format(os.path.dirname(os.path.abspath(__file__)))
		currentDir = currentDir.replace("\\", "/")
		sys.argv[1] = sys.argv[1].replace("\\", "/")
		path = "{}/".format('/'.join(sys.argv[1].split('/')[0:-1]))

		if not path[1] == ":" and not path[0] == "/":
			path = currentDir + path

		#print("Looking for files ({}) in {}:".format(repr(imports), path))
		files = [f for f in listdir(path) if isfile(join(path, f))]
		for file in files:
			for requiredImport in imports:
				if (file == "{}.py".format(requiredImport)):
					print("Found an import named {} in the path {}!".format(requiredImport, path))
					with open("{}{}.py".format(path, requiredImport), "r") as file:
						src += file.read()
						src += "\n"

	nodePath = []

	startNode = ast.parse(src)
	nodePath.append(startNode)

	#HandleNode(startNode, nodePath)
	IterateThroughNodes(startNode, nodePath)

	# Finalize
	if (usesIPV4) and (usesIPV6):
		print("Sockets are implemented for both IPv4 and IPv6.")
	else:
		if not usesIPV4:
			warnings.append("Socket connectivity is not configured for IPv4 connections")
		if not usesIPV6:
			warnings.append("Socket connectivity is not configured for IPv6 connections")

	# Print output

	print("") # Newline
	print("### Report ###")
	print("Errors:\t\t{}".format(len(errors)))
	print("Warnings:\t{}".format(len(warnings)))

	# Print errors
	if errors:
		print("\nErrors:")
		for error in errors:
			print("\t{}".format(error))

	# Print warnings
	if warnings:
		print("\nWarnings:")
		for warning in warnings:
			print("\t{}".format(warning))
else:
	print("Please specify a file to analyze.\n\tE.g.: python3 impscan.py example/client.py")