#!/usr/bin/python

import sys, getopt, os, re, shutil, time

sys.path.append('/opt/StorageEngineering/Python/modules')

from xml.dom import minidom
from EMC_Rep import VMAX_STORAGE
from HTML import HTML
from Utilities import DateString
from Utilities import Files
from Utilities import EMail


def createReports(sgObj,site,datacenter):
    www = HTML()
    mailObj = EMail()
    
    dates = DateString()
    tiers = ['EFD','FC','SATA']
    alertLimits = {}
    alertLimits['EFD'] = 99
    alertLimits['FC'] = 80
    alertLimits['SATA'] = 85
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
    csvfile = '/www/download/' + today + '/' + site + '_pools.csv'
    csvfileperm = '/www/download/' + site + '_pools.csv'
    csvlink = '<a href=/download/' + today + '/' + site + '_pools.csv>CSV</a>'
    yesterdaylink = '<a href=/history/' + yesterday + '/' + datacenter + site + '_EMC_Summary.html>' + yesterday + '</a>'  
    tomorrowlink = '<a href=/history/' + tomorrow + '/' + datacenter + site + '_EMC_Summary.html>' + tomorrow + '</a>' 
    htmlfile1 = '/www/history/' + today + '/' + datacenter + site + '_EMC_Summary.html'
    tempfile = '/www/history/' + tomorrow + '/' + datacenter + site + '_EMC_Summary.html'
    htmlfile2 = '/www/' + datacenter + site + '_EMC_Summary.html'

        
    reportDate =  str(time.strftime("%c")) 

    page.append(www.start_html('Thin Pool Report for ' + site))
    page.append(www.EMC_Header(site,datacenter,'',csvlink))
    
    page.append('<p><br><table align=center  border=3>\n')
    row = ['EMC Storage Summary Report',tomorrowlink,yesterdaylink]
    page.append(www.th_list(row)) 
    page.append(www.end_table)
    
    
    page.append(www.start_table(3,site))
    heading = ['Pool','Capacity','Used','Percent Used','Free','Provisioned','Subscription','Subscription Limit','PRC','Technology','Protection']
    page.append(www.th_list(heading))
    total_usable = 0 
    total_provisioned = 0 
    total_used = 0
    total_free = 0
    #csvpage.append('Thin Pool Report for ' + site + '\n\n')
    csvpage.append(', '.join(heading) + '\n')

    
    alertMessage = 'The following pools exceed set thresholds...\n\n'
    alerts = 0
    for tier in tiers:
      for pool in sgObj.pools.keys():
        comparepool = str(pool)
        comparepool = pool.upper()
        if tier in comparepool:
          ##########
          compression = sgObj.pooldetails[pool]['COMPRESSION']
          subscription_limit = sgObj.pooldetails[pool]['SUBSCRIPTION_LIMIT']
          PRC = sgObj.pooldetails[pool]['PRC']
          tech = sgObj.pooldetails[pool]['TECH']
          protection = sgObj.pooldetails[pool]['LAYOUT']
          ##########
          usable = float(sgObj.pools[pool]['total_usable_tracks_gb'])
          used = float(sgObj.pools[pool]['total_used_tracks_gb'])
          percent_used = sgObj.pools[pool]['percent_full']
          free = float(sgObj.pools[pool]['total_free_tracks_gb'])
          subscription = sgObj.pools[pool]['subs_percent']
          usable = int(round(usable,0))
          used = int(round(used,0))
          free = int(round(free,0))
          if int(subscription) == 0:
            provisioned = 0;
          else:
            provisioned = usable * ( float(subscription) / 100)
          total_provisioned += provisioned
          total_usable += usable
          total_used += used
          total_free += free
          html = www.tr
          if int(percent_used) >= alertLimits[tier]:
            html = www.alerttr
            alertMessage += "Thin pool " + comparepool + " is " + str(percent_used) + "% used.\n"
            alertMessage += str(free) + " GB free remain in the pool\n"
            alertMessage +=  " The threshold for " + comparepool + ' is set to ' + str(alertLimits[tier]) + '%\n\n'
            alerts += 1
          row = [pool,str(usable),str(used),str(percent_used),str(free),str(provisioned),subscription,subscription_limit,PRC,tech,protection]
          csvpage.append(', '.join(row) + '\n')
          
          page.append(www.tr_list(row))
          
    total_pct_used = int((int(total_used) / float(total_usable)) * 100)
    total_subscription = int((int(total_provisioned) / float(total_usable)) * 100)
    row = ['Totals',str(total_usable),str(total_used),str(total_pct_used),str(total_free),str(total_provisioned),str(total_subscription),'___','___','___','___']
    
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
      mailObj.subject = "Storage Capacity Alert, " + site + ', ' + datacenter
      mailObj.message = alertMessage
      mailObj.send_mail()   
    

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
    sgObj = VMAX_STORAGE(sid)
    sgObj.get_thinpools()
    createReports(sgObj,site,datacenter)        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

