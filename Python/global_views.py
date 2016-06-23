#!/usr/bin/python



import sys, getopt, os, re, shutil, time, subprocess

sys.path.append('/opt/StorageEngineering/Python/modules')

from HTML import HTML
from Utilities import Files

# Import modules for CGI handling 
import cgi, cgitb 

def getViews():
  globalViews = []
  curl = '/usr/bin/curl' 
  URLS = {}
  URLS['VMAX40K_1794']='http://chapdt3util01.ops.tiaa-cref.org/VMAX40K_1794/CSV/VMAX40K_1794_views.csv'
  URLS['VMAX10K_0957']='http://chatst3utsan01.ops.tiaa-cref.org/VMAX10K_0957/CSV/VMAX10K_0957_views.csv'
  URLS['VMAX40K_1852']='http://dendrt3util01.ops.tiaa-cref.org/VMAX40K_1852/CSV/VMAX40K_1852_views.csv'
    
  for url in URLS:
    cmd = curl + ' ' + URLS[url] 
    output = os.popen(cmd)
    for line in output:
      line = line.strip()
      line = url + ', ' + line + '\n'
      globalViews.append(line)
      
  outfile = '/var/www/html/CSV/global_views.csv'
  f = Files()
  f.dir = '/var/www/html/CSV'
  f.mkdir()
  f.write_file(outfile,globalViews)  



def main():
  getViews()

# Boiler plate call to main()
if __name__ == '__main__':
  main()
  
sys.exit() 