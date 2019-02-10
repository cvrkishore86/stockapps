import comtypes.client as cc
import datetime
from enum import Enum
import time
import asyncio

OLE_TIME_ZERO = datetime.datetime(1899, 12, 30, 0, 0, 0)
symbol_list = ['ACC', 'CENTURYTEX','VEDL']
sindex = 0
gotresponse = 0;
def ole2datetime(oledt):
    # return set to IST
    return OLE_TIME_ZERO + datetime.timedelta(days=float(oledt), hours=5, minutes=30)


def datetime2ole(dt):
    return (dt - OLE_TIME_ZERO).total_seconds() / (24 * 60 * 60)


#  Enter the path of the tlb file
module = cc.GetModule(
    'C:\Program Files (x86)\TrueData\TrueData Client API x86\Binary COM\TrueData.Velocity.External.tlb')


class PriceFields(Enum):
    BID = 1
    ASK = 2
    HIGH = 3
    LOW = 4
    OPEN = 5
    PREV = 7
    CHANGE = 8
    TRADEVOL = 10
    TOTALVOL = 11
    OPENINTEREST = 12
    BIDSIZE = 13
    ASKSIZE = 14
    LAST = 4109
    LAST_SNAPSHOT = 4110
    TRADEVOL_SNAPSHOT = 4111
    AUX1 = 4112
    AUX2 = 4113
    AVERAGE = 4114
    PREV_OI = 4115


class TrueDataExternalEventsSink:
    def OnBarData(self, RequestId, unknown):
        print("BarData event.")
        global sindex
        chart = unknown.QueryInterface(module.ITrueDataChart)
        count = chart.GetCount()
        lastupdatetime = datetime.datetime.utcnow();
        print("Request ID ", RequestId, " Bars count: ", count)
        for index in range(0, count):
            ohlc = chart.GetBar(index)
            date = ole2datetime(ohlc.date).strftime('%Y-%m-%d %H:%M:%S')
            print("Bar: ", symbol_list[sindex], date, round(ohlc.open, 2), round(ohlc.high, 2), round(ohlc.low, 2),
                  round(ohlc.close, 2), ohlc.volume, ohlc.oi)
        if sindex < len(symbol_list)-1:
        	sindex+=1
        else: 
        	sindex=0

        
        datefrom= datetime2ole(datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
        dateto= datetime2ole(datetime.datetime.utcnow())
        RequestTicks=truedata.RequestTicks(symbol_list[sindex], datefrom, dateto)	
		
    def OnRealTimeData(self, symbol, time, unknown):
        print("RealTimeData event.")
        update = unknown.QueryInterface(module.ITrueDataUpdate)
        count = update.GetCount()
        print("RT count: ", count)
        for index in range(0, count):
            price = update.GetUpdate(index)
            # date = ole2datetime(price.time).strftime('%Y-%m-%d %H:%M:%S')
            date = ole2datetime(price.time).strftime('%H:%M:%S')
            # see for price types in TrueDataFields of Truedata_Velocity_External type library
            price_type = price.id
            value = price.data
            print("RT Update:", symbol, PriceFields(
                price_type).name, str(date), value)
            if price_type == 4109:
                print(symbol, str(date), value)


# create object
truedata = cc.CreateObject("TrueDataExternal.1")

#  create sink class to receive events
sink = TrueDataExternalEventsSink()

#  advise the sink to make it receiving events
advise = cc.GetEvents(truedata, sink)

#  initialize API
truedata.VelocityInitialize()

#  wait while Velocity starts
truedata.VelocityWaitForReadyToProcess()
print("Velocity has been started")

#  request for real-time updates



# for symbols in symbol_list:
# 	 x = truedata.RequestRealTimeStart(symbols)


datefrom = datetime2ole(datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
dateto = datetime2ole(datetime.datetime.utcnow())
print(symbol_list[sindex])		
RequestIdTicks = truedata.RequestTicks(symbol_list[sindex], datefrom, dateto)	



# datefrom = datetime2ole(datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
# dateto = datetime2ole(datetime.datetime.utcnow())

# RequestIdTicks = truedata.RequestTicks(history_symbol, datefrom, dateto)
# time.sleep(30)	
# RequestIdTicks = truedata.RequestTicks('ACC', datefrom, dateto)

#  request history data up to now



# #  End-of-Day Data
# datefrom = datetime2ole(datetime.datetime.utcnow()-datetime.timedelta(days=10))
# RequestIdDays = truedata.RequestDaily(history_symbol, datefrom, dateto)
# print("Request id for days: ", RequestIdDays)

# Minute Data (1, 5, 15, 60 mins - replace in RequestMinutes)

# print(datefrom)
# RequestIdMinutes = truedata.RequestMinutes(history_symbol, datefrom, dateto, 1)
# print("Request id for minutes: ", RequestIdMinutes)


#  Tick  History Data

#  just wait for 5000 seconds before exit
cc.PumpEvents(5000)
#  stop to receive real-time
# truedata.RequestRealTimeStop("NIFTY-I")
#  uninitialize API
truedata.VelocityUninitialize()
#  stop advise (Force python to delete the object & free the memory)
advise = None

# price_type can be referred here
