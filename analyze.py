#!/bin/bash

import io
import tokenize

src = ""
with open("example/client.py", "r") as file:
	src = file.read()

src = bytes(src.encode())
src = io.BytesIO(src)

src = list(tokenize.tokenize(src.readline))

i = 0
while i < len(src):

	if (i > 0):
		previousToken = src[i-1]
	else:
		previousToken = None

	if (i < len(src) - 1):
		nextToken = src[i+1]
	else:
		nextToken = None

	token = src[i]

	keywords = ["recv", "send", "connect", "close"]

	for keyword in keywords:
		if (keyword in token.string) and (previousToken and previousToken.string == '.') and (nextToken and nextToken.string == '('):
			#print("Prev:\t{}".format(previousToken))
			#print("Curr:\t{}".format(token))
			#print("Next:\t{}".format(nextToken))
			socketName = src[i-2].string

			print("Found {} from socket named {} in line {}, position {}".format(keyword, socketName, token.start[0], token.start[1]))
			if (keyword == keywords[0]) or (keyword == keywords[1]):
				print("\tVariable in question: {}".format(src[i+2].string))

	i += 1
	#token.start
	#token.end
	#token.line
	#token.type
	#token.string
	#print(token)
	

src = tokenize.untokenize(src)