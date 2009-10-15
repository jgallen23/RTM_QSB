#!/usr/bin/python


# import urllib for url calling
import urllib

#import webbrowser to open auth webpage if necissary
import webbrowser

#import ElementTree to parse / work with XML
from xml.etree import ElementTree as ET

#import os to work with paths.  May not need this.
import os

def main():
	
	# Define some main variables. Don't change these.
	api_url='http://api.rememberthemilk.com/services/rest/?'
	auth_url='http://api.rememberthemilk.com/services/auth/?'
	api_key='60a9369798aa92cc5cc291b2280422f1'
	api_secret='6fdf8ca0e501715f'
	
	# Get the location of the response XML file.  May not need this.
	xml_resp = os.path.abspath(__file__)
	xml_resp = os.path.dirname(xml_resp)
	xml_resp = os.path.join(xml_resp, "resp.xml")
	
	def callURL(method):
		url=api_url+'method='+method+'&api_key='+api_key+'&test=chupacabra'

		page = urllib.urlopen(url)
		#the_resp=ET.parse(page)
		#tree=the_resp.getroot()
		
		the_resp=ET.parse(page).getroot()
		
		
		for element in the_resp:
			print element.text
			
		for element in the_resp.findall('api_key/'):
			var = element.text
		print
		print var
		
		#Write the response to the local XML file.  May not need this	
		#the_resp.write(xml_resp)
		
		pass
		
	method = 'rtm.test.echo'
	result = callURL(method)
			

if __name__ == "__main__":
	main()