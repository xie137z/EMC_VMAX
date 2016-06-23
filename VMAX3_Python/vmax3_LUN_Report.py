#!/usr/bin/python

import sys, getopt, os, re, shutil, time
import MySQLdb as mysql


sys.path.append('/opt/StorageEngineering/Python/modules')
from VMAX3_Rep import VMAX3_STORAGE
from HTML import HTML
from Utilities import DateString
from Utilities import Files
from Utilities import EMail




def createReports(sgObj,site,datacenter,sid):
  #
  f = Files()
  csv = []
  csv.append('LUN_ID,SIZE,ALLOCATED\n')
  csvfile = '/www/download/ThinLUN_Report_' + sid + '.csv'

  for key in sgObj.TDEVs.keys(): 
      lun_id = key
      size = sgObj.TDEVs[key][0]
      allocated = sgObj.TDEVs[key][1]
      csvline = str(lun_id) + ',' + str(size) + ',' + str(allocated) + '\n'
      csv.append(csvline)
  f.write_file(csvfile,csv)      


def main():

  Arrays = {}
  #Arrays['1794'] = 'VMAX40K'
  # Open the output page and catch exceptions.
  try:
    ARRAYS = open('/opt/EMC/Scripts/Python/VMAX3/arrays.cfg','r')
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
    sgObj = VMAX3_STORAGE(sid)
    sgObj.get_thin_luns()
    createReports(sgObj,site,datacenter,sid)

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

