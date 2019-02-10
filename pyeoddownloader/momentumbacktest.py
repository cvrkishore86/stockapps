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



def slope(ts):
    """
    Input: Price time series.
    Output: Annualized exponential regression slope, multipl
    """
    x = np.arange(len(ts))
    
    log_ts = np.log(ts)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_ts)
    # print(log_ts)
    annualized_slope = (np.power(np.exp(slope), 250) - 1) * 100
    # print(annualized_slope)
    return annualized_slope * (r_value ** 2)
def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
                 kpsh=False, valley=False, ax=None):
    x = np.atleast_1d(x).astype('float64')
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x

    # find indices of all peaks
    dx = x[1:] - x[:-1]

    # handle NaN's
    indnan = np.where(np.isnan(x))[0]

    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf

    ine, ire, ife = np.array([[], [], []], dtype=int)

    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]

    else:
        if edge.lower() in ['rising', 'both']:
            ire = np.where((np.hstack((dx, 0)) <= 0) &
                           (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) &
                           (np.hstack((0, dx)) >= 0))[0]

    ind = np.unique(np.hstack((ine, ire, ife)))

    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(
            np.hstack((indnan, indnan - 1, indnan + 1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size - 1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(
            np.vstack([x[ind] - x[ind - 1], x[ind] - x[ind + 1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
                    & (x[ind[i]] > x[ind] if kpsh else True)
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indices by their occurrence
        ind = np.sort(ind[~idel])

    return ind

def higher(df):
    test = df.copy()
    test.reset_index(level=0, inplace=True)
    found = False

    temp = test['close']
    # print(temp)
    length = len(test.index)
    if length >= 2:
        found =  temp[length-2] < temp[length -1]
    # if found:
    #     print(test['timestamp'], test['close'])

    return found


def lower(df):
    test = df.copy()
    test.reset_index(level=0, inplace=True)
    found = True
    try:
        for i in range(len(test.index)):

            temp = test['close']
            if i + 1 < len(test.index):
                high = temp[i] > temp[i + 1]
                found = found and high
    except Exception:
        found = False
        pass
    return found



engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)
buyamount = 0
sellamount = 0
profit = 0
loss = 0
allsig = pd.DataFrame()
short_window = 50
long_window = 100
trade={}    
    
shortavgname = 'close_50_ema'
longavgname = 'close_100_ema'

buyfield = 'close_xu_close_50_ema'
sellfield = 'close_xd_close_50_ema'

start = time.clock()

# buyfield = 'close_50_ema_xu_close_100_ema'
# sellfield = 'close_50_ema_xd_close_100_ema'
# data = pd.read_sql('select * from momentum_scan_backtest e ',con=engine)
# allsig = pd.read_sql('select * from momentum_scan_backtest',con=engine)
data = pd.read_sql('select * from eq_adjusted_data ',con=engine)

symbols = list(data['symbol'].unique())


data['Date'] =  pd.to_datetime(data['Date'])
# niftydf = pd.read_sql('SELECT * FROM eq_eod_data e where e.SYMBOL = "NIFTY"  order by STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y")', con=engine)


# niftysymdata['TIMESTAMP'] = pd.to_datetime(niftydf['TIMESTAMP'])
# niftysymdata['niftyupdown'] = niftysymdata['CLOSE'] > niftysymdata['OPEN']
# niftydf = niftysymdata[['TIMESTAMP', 'niftyupdown']]

for j in range(0, len(symbols)):
  print("For" , symbols[j])

  symdata = data[data['symbol'] == symbols[j]]
  if len(symdata) > 20 :
    symdata = symdata.reset_index(drop=True)
    symdata = symdata.sort_values('Date',ascending =True)
    # symdata =  pd.merge(symdata,niftydf,    how='inner',        left_on=['TIMESTAMP'],        right_on=['TIMESTAMP'])
    symdata = Sdf.retype(symdata)
    
    symdata['close_xd_close_50_ema']
    symdata['ema20'] = talib.EMA(np.array(symdata['close']),timeperiod=20)
    symdata['sma20'] = talib.SMA(np.array(symdata['close']),timeperiod=20)
    
    symdata['vol20'] = talib.SMA(np.array(symdata['volume'],dtype='f8'),timeperiod=20)
    symdata['volratio']  = symdata['volume']/symdata['vol20']
    
    symdata['tr'] = talib.TRANGE(np.array(symdata['high']),np.array(symdata['low']), np.array(symdata['close']))
    symdata['ematr20'] = talib.EMA(np.array(symdata['tr']), timeperiod=20)


    symdata['ema14'] = talib.EMA(np.array(symdata['close']),timeperiod=14)
    symdata['sma14'] = talib.SMA(np.array(symdata['close']),timeperiod=14)
    symdata['ematr14'] = talib.EMA(np.array(symdata['tr']), timeperiod=14)

    symdata['pgoema20'] = (symdata['close'] - symdata['ema20']) /symdata['ematr20']
    symdata['pgoema14'] = (symdata['close'] - symdata['ema14']) /symdata['ematr14']

    symdata['pgosma20'] = (symdata['close'] - symdata['sma20']) /symdata['ematr20']
    symdata['pgosma14'] = (symdata['close'] - symdata['sma14']) /symdata['ematr14']
    symdata.reset_index(drop=False,inplace=True , level=0)
    symdata.to_sql(name='pgo_backtest', con=engine, if_exists = 'append', index=False)    
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
#     allsig = allsig.append(symdata, ignore_index=True)    
# # allsig.to_csv('pgobacktest.csv', index=False)
# allsig.to_sql(name='pgo_backtest', con=engine, if_exists = 'replace', index=False, chunksize=5000)

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
#                 timestamp = symdata.loc[i, 'timestamp']
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
                    
#                     print("bought ", symbol , "on ", timestamp, " at ", close)
#                     trade[symbol] = close
#                 if  sellsignal and symbol in trade:
#                     print ("sold ", symbol , "on ", timestamp, " at ", close,"bought at ", trade[symbol], "profit" , close - trade[symbol])
#                     del trade[symbol]


# print(trade)
print(time.clock() - start)
