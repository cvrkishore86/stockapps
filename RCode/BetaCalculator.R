setwd('D:/code/workspace/NSEOIDownloader/temp3')
library(data.table)
library(xlsx) #load the package
library(lubridate)
library(greenbrown)
library(httr)
mydata1 = read.csv('D:/code/workspace/NSEOIDownloader/temp3/consolidated.csv', header=T, check.names = FALSE)
startDate = Sys.Date()-1;


temp = subset(mydata1, select=c("Date","SYMBOL","EXPIRY_DT","OPEN_INT", "CHG_IN_OI","OPEN","HIGH","LOW","CLOSE") )
colnames(temp)[colnames(temp)=="CLOSE"] <- "PRICE"
temp1 = temp[order(temp$"SYMBOL", ymd(temp$"Date")),];

SYMB<-unique(temp1$"SYMBOL")
symbtemp<-data.frame(SYMB)
colnames(symbtemp)<-c("SYMBOL")



# symbtemp <- read.csv("beta.csv");

nifty50 <- subset(temp1, temp1$"SYMBOL" =="NIFTY")
fitnifty <- lm(nifty50$PRICE~ymd(nifty50$"Date"))
niftyslope <- coef(fitnifty)[2]
niftyslope
length(SYMB)
for (k in 1:length(SYMB)){
  tryCatch({
    btemp<- subset(temp1, temp1$"SYMBOL" == SYMB[k])
    btemp$CHG_IN_OI<- NULL  
    fitbtemp <- lm(btemp$PRICE~ymd(btemp$"Date"))
    btemp20<- subset(btemp, ymd(btemp$"Date") > (Sys.Date()-20))
    btemp3m <- subset(btemp, ymd(btemp$"Date") > (Sys.Date()-90))
    fitbtemp3m <- lm(btemp3m$PRICE~ymd(btemp3m$"Date"))
    t<-btemp20[order(btemp20$PRICE), ];
    ts1=ts(data = btemp[,c(8)] ,class = "ts")
    ts3m=ts(data = btemp3m[,c(8)] ,class = "ts")
    trd <- Trend(ts1,  mosum.pval=1)
    trd3m <- Trend(ts3m,  mosum.pval=1)
    newSlope<-tail(trd$slope, n=1)
    newSlope3m<-tail(trd3m$slope, n=1)
    newTrendStart <- paste(btemp[tail(trd$bp$breakpoints, n=1),]$Date,collapse=" ")
    newTrendStart3m <- paste(btemp3m[tail(trd3m$bp$breakpoints, n=1),]$Date,collapse=" ")
    highs <-tail(t, n=1)
    lows <- head(t, n=1)
    
    if(symbtemp$SYMBOL[k] == SYMB[k]){
      
      
      symbtemp$rechighDay[k] <- format(highs$Date,format= "%y-%m-%d")
      # symbtemp$rechigh[k]<- highs$PRICE
      symbtemp$reclowDay[k] <- format(lows$Date, format="%y-%m-%d")
      # symbtemp$reclow[k] <-lows$PRICE
      symbtemp$slope[k] <- coef(fitbtemp)[2]
      symbtemp$slope3m[k] <- coef(fitbtemp3m)[2]
      symbtemp$beta[k] <- coef(fitbtemp)[2]/niftyslope
      symbtemp$newSlope[k]<-newSlope
      symbtemp$newtrendStDt[k]<-newTrendStart
      symbtemp$newSlope3m[k]<-newSlope3m
      symbtemp$newtrendStDt3m[k]<-newTrendStart3m
      
      
      # symbtemp$trendSlopes[k]<-paste(round(trd$slope,digits=2),collapse=" ")
      # btempresid<-subset(btemp, select=c("SYMBOL","Date"))
      # btempresid$minrsid<- min(rstandard(fitbtemp))
      # btempresid$maxrsid<- max(rstandard(fitbtemp))
      # btempresid$rstandard<-rstandard(fitbtemp)
      #  # deltarecords<-subset(btempresid, ymd(btempresid$"Date") >=  startDate)
      #  #  write.table(deltarecords,file="rstandard.csv",sep=",", eol="\n", row.names = FALSE, col.names = FALSE, append=TRUE)
      # if(k ==1 ){
      # write.table(btempresid,file="rstandard.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)
      # } else {
      #   write.table(btempresid,file="rstandard.csv",sep=",", eol="\n", row.names = FALSE, col.names = FALSE, append=TRUE)
      # }
    }
    write.table(symbtemp,file="beta.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)
  }, error=function(err){
    print(SYMB[k])
    print(err)
  }
  )
  
}

betadata <- read.csv('beta.csv', header=T);
mktlots <- read.csv('mktlots.csv', header=T);



consolidatebeta<-merge(mydata1, betadata);

consolidated<-merge(consolidatebeta,mktlots)

write.table(consolidated,file="consolidatefinal.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)


mydata1 = read.csv('D:/code/workspace/NSEOIDownloader/temp3/consolidatefinal.csv', header=T)



GET("https://www.nseindia.com/content/fo/fo_secban.csv", user_agent("Mozilla/5.0"), write_disk("fo_secban.csv", overwrite = TRUE))
ban <-read.csv("fo_secban.csv");

temp1 = mydata1[order(mydata1$"SYMBOL", ymd(mydata1$"Date")),];
temp1<-subset(temp1, (ymd(temp1$"Date") > Sys.Date()-90))

colnames(temp1)[colnames(temp1)=="CLOSE"] <- "PRICE"



temp1$DaysPriceChange <- temp1$PRICE - temp1$OPEN;
temp1$OPEN_INT <- as.numeric(as.character(temp1$OPEN_INT))
temp1$OIPercent <- with(temp1 , ((temp1$OPEN_INT - shift(temp1$OPEN_INT, 1L, type=c('lag')))/shift(temp1$OPEN_INT, 1, type='lag'))*100)



#Removing clutter in VPA Sheet


temp1$PricePercent <- with(temp1, ((temp1$PRICE - shift(temp1$PRICE, 1, type='lag'))/shift(temp1$PRICE, 1, type='lag'))*100)
temp1$OI3DayPercent <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 2, type="lag"),(temp1$OIPercent + shift(temp1$OIPercent, 1, type='lag')  + shift(temp1$OIPercent, 2, type='lag')), 0))
temp1$Price3DayPercent <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 2, type="lag"),(temp1$PricePercent + shift(temp1$PricePercent, 1, type='lag')  + shift(temp1$PricePercent, 2, type='lag')), 0))
temp1$STATUS = with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 1, type="lag"),
                                  ifelse(temp1$OIPercent > 0 & temp1$DaysPriceChange > 0 , "Long Building(bullish)",
                                         ifelse(temp1$OIPercent > 0 & temp1$DaysPriceChange < 0 , "Short Buildup(bearish)", 
                                                ifelse(temp1$OIPercent < 0 & temp1$DaysPriceChange < 0 , "Longs exiting(bearish)", 
                                                       ifelse(temp1$OIPercent < 0 & temp1$DaysPriceChange > 0 , "Shorts exiting(bullish)", "NA")))) , "NA"))
temp1$STATUS3Day = with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 1, type="lag"),
                                      ifelse(temp1$OI3DayPercent > 0 & temp1$Price3DayPercent > 0 , "Long Building(bullish)",
                                             ifelse(temp1$OI3DayPercent > 0 & temp1$Price3DayPercent < 0 , "Short Buildup(bearish)", 
                                                    ifelse(temp1$OI3DayPercent < 0 & temp1$Price3DayPercent < 0 , "Longs exiting(bearish)", 
                                                           ifelse(temp1$OI3DayPercent < 0 & temp1$Price3DayPercent > 0 , "Shorts exiting(bullish)", "NA")))) , "NA"))

temp1$tailPercent = ifelse (temp1$HIGH >temp1$LOW , (temp1$PRICE - temp1$LOW)/(temp1$HIGH - temp1$LOW), 0) 
temp1$previous3DayStatus<-shift(temp1$STATUS3Day, 1, type="lag")					

temp1$wickPercent = ifelse (temp1$HIGH > temp1$LOW , (temp1$HIGH - temp1$PRICE)/(temp1$HIGH - temp1$LOW), 0) 
temp1$nextdaypriper <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 1, type="lead"),shift(temp1$PricePercent,1,type="lead"),0))
temp1$next3daypriper <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 3, type="lead"),shift(temp1$PricePercent,1,type="lead")+shift(temp1$PricePercent,2,type="lead")+shift(temp1$PricePercent,3,type="lead"),0))

temp1$nxtdayDirection<-ifelse(temp1$nextdaypriper > 0 , 1 , 0)
write.table(temp1,file="merged2.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)


longs =  subset(temp1,ymd(temp1$Date) > (Sys.Date()-15))
longs = subset(longs,( longs$STATUS3Day == "Long Building(bullish)" |   longs$STATUS3Day == "Shorts exiting(bullish)"))
longs =subset(longs,((ymd(longs$reclowDay)>ymd(longs$rechighDay)) |  (ymd(longs$rechighDay)>ymd(longs$Date))))
longs = longs[order(longs$"Date",longs$"SYMBOL"), ];
longs$CONTRACTS <-NULL
longs$Volatility <-NULL
longs$CHG_IN_OI <-NULL



#filter by both status and status3Day as long buildup or shortbuildup with max or min error between -0.7 to 0.7
#above criteria gives stocks which already moved or moving towards middle or upper lines 
#also filter alchemy by same logic 


### Shorts code
# shorts =subset(temp1, (shift(temp1$STATUS3Day, 1, type="lag") == "Long Building(bullish)"  |  shift(temp1$STATUS3Day, 1, type="lag") == "Shorts exiting(bullish)" ))
shorts =  subset(temp1,ymd(temp1$Date) > (Sys.Date()-15))

shorts = subset(shorts,( shorts$STATUS3Day == "Longs exiting(bearish)" |   shorts$STATUS3Day == "Short Buildup(bearish)"))
shorts =subset(shorts,((ymd(shorts$rechighDay)>ymd(shorts$reclowDay)) |  (ymd(shorts$reclowDay)>ymd(shorts$Date))))
shorts = shorts[order(shorts$"Date",shorts$"SYMBOL"), ];


#&& temp1$OI3DayPercent > 1 && temp$"Date" == Sys.Date()-1
#Removing clutter in VPA Sheet
shorts$CONTRACTS <-NULL
shorts$Volatility <-NULL
shorts$CHG_IN_OI <-NULL



merged <- createWorkbook()


Longs <- createSheet(wb=merged, sheetName="Long5OI")
Shorts <- createSheet(wb=merged, sheetName="Short5OI")
SECBAN <-createSheet(wb=merged, sheetName ="SECBAN")


addDataFrame(x=longs, sheet=Longs, row.names=FALSE)
addDataFrame(x=shorts, sheet=Shorts, row.names=FALSE)
addDataFrame(x=data.frame(ban), sheet=SECBAN, row.names=FALSE)
saveWorkbook(merged, "merged.xlsx")




