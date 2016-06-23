#!/usr/bin/python

import sys, getopt, os, re, shutil, time

sys.path.append('/opt/StorageEngineering/Python/modules')

from xml.dom import minidom
from EMC_Disks import VMAX_Disk_Util
from HTML import HTML
from Utilities import DateString
from Utilities import Files
from Utilities import EMail


def createReports(sgObj,site,datacenter):
    www = HTML()
    mailObj = EMail()
    
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
    csvfile = '/www/download/' + today + '/' + datacenter +  site +  '_failed_disks.csv'
    csvfileperm = '/www/download/' + datacenter +  site +   '_failed_disks.csv'
    csvlink = '<a href=/download/' + today + '/' + datacenter +  site + '_failed_disks.csv>CSV</a>'
    yesterdaylink = '<a href=/history/' + yesterday  + '/' + datacenter + site +  '_Failed_disks.html>' + yesterday + '</a>'  
    tomorrowlink = '<a href=/history/' + tomorrow + '/' + datacenter + site + '_Failed_disks.html>' + tomorrow + '</a>' 
    htmlfile1 = '/www/history/' + today + '/' + datacenter + site + '_Failed_disks.html'
    tempfile = '/www/history/' + tomorrow + '/' + datacenter + site + '_Failed_disks.html'
    htmlfile2 = '/www/' + datacenter + site + '_Failed_disks.html'
    logfile = '/www/' + site + '_Failed_disks.log'
    log = []
        
    reportDate =  str(time.strftime("%c")) 

    page.append(www.start_html('Failed Disk Report for ' + site))
    page.append(www.EMC_Header(site,datacenter,'',csvlink))
    
    page.append('<p><br><table align=center  border=3>\n')
    row = ['Failed Disk Report',tomorrowlink,yesterdaylink]
    page.append(www.th_list(row)) 
    page.append(www.end_table)
    
    
    page.append(www.start_table(3,site))
    heading = ['Disk_ID','DA_Port','Spindle_ID','Tech','Speed','Vendor','Size','Failed']
    page.append(www.th_list(heading))
    csvpage.append(', '.join(heading) + '\n')

    
    alertMessage = 'Disk Error...\n\n'
    alertMessage += ', '.join(heading) + '\n\n'
    alerts = 0

    for disk in sgObj.FailedDisks:
      alerts += 1
      info = sgObj.FailedDisks[disk].split()
      row = [info[0],info[1],info[2],info[3],info[4],info[5],info[6],info[7]]
      alertMessage += ', '.join(row) + '\n\n'
      csvpage.append(', '.join(row) + '\n')
      page.append(www.tr_list(row))
          

    page.append(www.end_table)
    page.append(www.end_html)
    f.write_file(htmlfile2,page)
    f.write_file(htmlfile1,page)
    f.write_file(csvfile,csvpage)
    f.write_file(csvfileperm,csvpage)
    temppage.append(www.start_html())
    temppage.append(www.Not_Found_Header('Report not created yet for '+tomorrow))
    temppage.append(www.end_html)
    f.write_file(tempfile,temppage)
    if alerts > 0:
      
      mailObj.subject = "WARNING: DISK ERROR - VMAX Failed Disk Alert " + site + ', ' + datacenter
      mailObj.message = alertMessage
      mailObj.send_mail()

      if len(sgObj.New_Failures.keys()) > 0:
        reportDate =  str(time.strftime("%x - %X"))
        for failed_disk in sgObj.New_Failures.keys():
          log.append(reportDate + " :" + mailObj.subject + " " + failed_disk + "\n")      
        f.write_file(logfile,log) 
      
    # Generate new INC if sgObj.FailedDisks has any newly failed disks
    # New code goes below this line    
    

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
    sgObj = VMAX_Disk_Util(sid)
    sgObj.get_failed_disks()
    createReports(sgObj,site,datacenter)        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

