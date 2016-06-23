#!/usr/bin/python

import sys, getopt, os, re, shutil, subprocess, time
from xml.dom import minidom
                     


class VMAX3_STORAGE:
  
  def __init__(self, sid):
    self.sid = sid
    self.SGs = {}
    self.CapacityByTier = {}
    self.SG2Capacity = {}
    self.SGinMV = {}
    self.SG_IOPS_Limit = {} 	
    self.SG_MB_Limit = {}
    self.SGinSLO = {}
    self.ProvisionedCapacity = 0 
    self.Associations = {}
    self.SYMCLI = '/opt/emc/SYMCLI/bin/'
    self.pools = {}
    self.pooldetails = {}
    
    self.Views = {}
    self.mvCapTotal = 0
    self.slo_policies = {}
    self.HostInitiatorGroups = {}
    self.ClusterInitiatorGroups = {}
    self.or_list = []
    self.portgroups = {}
    self.tiers = {}
    self.tiernames = []
    self.wwpn_logins = {}
    self.FA2WWNmap = {}
    self.FA_Device_Count = {}
    self.SRP_NAME = 'SRP_1'
    self.SRP_Info = {}
    self.TDEVs = {}
    


  def get_thin_luns(self):
    SYMCLI = '/opt/emc/SYMCLI/bin/'
    cmd = SYMCLI + 'symcfg -sid ' + self.sid  + ' list -tdev -GB -output xml_e'
    
    # Exec the sym command...
    output = os.popen(cmd)

    # Write the XML to an XML file so that it can be passed to the parser
    XML = '/var/www/html/XML/' + self.sid + '_TDEVs.xml'
    f = open(XML, 'w')
    for line in output:
      #line = line.strip()
      f.write(line)
    f.close()

    # Now parse the XML file 
    doc = minidom.parse(XML)
    self.fast_policies = {}
    for node in doc.getElementsByTagName('ThinDevs'):    #
      for tdev in node.getElementsByTagName('Device'):
        for child in tdev.childNodes:
          if child.nodeType == 1:
            if child.nodeName == "dev_name":
              device_name = str(child.firstChild.nodeValue)
            if child.nodeName == "total_tracks_gb":
              capacity = str(child.firstChild.nodeValue)
            if child.nodeName == "alloc_tracks_gb":
              allocated = str(child.firstChild.nodeValue)
        self.TDEVs[device_name] = (capacity,allocated)
    
  def get_slo(self):
    SYMCLI = '/opt/emc/SYMCLI/bin/'
    cmd = SYMCLI + 'symcfg -sid ' + self.sid  + ' list -srp -slo -output xml_e'

    # Exec the sym command...
    output = os.popen(cmd)

    # Write the XML to an XML file so that it can be passed to the parser
    XML = '/var/www/html/XML/' + self.sid + '_fast.xml'
    f = open(XML, 'w')
    for line in output:
      #line = line.strip()
      f.write(line)
    f.close()

    # Now parse the XML file 
    doc = minidom.parse(XML)
    self.fast_policies = {}
    for node in doc.getElementsByTagName('SLO'):
      
      for info in node.getElementsByTagName('SLO_Info'):
        for child in info.childNodes:
          if child.nodeType == 1:
            if child.nodeName == "name":
              policy = child.firstChild.nodeValue
            if child.nodeName == "approx_avg_resp_time":
              responsetarget = child.firstChild.nodeValue
        self.slo_policies[str(policy)] = str(responsetarget)
              

  def get_SRP(self):
    
    cmd = self.SYMCLI + 'symcfg -sid ' + self.sid  + ' show -srp ' + self.SRP_NAME + ' -detail -output xml_e'
    output = os.popen(cmd)

    XML = '/var/www/html/XML/' + self.sid + 'SRP.xml'
    f = open(XML, 'w')
    for line in output:
      f.write(line)
    f.close()
    doc = minidom.parse(XML)
    


    for node in doc.getElementsByTagName('SRP_Info'):
      self.SRP_Info = {}
      for child in node.childNodes:
        if child.nodeType == 1:
          if child.nodeName == "usable_capacity_gigabytes":
            self.SRP_Info['USABLE'] = child.firstChild.nodeValue
 
          if child.nodeName == "allocated_capacity_gigabytes":
            self.SRP_Info['USED'] = child.firstChild.nodeValue
 
          if child.nodeName == "free_capacity_gigabytes":
            self.SRP_Info['FREE'] = child.firstChild.nodeValue
 
          if child.nodeName == "subscribed_capacity_gigabytes":
            self.SRP_Info['SUBSCRIBED'] = child.firstChild.nodeValue
 

    
  def get_thinpools(self):
    
    sid = '1794'
    cmd = self.SYMCLI + 'symcfg -sid ' + self.sid  + ' list -pool -thin -detail -output xml_e'
    output = os.popen(cmd)

    XML = '/var/www/html/XML/' + self.sid + '_pool.xml'
    f = open(XML, 'w')
    for line in output:
      f.write(line)
    f.close()
    doc = minidom.parse(XML)
    


    for node in doc.getElementsByTagName('DevicePool'):
      pooldata = {}
      for child in node.childNodes:
        if child.nodeType == 1:
          if child.nodeName == "pool_name":
            PoolName = child.firstChild.nodeValue
          else:
            pooldata[child.nodeName] = child.firstChild.nodeValue
          if child.nodeName == "subs_percent":
            self.pools[PoolName] = pooldata.copy()
            
    if 'pool_name' in self.pools:
      del self.pools['pool_name']
      
    for pool in self.pools.keys():
      cmd = self.SYMCLI + 'symcfg -sid ' + self.sid  + ' show -pool ' + pool + ' -thin -detail -output xml_e'
      output = os.popen(cmd)
      self.pooldetails[pool] = {}
      self.pooldetails[pool]['COMPRESSION'] = 'NOT_SET'
      self.pooldetails[pool]['SUBSCRIPTION_LIMIT'] =  'NOT_SET'
      self.pooldetails[pool]['PRC'] =  'NOT_SET'
      self.pooldetails[pool]['TECH'] =  'NOT_SET'
      self.pooldetails[pool]['LAYOUT'] =  'NOT_SET'
      XML = '/var/www/html/XML/' + self.sid + pool +'_pool.xml'
      f = open(XML, 'w')
      for line in output:
        f.write(line)
      f.close()
      doc = minidom.parse(XML)

      for node in doc.getElementsByTagName('DevicePool'):
        
        for child in node.childNodes:
          if child.nodeType == 1:
            if child.nodeName == "compression_state":
              self.pooldetails[pool]['COMPRESSION'] = child.firstChild.nodeValue
            if child.nodeName == "max_subs_percent":
              self.pooldetails[pool]['SUBSCRIPTION_LIMIT'] = child.firstChild.nodeValue   
            if child.nodeName == "pool_resv_cap":
              self.pooldetails[pool]['PRC'] = child.firstChild.nodeValue        
            if child.nodeName == "technology":
              self.pooldetails[pool]['TECH'] = child.firstChild.nodeValue      
            if child.nodeName == "configuration":
              self.pooldetails[pool]['LAYOUT'] = child.firstChild.nodeValue                

  
  def get_associations(self):
    SYMCLI = '/opt/emc/SYMCLI/bin/'
 
    cmd = SYMCLI + 'symfast -sid ' + self.sid  + ' -association list -output xml_e'

    # Exec the sym command...
    output = os.popen(cmd)

    # Write the XML to an XML file so that it can be passed to the parser
    XML = '/var/www/html/XML/' + self.sid + '_fp_associations.xml'
    f = open(XML, 'w')
    for line in output:
      #line = line.strip()
      f.write(line)
    f.close()

    # Now parse the XML file 
    doc = minidom.parse(XML)
    for node in doc.getElementsByTagName('Association_Info'):
      sgName = ""
      fastPolicy = ""
      for child in node.childNodes:
        if child.nodeType == 1:
          if child.nodeName == "sg_name":
            sgName = child.firstChild.nodeValue
          if child.nodeName == "policy_name":
            fastPolicy = str(child.firstChild.nodeValue)
            if sgName != "":
              self.Associations[sgName] = fastPolicy
            
    
    
    
    
  def get_sg(self):
    SYMCLI = '/opt/emc/SYMCLI/bin/'
 
    cmd = SYMCLI + 'symsg -sid ' + self.sid  + ' list -v -output xml_e'

    # Exec the sym command...
    output = os.popen(cmd)

    # Write the XML to an XML file so that it can be passed to the parser
    XML = '/var/www/html/XML/' + self.sid + '_sg.xml'
    f = open(XML, 'w')
    for line in output:
      #line = line.strip()
      f.write(line)
    f.close()

    # Now parse the XML file 
    doc = minidom.parse(XML)

    # Now iterate over a list of the SGs and for each SG, grab a lun list and capacity per lun. And the FAST Policy
    for node in doc.getElementsByTagName('SG'):
      sgdata = {}
      deviceList = {}
      capacityTotal = 0
      # Grab the SG_Info node for this SG so we can get the host name and FAST policy
      for sginfo in node.getElementsByTagName('SG_Info'):
        # Iterate over the SG_Info lines... 
        for child in sginfo.childNodes:
          if child.nodeType == 1:
            if child.nodeName == "name":
              sgName = child.firstChild.nodeValue
            if child.nodeName == "SLO_name":
              SLO_Policy = child.firstChild.nodeValue              
            if child.nodeName == "HostIOLimit_max_mb_sec":
              max_mb_sec = child.firstChild.nodeValue
            if child.nodeName == "HostIOLimit_max_io_sec":
              max_io_sec = child.firstChild.nodeValue              
            if child.nodeName == "Masking_views":
              MVs = child.firstChild.nodeValue			  
      # Now get the Device list for this SG
      for devListNode in node.getElementsByTagName('DEVS_List'):
        # And go down one more level and get the devices
        for deviceNode in devListNode.getElementsByTagName('Device'):  
          # Now, iterate over the devices and grab the device ID and capacity
          for devices in  deviceNode.childNodes:
            if devices.nodeType == 1:
              if devices.nodeName == "dev_name":
                deviceName = devices.firstChild.nodeValue
              if devices.nodeName == "megabytes":
                deviceList[deviceName] = devices.firstChild.nodeValue
                capacityTotal += long(str(devices.firstChild.nodeValue))

      self.ProvisionedCapacity += capacityTotal
      self.SGs[sgName] = deviceList.copy()
      self.SG2Capacity[sgName] = capacityTotal
      self.SG_IOPS_Limit[sgName] = max_io_sec  	
      self.SG_MB_Limit[sgName] = max_mb_sec  
      self.SGinMV[sgName] = MVs 
      self.SGinSLO[sgName] = str(SLO_Policy)
      
      
  def get_views(self):
    SYMCLI = '/opt/emc/SYMCLI/bin/'
 
    cmd = SYMCLI + 'symaccess -sid ' + self.sid  + ' list view -detail -output xml_e'

    # Exec the sym command...
    output = os.popen(cmd)

    # Write the XML to an XML file so that it can be passed to the parser
    XML = '/var/www/html/XML/' + self.sid + '_views.xml'
    f = open(XML, 'w')
    for line in output:
      #line = line.strip()
      f.write(line)
    f.close()

    # Now parse the XML file 
    doc = minidom.parse(XML)
    # Now iterate over a list of the masking views and for each view, grab a lun list and capacity per lun.
    for node in doc.getElementsByTagName('View_Info'):
      viewdata = {}
      viewName = 'None'
      igName = 'None'
      pgName = 'None'
      sgName = 'None'
      
      # get the host name for this View
      for child in node.childNodes:
        initiators = []
        if child.nodeType == 1:
          if child.nodeName == "view_name":
            viewName = child.firstChild.nodeValue
          if child.nodeName == "init_grpname":
            igName = child.firstChild.nodeValue
            igSplit = igName.split()
            igName = igSplit[0]
          if child.nodeName == "port_grpname":
            pgName = child.firstChild.nodeValue            
          if child.nodeName == "stor_grpname":
            sgName = child.firstChild.nodeValue                  
            
        # Grab the LUN list for this host/view
        devices = {}
        for devNode in node.getElementsByTagName('Totals'):
          for dev in devNode.childNodes:
            if dev.nodeType == 1:
              if dev.nodeName == "total_dev_cap_mb":
                mvCapacity = dev.firstChild.nodeValue
        initType = 'NOT_SET'
        for IG in node.getElementsByTagName('Initiators'):
          for initNode in IG.childNodes:
            if initNode.nodeType == 1:
              if initNode.nodeName == "wwn":
                initType = 'host'
                initiators.append(initNode.firstChild.nodeValue)
              if initNode.nodeName == "group_name":
                initType = 'cluster'
                initiators.append(initNode.firstChild.nodeValue)
        
        if initType == 'cluster':
          self.ClusterInitiatorGroups[igName] = initiators[:]
        if initType == 'host':
          self.HostInitiatorGroups[igName] = initiators[:]          
          

      if  igName != 'None': 
        if viewName not in self.Views:       
          self.mvCapTotal += int(str(mvCapacity))  
          viewdata['IG'] = igName
          viewdata['PG'] = pgName
          viewdata['SG'] = sgName
          viewdata['MB'] = mvCapacity
          viewdata['MV'] = viewName
          self.Views[viewName] = viewdata.copy()
          if pgName not in self.portgroups:
            self.portgroups[pgName] = []
          self.portgroups[pgName].append(viewdata.copy())
        
  def get_or_sessions(self):
    #
    cmd = self.SYMCLI + 'symrcopy -sid ' + self.sid  + ' list -detail'
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0]
    #output = os.popen(cmd)
    for line in output:
      self.or_list.append(line)
    
  
  def get_logins(self):
    SYMCLI = '/opt/emc/SYMCLI/bin/'
 
    cmd = SYMCLI + 'symaccess -sid ' + self.sid  + ' list logins  -output xml_e'

    # Exec the sym command...
    output = os.popen(cmd)

    # Write the XML to an XML file so that it can be passed to the parser
    XML = '/var/www/html/XML/' + self.sid + '_logins.xml'
    f = open(XML, 'w')
    for line in output:
      #line = line.strip()
      f.write(line)
    f.close()

    # Now parse the XML file 
    doc = minidom.parse(XML)
    for node in doc.getElementsByTagName('Devmask_Login_Record'):
      FA = "NULL"
      port = "NULL"
      FAport = 'NULL'
      
      for child in node.childNodes:
        if child.nodeType == 1:
          if child.nodeName == "director":
            FA = str(child.firstChild.nodeValue)
          if child.nodeName == "port":
            port = str(child.firstChild.nodeValue)
            FAport = FA + port
      for loginsNode in node.getElementsByTagName('Login'):
        for login in loginsNode.childNodes:
          if login.nodeType == 1:
            if login.nodeName == "originator_port_wwn":
              key = str(login.firstChild.nodeValue) + ' ' + FAport
              self.wwpn_logins[key] = FAport   

    
  def get_fa_info(self):
    SYMCLI = '/opt/emc/SYMCLI/bin/'
    cmd = SYMCLI + 'symcfg -sid ' + self.sid  + ' list -FA all -port -output xml_e'

    # Exec the sym command...
    output = os.popen(cmd)

    # Write the XML to an XML file so that it can be passed to the parser
    XML = '/var/www/html/XML/' + self.sid + '_FA_INFO.xml'
    f = open(XML, 'w')
    for line in output:
      #line = line.strip()
      f.write(line)
    f.close()

    # Now parse the XML file 
    doc = minidom.parse(XML)
    self.fast_policies = {}
    for node in doc.getElementsByTagName('Director'):
      
      for info in node.getElementsByTagName('Dir_Info'):
        for child in info.childNodes:
          if child.nodeType == 1:
            if child.nodeName == "id":
              fa_port = child.firstChild.nodeValue
              
      for port in node.getElementsByTagName('Port'):
        for info in port.getElementsByTagName('Port_Info'):
          for child in info.childNodes:
            if child.nodeType == 1:
              if child.nodeName == "port":
                portnumber = child.firstChild.nodeValue
              if child.nodeName == "port_wwn":
                port_wwn = child.firstChild.nodeValue
        FA_PORT = str(fa_port) + ':' + str(portnumber)
        TOTAL = str(fa_port) + ':' + 'Total'
        self.FA2WWNmap[FA_PORT] = port_wwn
        self.FA2WWNmap[TOTAL] = 'Total for FA'        
        self.FA_Device_Count[FA_PORT] = '0' 
        self.FA_Device_Count[TOTAL] = 0 
  
    cmd = SYMCLI + 'symcfg -sid ' + self.sid  + ' list -dir all -port -address -output xml_e'

    # Exec the sym command...
    output = os.popen(cmd)

    # Write the XML to an XML file so that it can be passed to the parser
    XML = '/var/www/html/XML/' + self.sid + '_FA_DevCount.xml'
    f = open(XML, 'w')
    for line in output:
      #line = line.strip()
      f.write(line)
    f.close()

    # Now parse the XML file 
    doc = minidom.parse(XML)
    self.fast_policies = {}
    for node in doc.getElementsByTagName('Director'):
      
      for info in node.getElementsByTagName('Dir_Info'):
        for child in info.childNodes:
          if child.nodeType == 1:
            if child.nodeName == "id":
              fa_port = child.firstChild.nodeValue
            if child.nodeName == "port":
              portnumber = child.firstChild.nodeValue
                
      for total in node.getElementsByTagName('Total'):
        for child in total.childNodes:
          if child.nodeType == 1:
            if child.nodeName == "mapped_devs_w_metamember":
              dev_count = child.firstChild.nodeValue
      FA_PORT = str(fa_port) + ':' + str(portnumber)
      TOTAL = str(fa_port) + ':' + 'Total'
      self.FA_Device_Count[FA_PORT] = dev_count 
      self.FA_Device_Count[TOTAL] += int(dev_count)      



                