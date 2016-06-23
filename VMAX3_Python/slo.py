#!/usr/bin/python


import sys, getopt, os, re, shutil, time

sys.path.append('/opt/StorageEngineering/Python/modules')

from xml.dom import minidom
from VMAX3_Rep import VMAX3_STORAGE
from HTML import HTML
from Utilities import Files
from Utilities import DateString



def createReports(sloObj,site,datacenter):
    
    www = HTML()
    html_index = '/www/' + site + '/fast.html'
    sloCSV = '/www/' + site + '/CSV/' + site + '_slo.csv'
    csv = open(sloCSV, 'w')
    f_index = open(html_index,'w')
    f_index.write(www.start_html('SLO Summary'))
    linkpath = "/" + site + "/CSV/"  + site + '_slo.csv'
    fpSummLink = '<a href=' + linkpath + '>SLO CSV</a>\n'
    f_index.write(www.EMC_Header(site,datacenter,'',fpSummLink))
    csv.write('SLO Report for ' + site + '\n\n')
    csv.write("SLO Policy,Response Time Target\n")
    
    f_index.write(www.start_table(3,'SLO Policies'))
    f_index.write(www.tr + www.th + 'Policy Name' + www.th + 'Response Time Target (ms)\n')
      
    for slo in sloObj.slo_policies:
      html = www.tr + www.td + slo +  www.td + sloObj.slo_policies[slo]  + "\n"
      csv.write(slo + ',' + sloObj.slo_policies[slo] + '\n')
      f_index.write(html)
    f_index.write(www.end_table)  
    f_index.write(www.end_html)  
    f_index.close()
    csv.close()


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
    sloObj = VMAX3_STORAGE(sid)
    sloObj.get_slo()
    createReports(sloObj,site,datacenter)  
 

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

