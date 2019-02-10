from flask import *
import pandas as pd
app = Flask(__name__)



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
    try:
        for i in range(len(df.index)):

            temp = df['c']
            if i + 1 < len(df.index):
                high = temp[i] < temp[i + 1]
                found = found and high
    except Exception:
        found = False
        pass
    return found


def lower(df):
    found = True
    try:
        for i in range(len(df.index)):

            temp = df['c']
            if i + 1 < len(df.index):
                high = temp[i] > temp[i + 1]
                found = found and high
    except Exception:
        found = False
        pass
    return found


def fetchPreMarket(symbol, exchange):

    link = "https://www.google.com/finance/getprices?x=NSE&i=60&p=1d&f=d,c,o,h,l,v,t&df=cpct&auto=1&q="
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
                        daylowsig = 1
                    if ((close / y['h'].max() > 0.999) and (close / y['h'].max() < 1.001)):
                        print(
                            "Stock near days High watch out ----------", symbol, dt1)
                        dayhighsig = 1
            signals.append(('symbol','time', 'opn', 'high', 'low', 'close', 'volume','volsig', 'pallsig', 'pahhsig', 'daylowsig', 'dayhighsig'))
            signals.append((symbol,dt1, opn, high, low, close, volume,
                            volsig, pallsig, pahhsig, daylowsig, dayhighsig))
            time.sleep(5)
            parsed_data.append((dt1, symbol, close, opn, high, low, volume))
            df = pd.DataFrame(parsed_data)
            with open("temp.csv", "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerows(signals)
    return df



@app.route("/tables")
def show_tables():
    data = pd.read_csv('temp.csv')
    data.set_index(['symbol'], inplace=True)
    data.index.name=None
    return render_template('view.html',data=data);

if __name__ == "__main__":
    app.run(debug=True)