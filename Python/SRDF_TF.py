#!/usr/bin/python

import sys, getopt, os, re, shutil, time

sys.path.append('/opt/StorageEngineering/Python/modules')


from EMC_SRDF import VMAX_SRDF_Util
from HTML import HTML
from Utilities import DateString
from Utilities import Files
from Utilities import EMail


def createReports(srdfObj,site,datacenter):
    Alerts = {}
    alert = 0
    www = HTML()
    f = Files()
    mailObj = EMail()
    dates = DateString()
    page = []
    csvpage = []
    htmlfile = '/www/SRDF.html'
    csvfile = '/www/SRDF.csv'
    reportDate =  str(time.strftime("%c")) 
    page.append(www.start_html('SRDF Report'))
    html = '<p>Report Date: ' + reportDate + '<br><br>'
    html += 'SRDF Status Report<br><br>'
    page.append(html)
    for group in srdfObj.SRDF_Groups:
      # Print header table
      page.append('<p><br><table align=center  border=3>\n')
      row = ['Group ID','SymID','RemoteSymID','Tracks Pending','Delta Time']
      page.append(www.th_list(row))  
      csvpage.append(', '.join(row) + '\n')
      info = srdfObj.SRDF_Groups_Info[group]
      row = [  group, info['symid'],info['remote_symid'],info['tracks'],info['delta']  ]
      page.append(www.tr_list(row)) 
      page.append(www.end_table)
      csvpage.append(', '.join(row) + '\n')
      # Print Pair data
      page.append('<p><br><table align=center  border=3>\n')
      row = ['Source','Target','Link State','Mode','Replication State']
      page.append(www.th_list(row)) 
      csvpage.append(', '.join(row) + '\n')     
      pairs = srdfObj.SRDF_Groups_Pairs[group]
      for pair in pairs:
        list = pair.split(',')
        if  list[4] != 'Consistent':
          bgcolor="#B0B3AF"
          alert += 1
          Alerts[group] = "SRDF is not in a consistent state for " + group
        else:
          bgcolor="#69F24E"
        page.append(www.tr_list(list,bgcolor)) 
        csvpage.append(', '.join(list) + '\n')     
      page.append(www.end_table)
     
    
    page.append(www.end_html)
    f.write_file(htmlfile,page)
    f.write_file(csvfile,csvpage)

    if alert > 0:
      alertMessage = "The Following SRDF Groups are not Consistent\n\n"
      for groupalert in Alerts:
        alertMessage += Alerts[groupalert]     
      mailObj.subject = "VMAX SRDF Alert " + site + ', ' + datacenter
      mailObj.message = alertMessage
      mailObj.send_mail()   

def main():
  sid = '1794'
  model = 'VMAX40K'
  datacenter = 'Charlotte'
  site = model + '_' + sid  
  srdfObj = VMAX_SRDF_Util()
  srdfObj.get_srdf_status()
  createReports(srdfObj,site,datacenter)        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

"""
Notes on usage...
>>> for group in srdfObj.SRDF_Groups:
...   info = srdfObj.SRDF_Groups_Info[group]
...   for data in info:
...     print data + ' ' + info[data]
...
remote_symid 000195701852
tracks 0
symid 000195701794
delta 00:00:17
remote_symid 000195701852
tracks 0
symid 000195701794
delta 00:00:24
"""

