library(httr)
# library(dplyr)
library(data.table)
library(lubridate)
library(RCurl)
startDate = Sys.Date()-10;
filenameDate = paste(as.character(startDate, "%d%m%Y"))


DeliveryData <- fread(paste("https://www.nseindia.com/archives/equities/mto/MTO_",filenameDate,".DAT", sep=""))
DeliveryData<-subset(DeliveryData,DeliveryData$V4=="EQ")
DeliveryData<-subset(DeliveryData,select=c("V3","V7"))
colnames(DeliveryData) <- c("SYMBOL","DeliveryPer")

GET(paste("https://www.nseindia.com/archives/nsccl/mwpl/combineoi_",filenameDate,".zip", sep=""), user_agent("Mozilla/5.0"), write_disk(paste("combineoi_18082017",".zip",sep=""), overwrite = TRUE))
unzip(paste("combineoi_18082017",".zip",sep=""))
combineOI <- read.csv("combineoi_18082017.csv", sep = ",") 
combineOI <- subset(combineOI, select=c("Date","NSE.Symbol","MWPL","Open.Interest","Limit.for.Next.Day"))
colnames(combineOI) <- c("Date","SYMBOL","MWPL","OPEN_INT","NextDayLimit")
OIDelivery <- merge(combineOI,DeliveryData)
OIDelivery$Date <-ymd(as.Date(OIDelivery$Date, format = "%d-%b-%Y"))



fofilenameDate = paste(as.character(startDate, "%y%m%d"), ".csv", sep = "")

fodownloadfilename=paste("fo", toupper(as.character(startDate, "%d%b%Y")), "bhav.csv", sep = "")

#https://www.nseindia.com/content/historical/DERIVATIVES/2015/FEB/fo02FEB2015bhav.csv.zip
#Generate URL https://www.nseindia.com/content/historical/DERIVATIVES/2017/MAY/fo30MAY2017bhav.csv.zip
myURL = paste("https://www.nseindia.com/content/historical/DERIVATIVES/", as.character(startDate, "%Y"), "/", toupper(as.character(startDate, "%b")), "/", fodownloadfilename, ".zip", sep = "")
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
fobhavoi <- subset(fobhavoi, (fobhavoi$INSTRUMENT=="FUTSTK"))
fobhavoi<- subset(fobhavoi, fobhavoi$EXPIRY_DT == min(fobhavoi$EXPIRY_DT))
fobhavoi$INSTRUMENT<-NULL
priceOIDelivery<-merge(fobhavoi,OIDelivery)  