#!/usr/bin/python

from Utilities import EMail


mailObj = EMail()
mailObj.message = 'This is a test of my new EMail python class...'
mailObj.send_mail()




