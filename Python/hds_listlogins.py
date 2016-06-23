#!/usr/bin/python

import sys, getopt, os, re, shutil, time
from xml.dom import minidom

HTML_BEGIN =  """
<HTML>
<HEAD>
  <Title>EMC Storage Summary</Title>
</HEAD>

<body align=center>
<p><H3><center>EMC Storage Summary</center></H3>
"""

SYMCLI = '/opt/emc/SYMCLI/bin/'
sid = '1794'
cmd = SYMCLI + 'symcfg -sid ' + sid  + ' list -pool -thin -detail -output xml_e'
output = os.popen(cmd)

XML = '/opt/EMC/Scripts/Python/DATA/pool.xml'
f = open(XML, 'w')
for line in output:
  f.write(line)
f.close()


doc = minidom.parse(XML)

pools = {}


for node in doc.getElementsByTagName('DevicePool'):
  pooldata = {}
  for child in node.childNodes:
    if child.nodeType == 1:
      if child.nodeName == "pool_name":
        PoolName = child.firstChild.nodeValue
      else:
        pooldata[child.nodeName] = child.firstChild.nodeValue
      if child.nodeName == "subs_percent":
        pools[PoolName] = pooldata.copy()
        
if 'pool_name' in pools:
  del pools['pool_name']


  
reportDate =  str(time.strftime("%c"))

  
  
f = open('/www/Charlotte_EMC_Summary.html','w')
f.write(HTML_BEGIN)
f.write("<p>Report created on " + reportDate + "<br>\n")
f.write('<p><br><table align=center  border=3>')
f.write('<caption>SSC_VMAX40K_1794</caption>')
f.write("<tr><th>Pool<th>Capacity<th>Used<th>Free<th>Subscription")  
for pool in pools.keys():
  usable = pools[pool]['total_usable_tracks_gb']
  used = pools[pool]['total_used_tracks_gb']
  free = pools[pool]['total_free_tracks_gb']
  subscription = pools[pool]['subs_percent']
  html = "<tr><td>" + pool + "<td>" + usable + "<td>" + used + "<td>" + free + "<td>" + subscription
  f.write(html)
f.write('</table>')
f.write('</body>')
f.write('</html>')
f.close()
