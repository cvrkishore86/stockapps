from sqlalchemy import types, create_engine, Table,MetaData, column, select, update, insert,delete
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from datetime import date, timedelta,datetime



engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)

Session = sessionmaker(bind=engine)
session = Session()



eqbhavcopy = pd.read_csv("D:/code/workspace/NSEOIDownloader/pyeoddownloader/Download/raw_fut_oi_volt_dlvy/cm01JAN2018bhav.csv", sep=',',index_col=False)
eqbhavcopy = eqbhavcopy[eqbhavcopy['SERIES']== 'EQ']
eqbhav = eqbhavcopy.loc[:, ['SYMBOL','TIMESTAMP','OPEN', 'HIGH','LOW','CLOSE','TOTTRDQTY','TOTTRDVAL','TOTALTRADES']]
eqbhav.to_sql(name='eq_eod_data', con=engine, if_exists = 'append', index=False)

# # df = pd.read_sql('SELECT * FROM stock_data', con=engine)
# # print(df.head(10))
# metadata = MetaData(bind=engine)
# my_portfolio = Table('my_portfolio', metadata, autoload=True)
# # i = insert(my_portfolio)
# # i = i.values({"symbol": "ACC", "buydate": date(2015,12,15),"buyprice":100,"quantity":10})
# # session.execute(i)
# # session.commit()
# my_portfolio.query.filter_by(symb= 'ACC').delete()
# i = delete(my_portfolio)	
# i = i.values()
# session.execute(i)
# session.commit()
# d = my_portfolio.delete(my_portfolio.c.symbol == 'test')
# d.execute()

# print(start_date)

# columns = ["SYMBOL","SERIES","52_WEEK_HIGH","52_WEEK_HIGH_DT","52_WEEK_LOW","52_WEEK_LOW_DT"] # Specifies Column Names
# highlow = pd.read_csv("D:/code/workspace/NSEOIDownloader/pyeoddownloader/Download/raw_fut_oi_volt_dlvy/CM_52_wk_High_low.csv", sep=',',index_col=False,skiprows=2)                                                               # Pandas Reads
# highlow.columns = columns
# highlow.drop(['SERIES'], axis=1,inplace=True)
# highlow['52_WEEK_HIGH_DT'] = pd.to_datetime(highlow['52_WEEK_HIGH_DT'], format='%d-%b-%Y')
# highlow['52_WEEK_LOW_DT'] = pd.to_datetime(highlow['52_WEEK_LOW_DT'], format='%d-%b-%Y')
# highlow.to_sql(name='stock_data', con=engine, if_exists = 'replace', index=False)
# print(highlow.head(10))


# def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
#                  kpsh=False, valley=False, ax=None):
#     x = np.atleast_1d(x).astype('float64')
#     if x.size < 3:
#         return np.array([], dtype=int)
#     if valley:
#         x = -x

#     # find indices of all peaks
#     dx = x[1:] - x[:-1]

#     # handle NaN's
#     indnan = np.where(np.isnan(x))[0]

#     if indnan.size:
#         x[indnan] = np.inf
#         dx[np.where(np.isnan(dx))[0]] = np.inf

#     ine, ire, ife = np.array([[], [], []], dtype=int)

#     if not edge:
#         ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]

#     else:
#         if edge.lower() in ['rising', 'both']:
#             ire = np.where((np.hstack((dx, 0)) <= 0) &
#                            (np.hstack((0, dx)) > 0))[0]
#         if edge.lower() in ['falling', 'both']:
#             ife = np.where((np.hstack((dx, 0)) < 0) &
#                            (np.hstack((0, dx)) >= 0))[0]

#     ind = np.unique(np.hstack((ine, ire, ife)))

#     # handle NaN's
#     if ind.size and indnan.size:
#         # NaN's and values close to NaN's cannot be peaks
#         ind = ind[np.in1d(ind, np.unique(
#             np.hstack((indnan, indnan - 1, indnan + 1))), invert=True)]
#     # first and last values of x cannot be peaks
#     if ind.size and ind[0] == 0:
#         ind = ind[1:]
#     if ind.size and ind[-1] == x.size - 1:
#         ind = ind[:-1]
#     # remove peaks < minimum peak height
#     if ind.size and mph is not None:
#         ind = ind[x[ind] >= mph]
#     # remove peaks - neighbors < threshold
#     if ind.size and threshold > 0:
#         dx = np.min(
#             np.vstack([x[ind] - x[ind - 1], x[ind] - x[ind + 1]]), axis=0)
#         ind = np.delete(ind, np.where(dx < threshold)[0])
#     # detect small peaks closer than minimum peak distance
#     if ind.size and mpd > 1:
#         ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
#         idel = np.zeros(ind.size, dtype=bool)
#         for i in range(ind.size):
#             if not idel[i]:
#                 # keep peaks with the same height if kpsh is True
#                 idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
#                     & (x[ind[i]] > x[ind] if kpsh else True)
#                 idel[i] = 0  # Keep current peak
#         # remove the small peaks and sort back the indices by their occurrence
#         ind = np.sort(ind[~idel])

#     return ind

# def higher(df,columnname):
#     test = df.copy()
#     test.reset_index(level=0, inplace=True)
#     found = True
#     for i in range(len(df.index)):

#             temp = test[columnname]

#             if i + 1 < len(test.index):
#                 high = temp[i] < temp[i + 1]
#                 found = found and high
#     return found


# def lower(df,columnname):
#     test = df.copy()
#     test.reset_index(level=0, inplace=True)
    
#     found = True
#     try:
#         for i in range(len(df.index)):

#             temp = test[columnname]
#             if i + 1 < len(test.index):
#                 high = temp[i] > temp[i + 1]
#                 found = found and high
#     except Exception:
#         found = False
#         pass
#     return found


# engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)

# df = pd.read_sql('select * from eod_data', con=engine)
# df =df.loc[:, ['nse_date','nse_symbol','nse_eq_close','nse_fut_close']]
# df = df[df['nse_symbol'] == "VEDL"]
# lows = detect_peaks(df['nse_eq_close'], valley=True, mpd=5)
# lowsdf = df.iloc[lows]

# highs = detect_peaks(df['nse_eq_close'], mpd=3,threshold=1.5)
# highsdf = df.iloc[highs]

# if (higher(df.iloc[highs].tail(2), "nse_eq_close") and higher(df.iloc[lows].tail(2),"nse_eq_close")):
#     	print("higher highs detected")
    
# # nifty50 <- subset(temp1, temp1$"SYMBOL" =="NIFTY")
# # fitnifty <- lm(nifty50$CLOSE~ymd(nifty50$"Date"))
# # niftyslope <- coef(fitnifty)[2]
# # niftyslope
# # length(SYMB)
# # for (k in 1:length(SYMB)){
# #   tryCatch({
# #     btemp<- subset(temp1, temp1$"SYMBOL" == SYMB[k])
# #     btemp$CHG_IN_OI<- NULL  
# #     fitbtemp <- lm(btemp$CLOSE~ymd(btemp$"Date"))
# #     btemp20<- subset(btemp, ymd(btemp$"Date") > (Sys.Date()-20))
# #     btemp6m <- subset(btemp, ymd(btemp$"Date") > (Sys.Date()-90))
# #     fitbtemp6m <- lm(btemp6m$CLOSE~ymd(btemp6m$"Date"))
# #     t<-btemp20[order(btemp20$CLOSE), ];
# #     highs <-tail(t, n=1)
# #     lows <- head(t, n=1)
    
# #     if(symbtemp$SYMBOL[k] == SYMB[k]){
      
      
# #       symbtemp$rechighDay[k] <- format(highs$Date,format= "%y-%m-%d")
# #       # symbtemp$rechigh[k]<- highs$CLOSE
# #       symbtemp$reclowDay[k] <- format(lows$Date, format="%y-%m-%d")
# #       # symbtemp$reclow[k] <-lows$CLOSE
# #       symbtemp$slope[k] <- coef(fitbtemp)[2]
# #       symbtemp$slope3m[k] <- coef(fitbtemp6m)[2]
# #       symbtemp$beta[k] <- coef(fitbtemp)[2]/niftyslope
# #     }
# #     write.table(symbtemp,file="beta.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)
# #   }, error=function(err){
# #     print(SYMB[k])
# #     print(err)
# #   }
# #   )
  
# # }
