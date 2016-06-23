#!/usr/bin/python


import datetime

today = datetime.date.today()
one_day = datetime.timedelta(days=1)
yesterday = today - one_day
tomorrow = today + one_day

print today,tomorrow,yesterday

