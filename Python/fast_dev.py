#!/usr/bin/python


import sys, getopt, os, re, shutil, time

sys.path.append('/opt/StorageEngineering/Python/modules')

from xml.dom import minidom
from EMC_Rep import VMAX_STORAGE
from HTML import HTML
from Utilities import Files



def createReports(fpObj,site,datacenter):
  htmlpage = []
  csvpage = []
  www = HTML()
  f = Files()
  html_index = '/www/' + site + '/fast_demand.html'
  fastCSV = '/www/' + site + '/CSV/' + site + '_fast_demand.csv'
  
  htmlpage.append(www.start_html('MV Summary'))
  linkpath = "/" + site + "/CSV/"  + site + '_fast_demand.csv'
  fpSummLink = '<a href=' + linkpath + '>FAST CSV</a>\n'
  htmlpage.append(www.EMC_Header(site,datacenter,'',fpSummLink))
  csvpage.append('FAST-VP Report for ' + site + '\n\n')
  
  htmlpage.append(www.start_table(3,'FAST-VP Demand report'))
  heading = ['SG_Name']
  for tier in fpObj.tiernames:
    heading.append(tier)
  htmlpage.append(www.th_list(heading))
  csvpage.append(', '.join(heading))

  for sg in fpObj.tiers:
    # 
    line = [str(sg)]
    for tiername in fpObj.tiernames:
      if tiername in fpObj.tiers[sg]:
        line.append(fpObj.tiers[sg][tiername])
      else:
        line.append('0')
    
    csvpage.append(', '.join(line))
    htmlpage.append(www.tr_list(line))
  htmlpage.append(www.end_table)  
  htmlpage.append(www.end_html)  
  f.write_file(html_index,htmlpage)
  f.write_file(fastCSV,csvpage)    


def main():
  Arrays = {}
  #Arrays['1794'] = 'VMAX40K'
  # Open the output page and catch exceptions.
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

