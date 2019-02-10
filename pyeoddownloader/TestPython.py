
import pandas as pd
import numpy as np
import urllib.request
import json
import time
import datetime as dt

data = [100,101,102,101.5,101.25,102, 103, 104, 103.5,103,104,105,104.5]
parsed_data = []
index = 0



def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
                 kpsh=False, valley=False,  ax=None):
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
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]

    ind = np.unique(np.hstack((ine, ire, ife)))

    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan-1, indnan+1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size-1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind]-x[ind-1], x[ind]-x[ind+1]]), axis=0)
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

		temp= df['c']
		if i+1 < len(df.index):
			high = temp[i] < temp[i+1] 
			found = found and high
	return found

def lower(df):
	found = True
	for i in range(len(df.index)):

		temp= df['c']
		if i+1 < len(df.index):
			high = temp[i] > temp[i+1] 
			found = found and high
	return found


for x in range(1,13):
				dt1 = dt.datetime.now() + dt.timedelta(minutes=x)
				close = float(data[x])
				parsed_data.append((dt1,close))
				
df = pd.DataFrame(parsed_data)
df.columns = ['ts', 'c']
df.index = df.ts
del df['ts']

lows = detect_peaks(df['c'], valley=True,mpd=3)
					


highs = detect_peaks(df['c'],mpd=3)
print(highs,higher(df.iloc[highs]))
print(lows,higher(df.iloc[lows]))








