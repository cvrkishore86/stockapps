library(httr)
# library(dplyr)
library(data.table)
library(lubridate)
library(RCurl)
# library(zoo)
#Define Working Directory, where files would be saved
setwd('D:/code/workspace/NSEOIDownloader/temp6')
#https://www.nseindia.com/archives/nsccl/mwpl/combineoi_18082017.zip
#https://www.nseindia.com/archives/nsccl/volt/FOVOLT_17082017.csv  -- volatality
#https://www.nseindia.com/content/nsccl/fao_participant_oi_17082017.csv - next
#https://www.nseindia.com/content/nsccl/fao_participant_vol_17082017.csv - next
#https://www.nseindia.com/archives/equities/mto/MTO_18082017.DAT - take percentage
#Define start and end dates, and convert them into date format
maxdate = read.csv('D:/code/workspace/NSEOIDownloader/temp6/consolidated.csv', header=T, check.names = FALSE, stringsAsFactors = FALSE)


startDate = ymd(tail(maxdate$Date, n=1))+1;
endDate = Sys.Date();



#work with date, month, year for which data has to be extracted
myDate = startDate
zippedFile <- tempfile() 
#Delete temp file - Bhavcopy
junk <- dir(pattern = "fo")
file.remove(junk)
junk <- dir(pattern = "combine")
file.remove(junk)
filename="consolidated.csv"
while (myDate <= endDate){
  filenameDate = paste(as.character(myDate, "%d%m%Y")) 
  #retrieve Zipped file
  deliveryurl = paste("https://www.nseindia.com/archives/equities/mto/MTO_",filenameDate,".DAT", sep="")
  print(http_status(GET(deliveryurl)))
  x <- http_status(GET(deliveryurl))
  
  if (x$category == "Success") {
  DeliveryData <- fread(deliveryurl)
  DeliveryData<-subset(DeliveryData,DeliveryData$V4=="EQ")
  DeliveryData<-subset(DeliveryData,select=c("V3","V7"))
  colnames(DeliveryData) <- c("SYMBOL","DeliveryPer")
  
    
    
    GET(paste("https://www.nseindia.com/archives/nsccl/mwpl/combineoi_",filenameDate,".zip", sep=""), user_agent("Mozilla/5.0"), write_disk(paste("combineoi_",filenameDate,".zip",sep=""), overwrite = TRUE))
    unzip(paste("combineoi_",filenameDate,".zip",sep=""))
    combineOI <- read.csv(paste("combineoi_",filenameDate,".csv", sep = "")) 
    combineOI <- subset(combineOI, select=c("Date","NSE.Symbol","MWPL","Open.Interest","Limit.for.Next.Day"))
    colnames(combineOI) <- c("Date","SYMBOL","MWPL","OPEN_INT","NextDayLimit")
    OIDelivery <- merge(combineOI,DeliveryData)
    OIDelivery$Date <-ymd(as.Date(OIDelivery$Date, format = "%d-%b-%Y"))
    if (year(OIDelivery$Date)  < year(myDate)) {
      #bad fix might fail year end
      year(OIDelivery$Date) <- year(myDate);
    }
    
    
    fofilenameDate = paste(as.character(myDate, "%y%m%d"), ".csv", sep = "")
    
    fodownloadfilename=paste("fo", toupper(as.character(myDate, "%d%b%Y")), "bhav.csv", sep = "")
    
    #https://www.nseindia.com/content/historical/DERIVATIVES/2015/FEB/fo02FEB2015bhav.csv.zip
    #Generate URL https://www.nseindia.com/content/historical/DERIVATIVES/2017/MAY/fo30MAY2017bhav.csv.zip
    myURL = paste("https://www.nseindia.com/content/historical/DERIVATIVES/", as.character(myDate, "%Y"), "/", toupper(as.character(myDate, "%b")), "/", fodownloadfilename, ".zip", sep = "")
    #28-10-2014: Fix for '403 Forbidden'
    #download.file(myURL,zippedFile, quiet=TRUE, mode="wb",cacheOK=TRUE)
    GET(myURL, user_agent("Mozilla/5.0"), write_disk(paste(fodownloadfilename,".zip",sep=""),overwrite = TRUE))
    
    
    #Unzip file and save it in temp 
    #28-10-2014: Fix for '403 Forbidden'
    fobhavoi <- read.csv(unzip(paste(fodownloadfilename,".zip",sep="")), sep = ",") 
    
    #Reorder Columns and Select relevant columns
    fobhavoi<-subset(fobhavoi,select=c("TIMESTAMP","INSTRUMENT","SYMBOL","EXPIRY_DT","OPEN","HIGH","LOW","CLOSE"))
    colnames(fobhavoi)[colnames(fobhavoi)=="TIMESTAMP"] <- "Date"
    fobhavoi$Date <- ymd(as.Date(fobhavoi$"Date", format = "%d-%b-%Y"))
    fobhavoi$EXPIRY_DT <- ymd(as.Date(fobhavoi$"EXPIRY_DT", format = "%d-%b-%Y"))
    
    fobhavoi <- subset(fobhavoi, (fobhavoi$INSTRUMENT=="FUTSTK") | (fobhavoi$SYMBOL=="NIFTY" & fobhavoi$INSTRUMENT == "FUTIDX"))
    fobhavoi<- subset(fobhavoi, fobhavoi$EXPIRY_DT == min(fobhavoi$EXPIRY_DT))
    fobhavoi$INSTRUMENT<-NULL
    
    priceOIDelivery<-merge(fobhavoi,OIDelivery, all.x = TRUE)  
    # temp2 <- merge(temp2, idx)
    
    #Write the csv in Monthly file
    if (file.exists(filename))
    {
      write.table(priceOIDelivery,file="consolidated.csv",sep=",", eol="\n", row.names = FALSE, col.names = FALSE, append=TRUE)

    }else
    {
      write.table(priceOIDelivery,file="consolidated.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)

      
    }
    
    
  }
  
  myDate <- myDate+1
  print(paste(myDate, "Next Record"))
}
junk <- dir(pattern = "fo")
file.remove(junk)
junk <- dir(pattern = "combine")
file.remove(junk)
mydata1 = read.csv('D:/code/workspace/NSEOIDownloader/temp6/consolidated.csv', header=T, check.names = FALSE)





temp1 = mydata1[order(mydata1$SYMBOL, ymd(mydata1$Date)),];

SYMB<-unique(temp1$"SYMBOL")
symbtemp<-data.frame(SYMB)
colnames(symbtemp)<-c("SYMBOL")



# symbtemp <- read.csv("beta.csv");

nifty50 <- subset(temp1, temp1$"SYMBOL" =="NIFTY")
fitnifty <- lm(nifty50$CLOSE~ymd(nifty50$"Date"))
niftyslope <- coef(fitnifty)[2]
niftyslope
length(SYMB)
for (k in 1:length(SYMB)){
  tryCatch({
    btemp<- subset(temp1, temp1$"SYMBOL" == SYMB[k])
    btemp$CHG_IN_OI<- NULL  
    fitbtemp <- lm(btemp$CLOSE~ymd(btemp$"Date"))
    btemp20<- subset(btemp, ymd(btemp$"Date") > (Sys.Date()-20))
    btemp6m <- subset(btemp, ymd(btemp$"Date") > (Sys.Date()-90))
    fitbtemp6m <- lm(btemp6m$CLOSE~ymd(btemp6m$"Date"))
    t<-btemp20[order(btemp20$CLOSE), ];
    highs <-tail(t, n=1)
    lows <- head(t, n=1)
    
    if(symbtemp$SYMBOL[k] == SYMB[k]){
      
      
      symbtemp$rechighDay[k] <- format(highs$Date,format= "%y-%m-%d")
      # symbtemp$rechigh[k]<- highs$CLOSE
      symbtemp$reclowDay[k] <- format(lows$Date, format="%y-%m-%d")
      # symbtemp$reclow[k] <-lows$CLOSE
      symbtemp$slope[k] <- coef(fitbtemp)[2]
      symbtemp$slope3m[k] <- coef(fitbtemp6m)[2]
      symbtemp$beta[k] <- coef(fitbtemp)[2]/niftyslope
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





temp1 = consolidated[order(consolidated$SYMBOL, ymd(consolidated$Date)),];
temp1<-subset(temp1, (ymd(temp1$"Date") > Sys.Date()-90))

colnames(temp1)[colnames(temp1)=="CLOSE"] <- "CLOSE"



temp1$DaysPriceChange <- temp1$CLOSE - temp1$OPEN;
temp1$OPEN_INT <- as.numeric(as.character(temp1$OPEN_INT))
temp1$OIPercent <- with(temp1 , ((temp1$OPEN_INT - shift(temp1$OPEN_INT, 1L, type=c('lag')))/shift(temp1$OPEN_INT, 1, type='lag'))*100)



#Removing clutter in VPA Sheet


temp1$PricePercent <- with(temp1, ((temp1$CLOSE - shift(temp1$CLOSE, 1, type='lag'))/shift(temp1$CLOSE, 1, type='lag'))*100)
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

write.table(temp1,file="merged2.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)



# 
# longs =  subset(temp1,ymd(temp1$Date) > (Sys.Date()-15))
# longs = subset(longs,( longs$STATUS3Day == "Long Building(bullish)" |   longs$STATUS3Day == "Shorts exiting(bullish)"))
# longs =subset(longs,((ymd(longs$reclowDay)>ymd(longs$rechighDay)) |  (ymd(longs$rechighDay)>ymd(longs$Date))))
# longs = longs[order(longs$"Date",longs$"SYMBOL"), ];
# longs$CONTRACTS <-NULL
# longs$Volatility <-NULL
# longs$CHG_IN_OI <-NULL
# 
# 
# 
# #filter by both status and status3Day as long buildup or shortbuildup with max or min error between -0.7 to 0.7
# #above criteria gives stocks which already moved or moving towards middle or upper lines 
# #also filter alchemy by same logic 
# 
# 
# ### Shorts code
# shorts =  subset(temp1,ymd(temp1$Date) > (Sys.Date()-15))
# 
# shorts = subset(shorts,( shorts$STATUS3Day == "Longs exiting(bearish)" |   shorts$STATUS3Day == "Short Buildup(bearish)"))
# shorts =subset(shorts,((ymd(shorts$rechighDay)>ymd(shorts$reclowDay)) |  (ymd(shorts$reclowDay)>ymd(shorts$Date))))
# shorts = shorts[order(shorts$"Date",shorts$"SYMBOL"), ];
# 
# 
# #&& temp1$OI3DayPercent > 1 && temp$"Date" == Sys.Date()-1
# #Removing clutter in VPA Sheet
# shorts$CONTRACTS <-NULL
# shorts$Volatility <-NULL
# shorts$CHG_IN_OI <-NULL
# 
# 
# 
# merged <- createWorkbook()
# 
# 
# Longs <- createSheet(wb=merged, sheetName="Long5OI")
# Shorts <- createSheet(wb=merged, sheetName="Short5OI")
# SECBAN <-createSheet(wb=merged, sheetName ="SECBAN")
# 
# 
# addDataFrame(x=longs, sheet=Longs, row.names=FALSE)
# addDataFrame(x=shorts, sheet=Shorts, row.names=FALSE)
# addDataFrame(x=data.frame(ban), sheet=SECBAN, row.names=FALSE)
# saveWorkbook(merged, "merged.xlsx")
# 
# 
# 
# 
