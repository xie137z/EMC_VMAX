#!/usr/bin/python


import sys, getopt, os, re, shutil, time, subprocess, datetime

sys.path.append('/opt/StorageEngineering/Python/modules')

from xml.dom import minidom
from VMAX3_Rep import VMAX3_STORAGE
from HTML import HTML
from Utilities import Files
import MySQLdb as mysql


def createReports(mvObj,site,datacenter):
    reportDate =  str(time.strftime("%c"))
    GB =  float(mvObj.mvCapTotal)/1024
    ProvisionedGB = "%.2f" % GB    
    info1 = 'Total Porvisioned=' + str(ProvisionedGB)
    www = HTML()
    f = Files()
    html_index = '/www/' + site + '/views.html'
    viewsCSV = '/www/' + site + '/CSV/' + site + '_views.csv'
    htmlpage = []
    csvpage = []
    
    htmlpage.append(www.start_html('MV Summary'))
    linkpath = "/" + site + "/CSV/"  + site + '_views.csv'
    mvSummLink = '<a href=' + linkpath + '>Views CSV</a>\n'
    htmlpage.append(www.EMC_Header(site,datacenter,info1,mvSummLink))
    csvpage.append('MV Report for ' + site + '\n\n')

    # Write out a table for Masking Views

    csvpage.append("View Name,SG,IG,PG,Capacity\n")
    for pg in mvObj.portgroups:
      htmlpage.append(www.start_table(3,'Masking Views on PG, ' + pg ))
      htmlpage.append("<tr><th>View Name<th>SG<th>IG<th>PG<th>Capacity</tr>\n")
      for mv in mvObj.portgroups[pg]:
        viewname = mv['MV']
        ig = mv['IG']
        pg = mv['PG']
        sg = mv['SG']
        gb = float(mv['MB'])/1024
        fmtgb =  "%.2f" % gb
        gb = str(fmtgb)
        sglink = "<a href=/" + site + "/SG/" + sg + ".html>" + sg + "</a>\n"
        iglink = "<a href=/" + site + "/IG/" + ig + ".html>" + ig + "</a>\n"
        row = [viewname,sglink,iglink,pg,gb]      
        htmlpage.append(www.tr_list(row))    
        csrow = [viewname,sg,ig,pg,gb]
        csvpage.append(', '.join(csrow) + '\n')
      htmlpage.append(www.end_table)    
    htmlpage.append(www.end_html)
    f.write_file(html_index,htmlpage)
    f.write_file(viewsCSV,csvpage)    


    
    
    dir = "/www/" + site + "/IG/"
    if not os.path.isdir(dir):
      subprocess.call(["mkdir", dir]) 
    
    for IG in mvObj.HostInitiatorGroups:
      igPage = '/www/' + site + '/IG/' + IG + '.html'
      f_ig = open(igPage,'w')
      f_ig.write(www.start_html('Initiator Group ' + IG))
      f_ig.write(www.EMC_Header(site,datacenter))
      # Write out a table for Masking Views
      f_ig.write(www.start_table(3,'Initiator Group ' + IG))
      f_ig.write("<tr><th>HBA Initiators</tr>\n")
     
      for wwpn in mvObj.HostInitiatorGroups[IG]:
        f_ig.write("<tr><th>" + wwpn + "</tr>\n")
      f_ig.write(www.end_table) 
      f_ig.write(www.end_html)
      f_ig.close()      

    for IG in mvObj.ClusterInitiatorGroups:
      igPage = '/www/' + site + '/IG/' + IG + '.html'
      f_ig = open(igPage,'w')
      f_ig.write(www.start_html('Cluster Initiator Group ' + IG))
      f_ig.write(www.EMC_Header(site,datacenter))
      # Write out a table for Masking Views
      f_ig.write(www.start_table(3,'Initiator Group ' + IG))
      f_ig.write("<tr><th>Cluster Nodes</tr>\n")
     
      for wwpn in mvObj.ClusterInitiatorGroups[IG]:
        link = '<a href=/' + site + '/IG/' + wwpn + '.html>' + wwpn + '</a>\n'
        f_ig.write("<tr><th>" + link + "</tr>\n")
      f_ig.write(www.end_table) 
      f_ig.write(www.end_html)
      f_ig.close()            

    # Database section
    # First, grab a list of known WWPN logins
    vmaxdb=mysql.connect(host="chatst3utsan01",user="emc",passwd="emc",db="vmax")
    cur = vmaxdb.cursor()
    query = "SELECT wwpn,ig FROM initiatorgroups"
    results  = cur.execute(query)
    rows = cur.fetchall()
    # Now create a simple list of logins. We use this to check whether we've seen a login before.
    # If we know this login, we just update the time seen and array/port.
    knownwwpns = []
    p = re.compile('\w+')
    for row in rows:
      wwpn = row[0]
      ig = row[1]

      key = ''.join(p.findall(wwpn + ig)).lower()    
      knownwwpns.append(key)
    # Now get the current date and time.
    today = datetime.date.today()
    formatteddate = today.strftime('%Y-%m-%d')
    now = datetime.datetime.now().time()
    formattedtime = now.strftime('%H:%M:%S')      
    
    for IG in mvObj.HostInitiatorGroups:
      for wwpn in mvObj.HostInitiatorGroups[IG]:
        wwpn = wwpn.lower()
        ig = str(IG)
        ig = ig.lower()
        
        insertquery = 'insert into initiatorgroups(wwpn,array_name,ig,record_date,record_time) '
        insertquery += " values('" + wwpn + "','" + site + "','"
        insertquery += ig + "',NOW(),NOW() );"

        updatequery = 'update initiatorgroups SET array_name = %s, ig = %s, record_date = %s, record_time = %s '
        updatequery += ' WHERE wwpn = %s AND ig = %s'

        wwpn_ig = ''.join(p.findall(wwpn + ig))
        
        if wwpn_ig in knownwwpns:
          
          results  = cur.execute(updatequery, (site,ig,formatteddate,formattedtime,wwpn,ig))
        else:
          results  = cur.execute(insertquery)       


    
      

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
    mvObj = VMAX3_STORAGE(sid)
    mvObj.get_views()
    createReports(mvObj,site,datacenter)        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

