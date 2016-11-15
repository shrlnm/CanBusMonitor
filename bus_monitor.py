#!/usr/bin/env python

from serial.tools import list_ports
import serial                                    #sudo easy_install pyserial
import sys
import os
import io
import time
from datetime import datetime

#print chr(27)+"[2J"+chr(27)+"[;H",

class ELM:

  comp = 0
  port = ""
  buff = ""

  statsfilter = ['OK','at ','AT','ELM','STO','327','CAN','?','BUF']
  filter = []
  
  stats = {}
  frames = {}
  ps = 0
  ct = 0

    
  def __init__(self, port, speed):
    self.comp = serial.Serial(port,baudrate=speed,timeout=5)    
    self.port = port
    
                        
  def new_line(self, line):
    
    global logfile
    
    line = line.strip()
    
    if len(line)<6: return    
    pref = line[:3]

    tm = int(round(time.time() * 1000))

    # Statistic
    if pref in self.statsfilter : return    

    if ord(line[4:5])<0x31 or ord(line[4:5])>0x38: return

    dlc = int(line[4:5])

    if len(line)<(dlc*3+5): return
      
    if pref not in self.stats.keys():
      self.stats[pref]=1
    else:
      self.stats[pref]=self.stats[pref]+1
      
    if pref not in self.filter:
      #print tm,';',line
      self.frames[pref]=line
      self.ct = time.time()
      if (self.ct-self.ps)>0.2:
        print chr(27)+"[2J"+chr(27)+"[;H",'###### Frames ######'
        for l in sorted(self.frames.keys()):
          print "%-40s # %d" % (self.frames[l],self.stats[l])
        self.ps = self.ct

    if logfile:
      logfile.write( str(tm)+';'+line+'\n' )
    

  def cmd(self, command):
    
    self.comp.write(command+"\r")    
    
    #print command
    
    self.buff = ""
    while(True):
      byte = self.comp.read()
      if byte=='\r' or byte=='\n':
        self.new_line(self.buff)
        self.buff = ""
        continue
      self.buff += byte
      if byte=='>':
        #print self.buff
        break
        
  def brd(self, boudrate):
    
    if boudrate==38400:
      self.comp.write("at brd 68\r")    
    else:
      self.comp.write("at brd 11\r")
      
    self.buff = ""
    while(True):
      byte = self.comp.read()
      if byte=='\r' or byte=='\n':
        self.new_line(self.buff)
        self.buff = ""
        continue
      self.buff += byte
      if self.buff=='OK':
        print self.buff
        break
    
    print "Changing baoudrate"
    if boudrate==38400:
      self.comp = serial.Serial(self.port,baudrate=38400,timeout=5)    
    else:
      self.comp = serial.Serial(self.port,baudrate=230400,timeout=5)    
      
    self.buff = ""
    while(True):
      byte = self.comp.read()
      if byte=='\r' or byte=='\n':
        self.print_line(self.buff)
        self.buff = ""
        continue
      self.buff += byte
      if self.buff=='ELM':
        print self.buff
        break

    self.comp.write("\r")    

opt_port  = ""
opt_speed = ""
opt_addr  = ""
opt_log   = ""
logfile   = 0

def optParser():
  
  import optparse

  global  opt_port  
  global  opt_speed 
  global  opt_addr
  global  opt_log   

  parser = optparse.OptionParser(
    usage = "%prog -p <port> [options]",
    version="%prog 0.1(alpha)",
    description = "can_monitor"
  )
  
  parser.add_option("-p", "--port",
      help="ELM327 com port name",
      dest="port",
      type="string")

  parser.add_option("-s", "--speed",
      help="com port speed",
      dest="speed",
      default="38400",
      type="string")

  parser.add_option("-a", "--addr",
      help="listening CANid",
      dest="addr")

  parser.add_option("--log",
      help="log file name",
      dest="logfile",
      default="",
      type="string")


  (options, args) = parser.parse_args()
  
  if not options.port:
    parser.print_help()
    iterator = sorted(list(list_ports.comports()))
    print ""
    print "Available COM ports:"
    for port, desc, hwid in iterator:
      print "%-30s \n\tdesc: %s \n\thwid: %s" % (port,desc,hwid)
    print ""
    exit(2)
  else:
    opt_port  = options.port
    opt_speed = options.speed
    opt_addr  = options.addr
    opt_log   = options.logfile
      
def main():
  
  global  opt_port  
  global  opt_speed 
  global  opt_addr
  global  opt_log
  global  logfile

  optParser()
  
  if len(opt_log)>0:
    logfile = open(opt_log, "wt")

  
  elm = ELM( opt_port, int(opt_speed) )
  
  elm.cmd('at z')
  elm.cmd("at e1")
  elm.cmd("at l1")
  elm.cmd("at h1")
  elm.cmd("at d1")
  elm.cmd("at caf0")
  elm.cmd("at sp 6")
  elm.cmd("at al")
  if opt_addr:
    elm.cmd("at cra "+opt_addr)
    
  #elm.brd(230400)
  elm.cmd("at")
  
  try:
    elm.cmd("at ma")  
    while(True):
      elm.cmd("") 
  finally:
    print 'Good by'
    #for k in elm.stats.keys():
    #  print k, '\t', elm.stats[k]

    elm.cmd("AT") 
    elm.brd(38400)
    if logfile:
      logfile.close()
    
  
if __name__ == '__main__':
  main()
  #curses.wrapper(main)
  
    
