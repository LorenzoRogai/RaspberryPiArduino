#!/usr/bin/python
import serial
import time
import os
import socket
from threading import Thread
from enum import Enum
import logging

log = ""
DEBUG = False

class Commands(Enum):
	clear = 1
	cursor1 = 2
	cursor2 = 3
	loadsymbol = 4
	ramsymbol = 5
	tempsymbol = 6
	downloadsymbol = 7	
	
def Log(message):
	global log, DEBUG
	if DEBUG:
		log += message + "\n"
		if len(log) > 10000:
			logging.info(log)
			log = ""	

def SendCommand(Command):	
	SendData(Command.name)
	
def SendData(data):
	global ser
	Log("Sent data to Arduino: " + data)
	ser.write(data + '\n')
	
logging.basicConfig(level=logging.INFO,                    
                    filename='/home/raspberrypiarduino.log'
					)
Log("RaspberryPiArduino started!")

ser = serial.Serial('/dev/ttyUSB0', 9600)
Log("Connected to Arduino serial")

time.sleep(2)

lastrx = 0

TCP_IP = '192.168.0.10'
TCP_PORT = 5005
BUFFER_SIZE = 35

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
Log("Server started on: " + TCP_IP + ":" + str(TCP_PORT))

current = 0
datafromclient = ""

def SwitchTimer():
	global current, clientconnected
	while True:
		time.sleep(20)		
		if current == 0:
			if datafromclient != "":
				current = 1			
				Log("Switched from Raspberry Pi to PC infos")
		else:
			Log("Switched from PC to Raspberry Pi infos")
			current = 0

def ServerThread():		
	global current, datafromclient
	while True:	
		conn, addr = s.accept()	
		Log("Incoming client connection from: " + str(addr))
		while 1:
			try:
				data = conn.recv(BUFFER_SIZE)
				if not data: 					
					break			
				datafromclient = data	
				Log("Received data from client: " + data)
			except:							
				current = 0
				datafromclient = ""
				Log("Client disconnected")
		conn.close()		
		current = 0
		datafromclient = ""
		Log("Client disconnected")

def MainThread():
	global current, lastrx, datafromclient
	while True:			
		if current == 0:			
			loadavg = " " + os.popen("cat /proc/loadavg").read().split()[0]
			ram = " " + os.popen("free -m | awk 'NR==2 { print $3; }'").read().strip() + "Mb"
			
			temp = str(int(os.popen("cat /sys/class/thermal/thermal_zone0/temp").read()) / 1000)
			rx = int(round(float(int(os.popen("//sbin/ifconfig eth0 | grep \"RX bytes\" | awk '{ print substr($2,7) }'").read().strip()) * 0.8)))
			downloadspeed = 0
			if lastrx != 0:
				downloadspeed = (rx - lastrx) / 1024
			lastrx = rx
			rx = rx / 1024 / 1024	
			download = " " + str(rx) + "/" + str(downloadspeed)			
			
			#SendCommand(Commands.clear)
			SendCommand(Commands.cursor1)
			SendCommand(Commands.loadsymbol)
			SendData(loadavg)
			for i in range(0, 14 - len(loadavg) - len(ram)):
				SendData(" ")
			SendCommand(Commands.ramsymbol)
			SendData(ram)
			SendCommand(Commands.cursor2)
			SendData(temp)
			SendCommand(Commands.tempsymbol)
			for i in range(0, 14 - len(temp) - len(download)):
				SendData(" ")
			SendCommand(Commands.downloadsymbol)
			SendData(download)	
		else:
			SendCommand(Commands.clear)
			SendData(datafromclient)
		time.sleep(1)

SwitchTimer = Thread(target=SwitchTimer, args=())
SwitchTimer.start()
Log("Started switch timer thread")
ServerThread = Thread(target=ServerThread, args=())
ServerThread.start()
Log("Started server thread")
MainThread = Thread(target=MainThread, args=())
MainThread.start()
Log("Started main thread")