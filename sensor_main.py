from sensor import *
import thread, time
from multiprocessing import Process


if __name__ == "__main__":
	# BROKER_ADDRESS = "iot.eclipse.org"
	# BROKER_ADDRESS = "192.168.0.104"
	BROKER_ADDRESS = "192.168.43.37"
	PORT = 1883
	KEEPALIVE = 60
	ph = client.pahoHandler()
	ph.connect_to_broker(BROKER_ADDRESS, PORT, KEEPALIVE)