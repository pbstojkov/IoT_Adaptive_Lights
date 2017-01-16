    # from webcam import *
from __future__ import absolute_import, division, print_function, unicode_literals
from light import *
from multiprocessing import Process
import thread, time
import sys, os, time
import subprocess
import re

# avahi-browse -rt _room1._sub._coap._udp | grep address | grep -E -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
def find_broker(room):
    # arg = ["avahi-browse", "-rta"]
    arg = ["avahi-browse", "-rt", "_room" + str(room) + "._sub._coap._udp"]
    services = subprocess.check_output([arg[0], arg[1], arg[2]])
    # print(services)
    m = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', services)
    if m:
        found = m.group()
        return found
    time.sleep(5)
    find_broker(room)

if __name__ == "__main__":
    ROOM = 1
    BROKER_ADDRESS = find_broker(ROOM)
    print(BROKER_ADDRESS)

    # BROKER_ADDRESS = "iot.eclipse.org"
    # BROKER_ADDRESS = "192.168.0.104"
    # BROKER_ADDRESS = "192.168.43.37"
    # PORT = 1883
    # KEEPALIVE = 60
    # ph = pahoHandler()
    # ph.connect_to_broker(BROKER_ADDRESS, PORT, KEEPALIVE)

    #test


