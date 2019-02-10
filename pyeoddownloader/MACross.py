from sqlalchemy import types, create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from datetime import date, timedelta,datetime



engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)

symbol = 'ACC'
df = pd.read_sql('SELECT * FROM eod_data where nse_symbol="'+symbol+'" order by nse_date', con=engine)

bars = df

short_window = 50
long_window = 100


"""Returns the DataFrame of symbols containing the signals
to go long, short or hold (1, -1 or 0)."""
signals = bars.copy()
signals['signal'] = 0.0

# Create the set of short and long simple moving averages over the 
# respective periods
signals['short_mavg'] = bars['nse_eq_close'].rolling(window=50,min_periods=1,center=False).mean()
signals['long_mavg'] = bars['nse_eq_close'].rolling(window=100,min_periods=1,center=False).mean()

# Create a 'signal' (invested or not invested) when the short moving average crosses the long
# moving average, but only for the period greater than the shortest moving average window
signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] 
    > signals['long_mavg'][short_window:], 1.0, 0.0)   

# Take the difference of the signals in order to generate actual trading orders
signals['positions'] = signals['signal'].diff()   
# print(signals.head(10))
temp = signals[signals['positions'] != 0.0]
sig = temp.loc[:, ['nse_date','nse_eq_close', 'positions']]
print(sig.head(10))
