library(httr)
library(reshape2)
library(xlsx)
# library(dplyr)
library(data.table)
library(lubridate)
# library(zoo)
#Define Working Directory, where files would be saved
setwd('D:/code/workspace/NSEOIDownloader/temp6')
#https://www.nseindia.com/archives/nsccl/mwpl/combineoi_18082017.zip
#https://www.nseindia.com/archives/nsccl/volt/FOVOLT_17082017.csv  -- volatality
#https://www.nseindia.com/content/nsccl/fao_participant_oi_17082017.csv - next
#https://www.nseindia.com/content/nsccl/fao_participant_vol_17082017.csv - next
#https://www.nseindia.com/archives/equities/mto/MTO_18082017.DAT - take percentage
#Define start and end dates, and convert them into date format
startDate = Sys.Date()-1;
endDate = Sys.Date();


#work with date, month, year for which data has to be extracted
myDate = startDate
zippedFile <- tempfile() 
#Delete temp file - Bhavcopy
junk <- dir(pattern = "fo")
file.remove(junk)
while (myDate <= endDate){
  filenameDate = paste(as.character(myDate, "%y%m%d"), ".csv", sep = "")
  filename=paste("consolidated.csv", sep = "")
  downloadfilename=paste("fo", toupper(as.character(myDate, "%d%b%Y")), "bhav.csv", sep = "")
  temp =""
  #https://www.nseindia.com/content/historical/DERIVATIVES/2015/FEB/fo02FEB2015bhav.csv.zip
  #Generate URL https://www.nseindia.com/content/historical/DERIVATIVES/2017/MAY/fo30MAY2017bhav.csv.zip
  myURL = paste("https://www.nseindia.com/content/historical/DERIVATIVES/", as.character(myDate, "%Y"), "/", toupper(as.character(myDate, "%b")), "/", downloadfilename, ".zip", sep = "")
  
  #retrieve Zipped file
  tryCatch({
    #Download Zipped File
    
    #28-10-2014: Fix for '403 Forbidden'
    #download.file(myURL,zippedFile, quiet=TRUE, mode="wb",cacheOK=TRUE)
    GET(myURL, user_agent("Mozilla/5.0"), write_disk(paste(downloadfilename,".zip",sep="")))
    
    
    #Unzip file and save it in temp 
    #28-10-2014: Fix for '403 Forbidden'
    temp <- read.csv(unzip(paste(downloadfilename,".zip",sep="")), sep = ",") 
    
    
    #Reorder Columns and Select relevant columns
    temp<-subset(temp,select=c("TIMESTAMP","INSTRUMENT","SYMBOL","EXPIRY_DT","OPEN","HIGH","LOW","CLOSE","OPEN_INT","CHG_IN_OI"))
    colnames(temp)[colnames(temp)=="TIMESTAMP"] <- "Date"
    temp$Date <- ymd(as.Date(temp$"Date", format = "%d-%b-%Y"))
    temp$EXPIRY_DT <- ymd(as.Date(temp$"EXPIRY_DT", format = "%d-%b-%Y"))
    temp <- subset(temp, (temp$INSTRUMENT=="FUTSTK") | (temp$SYMBOL=="NIFTY" & temp$INSTRUMENT == "FUTIDX"))
    oi <- melt(temp, measure.vars = "OPEN_INT")
    oiout <- dcast(oi, Date + SYMBOL ~ variable, fun.aggregate = sum)
    choi <- melt(temp, measure.vars = "CHG_IN_OI")
    choiout <- dcast(choi, Date + SYMBOL ~ variable, fun.aggregate = sum)
    
    temp1<- subset(temp, temp$EXPIRY_DT == min(temp$EXPIRY_DT))
    temp1$CHG_IN_OI <-NULL
    temp1$OPEN_INT <-NULL
    
    tempOI <-merge(choiout,oiout)
    temp2<-merge(temp1, tempOI)
    # temp2 <- merge(temp2, idx)
    
    #Write the csv in Monthly file
    if (file.exists(filename))
    {
      write.table(temp2,file="consolidated.csv",sep=",", eol="\n", row.names = FALSE, col.names = FALSE, append=TRUE)

    }else
    {
      write.table(temp2,file="consolidated.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=TRUE)

    }
    
    
  }, error=function(err){
    print(err)
  }
  )
  myDate <- myDate+1
  print(paste(myDate, "Next Record"))
}

mydata1 = read.csv('D:/code/workspace/NSEOIDownloader/temp6/consolidated.csv', header=T, check.names = FALSE)

mydata1$INSTRUMENT <-NULL

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
    btemp6m <- subset(btemp, ymd(btemp$"Date") > (Sys.Date()-90))
    fitbtemp6m <- lm(btemp6m$PRICE~ymd(btemp6m$"Date"))
    t<-btemp20[order(btemp20$PRICE), ];
    highs <-tail(t, n=1)
    lows <- head(t, n=1)
    
    if(symbtemp$SYMBOL[k] == SYMB[k]){
      
      
      symbtemp$rechighDay[k] <- format(highs$Date,format= "%y-%m-%d")
      # symbtemp$rechigh[k]<- highs$PRICE
      symbtemp$reclowDay[k] <- format(lows$Date, format="%y-%m-%d")
      # symbtemp$reclow[k] <-lows$PRICE
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




GET("https://www.nseindia.com/content/fo/fo_secban.csv", user_agent("Mozilla/5.0"), write_disk("fo_secban.csv", overwrite = TRUE))
ban <-read.csv("fo_secban.csv");

temp1 = consolidated[order(consolidated$"SYMBOL", ymd(consolidated$"Date")),];
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




