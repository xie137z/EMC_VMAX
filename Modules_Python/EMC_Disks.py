#!/usr/bin/python

import sys, getopt, os, re, shutil, subprocess, time
from xml.dom import minidom
sys.path.append('/opt/StorageEngineering/Python/modules')
from Utilities import Files                          


class VMAX_Disk_Util:
  
  def __init__(self, sid):
    self.sid = sid
    self.FailedDisks = {}
    self.Known_Failures = {}
    self.New_Failures = {}
    # Below code loads the current known failed disks
    self.failed_disks = '/opt/EMC/Scripts/Python/failed_disks.dat'
    self.now = int(time.time())
    DAYS_BETWEEN_INC = 10
    DAY = ( 60 * 60 * 24 )
    h = Files()
    h.read_file(self.failed_disks)
    for line in h.readfile:
      if not line.startswith("#"):
        list = line.split()
        if len(list) == 2:
          diskname = list[0] 
          failtime = int(list[1])
          deltatime = (self.now - failtime)
          if deltatime < ( DAYS_BETWEEN_INC * DAY):
            # Add the disk to the current list if its fail time is less that 5 days ago.
            # Otherwise, drop it from the list so a new INC gets created.
            # Key/value = diskname/time
            self.Known_Failures[diskname] = failtime
        

  def get_failed_disks(self):
    SYMCLI = '/opt/emc/SYMCLI/bin/'
 
    cmd = SYMCLI + 'symdisk -sid ' + self.sid  + ' list -failed -output xml_e'

    # Exec the sym command...
    output = os.popen(cmd)

    # Write the XML to an XML file so that it can be passed to the parser
    XML = '/var/www/html/XML/' + self.sid + '_failed_disks.xml'
    f = open(XML, 'w')
    for line in output:
      #line = line.strip()
      f.write(line)
    f.close()

    # Now parse the XML file 
    doc = minidom.parse(XML)
    for node in doc.getElementsByTagName('Disk'):
      ident = ""
      da = ""
      spindle_id = ""
      tech = ""
      speed = ""
      size = ""      
      vendor = ""
      failed = ""            
      for disk in node.getElementsByTagName('Disk_Info'):
        for child in disk.childNodes:
          if child.nodeType == 1:
            if child.nodeName == "ident":
              ident = child.firstChild.nodeValue
            if child.nodeName == "da_number":
              da = str(child.firstChild.nodeValue)
            if child.nodeName == "spindle_id":
              spindle_id = child.firstChild.nodeValue
            if child.nodeName == "technology":
              tech = str(child.firstChild.nodeValue)     
            if child.nodeName == "speed":
              speed = child.firstChild.nodeValue
            if child.nodeName == "vendor":
              vendor = str(child.firstChild.nodeValue)
            if child.nodeName == "rated_gigabytes":
              size = child.firstChild.nodeValue
            if child.nodeName == "failed_disk":
              failed = str(child.firstChild.nodeValue)   
                    
      data = str(ident) + " " + str(da) + " " + str(spindle_id) + " " + str(tech)
      data += " " + str(speed) + " " + str(vendor) + " " + str(size) + " " + str(failed)
      self.FailedDisks[str(spindle_id)] = data
      diskname = 'SID=' + self.sid + '__SPINDLE=' + str(spindle_id)
      if diskname not in self.Known_Failures:
        self.Known_Failures[diskname] = self.now
        self.New_Failures[diskname] = self.now
        
    out = []
    for disk in self.Known_Failures:
      out.append( disk + "  " + str(self.Known_Failures[disk]) + '\n')
    f = Files()
    f.write_file(self.failed_disks,out)