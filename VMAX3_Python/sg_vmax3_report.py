#!/usr/bin/python

import sys, getopt, os, re, shutil, time, subprocess

sys.path.append('/opt/StorageEngineering/Python/modules')

from xml.dom import minidom
from VMAX3_Rep import VMAX3_STORAGE
from HTML import HTML
from Utilities import Files



def createReports(sgObj,site,datacenter):
    #
    # Create directories if they don't exist
    orange = '#F7EE6F'
    green =  '#69F24E'       
    dir = "/www/" + site + "/SG/"
    if not os.path.isdir(dir):
      subprocess.call(["mkdir", dir]) 
    dir = '/www/' + site + '/CSV'      
    if not os.path.isdir(dir):
      subprocess.call(["mkdir", dir]) 
    #
    #    
    reportDate =  str(time.strftime("%c"))
    GB =  float(sgObj.ProvisionedCapacity)/1024
    ProvisionedGB = "%.2f" % GB
    info1 = 'Total Porvisioned(GB)=' + str(ProvisionedGB)

    www = HTML()
    html_index = '/www/' + site + '/index.html'
    sgSummCSV = '/www/' + site + '/CSV/' + site + '_SG_Summary.csv'
    f_index = open(html_index,'w')
    f_SummCSV = open(sgSummCSV,'w')
    f_SummCSV.write("Storage Group,SLO Policy,Capacity GB,Masking View,Max IOPS,Max MB/s\n")
    linkpath = "/" + site + "/CSV/"  + site + '_SG_Summary.csv'
    sgSummLink = '<a href=' + linkpath + '>Summary CSV</a>\n'
    f_index.write(www.start_html('SG Summary'))
    f_index.write(www.EMC_Header(site,datacenter,info1,sgSummLink))
    f_index.write(www.start_table())
    f_index.write(www.end_table)
    fpTables = {}
    policies = {}
    for sg in sgObj.SGs:

      #
      color = ''  
      link = "/" + site + "/SG/" + sg + ".html"
      sgGB = float(sgObj.SG2Capacity[sg])/1024
      sgProvisionedGB = "%.2f" % sgGB
      MVs = sgObj.SGinMV[sg]
      fp = sgObj.SGinSLO[sg]
      policies[fp] = 1
      if not fp in fpTables:
        fpTables[fp] = []      
      IOPS_LIMIT = str(sgObj.SG_IOPS_Limit[sg])
      MB_LIMIT = str(sgObj.SG_MB_Limit[sg])
      if MVs.upper() == 'NO':
        color = orange
      
      rowlist = ["<a href=" + link + '>' + sg + "</a>",fp, str(sgProvisionedGB),MVs,IOPS_LIMIT,MB_LIMIT]
      SGhtml = www.tr_list(rowlist,color)
      fpTables[fp].append(SGhtml)
      
      f_SummCSV.write(sg + ',' + fp + ',' + str(sgProvisionedGB)   + ',' + MVs + ',' + IOPS_LIMIT + ',' + MB_LIMIT + "\n")
      # go ahead and write out the sg detail HTML page.
      sgfile = "/www/" + site + "/SG/" + sg + ".html"
      sgCSV = "/www/" + site + "/CSV/" + site + '_' + sg + ".csv"
      linkpath = "/" + site + "/CSV/" + site + '_' + sg + ".csv"
      link1 = '<a href=' + linkpath + '>SG CSV</a>\n'
      f_sg = open(sgfile,'w')
      f_sgCSV = open(sgCSV,'w')
      f_sgCSV.write('Storage Group Report for ' + sg + '\n\n\n')
      f_sg.write(www.start_html('SG Detail'))
      f_sg.write(www.EMC_Header(site,datacenter,'',link1))
      html = "<p><H3><center>Detailed Storage Report for " + sg + " SSC_VMAX40K_1794</center></H3>\n"
      f_sg.write(html)
      f_sg.write(www.start_table())
      f_sg.write(www.tr + www.th + "Storage Group<th>SLO Policy<TH>Capacity GB</tr>\n") 
      html = www.tr + www.td +  sg + www.td + fp + www.td + str(sgProvisionedGB) + "\n"
      f_sg.write(html)
      f_sg.write(www.end_table)  
      
      f_sg.write(www.start_table(3,'Device List'))
      f_sg.write(www.tr + www.th + "Device<th>Capacity GB</tr>\n") 
      f_sgCSV.write("Volume,Capacity GB\n")
      for device in sgObj.SGs[sg]:
        devGB = float(sgObj.SGs[sg][device])/1024
        dev_formatted = "%.2f" % devGB
        html = www.tr + www.td + device + www.td + str(dev_formatted) +"\n"
        f_sg.write(html)
        f_sgCSV.write(device + ',' + str(dev_formatted) + '\n')
      f_sg.write(www.end_table)
      f_sg.write(www.end_html)
      f_sg.close()
      f_sgCSV.close()
      
    for fp in policies:
      f_index.write(www.start_table(3,'Groups with SLO ' + fp + ' Policy'))
      f_index.write("<tr><th>Storage Group<th>SLO Policy<TH>Capacity GB<TH>Masking View<TH>IOPS Limit<TH>MB/s Limit</tr>\n")   
      for line in fpTables[fp]:
        f_index.write(line)
      f_index.write(www.end_table)    
    f_index.write(www.end_html)  
    f_index.close()
    f_SummCSV.close()


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
    sgObj.get_sg()
    createReports(sgObj,site,datacenter)        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

