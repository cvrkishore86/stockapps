# TrueData External Client API for 64 bit
# Please make sure your Python environment (Pycharm or spyder etc..) is 'Run as admin

import comtypes.client as cc
import datetime

OLE_TIME_ZERO = datetime.datetime(1899, 12, 30, 0, 0, 0)


def ole2datetime(oledt):
	return OLE_TIME_ZERO + datetime.timedelta(days=float(oledt), hours=5, minutes=30)  # return set to IST


def datetime2ole(dt):
	return (dt - OLE_TIME_ZERO).total_seconds() / (24 * 60 * 60)


#  Enter the path of the tlb file (This is the default path. Make sure it is the same for you)
module = cc.GetModule('C:\Program Files\TrueData\TrueData Client API x64\Binary COM\TrueData.Velocity.External.tlb')


class TrueDataExternalEventsSink:
	def OnBarData(self, RequestId, unknown):
		print("BarData event.")
		chart = unknown.QueryInterface(module.ITrueDataChart)
		count = chart.GetCount()
		print("Request ID ", RequestId, " Bars count: ", count)
		for index in range(0, count):
			ohlc = chart.GetBar(index)
			date = ole2datetime(ohlc.date).strftime('%Y-%m-%d %H:%M:%S')
			print("Bar: ", history_symbol,  date, round(ohlc.open, 2), round(ohlc.high, 2), round(ohlc.low, 2),
				round(ohlc.close, 2), ohlc.volume, ohlc.oi)

	def OnRealTimeData(self, symbol, time, unknown):
		print("RealTimeData event.")
		update = unknown.QueryInterface(module.ITrueDataUpdate)
		count = update.GetCount()
		print("RT count: ", count)
		for index in range(0, count):
			price = update.GetUpdate(index)
			# date = ole2datetime(price.time).strftime('%Y-%m-%d %H:%M:%S')
			date = ole2datetime(price.time).strftime('%H:%M:%S')
			price_type = price.id  # see for price types in TrueDataFields of Truedata_Velocity_External type library
			value = price.data
			print("RT Update:", symbol, price_type, str(date), value)
			# if price_type == 4109:
			# 	print(symbol, str(date), value)
		print("BarData event.")
		chart = unknown.QueryInterface(module.ITrueDataChart)
		count = chart.GetCount()
		print("Request ID ", RequestId, " Bars count: ", count)
		for index in range(0, count):
			ohlc = chart.GetBar(index)
			date = ole2datetime(ohlc.date).strftime('%Y-%m-%d %H:%M:%S')
			print("Bar: ", history_symbol,  date, round(ohlc.open, 2), round(ohlc.high, 2), round(ohlc.low, 2),
				round(ohlc.close, 2), ohlc.volume, ohlc.oi)

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
symbol_list = ['NIFTY-I', 'BANKNIFTY-I']

for symbols in symbol_list:
	truedata.RequestRealTimeStart(symbols)

#  request history data up to now
history_symbol = 'NIFTY-I'
dateto = datetime2ole(datetime.datetime.utcnow())

#  End-of-Day Data
datefrom = datetime2ole(datetime.datetime.utcnow()-datetime.timedelta(days=10))
RequestIdDays = truedata.RequestDaily(history_symbol, datefrom, dateto)
print("Request id for days: ", RequestIdDays)

#  Minute Data (1, 5, 15, 60 mins - replace in RequestMinutes)
datefrom = datetime2ole(datetime.datetime.now()-datetime.timedelta(days=4))
RequestIdMinutes = truedata.RequestMinutes(history_symbol, datefrom, dateto, 1)
print()
print("Request id for minutes: ", RequestIdMinutes)

#  Tick  History Data
# datefrom = datetime2ole(datetime.datetime.utcnow()-datetime.timedelta(hours=12))
# RequestIdTicks = truedata.RequestTicks(history_symbol, datefrom, dateto)
# print("Request id for ticks: ", RequestIdTicks)

#  just wait for 5000 seconds before exit
cc.PumpEvents(5000)
#  stop to receive real-time
truedata.RequestRealTimeStop("NIFTY-I")
#  uninitialize API
truedata.VelocityUninitialize()
#  stop advise (Force python to delete the object & free the memory)
advise = None

# price_type can be referred here

# enum {
#    TrueDataFields_BID = 1,
#     TrueDataFields_ASK = 2,
#     TrueDataFields_HIGH = 3,
#     TrueDataFields_LOW = 4,
#     TrueDataFields_OPEN = 5,
#     TrueDataFields_PREV = 7,
#     TrueDataFields_CHANGE = 8,
#     TrueDataFields_TRADEVOL = 10,
#     TrueDataFields_TOTALVOL = 11,
#     TrueDataFields_OPENINTEREST = 12,
#     TrueDataFields_BIDSIZE = 13,
#     TrueDataFields_ASKSIZE = 14,
#     TrueDataFields_LAST = 4109,
#     TrueDataFields_LAST_SNAPSHOT = 4110,
#     TrueDataFields_TRADEVOL_SNAPSHOT = 4111,
#     TrueDataFields_AUX1 = 4112,
#     TrueDataFields_AUX2 = 4113,
#     TrueDataFields_AVERAGE = 4114,
#     TrueDataFields_PREV_OI = 4115
# } TrueDataFields;
