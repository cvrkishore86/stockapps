library(httr)
library(reshape2)

# library(dplyr)
library(data.table)
library(lubridate)
# library(zoo)
#Define Working Directory, where files would be saved
setwd('D:/code/workspace/NSEOIDownloader/temp3')

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
			# print("inside file exists")
			# write.table(temp,file=filename,sep=",", eol="\n", row.names = FALSE, col.names = FALSE, append=TRUE)
			write.table(temp2,file="consolidated.csv",sep=",", eol="\n", row.names = FALSE, col.names = FALSE, append=TRUE)
			# write.table(idx,file="consolidated.csv",sep=",", eol="\n", row.names = FALSE, col.names = FALSE, append=TRUE)
			
		}else
		{
			# print("inside file doesnt exists")
			# write.table(temp,file=filename,sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)
			write.table(temp2,file="consolidated.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=TRUE)
			# write.table(idx,file="consolidated.csv",sep=",", eol="\n", row.names = FALSE, col.names = FALSE, append=TRUE)
			
		}


		#Print Progress
		#print(paste (myDate, "-Done!", endDate-myDate, "left"))
	}, error=function(err){
		print(err)
	}
	)
 	myDate <- myDate+1
 	print(paste(myDate, "Next Record"))
}

	
