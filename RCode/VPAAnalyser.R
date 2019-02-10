  library(lubridate)
  setwd('D:/code/workspace/NSEOIDownloader/temp4')
  betadata <- read.csv('D:/code/workspace/NSEOIDownloader/temp3/beta.csv', header=T);
  stocks <- subset(betadata, !is.na(betadata$rechighDay))
  stocks <- stocks[!grepl("&", stocks$SYMBOL), ]
  # SYMB<-unique(temp1$"SYMBOL")  
  symbols = unique(stocks$"SYMBOL") 
  symbol = "CIPLA"  
  noDays = 15  
  interval = 60 #Seconds  
  
  unix2POSIXct <- function (time)  structure(time, class = c("POSIXt", "POSIXct"))  

  computeData <- function(fileName) {
  
  data = read.table(fileName,sep=",",col.names=c("DATE1","CLOSE","VOLUME"),fill=TRUE)  
  data$DATE = 0  
  data$TIME = 0  
  data$datetime=0
  data$CloseRound=0
  for (i in 8:nrow(data))  
  {  
    if(i==8 || substr(as.vector((data$DATE1[i])),1,1) == "a")  
    {  
      tempDate = unix2POSIXct(as.numeric(substr(as.vector((data$DATE1[i])),2,nchar(as.vector((data$DATE1[i]))))))    
      
      data$DATE[i] = as.numeric(format(tempDate,format="%Y%m%d"))  
      data$TIME[i] = as.numeric(format(tempDate,format="%H%M"))  
      data$datetime[i] = format(tempDate,format="%Y-%m-%d %H:%M")
      data$CloseRound[i] =  round(as.numeric(as.vector(data$CLOSE[i])),0)
    } else {  
      tempDate1 = tempDate + as.numeric(as.vector(data$DATE1[i]))*interval   
      data$datetime[i] = format(tempDate1,format="%Y-%m-%d %H:%M")
      data$DATE[i] = as.numeric(format(tempDate1,format="%Y%m%d"))  
      data$TIME[i] = as.numeric(format(tempDate1,format="%H%M"))  
      data$CloseRound[i] = round(as.numeric(as.vector(data$CLOSE[i])),0)
    }   
  }  
  data1=as.data.frame(data)  
  data1=(data1[data1$TIME>915 & data1$TIME<=1530,])  
  
  finalData = data.frame(DATE= data1$DATE, CLOSE=data1$CLOSE, CLOSERound=data1$CloseRound,VOLUME=data1$VOLUME,DateTime=data1$datetime)  
  return (finalData)
  }
  
 vpadata = matrix(ncol=2,nrow=length(symbols))
 
  for (k in 1:length(symbols)){
    symbol = symbols[k]
  fileName = paste(symbol,"1.csv",sep="")  
  
  # download.file(paste("http://www.google.com/finance/getprices?q=",symbol,"&x=NSE&i=",interval,"&p=",noDays,"d&f=d,c,v,t",sep=""), fileName)  
  
  computeddata = computeData(fileName)
  
  # beginDate=min(computeddata$DATE)
  # 
  # as.integer(as.POSIXct(Sys.Date()-60))
  
  vpa = subset(computeddata, select=c(CLOSERound, VOLUME))
  
  vpa1 = aggregate(as.numeric(VOLUME) ~ as.numeric(CLOSERound), vpa, sum)
  colnames(vpa1)[1] = "CloseRound"
  colnames(vpa1)[2] = "Volume"
  
  vpa1 = vpa1[order(-vpa1$Volume), ];
  vpadata[k,] = c(paste(symbol),paste(head(vpa1$CloseRound,10),collapse=" "))
  
  }
 
 write.table(vpadata,file="vpa.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)