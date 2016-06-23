#!/usr/bin/python

import sys, getopt, os, re, shutil, time, subprocess
sys.path.append('/opt/StorageEngineering/Python/modules')

from Utilities import Files




def get_thin_luns(sid):
  #
  f = Files()
  csv = []
  csv.append('LUN_ID,SIZE,ALLOCATED\n')
  csvfile = '/www/download/ThinLUN_Report_' + sid + '.csv'
  cmd =  '/emc/symcfg -sid ' + sid  + ' list -tdev -GB '
  output = os.popen(cmd)
  for line in output: 
    if 'PROD_FCR1' in line:
      #line.strip()
      fields = line.split()
      lun_id = fields[0]
      size = fields[3] 
      allocated = fields[4]
      
      csvline = str(lun_id) + ',' + str(size) + ',' + str(allocated) + '\n'
      #print csvline
      csv.append(csvline)
  f.write_file(csvfile,csv)      


def main():
  sid = '2545'
  get_thin_luns(sid)

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

