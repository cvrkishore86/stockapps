from alpha_vantage.timeseries import TimeSeries

import sys

def stockchart(symbol):
    ts = TimeSeries(key='9GMZ8HK7KZ7E3X6U', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=symbol,interval='1min', outputsize='full')
    print(data)
    print(len(data))


stockchart("VEDL")