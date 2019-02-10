library('lubridate')
library('MASS')
temp1 = read.csv('D:/code/workspace/NSEOIDownloader/merged2.csv', header=TRUE, stringsAsFactors=FALSE)
temp1<-subset(temp1, temp1$SYMBOL=="ITC")
lda.fit = lda(nxtdayDirection~OI3DayPercent+Price3DayPercent+tailPercent+rstandard, data=temp1, subset=ymd(Date) < Sys.Date()-60 )

temp1.sample = subset(temp1, ymd(Date) > Sys.Date()-60 & ymd(Date) < Sys.Date()-1)
lda.pred = predict(lda.fit, temp1.sample)
temp1.sample$class = lda.pred$class
lda.fit
table(lda.pred$class,temp1.sample$nxtdayDirection)

mean(lda.pred$class==temp1.sample$nxtdayDirection)