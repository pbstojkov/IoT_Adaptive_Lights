from __future__ import absolute_import, division, print_function, unicode_literals
from light import *
from general import * # AvahiDiscovery, WakaamaProc, ownership
# from multiprocessing import Process
# import thread, time
from general import AvahiDiscovery
from light import client

if __name__ == "__main__":
    ROOM = 1
    BROKER_ADDRESS = AvahiDiscovery.find_broker(ROOM)
    print(BROKER_ADDRESS)

    # BROKER_ADDRESS = "iot.eclipse.org"
    # BROKER_ADDRESS = "192.168.0.104"
    # BROKER_ADDRESS = "192.168.43.37"
    PORT = 1883
    KEEPALIVE = 60
    ph = client.pahoHandler()
    ph.connect_to_broker(BROKER_ADDRESS, PORT, KEEPALIVE)