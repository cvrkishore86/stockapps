from __future__ import print_function
from datetime import date, timedelta,datetime
import urllib, requests
import os,shutil,glob
from tqdm import tqdm
import pandas
from os.path import basename
from dateutil.parser import parse
import fnmatch, zipfile
import datetime as dt
import numpy
import pymysql
from sqlalchemy import types, create_engine

engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)

def nse_downloader(nse_url,nse_dir,nse_filename):
	response = requests.get(nse_url, stream=False)
	
	if response.status_code != 404:
		with open(nse_filename, "wb") as handle:
			for data in tqdm(response.iter_content(),disable=False):												#### Make it true to Stop Progress Bar
				handle.write(data)

		shutil.move(nse_filename, nse_dir + nse_filename)
	return (response.status_code != 404)


def unzipper(source):
	
	# os.chdir(source) # change directory from working dir to dir with files
	for item in os.listdir(source): # loop through items in dir
		if item.endswith('.zip'): # check for ".zip" extension

			file_name = source+'\\'+item
			print("--------------------file_name", file_name)
			zip_ref = zipfile.ZipFile(file_name) # create zipfile object

			zip_ref.extractall(source) # extract file to dir
			zip_ref.close() # close file
			os.remove(file_name) # delete zipped file

# https://www.nseindia.com/content/historical/EQUITIES/2017/OCT/cm03OCT2017bhav.csv.zip
nse_raw_path ="./Download/eqbhav/"
start_date = date(2016,1,6)
# delta_diff = date.today()-start_date 	
delta_diff = date.today() - start_date

for date_cntr in range(delta_diff.days + 1):							# date_cntr = Date Counter



	nse_tdate = parse(str((start_date + timedelta(days=date_cntr))))	# DATE

	i_nse_date  = int('{dt.day}'.format(dt=nse_tdate))					# INT
	nse_month   = '{dt:%b}'.format(dt=nse_tdate)						# STR
	i_nse_year  = int('{dt:%Y}'.format(dt=nse_tdate))					# INT

	s_nse_date  = str(i_nse_date)										# STR
	s_nse_month = str(nse_month).upper()								# STR
	s_nse_year  = str(i_nse_year)										# STR


	eq_bhav_link 		= 'https://www.nseindia.com/content/historical/EQUITIES/' + s_nse_year 	+ "/" 	+ s_nse_month + "/cm" + s_nse_date.zfill(2) + s_nse_month + s_nse_year + 'bhav.csv.zip'

	filedownloaded = nse_downloader(eq_bhav_link,nse_raw_path,str(eq_bhav_link).split('/')[-1])
	if filedownloaded:
		unzipper(os.path.abspath(nse_raw_path))
		fname_eq_bhav 	= 	basename(os.path.splitext(eq_bhav_link)[0]) 
		# columns = ['SYMBOL','OPEN', 'HIGH', 'LOW','CLOSE','TOTTRDQTY','TOTRDVAL','TIMESTAMP','TOTALTRADES']	# Specifies Column Names
		eqbhavcopy = pandas.read_csv(os.path.join(nse_raw_path, fname_eq_bhav), sep=',',index_col=False)
		eqbhav = eqbhavcopy.loc[:, ['SYMBOL','TIMESTAMP','OPEN', 'HIGH','LOW','CLOSE','TOTTRDQTY','TOTTRDVAL','TOTALTRADES']]
		eqbhav.to_sql(name='eq_eod_data', con=engine, if_exists = 'append', index=False)


