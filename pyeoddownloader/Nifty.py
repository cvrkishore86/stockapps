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

def monthtoholiday(argument):
	month_dict = {
					'2017_JAN' : [1,8,15,22,29,7,14,21,28,26],
					'2017_FEB' : [5,12,19,26,4,11,18,25,24],
					'2017_MAR' : [5,12,19,26,4,11,18,25,13],
					'2017_APR' : [2,9,16,23,30,1,8,15,22,29,4,14],
					'2017_MAY' : [7,14,21,28,6,13,20,27,1],
					'2017_JUN' : [4,11,18,25,3,10,17,24,26],
					'2017_JUL' : [2,9,16,23,30,1,8,15,22,29],
					'2017_AUG' : [6,13,20,27,5,12,19,26,15,25],
					'2017_SEP' : [3,10,17,24,2,9,16,23,30,],
					'2017_OCT' : [1,8,15,22,29,7,14,21,28,2,19,20],
					'2017_NOV' : [5,12,19,26,4,11,18,25],
					'2017_DEC' : [3,10,17,24,31,2,9,16,23,30,25],
					'2016_JAN' : [3,10,17,24,31,2,9,16,23,30,26],
					'2016_FEB' : [7,14,21,28,6,13,20,27],
					'2016_MAR' : [6,13,20,27,5,12,19,26,7,24,25],
					'2016_APR' : [3,10,17,24,2,9,16,23,30,14,15,19],
					'2016_MAY' : [1,8,15,22,29,7,14,21,28],
					'2016_JUN' : [5,12,19,26,4,11,18,25],
					'2016_JUL' : [3,10,17,24,31,2,9,16,23,30,6],
					'2016_AUG' : [7,14,21,28,6,13,20,27,15],
					'2016_SEP' : [4,11,18,25,3,10,17,24,5,13],
					'2016_OCT' : [2,9,16,23,30,1,8,15,22,29,11,12,31],
					'2016_NOV' : [6,13,20,27,5,12,19,26,14],
					'2016_DEC' : [4,11,18,25,3,10,17,24,31]
	}
	return month_dict.get(argument, "nothing")

def month_lastdate(argument):
    month_lastdate_dict = {
					'JAN' : 32,
					'FEB' : 29,
					'MAR' : 32,
					'APR' : 31,
					'MAY' : 32,
					'JUN' : 31,
					'JUL' : 32,
					'AUG' : 32,
					'SEP' : 31,
					'OCT' : 32,
					'NOV' : 31,
					'DEC' : 32
    }
    return month_lastdate_dict.get(argument, "nothing")

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
#=====================================================  DAT to CSV Converter - START  ====================================================================#
#=========================================================================================================================================================#

def convert_DAT_CSV(datpath, datname):
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	try:
	    os.remove(datname)
	except OSError:
	    pass

	print ("======== Converting Equity Delivery Percentage DAT File To CSV - %s ========" % (datname))

	with open(datpath + os.path.splitext(datname)[0] + '.DAT','r+') as f:
		csv_dpname = os.path.splitext(datname)[0] + ".csv"
		with open(datpath + csv_dpname ,'w+') as f1:
			next(f) # skip header line
			next(f) # skip header line
			next(f) # skip header line
			next(f) # skip header line
			f1.write("Dump1,Dump2,Symbol,Series,Traded Quantity,Delivery Quantity,Percentage Ratio Delivery To Traded\n")
			for line in f:
				f1.write(line)
#=========================================================================================================================================================#
#=====================================================  DAT to CSV Converter - END  ======================================================================#
#=========================================================================================================================================================#


#=========================================================================================================================================================#
#========================================================  Get last business day - START  ================================================================#
#=========================================================================================================================================================#

def getyestbusiness(nse_fulldate):
	nse_fulldate = datetime.strptime(str(nse_fulldate), "%Y-%m-%d") - dt.timedelta(days=1)
	busdate = int('{dt.day}'.format(dt=nse_fulldate))
	busmonth = '{dt:%b}'.format(dt=nse_fulldate)
	busyear = int('{dt:%Y}'.format(dt=nse_fulldate))
	holiday = str(busyear) + "_" + str(busmonth).upper()

	return nse_fulldate.date() if busdate < 32 and busdate not in monthtoholiday(holiday) else getyestbusiness(nse_fulldate.date())


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
	nse_raw_path ="./Download/niftytemp/"
																								 												  #===========#
	start_date = date(2016,1,1) #### YYYY-MM-DD			
	# to_date = date(2015,12,18)
	# delta_diff = to_date - start_date
																				 		  	  #===========#
	# start_date = datep + timedelta(days=1)																		 		  	  #===========#

	delta_diff = date.today()-start_date 																							 			  #===========#



																								 												  #===========#																							 												  #===========#
																								 												  #===========#
																								 												  #===========#
	#=========================================================================================================================================================#
	#===========================================================  INPUTS NEEDED - END  =======================================================================#
	#=========================================================================================================================================================#



	allsig = pandas.DataFrame(columns=['SYMBOL','TIMESTAMP','OPEN', 'HIGH','LOW','CLOSE'])

	for date_cntr in range(delta_diff.days + 1):							# date_cntr = Date Counter

		dir_create()														# Creates Directories

		nse_tdate = parse(str((start_date + timedelta(days=date_cntr))))	# DATE

		i_nse_date  = int('{dt.day}'.format(dt=nse_tdate))					# INT
		nse_month   = '{dt:%b}'.format(dt=nse_tdate)						# STR
		i_nse_year  = int('{dt:%Y}'.format(dt=nse_tdate))					# INT

		s_nse_date  = str(i_nse_date)										# STR
		s_nse_month = str(nse_month).upper()								# STR
		s_nse_year  = str(i_nse_year)										# STR



		# if i_nse_date not in monthtoholiday(s_nse_year + "_" + s_nse_month): # nse_month = Format is JUL - Checks for Holidays
		# 	if i_nse_date <  month_lastdate(s_nse_month): 					 # Checks if its not out of the Range Date

	#=================================================================================== Download Links ===========================================================================================================================#

		fut_bhav_link 		= 'https://www.nseindia.com/content/historical/DERIVATIVES/' + s_nse_year 	+ "/" 	+ s_nse_month + "/fo" + s_nse_date.zfill(2) + s_nse_month + s_nse_year + 'bhav.csv.zip'
	# 	fut_cmboi_link	 	= 'https://www.nseindia.com/archives/nsccl/mwpl/combineoi_'  + s_nse_date.zfill(2) 	+ datetime.strptime(nse_month,'%b').strftime('%m') + s_nse_year + '.zip'
	# 	fut_volatility_link = 'https://www.nseindia.com/archives/nsccl/volt/FOVOLT_' 	 + s_nse_date.zfill(2) 	+ datetime.strptime(nse_month,'%b').strftime('%m') + s_nse_year + '.csv'
	# 	eq_tradevol_link 	= 'https://www.nseindia.com/archives/equities/mto/MTO_'		 + s_nse_date.zfill(2) 	+ datetime.strptime(nse_month,'%b').strftime('%m') + s_nse_year + '.DAT'

	# 	year_highlow_link 	= 'https://www.nseindia.com/content/CM_52_wk_High_low.csv'
	# 	eq_bhav_link 		= 'https://www.nseindia.com/content/historical/EQUITIES/' + s_nse_year 	+ "/" 	+ s_nse_month + "/cm" + s_nse_date.zfill(2) + s_nse_month + s_nse_year + 'bhav.csv.zip'
	# #=================================================================================== Downloader ===============================================================================================================================#
		os.chdir(os.path.dirname(os.path.realpath(__file__)))
															# Sets the Default Working Dir.
			# unzipper(os.path.abspath('./Download/niftytemp/'))										# Unzips the Whole Folder

		#===================================================================================== File Names =============================================================================================================================#

		fname_fut_bhav 	= 	basename(os.path.splitext(fut_bhav_link)[0])
		# filedownloaded =nse_downloader (fut_bhav_link,nse_raw_path,str(fut_bhav_link).split('/')[-1])						# Arguments = Future Bhavcopy Link, File Download Path, Filename (These Files Contain Addtional .zip as extn)
		filedownloaded = os.path.isfile(os.path.join(nse_raw_path, fname_fut_bhav)) 
		# nse_downloader (fut_cmboi_link,nse_raw_path,str(fut_cmboi_link).split('/')[-1])						# Arguments = Future Bhavcopy Link, File Download Path, Filename (These Files Contain Addtional .zip as extn)
		# nse_downloader (fut_volatility_link,nse_raw_path,str(fut_volatility_link).split('/')[-1])			# Arguments = Future Bhavcopy Link, File Download Path, Filename (These Files Contain Addtional .zip as extn)
		# nse_downloader (eq_tradevol_link,nse_raw_path,str(eq_tradevol_link).split('/')[-1])					# Arguments = Future Bhavcopy Link, File Download Path, Filename (These Files Contain Addtional .zip as extn)
		# nse_downloader (year_highlow_link,nse_raw_path,str(year_highlow_link).split('/')[-1])
		 # nse_downloader(eq_bhav_link,nse_raw_path,str(eq_bhav_link).split('/')[-1])
		if filedownloaded:
	#===================================================================================== Unzipper ===============================================================================================================================#

			 									# Future Bhavcopy Unzipped File Name
			# fname_coi 		= 	basename(os.path.splitext(fut_cmboi_link)[0]) + '.csv'							# Combine OI Unzipped Unzipped File Name
			# fname_volt		=	basename(fut_volatility_link)													# Volatility File Name
			# fname_dlvy		=	basename(os.path.splitext(eq_tradevol_link)[0]) + '.csv'						# Delivery Percentage Unzipped File Name
			
			# fname_yearhighlow = 'CM_52_wk_High_low.csv'
		#===================================================================================== Convert DAT To CSV =====================================================================================================================#

			print("====================================================================================================================================================================")
			# convert_DAT_CSV(nse_raw_path,fname_dlvy)															# DAT to CSV Converter
			os.chdir(os.path.dirname(os.path.realpath(__file__)))												# Sets the Default Working Dir.

		#===================================================================================== File Processor =========================================================================================================================#
		#============================================================================ Future Bhavcopy Splitter ========================================================================================================================#

			# print ("======== Splitting 52 week High Low - %s ========" % (fname_yearhighlow))
			# columns = ["SYMBOL","SERIES","YEAR_HIGH","YEAR_HIGH_DT","YEAR_LOW","YEAR_LOW_DT"] # Specifies Column Names
			# highlow = pandas.read_csv("D:/code/workspace/NSEOIDownloader/pyeoddownloader/Download/raw_fut_oi_volt_dlvy/CM_52_wk_High_low.csv", sep=',',index_col=False,skiprows=2)                                                               # Pandas Reads
			# highlow.columns = columns
			# highlow.drop(['SERIES'], axis=1,inplace=True)
			# highlow.to_sql(name='stock_data', con=engine, if_exists = 'replace', index=False)

			print ("======== Splitting FnO Bhavcopy  - %s ========" % (fname_fut_bhav))
			columns = ['INSTRUMENT','SYMBOL','EXPIRY_DT','STRIKE_PR','OPTION_TYP','OPEN','HIGH','LOW','CLOSE','SETTLE_PR','CONTRACTS','VAL_INLAKH','OPEN_INT','CHG_IN_OI','TIMESTAMP']	# Specifies Column Names

			bhavcopy = pandas.read_csv(os.path.join(nse_raw_path, fname_fut_bhav), sep=',',usecols=columns,index_col=False)																# Pandas Reads


		# ADD SQL RAW Code Here - For Bhavcopy Futures Only
			
			niftyIndex = bhavcopy.copy()
			niftyIndex = niftyIndex[niftyIndex['INSTRUMENT'].str.contains("(?i)FUTIDX")]																							# Data Only with Instrument = FUTSTK
			niftyIndex.drop(['STRIKE_PR', 'OPTION_TYP'], axis=1,inplace=True) ### Comment this if not Required																		# Remove OPTION_TYP and STRIKE_PR
			sequence = ['SYMBOL','TIMESTAMP','OPEN','HIGH','LOW','CLOSE']							# Rearranged Columns
			niftyIndex = niftyIndex[sequence]			
			Index_OHLC = niftyIndex.groupby(['SYMBOL'])[['TIMESTAMP','OPEN','HIGH','LOW','CLOSE']].first().reset_index()
			allsig = allsig.append(fut_OHLC, ignore_index=True)			
			
	
	allsig.to_sql(name='eq_eod_data', con=engine, if_exists = 'append', index=False)



				
				#shutil.rmtree('./Download/raw_fut_oi_volt_dlvy')

if __name__ == '__main__':
    execute()








