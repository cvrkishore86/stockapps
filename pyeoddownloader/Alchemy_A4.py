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

	with open(nse_filename, "wb") as handle:
		for data in tqdm(response.iter_content(),disable=False):												#### Make it true to Stop Progress Bar
			handle.write(data)

	shutil.move(nse_filename, nse_dir + nse_filename)


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


#=========================================================================================================================================================#
#==========================================================  INPUTS NEEDED - START  ======================================================================#
#=========================================================================================================================================================#
																							 												  #===========#
																							 												  #===========#
nse_raw_path ="./Download/raw_fut_oi_volt_dlvy/"																							  #===========#
nse_proc_path = "./Download/proc_fut_oi_volt_dlvy/"																							  #===========#
																							 												  #===========#
# start_date = date(2017,5,13) #### YYYY-MM-DD			
# to_date = date(2017,6,1)
# delta_diff = to_date - start_date
																			 		  	  #===========#
datepd = pandas.read_sql('SELECT max(nse_date) FROM eod_data', con=engine)		
datep = datepd["max(nse_date)"][0]																	 		  	  #===========#
start_date = datep + timedelta(days=1)																		 		  	  #===========#

delta_diff = date.today()-start_date 																							 			  #===========#



																							 												  #===========#																							 												  #===========#
																							 												  #===========#
																							 												  #===========#
#=========================================================================================================================================================#
#===========================================================  INPUTS NEEDED - END  =======================================================================#
#=========================================================================================================================================================#





for date_cntr in range(delta_diff.days + 1):							# date_cntr = Date Counter

	dir_create()														# Creates Directories

	nse_tdate = parse(str((start_date + timedelta(days=date_cntr))))	# DATE

	i_nse_date  = int('{dt.day}'.format(dt=nse_tdate))					# INT
	nse_month   = '{dt:%b}'.format(dt=nse_tdate)						# STR
	i_nse_year  = int('{dt:%Y}'.format(dt=nse_tdate))					# INT

	s_nse_date  = str(i_nse_date)										# STR
	s_nse_month = str(nse_month).upper()								# STR
	s_nse_year  = str(i_nse_year)										# STR



	if i_nse_date not in monthtoholiday(s_nse_year + "_" + s_nse_month): # nse_month = Format is JUL - Checks for Holidays
		if i_nse_date <  month_lastdate(s_nse_month): 					 # Checks if its not out of the Range Date

#=================================================================================== Download Links ===========================================================================================================================#

			fut_bhav_link 		= 'https://www.nseindia.com/content/historical/DERIVATIVES/' + s_nse_year 	+ "/" 	+ s_nse_month + "/fo" + s_nse_date.zfill(2) + s_nse_month + s_nse_year + 'bhav.csv.zip'
			fut_cmboi_link	 	= 'https://www.nseindia.com/archives/nsccl/mwpl/combineoi_'  + s_nse_date.zfill(2) 	+ datetime.strptime(nse_month,'%b').strftime('%m') + s_nse_year + '.zip'
			fut_volatility_link = 'https://www.nseindia.com/archives/nsccl/volt/FOVOLT_' 	 + s_nse_date.zfill(2) 	+ datetime.strptime(nse_month,'%b').strftime('%m') + s_nse_year + '.csv'
			eq_tradevol_link 	= 'https://www.nseindia.com/archives/equities/mto/MTO_'		 + s_nse_date.zfill(2) 	+ datetime.strptime(nse_month,'%b').strftime('%m') + s_nse_year + '.DAT'

			year_highlow_link 	= 'https://www.nseindia.com/content/CM_52_wk_High_low.csv'

#=================================================================================== Downloader ===============================================================================================================================#

			nse_downloader (fut_bhav_link,nse_raw_path,str(fut_bhav_link).split('/')[-1])						# Arguments = Future Bhavcopy Link, File Download Path, Filename (These Files Contain Addtional .zip as extn)
			nse_downloader (fut_cmboi_link,nse_raw_path,str(fut_cmboi_link).split('/')[-1])						# Arguments = Future Bhavcopy Link, File Download Path, Filename (These Files Contain Addtional .zip as extn)
			nse_downloader (fut_volatility_link,nse_raw_path,str(fut_volatility_link).split('/')[-1])			# Arguments = Future Bhavcopy Link, File Download Path, Filename (These Files Contain Addtional .zip as extn)
			nse_downloader (eq_tradevol_link,nse_raw_path,str(eq_tradevol_link).split('/')[-1])					# Arguments = Future Bhavcopy Link, File Download Path, Filename (These Files Contain Addtional .zip as extn)
			nse_downloader (year_highlow_link,nse_raw_path,str(year_highlow_link).split('/')[-1])

#===================================================================================== Unzipper ===============================================================================================================================#

			os.chdir(os.path.dirname(os.path.realpath(__file__)))
															# Sets the Default Working Dir.
			unzipper(os.path.abspath('./Download/raw_fut_oi_volt_dlvy/'))										# Unzips the Whole Folder

#===================================================================================== File Names =============================================================================================================================#

			fname_fut_bhav 	= 	basename(os.path.splitext(fut_bhav_link)[0]) 									# Future Bhavcopy Unzipped File Name
			fname_coi 		= 	basename(os.path.splitext(fut_cmboi_link)[0]) + '.csv'							# Combine OI Unzipped Unzipped File Name
			fname_volt		=	basename(fut_volatility_link)													# Volatility File Name
			fname_dlvy		=	basename(os.path.splitext(eq_tradevol_link)[0]) + '.csv'						# Delivery Percentage Unzipped File Name
			
			fname_yearhighlow = 'CM_52_wk_High_low.csv'
#===================================================================================== Convert DAT To CSV =====================================================================================================================#

			print("====================================================================================================================================================================")
			convert_DAT_CSV(nse_raw_path,fname_dlvy)															# DAT to CSV Converter
			os.chdir(os.path.dirname(os.path.realpath(__file__)))												# Sets the Default Working Dir.

#===================================================================================== File Processor =========================================================================================================================#
#============================================================================ Future Bhavcopy Splitter ========================================================================================================================#

			print ("======== Splitting 52 week High Low - %s ========" % (fname_yearhighlow))
			columns = ["SYMBOL","SERIES","YEAR_HIGH","YEAR_HIGH_DT","YEAR_LOW","YEAR_LOW_DT"] # Specifies Column Names
			highlow = pandas.read_csv("D:/code/workspace/NSEOIDownloader/pyeoddownloader/Download/raw_fut_oi_volt_dlvy/CM_52_wk_High_low.csv", sep=',',index_col=False,skiprows=2)                                                               # Pandas Reads
			highlow.columns = columns
			highlow.drop(['SERIES'], axis=1,inplace=True)
			highlow.to_sql(name='stock_data', con=engine, if_exists = 'replace', index=False)

			print ("======== Splitting FnO Bhavcopy  - %s ========" % (fname_fut_bhav))
			columns = ['INSTRUMENT','SYMBOL','EXPIRY_DT','STRIKE_PR','OPTION_TYP','OPEN','HIGH','LOW','CLOSE','SETTLE_PR','CONTRACTS','VAL_INLAKH','OPEN_INT','CHG_IN_OI','TIMESTAMP']	# Specifies Column Names
			bhavcopy = pandas.read_csv(os.path.join(nse_raw_path, fname_fut_bhav), sep=',',usecols=columns,index_col=False)																# Pandas Reads


# ADD SQL RAW Code Here - For Bhavcopy Futures Only
			
			fut_bhavcopy = bhavcopy.copy()
			fut_bhavcopy = fut_bhavcopy[fut_bhavcopy['INSTRUMENT'].str.contains("(?i)FUTSTK")]																							# Data Only with Instrument = FUTSTK
			fut_bhavcopy.drop(['STRIKE_PR', 'OPTION_TYP'], axis=1,inplace=True) ### Comment this if not Required																		# Remove OPTION_TYP and STRIKE_PR
			sequence = ['TIMESTAMP','SYMBOL','INSTRUMENT','EXPIRY_DT','OPEN','HIGH','LOW','CLOSE','SETTLE_PR','CONTRACTS','VAL_INLAKH','OPEN_INT','CHG_IN_OI']							# Rearranged Columns
			fut_bhavcopy = fut_bhavcopy[sequence]																																		# Rearranged Columns

#============================================================================= Volatility Splitter =============================================================================================================================#	

			print ("======== Splitting Volatility - %s ========" % (fname_volt))
			volatility = pandas.read_csv(os.path.join(nse_raw_path, fname_volt), sep=',',index_col=False)																				# Pandas Reads			
			volatility.columns = volatility.columns.str.strip(' ')																														# Splits Any Additional Delimiters

# ADD SQL RAW Code Here - For Volatility Only

			volatility.drop(volatility.columns[[3,4,5,9,10,11]], axis=1,inplace=True)																									# Removed Unwanted Columns
			volatility.columns =['Date','Symbol','EQ_Close','EQ_daily_volt','EQ_Ann_volt','FUT_Close','FUT_daily_volt','FUT_Ann_volt','daily_volt','ann_volt']							# Renamed Columns Names

#============================================================================= Volatility Splitter =============================================================================================================================#	

			print ("======== Splitting Delivery Percentage - %s ========" % (fname_dlvy))
			columns = ['Dump1','Dump2','Symbol','Series','Traded Quantity','Delivery Quantity','Percentage Ratio Delivery To Traded']													# Assigns Columns
			dpct = pandas.read_csv(os.path.join(nse_raw_path, fname_dlvy), sep=',',names=columns,index_col=False)																		# Pandas Reads
			dpct = dpct[dpct['Series'] == 'EQ']																																			# Gets Only EQ Columns
			dpct.drop(['Dump1', 'Dump2','Series'], axis=1,inplace=True) ### Comment this if not Required																				# Dumps Unwanted Columns
			dpct_nm = os.path.splitext(fname_dlvy)[0].replace('MTO_','')																												# Adds Date Column in File.
			dpct.insert(0, 'Date', datetime.strptime(dpct_nm,'%d%m%Y').strftime('%d-%b-%y'))																							# Adds Date Column in File.
			sequence = ['Date','Symbol','Traded Quantity','Delivery Quantity','Percentage Ratio Delivery To Traded']																	# Rearranged Columns
			dpct = dpct[sequence]																																						# Rearranged Columns

#============================================================================= Combine OI Splitter =============================================================================================================================#	

			print ("======== Splitting Combine OI - %s ========" % (fname_coi))
			combineoi = pandas.read_csv(os.path.join(nse_raw_path, fname_coi), sep=',',index_col=False)																					# Pandas Reads
			combineoi.columns = combineoi.columns.str.strip(' ')																														# Removed White Spaces from Columns

# ADD SQL RAW Code Here - For Combine OI Only

			combineoi.drop(['ISIN','Scrip Name'], axis=1,inplace=True) ### Comment this if not Required																					# Drops Unwanted Columns

#================================================================================ Date Finder ==================================================================================================================================#	
			
			cur_date  = str(s_nse_year) + "-" + datetime.strptime(nse_month,'%b').strftime('%m') + "-" + str(i_nse_date).zfill(2)														# Gets Current Date or Download Date
			prev_date = getyestbusiness(cur_date)																																		# Gets Last Date or Last Business Date

			cur_fname = str(i_nse_date).zfill(2) + datetime.strptime(nse_month,'%b').strftime('%m') + s_nse_year + '.csv'																# Current File Name															
			prev_fname = str(datetime.strptime(str(prev_date),'%Y-%m-%d').strftime('%d%m%Y'))+'.csv'																					# Yesterday's File Name


#================================================================================ Save Processed Files. =================================================================================================================================#

			fut_bhavcopy.to_csv			(nse_proc_path	+ "bhavcopy_" 		+ str(cur_fname), sep=',',index=False)																					# Saves Future Bhavcopy File
			volatility.to_csv			(nse_proc_path	+ "volatility_" 	+ str(cur_fname), sep=',',index=False)																					# Saves Volatility File
			dpct.to_csv					(nse_proc_path	+ "deliverypct_" 	+ str(cur_fname), sep=',',index=False)																					# Saves Delivery Percentage File
			combineoi.to_csv			(nse_proc_path	+ "combineoi_" 		+ str(cur_fname), sep=',',index=False)																					# Saves Combine OI File

#================================================================================ Read Processed Files. =================================================================================================================================#

			fut_bhavcopy 	= pandas.read_csv(os.path.join(nse_proc_path, "bhavcopy_" 		+ str(cur_fname)), sep=',',index_col=False,usecols=[1,4,5,6,7,9,10,11,12])								# Reads Future Bhavcopy
			volatility 		= pandas.read_csv(os.path.join(nse_proc_path, "volatility_" 	+ str(cur_fname)), sep=',',index_col=False,usecols=[0,1,2,3,4,5,6,7,8,9])								# Reads Volatility
			dpct 			= pandas.read_csv(os.path.join(nse_proc_path, "deliverypct_" 	+ str(cur_fname)), sep=',',index_col=False,usecols=[1,2,3,4])											# Reads Delivery Percentage
			combineoi 		= pandas.read_csv(os.path.join(nse_proc_path, "combineoi_" 		+ str(cur_fname)), sep=',',index_col=False,usecols=[1,2,3,4])											# Reads Combine OI
			
#================================================================================ Remove Processed Files. ================================================================================================================================#
			
			os.remove(os.path.join(nse_proc_path, "bhavcopy_" 		+ str(cur_fname)))																												# Removed Bhavcopy Future 
			os.remove(os.path.join(nse_proc_path, "volatility_" 	+ str(cur_fname)))																												# Removed Volatility
			os.remove(os.path.join(nse_proc_path, "deliverypct_" 	+ str(cur_fname)))																												# Removed Delivery Percentage
			os.remove(os.path.join(nse_proc_path, "combineoi_" 		+ str(cur_fname)))																												# Removed Combine OI

#===================================================================================== File Merging ======================================================================================================================================#
			fut_OHLC = fut_bhavcopy.copy()

			fut_bhavcopy = fut_bhavcopy.groupby(['SYMBOL'])[['CONTRACTS','VAL_INLAKH','OPEN_INT','CHG_IN_OI']].sum().reset_index()
			fut_OHLC = fut_OHLC.groupby(['SYMBOL'])[['OPEN','HIGH','LOW','CLOSE']].first().reset_index()

			fut_bhavcopy = pandas.merge(fut_OHLC,fut_bhavcopy,	how='inner',		left_on=['SYMBOL'],		right_on=['SYMBOL'])
			df1 = pandas.merge(volatility,fut_bhavcopy,			how='inner',		left_on=['Symbol'],		right_on=['SYMBOL'])
			df2 = pandas.merge(combineoi,dpct,					how='inner',		left_on=['NSE Symbol'],	right_on=['Symbol'])
			merge_cur = pandas.merge(df1,df2,					how='inner',		left_on=['Symbol'],		right_on=['Symbol'])

			print("====================================================================================================================================================================")
			print(cur_date,prev_date,cur_fname,prev_fname)	
			print("====================================================================================================================================================================")

			merge_cur=merge_cur.rename(columns = {'Date_x':'Date'})

			merge_cur.to_csv(nse_proc_path+ str(cur_fname), sep=',',index=False)
			
#======================================================================================== File Comparison ================================================================================================================================#
	
			# if os.path.exists(nse_proc_path):
			if os.path.exists(nse_proc_path + prev_fname):
				print("inside if")
				ipcols = ['Date','Symbol','EQ_Close','EQ_daily_volt','EQ_Ann_volt','FUT_Close','FUT_daily_volt','FUT_Ann_volt','daily_volt','ann_volt','SYMBOL','OPEN','HIGH','LOW','CLOSE','CONTRACTS','VAL_INLAKH','OPEN_INT','CHG_IN_OI','NSE Symbol','MWPL','Open Interest','Limit for Next Day','Traded Quantity','Delivery Quantity','Percentage Ratio Delivery To Traded']
				merge_prev = pandas.read_csv(nse_proc_path + prev_fname, sep=',',index_col=False,usecols =ipcols)

				difference_pd = merge_cur.copy()
				difference = pandas.merge(merge_cur,merge_prev, how='left',on=['Symbol'])
			
				
				difference_pd["EQ_CHANGE"] 			= ((difference['EQ_Close_x'] 		- difference['EQ_Close_y'])		/difference['EQ_Close_y'])		*100
				difference_pd["Fut_CHANGE"]			= ((difference['FUT_Close_x'] 		- difference['FUT_Close_y'])	/difference['FUT_Close_y'])		*100

				difference_pd["CONTRACTS_CHANGE"] 	= ((difference['CONTRACTS_x'] 		- difference['CONTRACTS_y'])	/difference['CONTRACTS_y'])		*100
				difference_pd["VAL_INLAKH_CHANGE"] 	= ((difference['VAL_INLAKH_x'] 		- difference['VAL_INLAKH_y'])	/difference['VAL_INLAKH_y'])	*100
				difference_pd["OPEN_INT_CHANGE"]	= ((difference['OPEN_INT_x'] 		- difference['OPEN_INT_y'])		/difference['OPEN_INT_y'])		*100
				difference_pd["TOT_OI_CHANGE"] 		= ((difference['Open Interest_x'] 	- difference['Open Interest_y'])/difference['Open Interest_y'])	*100

				difference_pd["MWPL_pct"] 			= 100-(((difference['MWPL_x'] - difference['Open Interest_x'])/difference['MWPL_x'])*100)

				difference_pd['ban_status']  =		  difference['Limit for Next Day_x'].map({'No Fresh Positions': "Banned"})
				difference_pd['ban_status']  = 		  difference_pd['ban_status'].fillna("Open")

				difference_pd['handle_up'] 	 = 		  (numpy.ceil(difference['FUT_Close_x'] / 100.0) * 100) - difference['FUT_Close_x']
				difference_pd['handle_down'] = 		  difference['FUT_Close_x'] - (numpy.floor(difference['FUT_Close_x'] / 100.0) * 100)

				difference_pd['Date'] = pandas.to_datetime(difference_pd['Date']).apply(lambda x:x.strftime('%Y-%m-%d'))

				difference_pd.drop(difference_pd.columns[[10,19]], axis=1,inplace=True)
				#difference_pd.to_csv('./Archive/reports/' + cur_fname,index=False)
				difference_pd.columns = ['nse_date','nse_symbol','nse_eq_close','nse_eq_daily_volt','nse_eq_ann_volt','nse_fut_close','nse_fut_daily_volt','nse_fut_ann_volt','nse_daily_volt','nse_ann_volt',
										'nse_open','nse_high','nse_low','nse_close','nse_contracts','nse_val_inlakh','nse_open_int','nse_chg_in_oi','nse_mwpl','nse_open_interest','nse_limit_for_next_day','nse_traded_quantity',
										'nse_delivery_quantity','nse_pct_delivery_to_traded','nse_eq_change','nse_fut_change','nse_contracts_change','nse_val_inlakh_change','nse_open_int_change','nse_tot_oi_change','nse_mwpl_pct',
										'nse_ban_status','nse_handle_up','nse_handle_down']
				
				print ("======== Sending Data to MySQL Server... Stay Tuned!! ========")
				difference_pd.to_sql(name='eod_data', con=engine, if_exists = 'append', index=False)

				difference_pd.to_csv('./Archive/reports/' + 'AlchemyReport.csv',index=False,mode='a',header=False)


			else:
				#shutil.rmtree('./Download/raw_fut_oi_volt_dlvy')
				quit()

			
			#shutil.rmtree('./Download/raw_fut_oi_volt_dlvy')









'''
CREATE TABLE `eod_data` (
  `nse_date` date DEFAULT NULL,
  `nse_symbol` varchar(45) DEFAULT NULL,
  `nse_eq_close` float DEFAULT NULL,
  `nse_eq_daily_volt` float DEFAULT NULL,
  `nse_eq_ann_volt` float DEFAULT NULL,
  `nse_fut_close` float DEFAULT NULL,
  `nse_fut_daily_volt` float DEFAULT NULL,
  `nse_fut_ann_volt` float DEFAULT NULL,
  `nse_daily_volt` float DEFAULT NULL,
  `nse_ann_volt` float DEFAULT NULL,
  `nse_open` float DEFAULT NULL,
  `nse_high` float DEFAULT NULL,
  `nse_low` float DEFAULT NULL,
  `nse_close` float DEFAULT NULL,
  `nse_contracts` float DEFAULT NULL,
  `nse_val_inlakh` float DEFAULT NULL,
  `nse_open_int` float DEFAULT NULL,
  `nse_chg_in_oi` float DEFAULT NULL,
  `nse_mwpl` float DEFAULT NULL,
  `nse_open_interest` float DEFAULT NULL,
  `nse_limit_for_next_day` varchar(100) DEFAULT NULL,
  `nse_traded_quantity` float DEFAULT NULL,
  `nse_delivery_quantity` float DEFAULT NULL,
  `nse_pct_delivery_to_traded` float DEFAULT NULL,
  `nse_eq_change` float DEFAULT NULL,
  `nse_fut_change` float DEFAULT NULL,
  `nse_contracts_change` float DEFAULT NULL,
  `nse_val_inlakh_change` float DEFAULT NULL,
  `nse_open_int_change` float DEFAULT NULL,
  `nse_tot_oi_change` float DEFAULT NULL,
  `nse_mwpl_pct` float DEFAULT NULL,
  `nse_ban_status` varchar(10) DEFAULT NULL,
  `nse_handle_up` float DEFAULT NULL,
  `nse_handle_down` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='End of the Day Data'
'''