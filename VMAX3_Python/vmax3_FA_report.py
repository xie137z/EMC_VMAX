#!/usr/bin/python

import sys, getopt, os, re, shutil, time
import MySQLdb as mysql


sys.path.append('/opt/StorageEngineering/Python/modules')
from BRCD import BRCD
from xml.dom import minidom
from VMAX3_Rep import VMAX3_STORAGE
from HTML import HTML
from Utilities import DateString
from Utilities import Files
from Utilities import EMail




def createReports(sgObj,site,datacenter):
    www = HTML()
    mailObj = EMail()
    swObj = BRCD()
    swObj.get_connection_map()    
    dates = DateString()

    page = []
    csvpage = []
    temppage = []    
    today =  dates.today
    yesterday = dates.yesterday
    tomorrow = dates.tomorrow
    pagedirs = ['download','history']
    subdirs = [today,tomorrow,yesterday]
    f = Files()
    for dir in pagedirs:
      f.dir = '/var/www/html/' + dir
      f.mkdir() 
      for sub in subdirs:
        f.dir = '/var/www/html/' + dir + '/' + sub
        f.mkdir() 
    csvfile = '/www/download/' + today + '/' + site + '_FA.csv'
    csvlink = '<a href=/download/' + today + '/' + site + '_FA.csv>CSV</a>'
    htmlfile = '/www/' + site + '/FA_Ports.html'

        
    reportDate =  str(time.strftime("%c")) 

    page.append(www.start_html('FA Port Report for ' + site))
    page.append(www.EMC_Header(site,datacenter,'',csvlink))
    
     
    page.append(www.start_table(3,site))
    heading = ['FA Port','WWN','Device Count', 'Switch', 'Portname', 'Port']
    page.append(www.th_list(heading))
 
    csvpage.append('FA Port Report for ' + site + '\n\n')
    csvpage.append(', '.join(heading) + '\n')
    
 
    for FAPORT in sorted(sgObj.FA2WWNmap):
      port = str(FAPORT)

      wwn = str(sgObj.FA2WWNmap[FAPORT])
      if wwn.lower() in swObj.connectionmap:
        fields = swObj.connectionmap[wwn.lower()]
        switchname = fields[0] 
        switchportname =   fields[1]
        switchport =   fields[2]
      else:
        switchname = 'Not_Connected' 
        switchportname =   'Not_Connected' 
        switchport =   'Not_Connected'       
      if 'Total' in port:
        color = '#C7C5C6'
        switchname = '---' 
        switchportname =   '---' 
        switchport =   '---'       
      else:
        color = '#DEF2FA'              
      dev_count  = str(sgObj.FA_Device_Count[FAPORT])
      row = [port,wwn, dev_count, switchname, switchportname, switchport]
      csvpage.append(', '.join(row) + '\n')
      page.append(www.tr_list(row,color))
    page.append(www.end_table)
    page.append(www.end_html)
    f.write_file(htmlfile,page)
    f.write_file(csvfile,csvpage)
 
    

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
    sgObj.get_fa_info()
    createReports(sgObj,site,datacenter)        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

