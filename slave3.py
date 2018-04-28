#RPi Pinouts

#I2C Pins 
#GPIO2 -> SDA
#GPIO3 -> SCL

# IMPORTS

import time
import pysher
import json
import sys
import urllib.request


# Testing diables some things (so it runs away from raspi)
testMode = False
if(not testMode):
	import smbus
	# for RPI version 1, use "bus = smbus.SMBus(0)"
	bus = smbus.SMBus(1)

# CONSTANTS
# Pusher Constants
app_id = "506429"
key = "161ccb0b7e8071fb8505"
secret = "b6b6fe9319b068be1bff"
cluster = "us2"

channelName = 'rooms'
eventName = 'ModuleChange'

# RESTful endpoint
base_url = "http://ehmain.rh.rit.edu/api/"
pre_api = "rooms/"
post_api = "/config"


#Slave Address 1
address = 0x04

def main():


	roomId = -1

	try:
		f = open('./room_id.conf', 'r')
	except FileNotFoundError as e:
		roomId = 8126
	else:	
		roomId = int(f.readLine().strip())
		f.close()
	
	#Establish pusher connection
	pusher = pysher.Pusher(appkey)

	def connectionHandler(data):
		channel = pusher.subscribe(channelName)
		channel.bind(eventName, eventHandler)

	pusher.connection.bind('pusher:connection_established', connectionHandler)
	pusher.connect()

	# Listen for incoming messages from the board
	while True:

		if(not testMode):
			#Receives the data from the User
			data = raw_input("Enter the led command to be sent: ")
			data_list = list(data)
			for i in data_list:
				try:
					#Sends to the Slaves 
					writeNumber(ord(i))
					time.sleep(.1)
				except Exception as e:
					print(e)
		
			try:
				writeNumber(0x0A)
			except Exception as e:
					print(e)




def eventHandler(*args, **kwargs):
	print(args)
	print(kwargs)
	if(not testMode):
		event = json.loads( kwargs["data"] )

		bus.write_byte_data(address, 0, value)


def postConfirmation(currentState):
	req = urllib.request.Request(url=base_url+pre_api+str(roomId)+post_api,
									method='POST',
									data=json.dumps(currentState))

	res = urllib.request.urlopen(req)
	return res.read().decode('utf-8')


class Module:
	def __init__(self, id_, addr):
		self.id = id_
		self.address = addr
		status = 0

	def getStatus(self):
		return {
				"add" : [
					{
					"type": self.getType(),
					"status": self.fromCode(self.status),
					"ic2_address": self.address
					}
				]
			}

	def setStatus(self, status):
		self.status = self.fromWord(status)


class LEDModule(Module):

	def __init__(self, id_, addr):
		Module.__init__(self, id_, addr)
		last_status = None

	statuses = {
		"ERROR":0,
		"RGB_FADE_1":1,
		"WHITE":2,
		"RGB_COLOR_WIPE":3,
		"RGB_FADE_2":4,
		"OFF":5,
		"ON":6
	}

	def fromWord(self.status):
		return LEDModule.statuses[status]

	def fromCode(self.status):
		return list(LEDModule.statuses.keys())[status]

	def setStatus(self, status):
		if(status == "ON"):
			self.status, self.last_status = self.last_status, self.status
		else:
			self.last_status = self.status
			self.status = self.fromWord(status)
	
	def getType(self):
		return "LED"


class BlindModule(Module):
	statuses = [
		"DOWN":0,
		"UP":1,
		"IDLE":2
	]
	
	def fromWord(self.status):
		return LEDModule.statuses[status]

	def fromCode(self.status):
		return list(LEDModule.statuses.keys())[status]

	def getType(self):
		return "BLIND"



main()
