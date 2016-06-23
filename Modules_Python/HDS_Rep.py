#!/usr/bin/python

import sys, getopt, os, re, shutil, subprocess, time, datetime
sys.path.append('/opt/StorageEngineering/Python/modules')
from Utilities import Files
   


class HDS_STORAGE:
  
  def __init__(self,site):
    self.Site = site
    self.CLI = '/opt/HDS/HiCmdCLI_' + site + '/hicommandcli'
    self.Command = '/opt/HDS/HiCmdCLI_' + site + '/hicommandcli'
    self.AlertFile = '/opt/HDS/logs/Alerts_' + site + '.log'
    self.DiskErrors = []
    self.ArrayErrors = []
    self.Arrays = {}
    self.Arrays["45217"] = 'NYC_USPV1'
    self.Arrays["67034"] = 'SSC-MFVSP3'
    self.Arrays["55593"] = 'SSC-MFVSP4'
    self.Arrays["66195"] = 'SSC_VSP2'
    self.Arrays["53792"] = 'SSC_VSP1'
    self.Arrays["94077"] = 'SSC_VSP5'
    self.Arrays["45196"] = 'SSC_USPV1'
    self.Arrays["17550"] = 'SSC_USPV2'
    self.Arrays["48581"] = 'SSC_USPV4'
    self.Arrays["45175"] = 'SSC_USPV6'
    self.Arrays["17499"] = 'BFC_USPV2'
    self.Arrays["49073"] = 'BFC_USPV6'
    self.Arrays["49076"] = 'BFC_USPV7'
    self.Arrays["66198"] = 'BFC_VSP1'
    self.Arrays["67035"] = 'BFC_MFVSP2'
    


    
  def get_alerts(self):

    yesterday = str(datetime.date.fromtimestamp(time.time() - (60*60*24) ).strftime("%Y/%m/%d"))
    filter =  "\"timefilter=" + yesterday + " 00:00:00\""
    cmd = self.CLI + ' getalerts ' + filter
    self.Command = cmd
    # Exec the command...
    output = os.popen(cmd)
    
    for line in output:
      line = line.strip()
      
      ########## Array
      if "source=ARRAY" in line:
        source = line
        diskerror = 0
        fields = source.split('=')
        array = fields[1].split('.')
        array_serial = array[2]
        array_name = self.Arrays[array_serial] + "_" + array_serial
      elif "source=" in line:
        othersource = line      

      if "severity=" in line:
        severity = line      
        fields = line.split('=')
        severity_num = fields[1]
       
      if "description=" in line:
        description = line
        
      if "error reported for DKU Drive" in line:
        error = line
        diskerror += 1
        if array_serial == "67034" or array_serial == "55593":
          diskerror = 0
        
      if "timeOfAlert=" in line:
        event_time = line
        if array_serial == "67034" or array_serial == "55593":
          pass
        elif diskerror > 0:
          data = [array_name,severity,error,event_time]
          self.DiskErrors.append(', '.join(data))
        elif "back to normal" not in description:
          data = [array_name,severity,description,event_time]
          self.ArrayErrors.append(', '.join(data))          
          

      
      
"""    An instance of Alert
      number=773
      type=Server
      source=ARRAY.R700.66198
      severity=3
      component=DKU Drive
      description=Serious error reported for DKU Drive.
      actionToTake=Contact your service representative.
      data=The component is no longer working.
      timeOfAlert=2015/12/15 02:43:22

    An instance of Alert
      number=1233
      type=Server
      source=ARRAY.R700.67034
      severity=5
      component=DKU Drive
      description=Service error reported for DKU Drive.
      actionToTake=Contact your service representative.
      data=A minor error has occurred.
      timeOfAlert=2015/12/15 08:16:47
      
12/29/15 - 15:00:15 :WARNING: DISK ERROR - VMAX Failed Disk Alert VMAX40K_2545, BFC_vBlock SID=2545__SPINDLE=1B38
12/30/15 - 03:00:08 :WARNING: DISK ERROR - VMAX Failed Disk Alert VMAX200K_1358, Broomfield SID=1358__SPINDLE=1044
12/29/15 - 15:00:09 :WARNING: DISK ERROR - VMAX Failed Disk Alert VMAX10K_0957, Charlotte SID=0957__SPINDLE=F2
      
"""
      