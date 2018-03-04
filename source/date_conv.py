#日付・時間を扱う関数群 [date_conv.py]

import datetime
import sys

def todaysStr():
	return datetime.datetime.now().strftime("%Y-%m-%d")

def todaysDatetimeStr():
	return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def yesterdaysStr():
	dt = datetime.datetime.now()
	dt -= datetime.timedelta(days = 1)
	return dt.strftime("%Y-%m-%d")

def todaysDatetime():
	return datetime.datetime.now()

def str2Datetime(string):
	return datetime.datetime.strptime((string.split('+')[0]),"%Y-%m-%dT%H:%M:%S")

def str2Date(string):
	return datetime.datetime.strptime(string,"%Y-%m-%d")

def calcDurMin(time_s, time_e):
	return (time_e-time_s).total_seconds()/60

def returnMidnightDatetime(raw_datetime):
	conved = datetime.datetime(raw_datetime.year, raw_datetime.month, raw_datetime.day,0,0,0)
	return conved