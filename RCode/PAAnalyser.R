setwd('D:/code/workspace/NSEOIDownloader/temp2')
  library('tseries')
  library('lubridate')
  library(data.table)
  temp = read.csv('D:/code/workspace/NSEOIDownloader/temp2/c16end.csv', header=T, check.names = FALSE)
 
 SYMB<-unique(temp$"SYMBOL")
 
 for (k in 1:length(SYMB)){
   t <- subset(temp , temp$SYMBOL ==  SYMB[k])
   for (l in 1:length(t$Date)){
     
     x<-t[l,]
     if(l>15) {
       s=l-15
       y<-t[s:l,]
       
       y<-y[order(y$CLOSE), ]
       highs <-tail(y, n=1)
       lows <- head(y, n=1)
       x$rechighDate<-highs$Date
       x$rechighCLOSE<-highs$CLOSE
       x$reclowDate<-lows$Date
       x$reclowCLOSE<-lows$CLOSE
       z<-t[1:l,]
       fitbtemp <- lm(z$CLOSE~mdy(z$Date))
       x$slope<- coef(fitbtemp)[2]
       x$minrsid<- min(rstandard(fitbtemp))
       x$maxrsid<- max(rstandard(fitbtemp))
       x$rstandard<-rstandard(fitbtemp)[l]
       
     } else{
       x$rechighDate<-NA
       x$rechighCLOSE<-NA
       x$reclowDate<-NA
       x$reclowCLOSE<-NA
       x$slope<- NA
       x$minrsid<-NA
       x$maxrsid<- NA
       x$rstandard<-NA
     }
     if(k==1 && l==1){
     write.table(x,file="PA.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)
     } else {
       write.table(x,file="PA.csv",sep=",", eol="\n", row.names = FALSE, col.names = FALSE, append=TRUE)
     }
   }
 }
 
 temp1 = read.csv('D:/code/workspace/NSEOIDownloader/temp2/PA.csv', header=T, check.names = FALSE)
 temp1$DaysCLOSEChange <- temp1$CLOSE - temp1$OPEN;
 temp1$OIPercent <- with(temp1 , ((temp1$OPEN_INT - shift(temp1$OPEN_INT, 1, type='lag'))/shift(temp1$OPEN_INT, 1, type='lag'))*100)
 
 temp1$CLOSEPercent <- with(temp1, ((temp1$CLOSE - shift(temp1$CLOSE, 1, type='lag'))/shift(temp1$CLOSE, 1, type='lag'))*100)
 temp1$OI3DayPercent <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 2, type="lag"),(temp1$OIPercent + shift(temp1$OIPercent, 1, type='lag')  + shift(temp1$OIPercent, 2, type='lag')), 0))
 temp1$CLOSE3DayPercent <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 2, type="lag"),(temp1$CLOSEPercent + shift(temp1$CLOSEPercent, 1, type='lag')  + shift(temp1$CLOSEPercent, 2, type='lag')), 0))
 temp1$STATUS = with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 1, type="lag"),
                                   ifelse(temp1$OIPercent > 0 & temp1$DaysCLOSEChange > 0 , "Long Building(bullish)",
                                          ifelse(temp1$OIPercent > 0 & temp1$DaysCLOSEChange < 0 , "Short Buildup(bearish)", 
                                                 ifelse(temp1$OIPercent < 0 & temp1$DaysCLOSEChange < 0 , "Longs exiting(bearish)", 
                                                        ifelse(temp1$OIPercent < 0 & temp1$DaysCLOSEChange > 0 , "Shorts exiting(bullish)", "NA")))) , "NA"))
 temp1$STATUS3Day = with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 1, type="lag"),
                                       ifelse(temp1$OI3DayPercent > 0 & temp1$CLOSE3DayPercent > 0 , "Long Building(bullish)",
                                              ifelse(temp1$OI3DayPercent > 0 & temp1$CLOSE3DayPercent < 0 , "Short Buildup(bearish)", 
                                                     ifelse(temp1$OI3DayPercent < 0 & temp1$CLOSE3DayPercent < 0 , "Longs exiting(bearish)", 
                                                            ifelse(temp1$OI3DayPercent < 0 & temp1$CLOSE3DayPercent > 0 , "Shorts exiting(bullish)", "NA")))) , "NA"))
 
 temp1$tailPercent = ifelse (temp1$HIGH >temp1$LOW , (temp1$CLOSE - temp1$LOW)/(temp1$HIGH - temp1$LOW), 0) 
 temp1$previous3DayStatus<-shift(temp1$STATUS3Day, 1, type="lag")					
 
 temp1$wickPercent = ifelse (temp1$HIGH > temp1$LOW , (temp1$HIGH - temp1$CLOSE)/(temp1$HIGH - temp1$LOW), 0) 
 temp1$nextdaypriper <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 1, type="lead"),shift(temp1$CLOSEPercent,1,type="lead"),0))
 temp1$next3daypriper <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 3, type="lead"),shift(temp1$CLOSEPercent,1,type="lead")+shift(temp1$CLOSEPercent,2,type="lead")+shift(temp1$CLOSEPercent,3,type="lead"),0))
 temp1$next5daypriper <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 5, type="lead"),shift(temp1$CLOSEPercent,1,type="lead")+shift(temp1$CLOSEPercent,2,type="lead")+shift(temp1$CLOSEPercent,3,type="lead")+shift(temp1$CLOSEPercent,4,type="lead")+shift(temp1$CLOSEPercent,5,type="lead"),0))
 temp1$next7daypriper <- with(temp1, ifelse(temp1$SYMBOL == shift(temp1$SYMBOL, 7, type="lead"),shift(temp1$CLOSEPercent,1,type="lead")+shift(temp1$CLOSEPercent,2,type="lead")+shift(temp1$CLOSEPercent,3,type="lead")+shift(temp1$CLOSEPercent,4,type="lead")+shift(temp1$CLOSEPercent,5,type="lead")+shift(temp1$CLOSEPercent,6,type="lead")+shift(temp1$CLOSEPercent,7,type="lead"),0))
 temp1$minerror <-temp1$rstandard/temp1$minrsid;
 temp1$maxerror <-temp1$rstandard/temp1$maxrsid;
 
 temp1$nxtdayDirection<-ifelse(temp1$nextdaypriper > 0 , 1 , 0)
 
 write.table(temp1,file="PAMerged.csv",sep=",", eol="\n", row.names = FALSE, col.names = TRUE, append=FALSE)

 
 