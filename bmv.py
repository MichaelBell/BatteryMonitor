#!/usr/bin/env python
# JH 2015-07-05
# Read data from the USB serial attached to a BMV-700 
# battery monitor, and log to a file

import time
import serial
import cherrypy

# open the USB serial port at 19200 baud
bmvSerial = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=3.0)

# open the log file for appending to
# 2015-09-20 - Log to RAMDISK mounted on /var/tmp
#logFile = open("/home/pi/bmv/bmv.log", "a")
logFile = open("/var/tmp/bmv.log", "a")
logFile.write("Ticks,V,I,P,CE,SOC,TTG,Alarm,AR,H1,H2,H3,H4,H5,H6,H7,H8,H9,H10,H11,H12,H17,H18\n")

dataDict = {}

# Write the current BMV dictioanry data to the "current data" file
def writeDataToCurrentFile(ticks) :
	#tfile = open("/home/pi/bmv/bmv.latest", "w")
	tfile = open("/var/tmp/bmv.latest", "w")
	localtime = time.asctime(time.localtime(ticks))
	tfile.write("Time=%s\n" % localtime)
	#tfile.write("PID=%s\n" % dataDict.get("PID", "???"))
	f = float(dataDict.get("V", "0")) / 1000.0
	tfile.write("V=%.3f V\n" % f)
	f = float(dataDict.get("I", "0")) / 1000.0
	tfile.write("I=%.3f A\n" % f)
	tfile.write("P=%s W\n" % dataDict.get("P", "???"))
	#f = float(dataDict.get("CE", "0")) / 1000.0
	#tfile.write("CE=%.3f Ah\n" % f)
	f = float(dataDict.get("SOC", "0")) / 10.0
	tfile.write("SOC=%.1f %%\n" % f)
	tfile.write("TTG=%s\n" % dataDict.get("TTG", "???"))
	tfile.write("Alarm=%s\n" % dataDict.get("Alarm", "???"))
	#tfile.write("Relay=%s\n" % dataDict.get("Relay", "???"))
	tfile.close()
	return 0

# Write the current "historical" data to the "historical" data file
def writeDataToHistoryFile(ticks) :
	#tfile = open("/home/pi/bmv/bmv.history", "w")
	tfile = open("/var/tmp/bmv.history", "w")
	localtime = time.asctime(time.localtime(ticks))
	tfile.write("Time=%s\n" % localtime)
	f = float(dataDict.get("H2", "0")) / 1000.0
	tfile.write("Last discharge: %.3f Ah\n" % f)
	f = float(dataDict.get("H3", "0")) / 1000.0
	tfile.write("Avg. discharge: %.3f Ah\n" % f)
	f = float(dataDict.get("H1", "0")) / 1000.0
	tfile.write("Deepest disch.: %.3f Ah\n" % f)
	tfile.write("Tot chg cycles: %s\n" % dataDict.get("H4", "???"))
	tfile.write("Num full disch: %s\n" % dataDict.get("H5", "???"))
	f = float(dataDict.get("H6", "0")) / 1000.0
	tfile.write("Cumulative Ah:  %.3f Ah\n" % f)
	tfile.write("Min batt volts: %s mV\n" % dataDict.get("H7", "???"))
	tfile.write("Max batt volts: %s mV\n" % dataDict.get("H8", "???"))
	f = float(dataDict.get("H9", "0")) / 3600.0
	tfile.write("Last full chg:  %.2f hours ago\n" % f)
	tfile.write("Num auto syncs: %s\n" % dataDict.get("H10", "???"))
	tfile.write("Num low main V alarms:  %s\n" % dataDict.get("H11", "???"))
	tfile.write("Num high main V alarms: %s\n" % dataDict.get("H12", "???"))
	f = float(dataDict.get("H17", "0")) / 100.0
	tfile.write("Tot discharged energy:  %.2f kWh\n" % f)
	f = float(dataDict.get("H18", "0")) / 100.0
	tfile.write("Tot charged energy:     %.2f kWh\n" % f)
	tfile.close()
	return

# Write the current data to the log file
def writeDataToLogFile(ticks) :
	#"Ticks,V,I,P,CE,SOC,TTG,Alarm,AR,H1,H2,H3,H4,H5,H6,H7,H8,H9,H10,H11,H12,H17,H18\n")
	logFile.write("%.0f," % ticks)
	logFile.write("%s," % dataDict.get("V", "?"))
	logFile.write("%s," % dataDict.get("I", "?"))
	logFile.write("%s," % dataDict.get("P", "?"))
	logFile.write("%s," % dataDict.get("CE", "?"))
	logFile.write("%s," % dataDict.get("SOC", "?"))
	logFile.write("%s," % dataDict.get("TTG", "?"))
	logFile.write("%s," % dataDict.get("Alarm", "?"))
	logFile.write("%s," % dataDict.get("AR", "?"))
	logFile.write("%s," % dataDict.get("H1", "?"))
	logFile.write("%s," % dataDict.get("H2", "?"))
	logFile.write("%s," % dataDict.get("H3", "?"))
	logFile.write("%s," % dataDict.get("H4", "?"))
	logFile.write("%s," % dataDict.get("H5", "?"))
	logFile.write("%s," % dataDict.get("H6", "?"))
	logFile.write("%s," % dataDict.get("H7", "?"))
	logFile.write("%s," % dataDict.get("H8", "?"))
	logFile.write("%s," % dataDict.get("H9", "?"))
	logFile.write("%s," % dataDict.get("H10", "?"))
	logFile.write("%s," % dataDict.get("H11", "?"))
	logFile.write("%s," % dataDict.get("H12", "?"))
	logFile.write("%s," % dataDict.get("H17", "?"))
	logFile.write("%s\n" % dataDict.get("H18", "?"))
	return

class BatteryServer:
  def __init__(self):
    self.data = {}
    self.history_data = []
    self.last_history = time.time()

  def set_data(self, time, data):
    self.data = {"Time":    int(time),
                 "Power":   int(dataDict["P"]), 
                 "Charge":  int(dataDict["SOC"])/10.0,
                 "Voltage": int(dataDict["V"])/1000.0,
                 "Current": int(dataDict["I"])/1000.0}
    if time > self.last_history + 9.0:
      self.history_data.append(self.data)
      self.last_history += 10.0

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def status(self):
    return self.data

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def history(self, readings="300", interval="1"):
    readings, interval = int(readings), int(interval)
    start = -readings*interval
    if -start > len(self.history_data):
      start = len(self.history_data)
      start = start - (start % interval)
      start = -start
    data = []
    for i in xrange(start, -interval, interval):
      data_slice = self.history_data[i:i+interval]
      data.append({
        "Time"   : data_slice[-1]["Time"],
        "Power"  : sum([d['Power'] for d in data_slice]) / interval,
        "Charge" : data_slice[-1]["Charge"],
        "Voltage": sum([d['Voltage'] for d in data_slice]) / interval,
        "Current": sum([d['Current'] for d in data_slice]) / interval
      })
    interval = interval if len(self.history_data) > interval else len(self.history_data)
    data_slice = self.history_data[-interval:]
    data.append({
      "Time"   : data_slice[-1]["Time"],
      "Power"  : sum([d['Power'] for d in data_slice]) / interval,
      "Charge" : data_slice[-1]["Charge"],
      "Voltage": sum([d['Voltage'] for d in data_slice]) / interval,
      "Current": sum([d['Current'] for d in data_slice]) / interval
    })
    return data

  @cherrypy.expose
  def index(self):
    return cherrypy.lib.static.serve_file('/home/pi/BatteryMonitor/index.html')

print "Starting web server"
server = BatteryServer()
cherrypy.tree.mount(server, '/', {'/static': {'tools.staticdir.on': True, 'tools.staticdir.dir': "/home/pi/BatteryMonitor/static"}})
cherrypy.config.update({'engine.autoreload.on': False,
                        'server.socket_host'  : '0.0.0.0'})
cherrypy.engine.start()

# Previous log tick - used for logging only every 10 seconds
prevLogTick = time.time()

try:
  print "Starting BMV-700 monitor/logger..."
  while True:
    s = bmvSerial.readline()
    s = s.strip("\r\n")
    values = s.split('\t')
    if len(values) == 2:
      dataDict[values[0]] = values[1]
      # New frame?
      # Write current data set to "current" data file AND log file
      ticks = time.time()
      if values[0] == "PID":
        if "P" in dataDict.keys(): server.set_data(ticks, dataDict)
        if (ticks - prevLogTick) > 29.0:
          prevLogTick = ticks
          writeDataToLogFile(ticks)
          print("Ticks: %.0f" % ticks)
          print("SOC: %s" % dataDict.get("SOC", "???"))
finally:
  cherrypy.engine.exit()
