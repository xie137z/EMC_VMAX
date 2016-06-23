#!/usr/bin/python

import sys, getopt, os, re, shutil, time, subprocess

sys.path.append('/opt/StorageEngineering/Python/modules')

from xml.dom import minidom
from VMAX3_Rep import VMAX3_STORAGE
from HTML import HTML
from Utilities import Files


def createReports(symObj,site,datacenter,sid):
    #
    www = HTML()
    # Create directories if they don't exist
    f = Files()
    f.dir = "/www/" + site + "/OR/"
    f.mkdir()
    htmlfile = '/www/' + site + '/OR/index.html'
    perf = '/opt/EMC/Scripts/shell/rcopyperf_' + sid + '.log'
    f.read_file(perf)
    page = []
    page.append(www.start_html_refresh('OR Sessions'))
    page.append(www.EMC_Header(site,datacenter))
    page.append(www.start_table(1,"OR Port Performance"))
    header = ["FA Port","MB/s","Ceiling","Number of Devices"]
    page.append(www.th_list(header))
    perftotal = 0
    for line in f.readfile:
      line = line.strip()
      fields = line.split()
      if len(fields) == 5:
        fields = fields[1:5]
      perftotal += int(fields[1])
      page.append(www.tr_list(fields))
    page.append(www.tr + www.th + "Total OR MB/s" + www.th + str(perftotal))
    page.append(www.end_table)  
    page.append('<br><br><pre>\n')
    for line in symObj.or_list:
      page.append(line)
    f.write_file(htmlfile,page)
    
    #
    #    

    


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
    symObj = VMAX3_STORAGE(sid)
    symObj.get_or_sessions()
    createReports(symObj,site,datacenter,sid)        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

