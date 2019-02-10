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
df = pd.read_sql('SELECT * FROM eq_eod_data e where e.SYMBOL = "VEDL" order by STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y")', con=engine)
df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
df['ema20'] = talib.EMA(np.array(df['CLOSE']),timeperiod=20)
df['sma20'] = talib.SMA(np.array(df['CLOSE']),timeperiod=20)
df['tr'] = talib.TRANGE(np.array(df['HIGH']),np.array(df['LOW']), np.array(df['CLOSE']))
df['ematr20'] = talib.EMA(np.array(df['tr']), timeperiod=20)


df['ema14'] = talib.EMA(np.array(df['CLOSE']),timeperiod=14)
df['sma14'] = talib.SMA(np.array(df['CLOSE']),timeperiod=14)
df['ematr14'] = talib.EMA(np.array(df['tr']), timeperiod=14)

df['pgoema20'] = (df['CLOSE'] - df['ema20']) /df['ematr20']
df['pgoema14'] = (df['CLOSE'] - df['ema14']) /df['ematr14']

df['pgosma20'] = (df['CLOSE'] - df['sma20']) /df['ematr20']
df['pgosma14'] = (df['CLOSE'] - df['sma14']) /df['ematr14']

df['typprice'] = talib.TYPPRICE(np.array(df['HIGH']),np.array(df['LOW']), np.array(df['CLOSE']))
df['ematyp'] = talib.EMA(np.array(df['typprice']), timeperiod=20)
upperband, middleband, lowerband = talib.BBANDS(np.array(df['CLOSE']), timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
df['bbupper'] = upperband
df['bblower']  = lowerband
df['atr'] = talib.ATR(np.array(df['HIGH']),np.array(df['LOW']), np.array(df['CLOSE']), timeperiod=20)
df['kupperband']=df['ematyp']+1.5 * df['atr']
df['klowerband']=df['ematyp']-1.5 * df['atr']
df['arronosc'] = talib.AROONOSC(np.array(df['HIGH']),np.array(df['LOW']), timeperiod=10)

df['bbinsideKelt'] = (df['bbupper'] < df['kupperband']) & (df['bblower'] > df['klowerband']) 
df['keltinsidebb'] = (df['bbupper'] > df['kupperband']) & (df['bblower'] < df['klowerband']) 


df['breakaway'] = talib.CDLBREAKAWAY(np.array(df['OPEN']), np.array(df['HIGH']),np.array(df['LOW']), np.array(df['CLOSE']))
signalsshortwindow = df.tail(70)
breakaway = df[df['pgosma20'] >3]
print(breakaway)
print(signalsshortwindow[['TIMESTAMP','CLOSE', 'pgosma14', 'pgoema14', 'pgosma20','pgoema20']])

# print(df.tail(30))

