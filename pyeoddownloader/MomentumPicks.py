from sqlalchemy import types, create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from datetime import date, timedelta,datetime
from stockstats import StockDataFrame as Sdf
import statsmodels.formula.api as sm
from scipy import stats 
import talib


engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)


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


def generateMomentumPicks(short_window , long_window ):
	allsig = pd.DataFrame(columns=['symbol','timestamp','close'])
	
	print("trying to retrieve values")
		
	shortavgname = 'close_' + str(short_window) + '_ema'
	longavgname = 'close_' + str(long_window) + '_ema'

	#df = pd.read_sql('SELECT * FROM eq_eod_data e  where e.symbol="RAIN" and  STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y") >= NOW() - INTERVAL 400 DAY order by STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y")', con=engine)
	df = pd.read_sql('SELECT * FROM eq_eod_data e where  STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y") >= NOW() - INTERVAL 400 DAY order by STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y")', con=engine)

	niftydf = pd.read_sql('SELECT * FROM eq_eod_data e where e.SYMBOL = "NIFTY" and  STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y") >= NOW() - INTERVAL 400 DAY order by STR_TO_DATE(e.TIMESTAMP, "%%d-%%M-%%Y")', con=engine)
	print(niftydf.tail(1))
	df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
	niftydf['TIMESTAMP'] = pd.to_datetime(niftydf['TIMESTAMP'])
	niftydf['niftyupdown'] = niftydf['CLOSE'] > niftydf['OPEN']
	niftydf = niftydf[['TIMESTAMP', 'niftyupdown']]
	df['date1'] = df['TIMESTAMP']
		
	symbols = list(df['SYMBOL'].unique())

	for j in range(0, len(symbols)):
		
		symdata = df[df['SYMBOL'] == symbols[j]]
		symdata =  pd.merge(symdata,niftydf,	how='inner',		left_on=['TIMESTAMP'],		right_on=['TIMESTAMP'])
		symdata['momentumscore'] = 0
		
		if len(symdata) >long_window:
			print("inside if for ", symbols[j])
			# bars = symdata.sort_values('TIMESTAMP',ascending =False)
			
			"""Returns the DataFrame of symbols containing the signals
			to go long, short or hold (1, -1 or 0)."""
			test = symdata.copy();
			test = test.set_index('TIMESTAMP')
			test2 = test.groupby(pd.Grouper(freq='M')).date1.max()
			test2 = test2.reset_index(level=0)
			testing = test[test['date1'].isin(list(test2['date1']))]
			# testing = testing.set_index('TIMESTAMP')
			
			testdata = testing.CLOSE.pct_change() + 1
			# testdata1= test.asfreq('BM').CLOSE.pct_change() + 1
			
			
			if (len(testdata) > 12) :

				temp = testdata.tail(13)
				# print(temp)
				# print(temp[0] ,temp[1],temp[2] ,temp[3],temp[4] ,temp[5],temp[6] ,temp[7],temp[8] ,temp[9],temp[10] ,temp[11], temp[12])
				mul = ((temp[0] *temp[1]*temp[2] *temp[3]*temp[4] *temp[5]*temp[6] *temp[7]*temp[8] *temp[9]*temp[10] *temp[11]) -1)*100
				mul6 = ((temp[6] *temp[7]*temp[8] *temp[9]*temp[10] *temp[11]) -1)*100
				mul3 = ((temp[9]*temp[10] *temp[11]) -1)*100
				if np.isnan(mul) :
					mul = 0
				
			signals = Sdf.retype(symdata)
			# signals = signals.reset_index(level=0)
			# print(signals.head(10))
			signals['ema'] = talib.EMA(np.array(signals['close']),timeperiod=20)
			signals['tr'] = talib.TRANGE(np.array(signals['high']),np.array(signals['low']), np.array(signals['close']))
			signals['ematr'] = talib.EMA(np.array(signals['tr']), timeperiod=20)
			signals['pgo'] = (signals['close'] - signals['ema']) /signals['ematr']
			signals['momscore12'] = mul
			signals['momscore6'] = mul6
			signals['momscore3'] = mul3
			# signals[shortavgname]
			# signals[longavgname]
			# signals['signal'] = 0.0
			signals[shortavgname+'_xu_'+longavgname]
			signals[shortavgname+'_xd_'+longavgname]
			signals['close_200_ema']

			signals['updown'] = signals['close']> signals['open']
			signalsshortwindow = signals.tail(short_window)
			niftyreddays = signalsshortwindow[signalsshortwindow['niftyupdown'] == False]
			greenwhenniftyred = niftyreddays['updown'].sum()
			niftyreddays = len(niftyreddays)
			xu = signals[signals['close_50_ema_xu_close_100_ema']==1]
			xd = signals[signals['close_50_ema_xd_close_100_ema']==1]
			higherlow = False
			goldcross = False
			higherlowdt = ''
			if len(xu) > 0:
				if len(xd) > 0:
					goldcross = xu.index[-1] > xd.index[-1]

				else :
					goldcross = True
			if goldcross:
				aftercross = signals[xu.index[-1]-50:]

				lows = detect_peaks(aftercross['close'], valley=True,mpd=5, threshold=1.25)
				aftercross.reset_index(level=0, inplace=True)
				if (len(lows) > 0):
					higherlowdt = aftercross.loc[lows[len(lows)-1],'timestamp']
				higherlow = higher(aftercross.iloc[lows])

			signals['higherlow'] = higherlow
			signals['higherlowdt'] = str(higherlowdt)

			signals30 = signals.tail(30)
			
			latest = signals.tail(1);
			latest = latest.reset_index(drop=True)
			
			signals['last_pgo'] = latest.loc[0, 'pgo']
			signals['last_close_50_ema'] = latest.loc[0, 'close_50_ema']
			signals['last_close_100_ema'] = latest.loc[0, 'close_100_ema']
			pgogt3 = signalsshortwindow[(signalsshortwindow['pgo'] >= 3)]
			pgolt0 = signalsshortwindow[(signalsshortwindow['pgo'] <0)]
			pgo_gt_3 = False
			if len(pgogt3) > 0 :
				 if len(pgolt0)> 0 :
				 	pgo_gt_3 = pgogt3.index[-1]  > pgolt0.index[-1] 
				 else :
				 	pgo_gt_3 = True
			signals['pgo_gt_3'] = pgo_gt_3
			
			
			# result1 = sm.ols(formula=shortavgname+" ~ timestamp", data=signalsshortwindow).fit()
			# signals[shortavgname+'_slope'] = result1.params[len(result1.params)-1];
			# # print(result1.params.Intercept)
			# # print(signals)
			# result2 = sm.ols(formula=longavgname+" ~ timestamp", data=signalsshortwindow).fit()
			# signals[longavgname+'_slope'] = result2.params[len(result2.params)-1];

			
			
			greendays = signalsshortwindow['updown'].sum()
			reddays = len(signalsshortwindow)- greendays
			signals['greendays'] = greendays
			signals['reddays'] = reddays
			first = signalsshortwindow.head(1);
			first = first.reset_index(drop=True)
			signals['annualslope'] = slope(signalsshortwindow['close']);
			signals['slope30'] = slope(signals30['close']);
			
			# print(symbols[j],first.loc[0,'timestamp'], greenwhenniftyred, niftyreddays)
			signals['greenonniftyred'] = greenwhenniftyred/niftyreddays
			signals.drop(['updown', 'niftyupdown','tottrdval','totaltrades','pgo','ema','tr','ematr'], axis=1,inplace=True) 
			
			
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
			temp = signals[(signals[shortavgname+'_xu_'+longavgname] == True) | (signals[shortavgname+'_xd_'+longavgname] == True)]
			# sig = temp.loc[:, ['symbol','timestamp','close',shortavgname,longavgname, shortavgname+'_xu_'+longavgname]]
			
			allsig = allsig.append(temp, ignore_index=True)
	#print(allsig)
	allsig.to_sql(name='momentum_scan', con=engine, if_exists = 'replace', index=False)


if __name__ == '__main__':
    generateMomentumPicks(50,100)
