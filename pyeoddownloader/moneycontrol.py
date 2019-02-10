import pandas
from bs4 import BeautifulSoup
import requests
import os


if not os.path.exists('./MMT/BSE/'):
	os.makedirs('./MMT/BSE/')

if not os.path.exists('./MMT/NSE/'):
	os.makedirs('./MMT/NSE/')


df_mmt = pandas.read_csv('./MMT_Book.csv',index_col=0)

df_mmt_stocks = pandas.DataFrame(columns=['Stocks'])

for row in df_mmt.itertuples():


	df_iifl_stocks = []
	stocks = []
	mmt_request = requests.get(row[1])

	soup = BeautifulSoup(mmt_request.text, "html.parser")


	for ul in soup.findAll(class_="brdrgtgry"):
		for link in ul.find_all('a',class_='bl_12', href=True):
			stocks.append(str(link.text).strip())


	
	df_mmt_stocks = pandas.DataFrame({'Stocks':stocks})

	file_name = str(row[0]).split("\\",2)[2]

	df_mmt_stocks.to_csv('./' + str(row[0]).split("\\",1)[0] +  '/' + str(row[0]).split("\\",2)[1] + '/' + file_name+'.csv', index=False, header=False)