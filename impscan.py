import ast

functionKeywords = ["socket", "connect", "send", "recv"]
functionNames = []

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
	PrintNode(aNode)

	fields = [(name, PrintNode(val)) for name, val in ast.iter_fields(aNode) if name not in ('left', 'right')]	

	if (isinstance(aNode, ast.Call)):
			for field in fields:
				#print(repr(field))
				#id='variable_name'
				#attr=function, e.g.: 
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

							#for (varName in variableNames):
								
							#
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
src = ""
with open("example/client.py", "r") as file:
	src = file.read()

nodePath = []

startNode = ast.parse(src)
nodePath.append(startNode)

#HandleNode(startNode, nodePath)
IterateThroughNodes(startNode, nodePath)
