import pandas as pd
import numpy as np
import urllib.request
import json
import time
import datetime as dt
import csv
from stockstats import StockDataFrame as Sdf

parsed_data = []
signals=[]
index = 0
msgs = {}

def supertrend(df,period, multiplier):
    
    st = 'st_' + str(period) + '_' + str(multiplier)
    # Compute basic upper and lower bands
    df['basic_ub'] = (df['high'] + df['low']) / 2 + multiplier * df['atr']
    df['basic_lb'] = (df['high'] + df['low']) / 2 - multiplier * df['atr']

    # Compute final upper and lower bands
    for i in range(0, len(df)):
        if i < period:
            df.set_value(i, 'basic_ub', 0.00)
            df.set_value(i, 'basic_lb', 0.00)
            df.set_value(i, 'final_ub', 0.00)
            df.set_value(i, 'final_lb', 0.00)
        else:
            df.set_value(i, 'final_ub', (df.get_value(i, 'basic_ub') 
                                         if df.get_value(i, 'basic_ub') < df.get_value(i-1, 'final_ub') or df.get_value(i-1, 'close') > df.get_value(i-1, 'final_ub') 
                                         else df.get_value(i-1, 'final_ub')))
            df.set_value(i, 'final_lb', (df.get_value(i, 'basic_lb') 
                                         if df.get_value(i, 'basic_lb') > df.get_value(i-1, 'final_lb') or df.get_value(i-1, 'close') < df.get_value(i-1, 'final_lb') 
                                         else df.get_value(i-1, 'final_lb')))

    # Set the Supertrend value
    for i in range(0, len(df)):
        if i < period:
            df.set_value(i, st, 0.00)
        else:
            df.set_value(i, st, (df.get_value(i, 'final_ub')
                                 if ((df.get_value(i-1, st) == df.get_value(i-1, 'final_ub')) and (df.get_value(i, 'close') <= df.get_value(i, 'final_ub')))
                                 else (df.get_value(i, 'final_lb')
                                       if ((df.get_value(i-1, st) == df.get_value(i-1, 'final_ub')) and (df.get_value(i, 'close') > df.get_value(i, 'final_ub')))
                                       else (df.get_value(i, 'final_lb')
                                             if ((df.get_value(i-1, st) == df.get_value(i-1, 'final_lb')) and (df.get_value(i, 'close') >= df.get_value(i, 'final_lb')))
                                             else (df.get_value(i, 'final_ub')
                                                   if((df.get_value(i-1, st) == df.get_value(i-1, 'final_lb')) and (df.get_value(i, 'close') < df.get_value(i, 'final_lb')))
                                                   else 0.00
                                                  )
                                            )
                                      ) 
                                )
                        )


    # Mark the trend direction up/down
    df['stx'] = np.where((df[st] > 0.00), np.where((df['close'] < df[st]), 'down',  'up'), np.NaN)

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
    found = True
    for i in range(len(df.index)):

        temp = df['c']
        if i + 1 < len(df.index):
            high = temp[i] < temp[i + 1]
            found = found and high
    return found


def lower(df):
    found = True
    for i in range(len(df.index)):

        temp = df['c']
        if i + 1 < len(df.index):
            high = temp[i] > temp[i + 1]
            found = found and high
    return found


def fetchPreMarket(symbol, exchange):

    link = "https://www.google.com/finance/getprices?x=NSE&i=60&p=2d&f=d,c,o,h,l,v,t&df=cpct&auto=1&q="
    url = link + symbol
    response = urllib.request.urlopen(url)
    df = None
    # actual data starts at index = 7
    # first line contains full timestamp,
    # every other line is offset of period from timestamp

    anchor_stamp = ''
    lineno = 0
    for line1 in response:

        line = str(line1)
        line = line.replace("b'", "")
        line = line.replace("\\n'", "")

        cdata = line.split(',')
        lineno = lineno + 1
        signals=[]
        if lineno > 7:
            if line.startswith('a'):
                anchor_stamp = cdata[0].replace('a', '')
                cts = int(anchor_stamp)
            else:
                coffset = int(cdata[0])
                cts = int(anchor_stamp) + (coffset * 60)
            dt1 = dt.datetime.fromtimestamp(cts)
            close = float(cdata[1])
            opn = float(cdata[2])
            high = float(cdata[3])
            low = float(cdata[3])
            volume = float(cdata[5])
            volsig = 0
            pahhsig = 0
            pallsig = 0
            daylowsig = 0
            dayhighsig = 0
            time1 = dt1.strftime('%H:%M:%S')
            if lineno > 8:
                df = pd.DataFrame(parsed_data)
                df.columns = ['ts', 's', 'c', 'o', 'h', 'l', 'v']
                df.index = df.ts
                del df['ts']
                z = df.copy()
                z = z[z['s'] == symbol]

                if len(z.index) > 15:
                    z = z.tail(15)
                    if ((volume >= z['v'].max())):
                        print("Highest Volume found for ---------", symbol, dt1)
                        msgs[symbol] = "Highest Volume found "+time1
                        volsig = 1
                x = df.copy()
                x = x[x['s'] == symbol]

                if len(x.index) > 20:
                    x = x.tail(20)

                    lows = detect_peaks(x['c'], valley=True, mpd=3)
                    highs = detect_peaks(x['c'], mpd=3)

                    if len(highs) > 3 or len(lows) > 3:
                        if (higher(x.iloc[highs]) and higher(x.iloc[lows])):
                            print(
                                "higher highs or higher lows found for Long -------", symbol, dt1)
                            msgs[symbol] = "higher highs or higher lows found for LONG"+time1    
                            pahhsig = 1
                        if (lower(x.iloc[highs]) and lower(x.iloc[lows])):
                            print(
                                "lower highs or lower lows found for short--------", symbol, dt1)

                            pallsig = 1
                y = df.copy()
                y = y[y['s'] == symbol]
                y = y.head(len(y.index) - 30)
                if len(y.index) > 30:
                    if (((close / y['l'].min()) > 0.999) and ((close / y['l'].min()) < 1.001)):
                        print(
                            "Stock near days Low watch out ----------- ", symbol, dt1)
                        msgs[symbol] = "near days LOW watch out"+time1   
                        daylowsig = 1
                    if ((close / y['h'].max() > 0.999) and (close / y['h'].max() < 1.001)):
                        print(
                            "Stock near days High watch out ----------", symbol, dt1)
                        msgs[symbol] = "near days HIGH watch out"+time1 
                        dayhighsig = 1
            
                       
            parsed_data.append((dt1, symbol, close, opn, high, low, volume))
            df = pd.DataFrame(parsed_data)
            df.columns = ['ts', 's', 'c', 'o', 'h', 'l', 'v']
            stats = df.copy();
            stats.columns = ['ts', 's', 'close', 'open', 'high', 'low', 'volume']
            
            stock_df = Sdf.retype(stats)
            cci34 = round(stock_df['cci_34'][len(df.index)-1])
            stock_df['atr']
            supertrend(stock_df,10,3)
            superTrend = stock_df['stx'][len(df.index)-1]
            time1 = dt1.strftime('%H:%M:%S')
            
            signals.append(('symbol','time', 'opn', 'high', 'low', 'close', 'volume','volsig', 'pallsig', 'pahhsig', 'daylowsig', 'dayhighsig', 'cci34', 'SuperTrend','msg'))
            signals.append((symbol,time1, opn, high, low, close, volume,
                            volsig, pallsig, pahhsig, daylowsig, dayhighsig, cci34,superTrend,msgs.get(symbol,"")))
            
            with open("temp.csv", "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerows(signals)
            time.sleep(2)
    return df



print("program started at ", dt.datetime.now())
# while True:
# content = fetchPreMarket("CAPF","NSE")
# content = fetchPreMarket("BHARATFORG","NSE")
# content = fetchPreMarket("ARVIND","NSE")
# content = fetchPreMarket("CEATLTD","NSE")
# content = fetchPreMarket("MARICO","NSE")
# content = fetchPreMarket("APOLLOTYRE","NSE")
content = fetchPreMarket("BALKRISIND", "NSE")

# time.sleep(30)
