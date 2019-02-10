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



engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)
buyamount = 0
sellamount = 0
profit = 0
loss = 0
allsig = pd.DataFrame(columns=['symbol','timestamp','close'])
short_window = 50
long_window = 100


shortavgname = 'close_50_ema'
longavgname = 'close_100_ema'

buyfield = 'close_xu_close_50_ema'
sellfield = 'close_xd_close_50_ema'
df = pd.read_sql('SELECT * FROM eq_eod_data e order by STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y")', con=engine)
df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])


symbols = list(df['SYMBOL'].unique())

for j in range(0, len(symbols)):
	
	symdata = df[df['SYMBOL'] == symbols[j]]
	print(symbols[j], len(symdata), long_window)
	if len(symdata) >long_window:
		# print("inside if for ", symbols[j])
		# bars = symdata.sort_values('TIMESTAMP',ascending =False)
		
		"""Returns the DataFrame of symbols containing the signals
		to go long, short or hold (1, -1 or 0)."""
		signals = Sdf.retype(symdata)
		# signals[shortavgname]
		# signals[longavgname]
		# signals['signal'] = 0.0
		signals[buyfield]
		signals[sellfield]
		# Create the set of short and long simple moving averages over the 
		# respective periods
		# signals['short_mavg'] = bars['close'].rolling(window=short_window,min_periods=1,center=False).mean()
		# signals['long_mavg'] = bars['close'].rolling(window=long_window,min_periods=1,center=False).mean()

		# Create a 'signal' (invested or not invested) when the short moving average crosses the long
		# moving average, but only for the period greater than the shortest moving average window
		# signals['signal'][short_window:] = np.where(signals[shortavgname][short_window:] 
		#     > signals[longavgname][short_window:], 1.0, 0.0)   

		# # Take the difference of the signals in order to generate actual trading orders
		# signals['positions'] = signals['signal'].diff()   
		# print(signals.head(10))
		temp = signals[(signals[buyfield] == True) | (signals[sellfield] == True)]
		# sig = temp.loc[:, ['symbol','timestamp','close',shortavgname,longavgname, shortavgname+'_xu_'+longavgname]]
		
		allsig = allsig.append(temp, ignore_index=True)
	
	

# data = pd.read_sql('SELECT * FROM momentum_scan', con=engine)
data = allsig.copy();
eqdata = pd.read_sql('select * from eq_eod_data e  where STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y") >= NOW() - INTERVAL 2 DAY',con=engine)
symbols = list(data['symbol'].unique())
data = data[data['timestamp'] > date(2016,3,1)]
data['timestamp'] =  data['timestamp'].apply( lambda x: x.strftime('%Y-%m-%d')  )

for j in range(0, len(symbols)):
	print("For" , j)
	symdata = data[data['symbol'] == symbols[j]]
	symdata = symdata.reset_index(drop=True)
	symdata = symdata.sort_values('timestamp',ascending =True)
	for  i in range(0, len(symdata)) :
		buysignal = symdata.loc[i, buyfield] 
		sellsignal = symdata.loc[i, sellfield] 
		close = symdata.loc[i, 'close'] 
		timestamp = symdata.loc[i, 'timestamp'] 
		symbol = symdata.loc[i, 'symbol'] 
		if (close > 50):
			if (buysignal == 1) :
				buyamount = buyamount + close
				if (i < len(symdata) - 1) :
					buysignal1 = symdata.loc[i+1, buyfield] 
					sellsignal1 = symdata.loc[i+1, sellfield] 
					close1 = symdata.loc[i+1, 'close'] 
					timestamp1 = symdata.loc[i+1, 'timestamp'] 
					
					if (sellsignal1 == 1 ) :
						sellamount = sellamount + close1
						if (close1 > close):
							profit = profit + (close1 - close)
						else :
							loss = loss + (close1 - close)
					print ("bought ", symbol , "at price " , close ,"on ", timestamp,  "sold at ", close1, " on ", timestamp1)
				elif (i == len(symdata)-1) :
					symboldata = eqdata[eqdata['SYMBOL'] == symbol]
					if (len(symboldata) > 0) :
						newclose = symboldata.head(1)['CLOSE'].iloc[0]
						
						sellamount  = sellamount + newclose
						if (newclose > close):
								profit = profit + (newclose - close)
						else :
								loss = loss + (newclose - close)
						print ("bought ", symbol , "at price " , close ,"on ", timestamp, "sold today at ", newclose,"on ", timestamp1)
	

print ( "buy amount", buyamount, "sell amount" , sellamount , "profit" , profit , "loss" , loss)			
