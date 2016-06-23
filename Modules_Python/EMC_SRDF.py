#!/usr/bin/python

import sys, getopt, os, re, shutil, subprocess, time
from xml.dom import minidom
sys.path.append('/opt/StorageEngineering/Python/modules')
from Utilities import Files                     


class VMAX_SRDF_Util:
  
  def __init__(self):
    
    self.SRDF_Groups = {}
    self.SRDF_Groups_Info = {}
    # self.SRDF_Groups_pairs[group] = pairs (pairs is a dict with keys like [src tgt state] )
    self.SRDF_Groups_Pairs = {}
    self.SRDF_Groups_Info = {}
    
    # Load group file
    self.groupfile = '/opt/EMC/Scripts/SRDF/etc/srdf_groups.conf'
    g = Files()
    g.read_file(self.groupfile)
    for line in g.readfile:
      if not line.startswith("#"):
        self.SRDF_Groups[line] = 1
        #print line
    
    

  def get_srdf_status(self):
    for group in self.SRDF_Groups:
      SYMCLI = '/opt/emc/SYMCLI/bin/'
      cmd = SYMCLI + 'symrdf' + ' -g ' + group + ' query -output xml_e'
      # Exec the sym command...
      output = os.popen(cmd)

      # Write the XML to an XML file so that it can be passed to the parser
      XML = '/var/www/html/XML/SRDF.xml'
      f = open(XML, 'w')
      for line in output:
        #line = line.strip()
        f.write(line)
      f.close()

      # Now parse the XML file 
      doc = minidom.parse(XML)
      
      for node in doc.getElementsByTagName('DG'):
        info = {}
        pairs = []
        info['remote_symid'] = 'N/A'
        info['symid'] = 'N/A'
        info['tracks'] = 'N/A'
        info['delta'] = 'N/A'
        for item in node.getElementsByTagName('DG_Info'):
          for child in item.childNodes:
            if child.nodeType == 1:
              #print child.nodeName
              if child.nodeName == "symid":
                info['symid'] = child.firstChild.nodeValue
              if child.nodeName == "remote_symid":
                info['remote_symid'] = str(child.firstChild.nodeValue)
              if child.nodeName == "tracks_not_committed_to_r2_side":
                info['tracks'] = child.firstChild.nodeValue
              if child.nodeName == "rdfa_time_r2_is_behind_r1":
                info['delta'] = str(child.firstChild.nodeValue)     
        
        for item in node.getElementsByTagName('RDF_Pair'):
          for child in item.childNodes:
            if child.nodeType == 1:
              #print child.nodeName
              if child.nodeName == "link_status":
                link_status = str(child.firstChild.nodeValue)
              if child.nodeName == "mode":
                mode  = str(child.firstChild.nodeValue)
              if child.nodeName == "pair_state":
                pair_state = str(child.firstChild.nodeValue)

          for volume in item.getElementsByTagName('Source'):
            for child in volume.childNodes:
              if child.nodeType == 1:
                #print child.nodeName
                if child.nodeName == "dev_name":
                  source = str(child.firstChild.nodeValue)
                if child.nodeName == "state":
                  source_lun = source + '_' + str(child.firstChild.nodeValue)
                
          for volume in item.getElementsByTagName('Target'):
            for child in volume.childNodes:
              if child.nodeType == 1:
                #print child.nodeName
                if child.nodeName == "dev_name":
                  target = str(child.firstChild.nodeValue)
                if child.nodeName == "state":
                  target_lun = target + '_' + str(child.firstChild.nodeValue)
          
          pair =  source_lun + ',' +  target_lun + ',' +  link_status 
          pair += ',' +  mode + ',' + pair_state
          pairs.append(pair)          
      self.SRDF_Groups_Info[group] = info
      self.SRDF_Groups_Pairs[group] = pairs
 
      