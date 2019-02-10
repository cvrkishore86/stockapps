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

#=========================================================================================================================================================#
#======================================================  Create Directories - START ======================================================================#
#=========================================================================================================================================================#

def dir_create():

	# Download Directories -: Will be used to Download Bare NSE Files.
	if not os.path.exists("./Download/raw_fut_oi_volt_dlvy/"):
		os.makedirs("./Download/raw_fut_oi_volt_dlvy/")				#### Fut Bhavcopy, CombineOI, Volatiliy, Delivery
	
	if not os.path.exists("./Download/proc_fut_oi_volt_dlvy/"):
		os.makedirs("./Download/proc_fut_oi_volt_dlvy/")		


	# Processed Directories -: Will be used to Download Bare NSE Files.
	if not os.path.exists("./Archive/reports/"):					
		os.makedirs("./Archive/reports/")

#=========================================================================================================================================================#
#======================================================  Create Directories - END ========================================================================#
#=========================================================================================================================================================#

#=========================================================================================================================================================#
#==========================================================  Downloader - START ==========================================================================#
#=========================================================================================================================================================#


def nse_downloader(nse_url,nse_dir,nse_filename):
	response = requests.get(nse_url, stream=False)
	
	if response.status_code != 404:
		with open(nse_filename, "wb") as handle:
			for data in tqdm(response.iter_content(),disable=False):												#### Make it true to Stop Progress Bar
				handle.write(data)

		shutil.move(nse_filename, nse_dir + nse_filename)
	return (response.status_code != 404)


#=========================================================================================================================================================#
#============================================================  Downloader - END ==========================================================================#
#=========================================================================================================================================================#

#=========================================================================================================================================================#
#======================================================  Holidays & Months - START =======================================================================#
#=========================================================================================================================================================#


#=========================================================================================================================================================#
#======================================================  Holidays & Months - END =========================================================================#
#=========================================================================================================================================================#


#=========================================================================================================================================================#
#========================================================  Unzipper - START  =============================================================================#
#=========================================================================================================================================================#

def unzipper(source):
	os.chdir(source) # change directory from working dir to dir with files
	for item in os.listdir(source): # loop through items in dir
		if item.endswith('.zip'): # check for ".zip" extension

			file_name = os.path.abspath(item) # get full path of files
			print("--------------------file_name", file_name)
			zip_ref = zipfile.ZipFile(file_name) # create zipfile object

			zip_ref.extractall(source) # extract file to dir
			zip_ref.close() # close file
			os.remove(file_name) # delete zipped file


#=========================================================================================================================================================#
#==========================================================  Unzipper - END  =============================================================================#
#=========================================================================================================================================================#




#=========================================================================================================================================================#
#========================================================  Get last business day - START  ================================================================#
#=========================================================================================================================================================#



#=========================================================================================================================================================#
#========================================================  Get last business day - END  ==================================================================#
#=========================================================================================================================================================#

engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)

def execute():
	#=========================================================================================================================================================#
	#==========================================================  INPUTS NEEDED - START  ======================================================================#
	#=========================================================================================================================================================#
																								 												  #===========#
																								 												  #===========#
	nse_raw_path ="./Download/raw_fut_oi_volt_dlvy/"
	nse_eq_path ="./Download/eqbhav/"																							  #===========#
	nse_proc_path = "./Download/proc_fut_oi_volt_dlvy/"																							  #===========#
																								 												  #===========#
	# start_date = date(2015,12,15) #### YYYY-MM-DD			
	# to_date = date(2015,12,18)
	# delta_diff = to_date - start_date
																				 		  	  #===========#
	datepd = pandas.read_sql('SELECT max(STR_TO_DATE(TIMESTAMP, "%%d-%%M-%%Y")) FROM eq_eod_data where SYMBOL="NIFTY"', con=engine)		
	
	datep = datepd['max(STR_TO_DATE(TIMESTAMP, "%d-%M-%Y"))'][0]																	 		  	  #===========#
	start_date = datetime.strptime(datep,'%Y-%m-%d')  + timedelta(days=1)
	print(start_date)																		 		  	  #===========#

	delta_diff = date.today()-start_date.date() 																							 			  #===========#



																								 												  #===========#																							 												  #===========#
																								 												  #===========#
																								 												  #===========#
	#=========================================================================================================================================================#
	#===========================================================  INPUTS NEEDED - END  =======================================================================#
	#=========================================================================================================================================================#





	for date_cntr in range(delta_diff.days + 1):							# date_cntr = Date Counter

		dir_create()														# Creates Directories

		nse_tdate = parse(str((start_date + timedelta(days=date_cntr))))	# DATE

		i_TIMESTAMP  = int('{dt.day}'.format(dt=nse_tdate))					# INT
		nse_month   = '{dt:%b}'.format(dt=nse_tdate)						# STR
		i_nse_year  = int('{dt:%Y}'.format(dt=nse_tdate))					# INT

		s_TIMESTAMP  = str(i_TIMESTAMP)										# STR
		s_nse_month = str(nse_month).upper()								# STR
		s_nse_year  = str(i_nse_year)										# STR



		# if i_TIMESTAMP not in monthtoholiday(s_nse_year + "_" + s_nse_month): # nse_month = Format is JUL - Checks for Holidays
		# 	if i_TIMESTAMP <  month_lastdate(s_nse_month): 					 # Checks if its not out of the Range Date

	#=================================================================================== Download Links ===========================================================================================================================#
		fut_bhav_link 		= 'https://www.nseindia.com/content/historical/DERIVATIVES/' + s_nse_year 	+ "/" 	+ s_nse_month + "/fo" + s_TIMESTAMP.zfill(2) + s_nse_month + s_nse_year + 'bhav.csv.zip'
		eq_bhav_link 		= 'https://www.nseindia.com/content/historical/EQUITIES/' + s_nse_year 	+ "/" 	+ s_nse_month + "/cm" + s_TIMESTAMP.zfill(2) + s_nse_month + s_nse_year + 'bhav.csv.zip'
	#=================================================================================== Downloader ===============================================================================================================================#
		fname_fut_bhav 	= 	basename(os.path.splitext(fut_bhav_link)[0])
		nse_downloader (fut_bhav_link,nse_raw_path,str(fut_bhav_link).split('/')[-1])						# Arguments = Future Bhavcopy Link, File Download Path, Filename (These Files Contain Addtional .zip as extn)
		filedownloaded = nse_downloader(eq_bhav_link,nse_raw_path,str(eq_bhav_link).split('/')[-1])
		if filedownloaded:
	#===================================================================================== Unzipper ===============================================================================================================================#

			os.chdir(os.path.dirname(os.path.realpath(__file__)))
															# Sets the Default Working Dir.
			unzipper(os.path.abspath('./Download/raw_fut_oi_volt_dlvy/'))										# Unzips the Whole Folder

		#===================================================================================== File Names =============================================================================================================================#

			os.chdir(os.path.dirname(os.path.realpath(__file__)))												# Sets the Default Working Dir.

		#===================================================================================== File Processor =========================================================================================================================#
		#============================================================================ Future Bhavcopy Splitter ========================================================================================================================#
			fname_eq_bhav 	= 	basename(os.path.splitext(eq_bhav_link)[0]) 
			columns = ['SYMBOL','OPEN', 'HIGH', 'LOW','CLOSE','TOTTRDQTY','TOTRDVAL','TIMESTAMP','TOTALTRADES']	# Specifies Column Names

			eqbhavcopy = pandas.read_csv(os.path.join(nse_raw_path, fname_eq_bhav), sep=',',index_col=False)
			eqbhavcopy = eqbhavcopy[eqbhavcopy['SERIES']== 'EQ']
			eqbhav = eqbhavcopy.loc[:, ['SYMBOL','TIMESTAMP','OPEN', 'HIGH','LOW','CLOSE','TOTTRDQTY','TOTTRDVAL','TOTALTRADES']]
			eqbhav.to_sql(name='eq_eod_data', con=engine, if_exists = 'append', index=False)


			print ("======== Splitting FnO Bhavcopy  - %s ========" % (fname_fut_bhav))
			columns = ['INSTRUMENT','SYMBOL','EXPIRY_DT','STRIKE_PR','OPTION_TYP','OPEN','HIGH','LOW','CLOSE','SETTLE_PR','CONTRACTS','VAL_INLAKH','OPEN_INT','CHG_IN_OI','TIMESTAMP']	# Specifies Column Names
			bhavcopy = pandas.read_csv(os.path.join(nse_raw_path, fname_fut_bhav), sep=',',usecols=columns,index_col=False)																# Pandas Reads
																															# Rearranged Columns

			niftyIndex = bhavcopy.copy()
			niftyIndex = niftyIndex[niftyIndex['INSTRUMENT'].str.contains("(?i)FUTIDX")]																							# Data Only with Instrument = FUTSTK
			niftyIndex.drop(['STRIKE_PR', 'OPTION_TYP'], axis=1,inplace=True) ### Comment this if not Required																		# Remove OPTION_TYP and STRIKE_PR
			sequence = ['SYMBOL','TIMESTAMP','OPEN','HIGH','LOW','CLOSE']							# Rearranged Columns
			niftyIndex = niftyIndex[sequence]			
			Index_OHLC = niftyIndex.groupby(['SYMBOL'])[['TIMESTAMP','OPEN','HIGH','LOW','CLOSE']].first().reset_index()
			Index_OHLC.to_sql(name='eq_eod_data', con=engine, if_exists = 'append', index=False)



				
				#shutil.rmtree('./Download/raw_fut_oi_volt_dlvy')

if __name__ == '__main__':
    execute()








