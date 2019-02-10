library('quantmod')
library('tseries')
library('rugarch')
library('fGarch')
library('forecast')


getSymbols('VEDL.NS', from='2016-01-31', to='2017-08-16')

VEDL.NS = na.omit(VEDL.NS)

VEDL=VEDL.NS[,6] # adjusted closing price


data=(log(VEDL)) 

data <- data[!is.na(data)]

plot(data,type='l')



VEDLfinal.aic <- Inf
VEDLfinal.order <- c(0,0,0)
for (p in 1:3) for (d in 0:1) for (q in 1:3) {
  VEDLcurrent.aic <- AIC(arima(data, order=c(p, d, q)))
  if (VEDLcurrent.aic < VEDLfinal.aic) {
    VEDLfinal.aic <- VEDLcurrent.aic
    VEDLfinal.order <- c(p, d, q)
    VEDLfinal.arima <- arima(data, order=VEDLfinal.order)
  }
}

fit3=VEDLfinal.arima

summary(fit3)

# One step forecast 


#Generate  l-step forecast, and plot of forecast:

VEDL.forecast=forecast(fit3,1,level=95)


VEDL.forecast=as.data.frame(VEDL.forecast)


 # arima forecast

VEDL.price = exp(VEDL.forecast)#Price of VEDL


#Need to add GARCH to this

