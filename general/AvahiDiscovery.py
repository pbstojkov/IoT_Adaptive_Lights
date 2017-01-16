import sys, os, time
import subprocess
import re

# avahi-browse -rt _room1._sub._coap._udp | grep address | grep -E -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
def find_broker(room):
    # arg = ["avahi-browse", "-rta"]
    arg = ["avahi-browse", "-rt", "_room" + str(room) + "._sub._coap._udp"]
    while True:
	    services = subprocess.check_output([arg[0], arg[1], arg[2]])
	    # print(services)
	    m = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', services)
	    if m:
	        found = m.group()
	        return found
	    time.sleep(3)
	    # find_broker(room)