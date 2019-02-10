# buyfield = 'close_50_ema_xu_close_100_ema'	
# sellfield = 'close_50_ema_xd_close_100_ema'
from sqlalchemy import types, create_engine, Table,MetaData, column, select, update, insert
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from datetime import date, timedelta,datetime
from sqlalchemy import types, create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from datetime import date, timedelta,datetime
from stockstats import StockDataFrame as Sdf
import statsmodels.formula.api as sm
import talib


engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)
allsig = pd.DataFrame(columns=['symbol','timestamp','close'])

nifty500 = pd.read_csv("ind_nifty500list.csv")
symbols500 = list(nifty500['Symbol'].unique())

df = pd.read_sql('SELECT * FROM eq_eod_data e order by STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y")', con=engine)
# df = pd.read_sql('SELECT * FROM eq_eod_data e where e.SYMBOL ="SWANENERGY"  order by STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y")', con=engine)

df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])

lookbackperiod = 3


trades =  pd.DataFrame(columns=['SYMBOL','momscore','buydate', 'buyprice', 'todayprice'])
for i in range(20 , 1,-1) :
	momentumscores =  pd.DataFrame(columns=['SYMBOL','momscore','buyprice', 'todayprice'])
	arr =[]
	for j in range(0, len(symbols500)):
		# if symbols500[j] == "SWANENERGY" :
			symdata = df[df['SYMBOL'] == symbols500[j]]
			# symdata['ema'] = talib.EMA(np.array(symdata['CLOSE']),timeperiod=150)
			symdata['date'] = symdata['TIMESTAMP']
			symdata = symdata.set_index('TIMESTAMP')
			test = symdata.groupby(pd.TimeGrouper('M')).date.max()
			test = test.reset_index(level=0)
			
			testing = symdata[symdata['date'].isin(list(test['date']))]
			testdata = testing.CLOSE.pct_change() + 1
			length = len(testdata) - 1 -i
			temp = testdata[length-lookbackperiod : length]
			# bought = trades[trades['SYMBOL'] == symbols500[j]]


			# if len(bought) > 1 : 
			# 	if testing['CLOSE'][length] < testing['ema'][length] :

			# 		print( symbols500[j] , "bought",bought['buyprice'][0],bought['buydate'][0],  "sold "  , "price",  testing['CLOSE'][length]  , "date" , testing['date'][length] )
				
			mul=0
			if (len(temp) > lookbackperiod -1) :
				# mul = ((temp[0] *temp[1]*temp[2] *temp[3]*temp[4] *temp[5]) -1)*100
				mul = 1
				for k in range(0, lookbackperiod) :
					
					mul = mul * temp[k]
				# mul = ((temp[0] *temp[1]*temp[2] *temp[3]*temp[4] *temp[5]*temp[6] *temp[7]*temp[8] *temp[9]*temp[10] *temp[11]) -1)*100
				if np.isnan(mul) :
					mul = 0
				else : 
					mul = (mul -1) * 100
				arr.append((symbols500[j], mul,testing['date'][length], testing['CLOSE'][length], testing['CLOSE'][-1]))
		# momentumscores.append({'SYMBOL': symbols500[j],'momscore' : mul,'buyprice' : testing['CLOSE'][length], 'todayprice' : testing['CLOSE'][-1]})

	momentumscores = pd.DataFrame(arr)
	momentumscores.columns = ['SYMBOL','momscore','buydate', 'buyprice', 'todayprice']
	momentumscores = momentumscores.sort_values('momscore',ascending =False)
	trades = trades.append(momentumscores.head(15))
	print(momentumscores.head(15))
	
# print(trades)
# print(symbols500[j], mul, testing['CLOSE'][length], testing['CLOSE'][-1])