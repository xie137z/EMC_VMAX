#!/usr/bin/python


import sys, getopt, os, re, shutil, time

sys.path.append('/opt/StorageEngineering/Python/modules')

from xml.dom import minidom
from EMC_Rep import VMAX_STORAGE
from HTML import HTML




def createReports(fpObj,site,datacenter):


  # 
  heading = ['SG_Name']
  for tier in fpObj.tiernames:
    heading.append(tier)
  print heading
  for sg in fpObj.tiers:
    line = [str(sg)]
    for tiername in fpObj.tiernames:
      if tiername in fpObj.tiers[sg]:
        line.append(fpObj.tiers[sg][tiername])
      else:
        line.append('0')
    print line
 


def main():
  Arrays = {}

  try:
    ARRAYS = open('/opt/EMC/Scripts/Python/arrays.cfg','r')
  except IOError:
    print "Failed opening ", report
    sys.exit(2)
  for line in ARRAYS:
    line = line.strip()
    lines = line.split()
    if len(lines) == 3:
      # Skip comments
      if not line.startswith("#"):
        Arrays[lines[0]] = lines[1]
        datacenter = lines[2]
  for sid in Arrays:
    model = Arrays[sid]
    site = model + '_' + sid  
    fpObj = VMAX_STORAGE(sid)
    fpObj.get_fast_demand()
    createReports(fpObj,site,datacenter)        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

