#-------------------------------------------------------------------------------
# File Name : ServiceDiscovery.py
# Purpose   : Service discovery for Client 
# Author    : Sri Muthu Narayanan Balasubramanian
# Created   : 8 Jan 2016
# Copyright :
#-------------------------------------------------------------------------------
import sys, os, time
import subprocess
import re
# from Error import *

# arg = ["avahi-browse","-rt","_coap._udp"]
# arg = ["avahi-browse","-rt", "_room1._sub._coap._udp"]
arg = ["avahi-browse","-rt", "-a"]
# arg = ["avahi-browse", "-rt", "_room1._sub._coap._udp", "| grep address | grep -E -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'"]

class SD():

	def __init__(self):
		self.__InitSuccess = False

	def Discover_services(self):
		
		try:
			services = subprocess.check_output([arg[0], arg[1], arg[2]])
		except:
			print "error"
			return 0

		# ip = services
		ip = "error"
		# found = False
		for line in services.splitlines():
			if "address" in line:
				ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line)
				# print type(ip)
				if len(ip) > 0:
					res = ip[0]
					# print ip[0]		

		self.__InitSuccess = True
		# print "Avahi Found "+str(len(service_list))+" "+broker_name+" "+protocol+" Service(s)"
		return res

# test = SD().Discover_services()
# OR
# sd = SD()
# test = sd.Discover_services()

# print test
# print type(test)