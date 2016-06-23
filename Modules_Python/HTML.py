#!/usr/bin/python

import time

class HTML:

  def __init__(self):
    self.tr = '<TR>'
    self.td = '<TD>'
    self.alerttr = '<TR bgcolor=#F2D072>'
    self.th = '<TH>'
    self.end_table = '\n</table>\n'
    self.end_html = '</body>\n</html>\n'
    self.http_header = 'Content Type: text/html\n\n'

 
  
  def th_list(self,row,bgcolor='#BAB9B8'):
    
    html = '<tr bgcolor=' + bgcolor + '>'
    for cell in row:
      html += '<th>' + str(cell)
    html += '\n'
    return html

  def tr_list(self,row,bgcolor=''):
    html = '<tr bgcolor=' + bgcolor + '>'
    for cell in row:
      html += '<td>' + str(cell)
    html += '\n'
    return html   
 
 
  def start_html_refresh(self,title='EMC Report',align='center',refreshtime=60): 
    html =   "<HTML>\n<HEAD><META HTTP-EQUIV=refresh CONTENT=" + str(refreshtime) + ">\n"
    html += "<Title>" + title + "</Title>\n</HEAD>\n<body align=" + align + ">"
    return  html

  def start_html(self,title='Web Report Page',align='center'): 
    html =   "<HTML>\n<HEAD><Title>" + title + "</Title></HEAD>\n<body align=" + align + ">"
    return  html
    
 
  def start_table(self,border='1',caption=''):
    html = '<p><br><table align=center  border=' + str(border) + '><caption>' + caption + '</caption>\n'
    return  html
    
  def EMC_Header(self,site,datacenter,info1='',link1=''):
    reportDate =  str(time.strftime("%c"))
    #
    search_form = """<a href=http://chapdt3util01.ops.tiaa-cref.org/vmax_search_page.html target=_parent>
                  Host and WWPN Search</a>"""
    
        
    dateString = "Report created on " + reportDate
    sgLink = '/' + site + '/index.html'  
    faLink = '/' + site + '/FA_Ports.html'  
    mvLink = '/' + site + '/views.html'  
    fpLink = '/' + site + '/fast.html'  
    linkpath = '/' + site + '/OR/index.html'
    orLink = '<a href=' + linkpath + '>OR Status</a>\n'        
    backLink = '<a href="javascript: history.go(-1)">Back</a>'
    xmlLink = '<a href="/XML">XML</a>\n'
    backbutton = '''<FORM>
                    <INPUT TYPE="button" onClick="history.go(-1)" VALUE="<<<">
                    </FORM>'''         
    reloadbutton = '''<FORM>
                    <INPUT TYPE="button" onClick="history.go(0)" VALUE="Refresh">
                    </FORM>'''     
    summaryLink = '/' + datacenter + site + '_EMC_Summary.html'
    diskfailedLink = '/' + datacenter + site + '_Failed_disks.html'
    
    EMC_Array_Header = '\n\n<table align=center  border=1><tr>\n'
    EMC_Array_Header += '<th>' + dateString + '\n'
    EMC_Array_Header += '<th>' + info1 + '\n'
    EMC_Array_Header += '<th>' + search_form + '\n'
    EMC_Array_Header += '</table>\n'
    EMC_Array_Header += '\n\n<table align=center  border=1><tr>\n'
    #EMC_Array_Header += '<th>' + backLink + '\n'    
    EMC_Array_Header += '<th>' + backbutton + '\n'
    EMC_Array_Header += '<th>' + reloadbutton + '\n'        
    EMC_Array_Header += '<th><a href=' + summaryLink + '>Summary</a>\n'
    EMC_Array_Header += '<th><a href=' + sgLink + '>Storage Groups</a>\n'
    EMC_Array_Header += '<th><a href=' + faLink + '>FA Ports</a>\n'
    EMC_Array_Header += '<th><a href=' + mvLink + '>Masking Views</a>\n'    
    EMC_Array_Header += '<th><a href=' + fpLink + '>FAST-VP</a>\n'    
    EMC_Array_Header += '<th><a href=' + diskfailedLink + '>Failed Disks</a>\n'    
    EMC_Array_Header += '<th>' + orLink
    EMC_Array_Header += '<th>' + xmlLink   
    EMC_Array_Header += '<th>' + link1   
    EMC_Array_Header += '</table>\n'  
    EMC_Array_Header += '<p><center><h1>' + site + '</h1></center>\n'
        
    return EMC_Array_Header
    
  def Header(self,csvlink,yesterdaylink,tomorrowlink,auditlink=''):
    reportDate =  str(time.strftime("%c"))
    dateString = "Report created on " + reportDate
    backLink = '<a href="javascript: history.go(-1)">Back</a>'
    HEADER_TABLE = '\n\n<table align=center  border=1><tr>\n'
    HEADER_TABLE += '<th>' + backLink + '\n'
    HEADER_TABLE += '<th>' + dateString + '\n'
    HEADER_TABLE += '<th>' + csvlink + '\n'
    HEADER_TABLE += '<th>' + tomorrowlink + '\n'
    HEADER_TABLE += '<th>' + yesterdaylink + '\n' 
    if auditlink != '':    
      HEADER_TABLE += '<th>' + auditlink + '\n'        
    HEADER_TABLE += '</table>\n\n'  
    return HEADER_TABLE

  def aux_Header(self,link1,link2,link3,link4,link5,link6,name):
    HEADER_TABLE = '\n\n<table align=center  border=1><tr>\n'
    HEADER_TABLE += '<th>' + link1 + '\n'
    HEADER_TABLE += '<th>' + link2 + '\n'
    HEADER_TABLE += '<th>' + link3 + '\n'
    HEADER_TABLE += '<th>' + link4 + '\n'
    HEADER_TABLE += '<th>' + link5 + '\n'    
    HEADER_TABLE += '<th>' + link6 + '\n'        
    HEADER_TABLE += '</table>\n\n'  
    HEADER_TABLE += '<p><center><h1>' + name + '</h1></center>\n'
    return HEADER_TABLE    
    
  def Not_Found_Header(self,message='No such file'):
    backLink = '<a href="javascript: history.go(-1)">Back</a>'
    HEADER_TABLE = '\n\n<table align=center  border=1><tr>\n'
    HEADER_TABLE += '<th>' + backLink + '\n'
    HEADER_TABLE += '<th>' + message + '\n'
    HEADER_TABLE += '</table>\n\n'  
    return HEADER_TABLE    

  def CGI_Search_Header(self,site):
    reportDate =  str(time.strftime("%c"))
    dateString = "Report created on " + reportDate
    #
    search_form = """<a href=http://chapdt3util01.ops.tiaa-cref.org/vmax_search_page.html target=_parent>
                  Host and WWPN Search</a>"""
        
    sgLink = '/' + site + '/index.html'  
    mvLink = '/' + site + '/views.html'  
    fpLink = '/' + site + '/fast.html'  
    linkpath = '/' + site + '/OR/index.html'
    orLink = '<a href=' + linkpath + '>OR Status</a>\n'        
    backLink = '<a href="javascript: history.go(-1)">Back</a>'
    xmlLink = '<a href="/XML">XML</a>\n'
    backbutton = '''<FORM>
                    <INPUT TYPE="button" onClick="history.go(-1)" VALUE="<<<">
                    </FORM>'''         
    reloadbutton = '''<FORM>
                    <INPUT TYPE="button" onClick="history.go(0)" VALUE="Refresh">
                    </FORM>'''     
    EMC_Array_Header = '\n\n<table align=center  border=1><tr>\n'
    EMC_Array_Header += '<th>' + dateString + '\n'
    EMC_Array_Header += '<th>' + search_form + '\n'
    EMC_Array_Header += '</table>\n'
    EMC_Array_Header += '\n\n<table align=center  border=1><tr>\n'
    EMC_Array_Header += '<th>' + backbutton + '\n'
    EMC_Array_Header += '<th>' + reloadbutton + '\n'        
    EMC_Array_Header += '<th><a href=' + sgLink + '>Storage Groups</a>\n'
    EMC_Array_Header += '<th><a href=' + mvLink + '>Masking Views</a>\n'    
    EMC_Array_Header += '<th><a href=' + fpLink + '>FAST-VP</a>\n'    
    EMC_Array_Header += '<th>' + orLink
    EMC_Array_Header += '</table>\n'  
    EMC_Array_Header += '<p><center><h1>' + site + '</h1></center>\n'
        
    return EMC_Array_Header    

orange = '#F7EE6F'
green =  '#69F24E'       



