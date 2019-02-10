import pandas as pd
import numpy as np
import urllib.request
import json
import time
import datetime as dt


index = 0


def fetchPreMarket(symbol, exchange):
	global index
	parsed_data = []
	link = "https://www.google.com/finance/getprices?x=NSE&i=60&p=15d&f=d,c,o,h,l,v,t&df=cpct&auto=1&q="
	url = link+symbol
	response = urllib.request.urlopen(url)
	df = None;

	index = index+1
	
	#actual data starts at index = 7
	#first line contains full timestamp,
	#every other line is offset of period from timestamp
	
	anchor_stamp = ''
	lineno=0
	for line1 in response:

		line = str(line1)
		line = line.replace("b'","")
		line = line.replace("\\n'","")
		
		cdata = line.split(',')
		lineno = lineno+1;
		if lineno >7:
			if line.startswith('a'):
				anchor_stamp = cdata[0].replace('a', '')
				cts = int(anchor_stamp)
				firstdate = dt.datetime.fromtimestamp(cts)
				if (index==1 and lineno == 8): 
					print("starting from date ", firstdate)
			else:
				coffset = int(cdata[0])
				cts = int(anchor_stamp) + (coffset * 60)
			dt1 = dt.datetime.fromtimestamp(cts)
			close = float(cdata[1])
			close = round(close)
			opn =float(cdata[2])
			high = float(cdata[3])
			low = float(cdata[3])
			volume = float(cdata[5])
			if lineno >8:
				df = pd.DataFrame(parsed_data, columns= ['s','c','v'])
				
				# df.index = df.c
				# del df['c']
			parsed_data.append(( symbol , close, volume))
			df = pd.DataFrame(parsed_data)

	
	x = df.groupby(1).sum();
	x = x.sort_values(by=2, ascending=False)

	x.index = x.index.map(str)
	y = x.index.tolist()[:15]
	print(symbol, ', '.join(y))

	
	return df




print("program started at ", dt.datetime.now())
content = fetchPreMarket("MFSL","NSE")
content = fetchPreMarket("BEML","NSE")
content = fetchPreMarket("PCJEWELLER","NSE")
content = fetchPreMarket("RELCAPITAL","NSE")
content = fetchPreMarket("VEDL","NSE")  
content = fetchPreMarket("HEXAWARE","NSE")
content = fetchPreMarket("INFY","NSE")
content = fetchPreMarket("DISHTV","NSE")
content = fetchPreMarket("INDIGO","NSE")
content = fetchPreMarket("BATAINDIA","NSE")
content = fetchPreMarket("TATAELXSI","NSE")
content = fetchPreMarket("CAPF","NSE")
content = fetchPreMarket("APOLLOHOSP","NSE")
   # time.sleep(30)

			
