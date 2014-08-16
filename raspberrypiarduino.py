#!/usr/bin/python
import serial
import time
import os
import socket
from threading import Thread
from enum import Enum
import signal
import web 

class Commands(Enum):
	clear = 1
	cursor1 = 2
	cursor2 = 3
	loadsymbol = 4
	ramsymbol = 5
	tempsymbol = 6
	downloadsymbol = 7	
	fanstart = 8
	fanstop = 9
	fanmin = 10
	fanlow = 11
	fanmedium = 12
	fanfast = 13

def SendCommand(Command):	
	SendData(Command.name)
	
def SendData(data):
	global ser	
	ser.write(data + '\n')
	
fanstatus = 0
curfanspeed = 0
	
def FanThread():
	global fanstatus, curfanspeed
	temp = int(os.popen("cat /sys/class/thermal/thermal_zone0/temp").read()) / 1000
	loadavg = float(os.popen("cat /proc/loadavg").read().split()[0])
	
	while True:	
		temp = int(os.popen("cat /sys/class/thermal/thermal_zone0/temp").read()) / 1000
		loadavg = float(os.popen("cat /proc/loadavg").read().split()[0])
		if loadavg < 1:
			if temp < 50 and fanstatus != 0:
				SendCommand(Commands.fanstop)
				fanstatus = 0
				curfanspeed = 0
			elif temp >= 50 and curfanspeed != 1:
				if fanstatus == 0:
					SendCommand(Commands.fanstart)
					fanstatus = 1
				SendCommand(Commands.fanmin)
				curfanspeed = 1
				time.sleep(120)
		else:
			if fanstatus == 0:
				SendCommand(Commands.fanstart)		
				fanstatus = 1
			if temp >= 50 and curfanspeed != 3:
				SendCommand(Commands.fanmedium)
				curfanspeed = 3
			elif temp >= 45 and temp < 50 and curfanspeed != 2: 			
				SendCommand(Commands.fanlow)
				curfanspeed = 2
			elif temp > 35 and temp < 45 and curfanspeed != 1:
				SendCommand(Commands.fanmin)
				curfanspeed = 1
			elif temp <= 35 and fanstatus == 1:
				SendCommand(Commands.fanstop)
				fanstatus = 0
				time.sleep(120)
		time.sleep(1)

ser = serial.Serial('/dev/ttyUSB0', 9600)

time.sleep(2)

lastrx = 0
current = 0
SendCommand(Commands.fanstop)

'''
TCP_IP = '192.168.0.10'
TCP_PORT = 5005
BUFFER_SIZE = 35


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
Log("Server started on: " + TCP_IP + ":" + str(TCP_PORT))

clientconnected = False

def SwitchTimer():
	global current, clientconnected
	while True:
		time.sleep(20)		
		if current == 0:
			if clientconnected == True:
				current = 1			
				Log("Switched from Raspberry Pi to PC infos")
		else:
			Log("Switched from PC to Raspberry Pi infos")
			current = 0

def ServerThread():		
	global current, clientconnected
	while True:	
		conn, addr = s.accept()	
		Log("Incoming client connection from: " + str(addr))
		clientconnected = True
		while 1:
			try:
				data = conn.recv(BUFFER_SIZE)
				if not data: 					
					break		
				if current == 1:
					SendData(data)			
				Log("Received data from client: " + data)
			except:							
				current = 0
				clientconnected = False
				Log("Client disconnected")
		conn.close()		
		current = 0
		clientconnected = False
		Log("Client disconnected")
'''
loadavgw = ""
ramw = ""
temp = ""

def MainThread():
	global current, lastrx, datafromclient, fanstatus, loadavgw, ramw, temp
	while True:			
		if current == 0:	
			loadavgw = os.popen("cat /proc/loadavg").read().split()[0]
			loadavg = " " + loadavgw
			ramw = os.popen("free -m | awk 'NR==2 { print $3; }'").read().strip() + "Mb"
			ram = " " + ramw
			
			temp = str(int(os.popen("cat /sys/class/thermal/thermal_zone0/temp").read()) / 1000)
			
			'''rx = int(round(float(int(os.popen("//sbin/ifconfig wlan0 | grep \"RX bytes\" | awk '{ print substr($2,7) }'").read().strip()) * 0.8)))
			downloadspeed = 0
			if lastrx != 0:
				downloadspeed = (rx - lastrx) / 1024
			lastrx = rx
			rx = rx / 1024 / 1024	
			download = " " + str(rx) + "/" + str(downloadspeed)		'''	
			fant = ""
			if fanstatus == 0:
				fant = "Off"
			else:
				if curfanspeed == 1:
					fant = "Min"
				elif curfanspeed == 2:
					fant = "Med"
				elif curfanspeed == 3:
					fant = "Fast"
			fan = "Fan: " + fant
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
			for i in range(0, 15 - len(temp) - len(fan)):
				SendData(" ")
			SendData(fan)
			'''SendCommand(Commands.downloadsymbol)
			SendData(download)'''		
		time.sleep(1)
		
def ListenThread():
	global ser, shutdown
	while True:
		inc = ser.readline().strip()
		if (inc == "shutdown" and shutdown == 0):
			shutdown = 1
			Shutdown()

def Shutdown():
	SendCommand(Commands.fanstop)
	command = "/usr/bin/sudo /sbin/shutdown -h now"
	import subprocess
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print output
	
class index: 
	def GET(self): 
		global fanstatus, loadavgw, ramw, temp
		fant = ""
		if fanstatus == 0:
			fant = "Off"
		else:
			if curfanspeed == 1:
				fant = "Min"
			elif curfanspeed == 2:
				fant = "Med"
			elif curfanspeed == 3:
				fant = "Fast"		
		web.header('Content-Type','text/html; charset=utf-8', unique=True)		
		return '''<meta http-equiv="refresh" content="5">
		<style>
		body {
			font-family: Courier New;
		}
		.boxed {
		  border: 1px solid black ;
		  margin: 0 auto;
		  width: 300px;
		  text-align: center;
		}
		</style>
		<div class="boxed">
		  <img src="https://cdn1.iconfinder.com/data/icons/gnomeicontheme/24x24/apps/gnome-cpu.png" width="12px" height="12px"></img> Load Avg: ''' + loadavgw + '''<br>
		  <img src="https://cdn1.iconfinder.com/data/icons/seed-png/ram_driver.png" width="12px" height="12px"></img> Ram Used: ''' + ramw + '''<br>
		  <img src="https://cdn1.iconfinder.com/data/icons/3_Minicons-Free-_Pack/46/temperature.png" width="12px" height="12px"></img> Cpu Temp: ''' + temp + '''&deg;<br>
		  <img src="http://www.75fahrenheit.com/img/icons/icon-fan.png" width="12px" height="12px"></img> Fan: ''' + fant + '''<br>
		  
		</div>'''
	  
class WebServer(web.application): 
  def run(self, port=8888, *middleware): 
	  func = self.wsgifunc(*middleware) 	  
	  return web.httpserver.runsimple(func, ('192.168.0.10', port)) 
	  
def WebThread():
	urls = ('/', 'index') 
	app = WebServer(urls, globals()) 
	app.run(port=8888) 
	
'''
SwitchTimer = Thread(target=SwitchTimer, args=())
SwitchTimer.start()
Log("Started switch timer thread")
ServerThread = Thread(target=ServerThread, args=())
ServerThread.start()
Log("Started server thread")'''

MainThread = Thread(target=MainThread, args=())
MainThread.start()
WebThread = Thread(target=WebThread, args=())
WebThread.start() 
FanThread = Thread(target=FanThread, args=())
FanThread.start()
ListenThread = Thread(target=ListenThread, args=())
ListenThread.start()
