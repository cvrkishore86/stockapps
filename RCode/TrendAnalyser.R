
library(data.table)
library(greenbrown)
library(lubridate)
library(xts)
temp = read.csv('D:/code/workspace/NSEOIDownloader/temp3/consolidated.csv', header=T, check.names = FALSE)
temp1 = temp[order(temp$"SYMBOL", ymd(temp$"Date")),];
nifty50 <- subset(temp1, temp1$"SYMBOL" =="M&MFIN")
btemp3m <- subset(nifty50, ymd(nifty50$"Date") > (Sys.Date()-90))
nifty50$Date <- ymd(nifty50$Date)
ts1=ts(data = nifty50[,c(8)] ,class = "ts")
ts3m=ts(data = btemp3m[,c(8)] ,class = "ts")
trd3m <- Trend(ts3m,  mosum.pval=1)
trd <- Trend(ts1,  mosum.pval=1)

# trd<- Trend(ts1)
plot(trd)
trd
tail(trd$slope, n=1)
  plot(trd3m)
nifty50[tail(trd$bp$breakpoints, n=1),]$Date
x<-paste(round(trd$slope,digits=2),collapse=" ")