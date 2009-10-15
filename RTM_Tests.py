#!/usr/bin/python


# import urllib for url calling
import urllib

#import webbrowser to open auth webpage if necissary
import webbrowser

#import ElementTree to parse / work with XML
from xml.etree import ElementTree as ET

#import NSDictionary and NSString from Cocoa to work with the plist that will hold the token
from Cocoa import NSDictionary, NSString

#import os to work with paths. Needed to see if file exists, and to write to XML for dev.
import os

#Import hashlib for MD5 encoding
import hashlib

#import time to be used for the pause during auth.  This should be done more gracefully.
import time

def main():
	
	# Define some main variables. Don't change these.
	api_url='http://api.rememberthemilk.com/services/rest/?'
	auth_url='http://www.rememberthemilk.com/services/auth/?'
	api_key='60a9369798aa92cc5cc291b2280422f1'
	api_secret='6fdf8ca0e501715f'
	the_plist='~/Library/Preferences/com.google.RTM-QSB.plist'
	the_plist=NSString.stringByExpandingTildeInPath(the_plist)
	m=hashlib.md5()
	
	# Get the location of the response XML file.  May not need this.
	xml_resp = os.path.abspath(__file__)
	xml_resp = os.path.dirname(xml_resp)
	xml_resp = os.path.join(xml_resp, 'resp.xml')
	
	
	def getLocalToken():
		if os.path.exists(the_plist):
			mydict = NSDictionary.dictionaryWithContentsOfFile_(the_plist)
			token = mydict['Token']
			return token
			pass
		else:
			print 'No Token Found'
			return 0
	
	#Function to call specified URL, get response
	def checkToken(token):
		method = 'rtm.auth.checkToken'
		
		url=api_url+'method='+method+'&api_key='+api_key+'&auth_token='+token

		page = urllib.urlopen(url)
		
		#Seperate the variable from the file. Used to write the Resp to disk. Used for development. May not need this.
		the_resp=ET.parse(page)
		tree=the_resp.getroot()
		
		#Parse the XML
		#the_resp=ET.parse(page).getroot()
		
		#Grab the response message
		var = 0	
		for element in tree.findall('token/'):
			var = element.text
		
		#Write the response to the local XML file. Used for Dev only.	
		the_resp.write(xml_resp)
		
		return var
		pass
	
	#Function to write to the Plist.  Only sets the token for now.  Could add in more parameters later.
	def writePlist(token):
		mydict = {}
		mydict['Token']=token
		NSDictionary.dictionaryWithDictionary_(mydict).writeToFile_atomically_(the_plist, True)
		pass

	
	#get the Frob to begin auth process, because the token came back false
	def getFrob():
		method = 'rtm.auth.getFrob'
		
		the_sig = api_secret+'api_key'+api_key+'method'+method

		hashed_sig= createMD5(the_sig)
		
		url=api_url+'method='+method+'&api_key='+api_key+'&api_sig='+(str(hashed_sig))
		
		page = urllib.urlopen(url)
		
		the_resp=ET.parse(page).getroot()
		
		var = 0	
		for element in the_resp.findall('frob/'):
			var = element.text
		
		return var
		pass
	
	
	def createMD5(the_string):
		m.update(the_string)
		the_hash = m.hexdigest()
		return the_hash
		pass
	
	def doAuth(the_frob):
		the_sig = api_secret+'api_key'+api_key+'frob'+the_frob
		hashed_sig= createMD5(the_sig)
		url=auth_url+'api_key='+api_key+'&perms=delete&frob='+the_frob+'&api_sig='+(str(hashed_sig))
		
		webbrowser.open(url)
		print 'Website Opened:'
		print url
		#sleep for 30 seconds to allow user to grant auth before proceeding with getting the token.  This needs to be implimented better.
		time.sleep(30)
		
		method = 'rtm.auth.getToken'

		the_sig = api_secret+'api_key'+api_key+'frob'+the_frob+'method'+method

		hashed_sig= createMD5(the_sig)
		
		url=api_url+'method='+method+'&api_key='+api_key+'&frob='+the_frob+'&api_sig='+(str(hashed_sig))
		
		page = urllib.urlopen(url)

		#Seperate the variable from the file. Used to write the Resp to disk. Used for development. May not need this.
		the_resp=ET.parse(page)
		tree=the_resp.getroot()

		#Parse the XML
		#the_resp=ET.parse(page).getroot()

		#Grab the response message
		var = 0	
		for element in tree.findall('token/'):
			var = element.text

		#Write the response to the local XML file. Used for Dev only.	
		the_resp.write(xml_resp)

		return var
		pass
	
	#define the method to be used, use rtm.test.echo for testing	
	#method = 'rtm.test.echo'
	
	#Read the plist, grab the Token (using test string for dev)
	token=getLocalToken()
	
	#see if token var contains actual value
	if token != 0:
		#call the URL, pass the resp back to variable result
		result = checkToken(str(token))
		if result == 0:
			the_frob=getFrob()
			the_token=doAuth(the_frob)
			if the_token != 0:
				print 'Sucess'
			else:
				print 'Failure'
			

if __name__ == '__main__':
	main()