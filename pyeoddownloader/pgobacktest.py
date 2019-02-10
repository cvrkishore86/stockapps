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
from scipy import stats 
import time
import talib





engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)
buyamount = 0
sellamount = 0
profit = 0
loss = 0
allsig = pd.DataFrame()
short_window = 50
long_window = 100
trade={}    
    


start = time.clock()
df = pd.read_sql('SELECT distinct(symbol) FROM pgo_backtest where symbol="SONATASOFTW"', con=engine)
symbols = list(df['symbol'])


# niftydf = pd.read_sql('SELECT * FROM eq_eod_data e where e.SYMBOL = "NIFTY"  order by STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y")', con=engine)


# niftysymdata['TIMESTAMP'] = pd.to_datetime(niftydf['TIMESTAMP'])
# niftysymdata['niftyupdown'] = niftysymdata['CLOSE'] > niftysymdata['OPEN']
# niftydf = niftysymdata[['TIMESTAMP', 'niftyupdown']]

for j in range(0, len(symbols)):
# for j in range(0, 2):

    # print("For" , symbols[j])
    data = pd.read_sql('select * from pgo_backtest e where e.symbol='+"'"+symbols[j]+"' and e.date >  NOW() - INTERVAL 800 DAY",con=engine)
    data['date'] =  pd.to_datetime(data['date'])
    
    symdata = data.reset_index(drop=True)
    symdata = symdata.sort_values('date',ascending =True)
    symdata['gainpct'] = (symdata['close'] - symdata['open'] ) * 100/ symdata['open']
    i = 1 
    while i < len(symdata):

        pgo = symdata.loc[i, 'pgosma20']
        prevpgo = symdata.loc[i-1, 'pgosma20']
        gainpct = symdata.loc[i,'gainpct']
        volratio = symdata.loc[i,'volratio']
        close = symdata.loc[i, 'close']
        close50ema = symdata.loc[i, 'close_50_ema']
        if prevpgo < 3 and pgo >3.1 and gainpct < 5 and volratio > 1 and (close > close50ema):
            nextdata = symdata[i:len(symdata)]
            xd50ema = nextdata[nextdata['close_xd_close_50_ema'] == 1]
            buyprice = symdata.loc[i,'close']
            if i < len(symdata) -1:
                    buyprice = symdata.loc[i+1,'open']
            # print('pgo', symdata.loc[i, 'pgosma20'], 'prevpgo', symdata.loc[i-1, 'pgosma20'], 'gainpct' , gainpct)
            if len(xd50ema) >0 :
                sellindex = xd50ema.index[0]
                if sellindex < len(symdata) - 1 : 
                    print("symbol" , symbols[j], 'gainpct' , gainpct,"volratio",volratio,  "buydate", symdata.loc[i,'date'],"bought",  buyprice,'solddate', symdata.loc[sellindex+1, 'date'],"sellprice" , symdata.loc[sellindex+1, 'open']  )
                i = sellindex+1
            else : 
                print("symbol" , symbols[j], 'gainpct' , gainpct, "buydate", symdata.loc[i,'date'],"bought",  buyprice ,"didnt sell today sellprice" , symdata['close'].iloc[-1])
                i = len(symdata)+1
        else :
            i+=1
    # for  i in range(0, len(symdata)) :
    #     if i > 100 :
    #         symdata['updown'] = symdata['close']> symdata['open']

    #         signalsshortwindow = symdata.iloc[i-short_window:i]
            
    #         niftyreddays = signalsshortwindow[signalsshortwindow['niftyupdown'] == False]
    #         greenwhenniftyred = niftyreddays['updown'].sum()
    #         niftyreddays = len(niftyreddays)

    #         signals30 = symdata.iloc[i-30:i]

    #         greendays = signalsshortwindow['updown'].sum()
    #         reddays = len(signalsshortwindow)- greendays
    #         symdata.loc[i, 'greendays'] = greendays
    #         symdata.loc[i, 'reddays'] = reddays

    #         symdata.loc[i, 'annualslope'] = slope(signalsshortwindow['close']);
    #         symdata.loc[i, 'slope30'] = slope(signals30['close']);
            
    #         symdata.loc[i, 'greenonniftyred'] = greenwhenniftyred/niftyreddays

# > 100 slope after golden cross and  price action higher high or higher low with minimum amplitude  (find highest peak date)
print(time.clock() - start )

# for j in range(0, len(symbols)):
    
#     symdata = allsig[allsig['symbol'] == symbols[j]]
#     symdata = symdata.reset_index(drop=True)
#     for  i in range(0, len(symdata)) :
#         if i > 100:
#             signalsshortwindow = symdata.iloc[0:i]

#             xu = signalsshortwindow[signalsshortwindow['close_50_ema_xu_close_100_ema']==1]
#             xd = signalsshortwindow[signalsshortwindow['close_50_ema_xd_close_100_ema']==1]

#             goldcross = False
#             if len(xu) > 0:
#                 if len(xd) > 0:
#                     goldcross = xu.index[-1] > xd.index[-1]

#                 else :
#                     goldcross = True
#             if goldcross:
#                 aftercross = signalsshortwindow[xu.index[-1]-50:]

#                 lows = detect_peaks(aftercross['close'], valley=True,mpd=5, threshold=1.25)
                
                
#                 higherlow = higher(aftercross.iloc[lows])
#                 close50ema = symdata.loc[i, 'close_50_ema']
#                 close100ema = symdata.loc[i, 'close_100_ema']
#                 close = symdata.loc[i, 'close']
#                 date = symdata.loc[i, 'date']
#                 symbol = symdata.loc[i, 'symbol']
#                 annualslope = symdata.loc[i, 'annualslope']
#                 greendays = symdata.loc[i, 'greendays']
#                 reddays = symdata.loc[i, 'reddays']
#                 slope30 = symdata.loc[i, 'slope30']
#                 greenonniftyred = symdata.loc[i, 'greenonniftyred']
#                 updownratio = greendays/reddays
                
                
#                 sellsignal = close < close100ema
#                 print(symbol, goldcross,higherlow, close , slope30, updownratio,greenonniftyred)
#                 if goldcross and higherlow and slope30 > 100 and updownratio> 0.7 and greenonniftyred > 0.3 and  (not symbol in trade): 
                    
#                     print("bought ", symbol , "on ", date, " at ", close)
#                     trade[symbol] = close
#                 if  sellsignal and symbol in trade:
#                     print ("sold ", symbol , "on ", date, " at ", close,"bought at ", trade[symbol], "profit" , close - trade[symbol])
#                     del trade[symbol]


# print(trade)
print(time.clock() - start)
