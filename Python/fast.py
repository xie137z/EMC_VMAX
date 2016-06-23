#!/usr/bin/python


import sys, getopt, os, re, shutil, time

sys.path.append('/opt/StorageEngineering/Python/modules')

from xml.dom import minidom
from EMC_Rep import VMAX_STORAGE
from HTML import HTML
from Utilities import Files
from Utilities import DateString



def createReports(fpObj,site,datacenter):
    
    www = HTML()
    html_index = '/www/' + site + '/fast.html'
    fastCSV = '/www/' + site + '/CSV/' + site + '_fast.csv'
    csv = open(fastCSV, 'w')
    f_index = open(html_index,'w')
    f_index.write(www.start_html('MV Summary'))
    linkpath = "/" + site + "/CSV/"  + site + '_fast.csv'
    fpSummLink = '<a href=' + linkpath + '>FAST CSV</a>\n'
    
    demandReportPath = '/' + site + '/fast_demand.html'
    DemandReportLink = '<a href=' + demandReportPath + '>FAST-VP Demand Report</a>\n'
    fastReportPath = '/' + site + '/fast.html'
    fastReportLink = '<a href=' + fastReportPath + '>FAST-VP Policy Report</a>\n'

    
    
    f_index.write(www.EMC_Header(site,datacenter,'',fpSummLink))
    
    f_index.write('<p><br><table align=center  border=3>\n')
    row = [fastReportLink,DemandReportLink]
    f_index.write(www.th_list(row))
    f_index.write(www.end_table)
    
    csv.write('FAST-VP Report for ' + site + '\n\n')

    
    
    csv.write("Fast Policy,Tier,Max Percent per DG\n")
    for fp in fpObj.fast_policies:
      # Write out a table for FAST Policy
      txt = 'FAST-VP Policy: ' + fp + '\n'
      f_index.write(www.start_table(3,txt))
      f_index.write(www.tr + www.th + 'Tier Name' + www.th + 'Max Percent per SG\n')
      for tier in fpObj.fast_policies[fp]:
        html = www.tr + www.td + tier +  www.td + fpObj.fast_policies[fp][tier]  + "\n"
        csv.write(fp + ',' + tier + ',' + fpObj.fast_policies[fp][tier] + '\n')
        f_index.write(html)
      f_index.write(www.end_table)  
    f_index.write(www.end_html)  
    f_index.close()
    csv.close()

    

def createDemandReport(fpObj,sgObj,site,datacenter):
  dates = DateString()
  htmlpage = []
  csvpage = []
  temppage = []    
  www = HTML()
  f = Files()

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

  csvfile = '/www/download/' + today + '/' + site + '_fast_demand.csv'
  csvfileperm = '/www/download/' + site + '_fast_demand.csv'
  csvlink = '<a href=/download/' + today + '/' + site + '_fast_demand.csv>CSV</a>'
  yesterdaylink = '<a href=/history/' + yesterday + '/' + datacenter + '_fast_demand.html>' + yesterday + '</a>'  
  tomorrowlink = '<a href=/history/' + tomorrow + '/' + datacenter + '_fast_demand.html>' + tomorrow + '</a>' 
  htmlfile1 = '/www/history/' + today + '/' + datacenter + '_fast_demand.html'
  tempfile = '/www/history/' + tomorrow + '/' + datacenter + '_fast_demand.html'
  htmlfile2 = '/www/' + datacenter + '_fast_demand.html'      
  
  html_index = '/www/' + site + '/fast_demand.html'
  fastCSV = '/www/' + site + '/CSV/' + site + '_fast_demand.csv'
  
  htmlpage.append(www.start_html('FAST Demand'))
  htmlpage.append(www.EMC_Header(site,datacenter,'',csvlink))

  
  demandReportPath = '/' + site + '/fast_demand.html'
  DemandReportLink = '<a href=' + demandReportPath + '>FAST-VP Demand Report</a>\n'
  fastReportPath = '/' + site + '/fast.html'
  fastReportLink = '<a href=' + fastReportPath + '>FAST-VP Policy Report</a>\n'
  

  htmlpage.append('<p><br><table align=center  border=3>\n')
  row = [fastReportLink,DemandReportLink]
  htmlpage.append(www.th_list(row))
  htmlpage.append(www.end_table)

  htmlpage.append('<p><br><table align=center  border=3>\n')
  row = ['FAST Demand Report',tomorrowlink,yesterdaylink]
  htmlpage.append(www.th_list(row)) 
  htmlpage.append(www.end_table)
  
  csvpage.append('FAST-VP Report for ' + site + '\n\n')
  
  htmlpage.append(www.start_table(3,'FAST-VP Demand report'))
  heading = ['SG_Name','Policy']
  for tier in fpObj.tiernames:
    heading.append(tier)
  heading.append('SG_USED')
  heading.append('SG_PROVISIONED')
  htmlpage.append(www.th_list(heading))
  csvpage.append(', '.join(heading) + '\n')

  for sg in fpObj.tiers:
    policy = fpObj.Associations[sg]
    GB = float(sgObj.SG2Capacity[sg])/1024
    ProvisionedGB = "%.2f" % GB
    sg_provisioned =  str(ProvisionedGB)  + ' GB'
    # 
    sglinkpath = "/" + site + "/SG/" + sg + ".html"
    sglink = '<a href=' + sglinkpath + '>' + str(sg) + '</a>'
    line = [sglink,policy]
    line2 = [sg,policy]
    for tiername in fpObj.tiernames:
      if tiername in fpObj.tiers[sg]:
        line.append(fpObj.tiers[sg][tiername])
        line2.append(fpObj.tiers[sg][tiername])
      else:
        line.append('0')
        line2.append('0') 
    # The next 5 lines add total used and provisioned columns...
    sg_total = str(fpObj.tiers[sg]['SG_USED']) + ' GB'  
    line.append(sg_total)
    line2.append(sg_total)
    line.append(sg_provisioned)
    line2.append(sg_provisioned)
    #    
    csvpage.append(', '.join(line2) + '\n')
    htmlpage.append(www.tr_list(line))
  htmlpage.append(www.end_table)  
  htmlpage.append(www.end_html)  
  f.write_file(html_index,htmlpage)
  f.write_file(fastCSV,csvpage)        
  f.write_file(htmlfile2,htmlpage)
  f.write_file(htmlfile1,htmlpage)
  f.write_file(csvfile,csvpage)
  f.write_file(csvfileperm,csvpage)
  temppage.append(www.start_html())
  temppage.append(www.Not_Found_Header('Report not created yet for '+tomorrow))
  temppage.append(www.end_html)
  f.write_file(tempfile,temppage)    

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
    fpObj.get_fast()
    createReports(fpObj,site,datacenter)  
    fpObj.get_fast_demand() 
    sgObj = VMAX_STORAGE(sid)
    sgObj.get_sg()    
    createDemandReport(fpObj,sgObj,site,datacenter)        

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit()

