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
from alpha_vantage.timeseries import TimeSeries
import sys
import time

def stockchart(symbol):
    
    ts = TimeSeries(key='9GMZ8HK7KZ7E3X6U', output_format='pandas')
    data, meta_data = ts.get_daily_adjusted(symbol="NSE:"+symbol, outputsize='compact')
    data['symbol'] = symbol
    return data.tail(1)
    






start = time.clock()
engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)

# nifty500 = pd.read_csv("ind_nifty500list.csv")

# symbols = list(nifty500['Symbol'].unique())
df = pd.read_sql('SELECT distinct(symbol) FROM eq_adjusted_data e', con=engine)
test = list(df['symbol'])

# test = [item for item in symbols if item not in symbolsadj]
# print(test)
for j in range(0, len(test)):
	try:
		print("For ", test[j])
		symdata = stockchart(test[j])
		# print(symdata)
		# symdata.reset_index(drop=False,inplace=True , level=0)

		# symdata.to_sql(name='eq_adjusted_data', con=engine, if_exists = 'append', index=False)

	except Exception:
			print("didnt find for symbol " , test[j])

end = time.clock()

print(end-start)

