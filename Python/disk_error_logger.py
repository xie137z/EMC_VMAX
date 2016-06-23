#!/usr/bin/python

import sys, getopt, os, re, shutil, subprocess, time
from xml.dom import minidom
sys.path.append('/opt/StorageEngineering/Python/modules')
from Utilities import Files                          
  
def LogErrors():
  log = []
  unfiltered = []
  adds = []
  failed_disks_log = '/opt/EMC/log/failed_disks.log'
  failed_disks_unfiltered = '/opt/EMC/log/unfiltered.log'
  mylog = '/opt/EMC/log/monitor.log'
  h = Files()
  h.write_log(mylog,"Starting logger..." + "\n")
  h.read_file(failed_disks_log)
  for line in h.readfile:
    if not line.startswith("#"):
      log.append(line)
  h.read_file(failed_disks_unfiltered)
  for line in h.readfile:
    if not line.startswith("#"):
      unfiltered.append(line)  
  for line in unfiltered:
    if line not in log:
      h.write_log(mylog,"New Failed Disk!: " + line + "\n")
      adds.append(line + '\n')
    else:
      h.write_log(mylog,"Already in the log: " + line + "\n")

  if len(adds) > 0:
    h.write_file_append(failed_disks_log,adds)
        

def main():
  LogErrors()        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()