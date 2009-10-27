#!/usr/bin/python
#
#  Send_To_RTM.py
#  Send_To_RTM
#
#  Created by Gordon on 10/26/09.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

"""A python search source for QSB.
"""

__author__ = 'Gordon'


# import urllib for url calling
import urllib

#import webbrowser to open auth webpage if necissary
import webbrowser

#import ElementTree to parse / work with XML
from xml.etree import ElementTree as ET

#import NSDictionary and NSString from Cocoa to work with the plist that will hold the token
from Cocoa import NSDictionary, NSString

#import os to work with paths. Needed to see if file exists.
import os

#Import hashlib for MD5 encoding
import hashlib

#import time to be used for the pause during auth.	This should be done more gracefully.
import time

# These are imported by QSB.  Don't change these.
import sys
import thread
import AppKit
import Foundation

try:
  import Vermilion	# pylint: disable-msg=C6204
except ImportError:

  class Vermilion(object):
	"""A mock implementation of the Vermilion class.

	Vermilion is provided in native code by the QSB
	runtime. We create a stub Result class here so that we
	can develop and test outside of QSB from the command line.
	"""
	
	IDENTIFIER = 'IDENTIFIER'
	DISPLAY_NAME = 'DISPLAY_NAME'
	SNIPPET = 'SNIPPET'
	IMAGE = 'IMAGE'
	DEFAULT_ACTION = 'DEFAULT_ACTION'

	class Query(object):
	  """A mock implementation of the Vermilion.Query class.

	  Vermilion is provided in native code by the QSB
	  runtime. We create a stub Result class here so that we
	  can develop and test outside of QSB from the command line.
	  """
	  
	  def __init__(self, phrase):
		self.raw_query = phrase
		self.normalized_query = phrase
		self.pivot_object = None
		self.finished = False
		self.results = []

	  def SetResults(self, results):
		self.results = results

	  def Finish(self):
		self.finished = True

class Send_To_RTMAction(object):
  """Send_To_RTM Action

  This class conforms to the QSB search action protocol by
  providing the mandatory AppliesToResults and Perform methods.
  
  """
  def AppliesToResults(self, result):
	"""Determines if the result is one we can act upon."""
	return True

  def Perform(self, results):
	"""Perform the action"""
	for result in results:
		the_task = result[Vermilion.DISPLAY_NAME]
		"""Define some main variables. Don't change these."""
		api_url='http://api.rememberthemilk.com/services/rest/?'
		auth_url='http://www.rememberthemilk.com/services/auth/?'
		api_key='60a9369798aa92cc5cc291b2280422f1'
		api_secret='6fdf8ca0e501715f'
		the_plist='~/Library/Preferences/com.rememberthemilk.RTM-QSB.plist'
		the_plist=NSString.stringByExpandingTildeInPath(the_plist)
		#xml_resp = '~/Desktop/resp.xml'
		#xml_resp = NSString.stringByExpandingTildeInPath(xml_resp)
		auth=1
		the_token=0



		def getLocalToken():
			if os.path.exists(the_plist):
				mydict = NSDictionary.dictionaryWithContentsOfFile_(the_plist)
				the_token = mydict['Token']
				return the_token
			else:
				#print 'No Token Found'
				return 0

		"""Check to see if the Token is valid"""
		def checkToken(the_token):
			method = 'rtm.auth.checkToken'

			url = "%smethod=%s&api_key=%s&auth_token=%s" % (api_url, method, api_key, the_token)
			the_token = ParseURL(url, 'auth/token/')
			return the_token

		#Function to write to the plist.  Only sets the token for now.	Could add in more parameters later.
		def writePlist(the_token):
			mydict = {}
			mydict['Token']=the_token
			NSDictionary.dictionaryWithDictionary_(mydict).writeToFile_atomically_(the_plist, True)


		#get the Frob to begin auth process, because the token came back false
		def getFrob():
			method = 'rtm.auth.getFrob'

			the_sig = "%sapi_key%smethod%s" % (api_secret, api_key, method)
			hashed_sig= createMD5(the_sig)

			url = "%smethod=%s&api_key=%s&api_sig=%s" % (api_url, method, api_key, hashed_sig)

			the_frob=ParseURL(url, 'frob/')

			return the_frob

		def createMD5(the_string):
			return hashlib.md5(the_string).hexdigest()

		def doAuth():
			#Need to get a frob to be used to obtain a new token
			the_frob=getFrob()

			#Get the user to give their auth via the RTM website
			getAuth(the_frob)

			#sleep for 30 seconds to allow user to grant auth before proceeding with getting the token.	 This needs to be implimented better.
			time.sleep(15)
			#Should have auth by now.  May run into problems where user isn't paying attention, didn't auth.  Again, there may be a better solution for this.

			#Start to get the actual token that will be stored in our plist.
			the_token=getRemoteToken(the_frob)

			if the_token != 0:
				#Token came back successfully.	Display success message for Dev

				#print 'Sucess'
				#print 'Token: '+the_token

				#Store token in plist
				writePlist(the_token)
				return 1
			else:
				#Token did not come back succesfully Should maybe add some error handling here

				#print 'Failure'
				return 0

		def getRemoteToken(the_frob):
			method = 'rtm.auth.getToken'

			the_sig = "%sapi_key%sfrob%smethod%s" % (api_secret, api_key, the_frob, method)
			hashed_sig= createMD5(the_sig)

			url = "%smethod=%s&api_key=%s&frob=%s&api_sig=%s" % (api_url, method, api_key, the_frob, hashed_sig)

			the_token = ParseURL(url, 'auth/token/')
			return the_token

		def getAuth(the_frob):

			method = 'rtm.auth.getFrob'

			the_sig = "%sapi_key%sfrob%spermswrite" % (api_secret, api_key, the_frob)
			hashed_sig= createMD5(the_sig)

			url = "%sapi_key=%s&frob=%s&perms=write&api_sig=%s" % (auth_url, api_key, the_frob, hashed_sig)

			webbrowser.open(url)

			# For dev: Print out the full URL opened, for error checking.
			#print 'Website Opened:'
			#print url

		def SendTask(new_task):

			#get the local token (again.  Was having problems with the token not being recognized as global.  This solves the issue)
			the_token=getLocalToken()

			#need to create timeline.
			timeline=createTimeline(the_token)

			method ='rtm.tasks.add'

			#sets the parse value to 1.	 With it set to 1, smart-add is in effect.
			doParse = '1'
			
			the_sig = "%sapi_key%sauth_token%smethod%sname%sparse%stimeline%s" % (api_secret, api_key, the_token, method, new_task, doParse, timeline)
			hashed_sig=createMD5(the_sig)
			
			new_task=makeNetSafe(new_task)
			
			url = "%smethod=%s&api_key=%s&timeline=%s&name=%s&parse=%s&auth_token=%s&api_sig=%s" % (api_url, method, api_key, timeline, new_task, doParse, the_token, hashed_sig)
			ParseURL(url, 0)

		#function to create timeline for sendTask function
		def createTimeline(the_token):
			method='rtm.timelines.create'

			the_sig = "%sapi_key%sauth_token%smethod%s" % (api_secret, api_key, the_token, method)
			hashed_sig=createMD5(the_sig)

			url = "%smethod=%s&api_key=%s&auth_token=%s&api_sig=%s" % (api_url, method, api_key, the_token, hashed_sig)

			#send url to the parser
			timeline = ParseURL(url, 'timeline/')
			return timeline

		#Function to call and parse the URL.
		def ParseURL(url, ItemNeeded):

			page = urllib.urlopen(url)
			#print "Url sent: " + url
			#Seperate the variable from the file. Used to write the Resp to disk. Used for development. May not need this.
			#the_resp=ET.parse(page)
			#tree=the_resp.getroot()

			#Parse the XML
			the_resp=ET.parse(page).getroot()

			var = 0 
			if ItemNeeded !=0:
				#essentially, is this from the sendtask method.	 This sucks.  Figure out a better way to do this.

				#Grab the response message	
				for element in the_resp.findall(ItemNeeded):
					var = str(element.text)

			#Write the response to the local XML file. Used for Dev only.	
			#the_resp.write(xml_resp)

			return var

		def makeNetSafe(new_task):
			new_task=new_task.split()
			new_task= "%20".join(new_task)
			new_task=new_task.split("#")
			new_task="%23".join(new_task)
			return new_task

		#------------------------------------------------#
		#-----------END OF FUNCTIONS---------------------#
		#-------BEGIN MAIN FUNCTION----------------------#
		#------------------------------------------------#

		#Read the plist, grab the Token (using test string for dev)
		#print "Getting local token"
		local_token=getLocalToken()
		#print "local token recieved"

		if local_token != 0:
			#There is a token, need to check to make sure it isn't expired.

			#Check token't validity
			#print "Checking local token"
			result = checkToken(local_token)
			#print "Local token checked"
			if result == 0:
				# Token came back false, token is expired.
				#print "Doing auth"
				auth=doAuth()
				#print "Auth done"
		else:
			#There is no token. We need to run through the auth process and save a new plist
			#print "Doing Auth"
			auth=doAuth()
			#print "Auth done"

		if auth == 1:
			#Auth was sucessfull, should have a token to use.

			#Call SendTask function to create new task
			#print "Sending task"
			SendTask(the_task)
			#print "Task Sent"
		#else:
			#something went wrong. Print a failure message for dev.
			#print 'An error occured during the code.  Auth not sucessfull.'
		



def main():
  """Command line interface for easier testing."""
  argv = sys.argv[1:]
  if not argv:
	print 'Usage: Send_To_RTM <query>'
	return 1
  argv = " ".join(argv)
  print argv
  Send_To_RTMAction.Perform(Send_To_RTMAction(), argv)
	

if __name__ == '__main__':
  sys.exit(main())
