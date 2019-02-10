
  library('ggplot2')
  library('forecast')
  library('tseries')
  library('lubridate')
  temp1 = read.csv('D:/code/workspace/NSEOIDownloader/merged2.csv', header=TRUE, stringsAsFactors=FALSE)
  
  
  
    # nifty50 <- subset(temp1,(temp1$STATUS3Day== "Long Building(bullish)" & temp1$previous3DayStatus == "Long Building(bullish)"))
  # nifty50 <- subset(temp1,(temp1$STATUS3Day== "Longs exiting(bearish)" & temp1$previous3DayStatus == "Longs exiting(bearish)"))
  temp1$todayDirection=ifelse(temp1$PricePercent > 0 , 1 , 0)
  nifty50<-subset(temp1, temp1$SYMBOL=="GRASIM")
  nifty <-subset(nifty50, (ymd(nifty50$Date) < Sys.Date()-60 ))
  niftytest <-subset(nifty50, (ymd(nifty50$Date) > Sys.Date()-60 & ymd(nifty50$Date) < Sys.Date()-1))
  
  fitnifty <- glm(nxtdayDirection~OPEN_INT*todayDirection, nifty,family = binomial)
  
  fitnifty.probs=predict(fitnifty, newdata = niftytest, type="response")
  
  fitnifty.pred=ifelse(fitnifty.probs>0.5,1,0)
  niftytest$pred = fitnifty.pred
  niftytest$probs = fitnifty.probs
  summary(fitnifty)
  table(fitnifty.pred,niftytest$nxtdayDirection)
  
  mean(fitnifty.pred == niftytest$nxtdayDirection)
  