
setwd('D:/code/workspace/NSEOIDownloader')
library(data.table)
library(xlsx) #load the package

mydata1 = read.csv('D:/code/workspace/NSEOIDownloader/OIConsolidated.csv', header=T)
mydata2 = read.csv('D:/code/workspace/NSEOIDownloader/foConsolidated.csv', header=T)
mydata3 = read.csv('D:/code/workspace/NSEOIDownloader/fovoltConsolidated.csv', header=T)
colnames(mydata1)[colnames(mydata1)=="NSE.Open.Interest"] <- "NSEOI"




myfulldata = merge(mydata1, mydata2)
withvolume = merge( myfulldata, mydata3)


temp = subset(withvolume, select=c("Date","SYMBOL","Scrip.Name","NSEOI","EXPIRY_DT","CONTRACTS","Volatility","OPEN","HIGH","LOW","CLOSE") )
colnames(temp)[colnames(temp)=="CLOSE"] <- "PRICE"
temp1 = temp[order(temp$"SYMBOL", as.Date(temp$"Date", format = "%d-%b-%y")),];


# temp1$OICHANGE <- temp1$"NSEOI" - shift(temp1$"NSEOI")
# temp1$PRICECHANGE <- temp1$"PRICE" - shift(temp1$"PRICE")

write.xlsx2(temp1, file = "merged.xlsx",
        sheetName = "FUTData", row.names = FALSE)

# print(temp)


#OLD Formula
#STATUS=IF(B2=B1,IF((AND(D2>D1,H2>H1)),"Long Building",IF((AND(D2>D1,H2<H1)),"Short Buildup(bearish)",IF((AND(D2<D1,H2<H1)),"Longs exiting",IF((AND(D2<D1,H2>H1)),"SHorts Exiting","Fail")))),"NA")
#OICHANGE=IF(J2="NA","NA", ((D2-D1)/D1)*100)
#PRICECHANGE=IF(J2="NA","NA", ((H2-H1)/H1)*100)
#OIDelta =IF(J2="NA","NA", K2-K1)


# STATUS	OICHANGE	PRICECHange	OIDelta	PriceDelta	DaysPriceChange
# =IF(B2=B1,IF((AND(D2>D1,K2>K1)),"Long Building",IF((AND(D2>D1,K2<K1)),"Short Buildup(bearish)",IF((AND(D2<D1,K2<K1)),"Longs exiting",IF((AND(D2<D1,K2>K1)),"Shorts Exiting","Fail")))),"NA")	=IF(L2="NA","NA", ((D2-D1)/D1)*100)	=IF(L2="NA","NA", ((K2-K1)/K1)*100)	=IF(L1="NA","NA", M2-M1)	=IF(L1="NA","NA", K2-K1)	=K2-H2
