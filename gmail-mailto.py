#!/usr/bin/python

################################################################################
# Copyright (c) 2011 Mark Busby                                                #
#                                                                              #
# This software is licensed under the zlib/libpng license                      #
#                                                                              #
# This software is provided 'as-is', without any express or implied warranty   #
# In no event will the authors be held liable for any damages arising from the #
# use of this software.                                                        #
#                                                                              #
# Permission is granted to anyone to use this software for any purpose,        #
# including commercial applications, and to alter it and redistribute it       #
# freely, subject to the following restrictions:                               #
#                                                                              #
#     1. The origin of this software must not be misrepresented; you must not  #
#     claim that you wrote the original software. If you use this software in  #
#     a product, an acknowledgment in the product documentation would be       #
#     appreciated but is not required.                                         #
#                                                                              #
#     2. Altered source versions must be plainly marked as such, and must not  #
#     be misrepresented as being the original software.                        #
#                                                                              #
#     3. This notice may not be removed or altered from any source             #
#     distribution.                                                            #
################################################################################

# gmail-mailto.py
# v. 1.0
# set this script as your default "mailto" handler.  Opens a chromium-browser 
# window in app-mode ready to send a gmail-email.  Also works with google
# apps account
#
# Usage: gmail-mailto.py <url> [google apps account]
# example1: gmail-mailto.py 'mailto:foo@bar.baz?&subject=gmail-mailto.py Rocks!'
#   will launch a gmail compose page
# example2: gmail-mailto.py -a BusbyFreelance.com 'mailto:foo@bar.baz&subject=It works G Apps!!!'
#   will launch a google apps mail compose page
# In ubuntu, use this line as your preferred "Mail Reader" gmail-mailto.py [-a appsID] %s


import sys
import re
import os
import getopt

# test vector:
#mailto:hello@hello.hello?\
#to=hello2@hello.hello&\
#cc=hellocc1@hello.hello&\
#cc=hellocc2@hello.hello&\
#bcc=hellobcc@hello.hello&\
#bcc=hellobcc2@hello.hello&\
#subject=aSubject&body=aBody"

class launcher:
	def __init__(self, appsAccount):
		if (appsAccount != ""):
			self.baseURL = 'https://mail.google.com/a/' + appsAccount + '/'
		else:
			self.baseURL = 'https://mail.google.com/'
	
	def launch(self, params):
		cbArg = '--app="' + self.baseURL + 'mail'
		if (params != ""):
			#cbArg += '?view=cm&tf=0&' + params + '"'
			cbArg += '?ui=2&view=cm&tf=0&' + params + '"'
			#view-source:https://mail.google.com/mail/?ui=2&view=btop&ver=1s4dmo0mhdqld#cmid%253D1
		else:
			cbArg += '"'
		os.system('chromium-browser ' + cbArg)
		exit()

class Params:
	toList = ""
	ccList = ""
	bccList = ""
	subject = ""
	body = ""
	def getVar(self, varName):
		if (varName == "to"):
			return self.toList
		elif (varName == "cc"):
			return self.ccList
		elif (varName == "bcc"):
			return self.bccList
		elif (varName == "subject"):
			return self.subject
		elif (varName == "body"):
			return self.body
		return None
		
	def setVar(self, varName, value):
		if (varName == "to"):
			self.toList = value
		elif (varName == "cc"):
			self.ccList = value
		elif (varName == "bcc"):
			self.bccList = value
		elif (varName == "subject"):
			self.subject = value
		elif (varName == "body"):
			self.body = value
		return
	
	def addToVar(self, varName, value):
		if (varName == "to"):
			self.toList += value
		elif (varName == "cc"):
			self.ccList += value
		elif (varName == "bcc"):
			self.bccList += value
		elif (varName == "subject"):
			self.subject += value
		elif (varName == "body"):
			self.body += value
		return
			
	def add(self, varName, address):
		if (self.getVar(varName) == ""):
			self.setVar(varName, address)
		else:
			self.addToVar(varName, "," + address)
		return

def usage(name):
	print "Usage:"
	print "\t" + name + " [-a GoogleAppsAccountID] [mailtoURL]"
	exit()
	
def main():
	args, urlList = getopt.getopt(sys.argv[1:], "?ha:", "help")

	if (len(urlList) > 1):
		usage(sys.argv[0])
	if (len(urlList) == 1):
		url = urlList[0].replace('mailto:','') # get rid of mailto:, if present
	if (len(urlList) < 1):
		url = ""
	
	l = None
	for opt, val in args:
		if (opt == "-a"):
			l = launcher(val)
		if (opt in ("-h", "-?", "--help")):
			usage(sys.argv[0])
		
	if (l == None):
		l = launcher("")
	if (url == ""):
		l.launch(url);

	p = Params()

	# get the first "to" address (before first ?) if present
	position = url.find('?')
	if (position == -1):
		# there is no ?
		print "found to"
		l.launch("to=" + url)
	elif (position == 0):
		url = url[1 :]
	else:
		item = url[0 : position]
		url = url[position + 1 :]
		print "found to"
		p.add("to", item)

	regex = re.compile('&')

	while (url != ""):
		if (regex.search(url) == None):
			position = len(url)
		else:
			position = regex.search(url).start()
	
		item = url[0:position]
		if (item[0:3].lower() == 'to='):
			p.add("to", item[3:])
		elif (item[0:3].lower() == 'cc='):
			p.add("cc", item[3:])
		elif (item[0:4].lower() == 'bcc='):
			p.add("bcc", item[4:])
		elif (item[0:8].lower() == 'subject='):
			p.setVar("subject", item[8:])
		elif (item[0:3].lower() == 'su='):
			p.setVar("subject", item[3:])
		elif (item[0:5].lower() == 'body='):
			p.setVar("body", item[5:])
	
		if (position == len(url)):
			url = ""
		else:
			url = url[position + 1:]

	suffix = ""
	if (p.getVar("to") != ""):
		suffix += "to="
		suffix += p.getVar("to")
	if (p.getVar("cc") != ""):
		if (suffix != ""):
			suffix += "&"
		suffix += "cc="
		suffix += p.getVar("cc")
	if (p.getVar("bcc") != ""):
		if (suffix != ""):
			suffix += "&"
		suffix += "bcc="
		suffix += p.getVar("bcc")
	if (p.getVar("subject") != ""):
		if (suffix != ""):
			suffix += "&"
		suffix += "su="
		suffix += p.getVar("subject")
	if (p.getVar("body") != ""):
		if (suffix != ""):
			suffix += "&"
		suffix += "body="
		suffix += p.getVar("body")

	if (suffix == ""):
		print "invalid mailto: url -- no data found"
		exit(-1)

	l.launch(suffix)

main()
