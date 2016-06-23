#!/usr/bin/python




import re,os,time,datetime,subprocess,sys
import os.path
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib


class DateString:
  
  def __init__(self):
    self.yesterday = str(datetime.date.fromtimestamp(time.time() - (60*60*24) ).strftime("%Y-%m-%d"))
    self.today = str(datetime.date.fromtimestamp(time.time()).strftime("%Y-%m-%d"))
    self.tomorrow = str(datetime.date.fromtimestamp(time.time() + (60*60*24) ).strftime("%Y-%m-%d"))
    self.readfile = []
    self.file_exists = 0
 

class Files:

  def __init__(self):
    self.dir = '' 
    self.readfile = []

  def mkdir(self):
    if not os.path.isdir(self.dir):
      subprocess.call(["mkdir", self.dir]) 
      
  def write_file(self,filename,list):
    f = open(filename,'w')
    for line in list:
      f.write(line)
    f.close()

  def write_file_append(self,filename,list):
    f = open(filename,'a')
    for line in list:
      f.write(line)
    f.close()

  def write_log(self,logfile,logentry):
    f = open(logfile,'a')
    reportDate =  str(time.strftime("%x - %X"))
    f.write(reportDate + " :" + logentry)
    f.close()    
    
  def read_file(self,filename):
    self.readfile = []
    self.file_exists = 1
    # Testing if file exists.
    if os.path.isfile(filename): 
      try:
        f = open(filename,'r')
      except IOError:
        print "Failed opening ", filename
        sys.exit(2)
      for line in f:
        line = line.strip()
        self.readfile.append(line)
      f.close()
    else:
      # Set the file_exists flag in case caller cares.
      self.file_exists = 0
    

class EMail:
  def __init__(self):
    self.subject = "Storage Alert"
    self.sender = "vengle@tiaa-cref.org"
    self.send_to = "vengle@tiaa-cref.org, DL_SANSupport@tiaa-cref.org"
    self.cc = "vengle@tiaa-cref.org"
    self.message = ""
    self.mailhost = "smtp.glb.tiaa-cref.org"

  def send_mail(self):
    
    msg = MIMEMultipart()
    msg["Subject"] = self.subject
    msg["From"] = self.sender
    msg["To"] = self.send_to
    msg["Cc"] = self.cc
    body = MIMEText(self.message)
    msg.attach(body)
    smtp = smtplib.SMTP(self.mailhost, 25)
    smtp.sendmail(msg["From"], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
    smtp.quit()    
    
    
class NetPing:
  def __init__(self):
    self.ip = '192.168.0.1'


  def PingTest(self):
    cmd = '/bin/ping -c 1 -w 5 ' + self.ip
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                              stderr=subprocess.STDOUT, 
                              shell=True).communicate()[0]

    if  '100% packet loss' in output:
      return "OFFLINE"
    else:
      return "ONLINE"
    
