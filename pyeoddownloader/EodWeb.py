from flask import Flask , request,jsonify
import pandas as pd
from sqlalchemy import types, create_engine, Table,MetaData, column, select, update, insert,delete
from datetime import date, timedelta,datetime
import datetime as dt
import SentimentAnalysis
import numpy as np
import DailyEq
import MomentumPicks
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('mysql+pymysql://root:mysql@localhost/stocks', echo=False)
metadata = MetaData(bind=engine)
my_portfolio = Table('my_portfolio', metadata, autoload=True)

@app.route("/eoddata")
def show_tables():
   
    return render_template('stockdata.html' );

@app.route('/api/stockdata', methods=['GET'])
def get_stockdata():
	
	data = pd.read_sql('SELECT * FROM stock_data', con=engine)
	
	data.index.name=None
	return jsonify({'data': data.to_json(orient='records')})



@app.route('/api/momentumscan', methods=['GET'])
def get_momentum():
	
	data = pd.read_sql('SELECT e.*, eq.CLOSE,eq.HIGH,eq.LOW FROM  stocks.momentum_scan e, stocks.eq_eod_data eq where  e.symbol=eq.SYMBOL and STR_TO_DATE(eq.TIMESTAMP, "%%d-%%M-%%Y") = (SELECT MAX(STR_TO_DATE(eq1.TIMESTAMP, "%%d-%%M-%%Y")) FROM stocks.eq_eod_data eq1)', con=engine)
	data = data.sort_values('timestamp', ascending=False).drop_duplicates('symbol')

	data['timestamp'] =  data['timestamp'].apply( lambda x: x.strftime('%Y-%m-%d')  )

	data['updownratio'] = data['greendays']/data['reddays']
	data.rename(columns = {'close_50_ema_xd_close_100_ema':'deathcross'}, inplace = True)
	data.rename(columns = {'close_50_ema_xu_close_100_ema':'goldcross'}, inplace = True)
	data.index.name=None
	return jsonify({'data': data.to_json(orient='records')})

@app.route('/api/loaddata', methods=['GET'])
def get_loaddata():
	
	DailyEq.execute();
	return jsonify({'success': True})

@app.route('/api/generatemomentum', methods=['GET'])
def generatemomentumpicks():
	
	MomentumPicks.generateMomentumPicks(50,100)
	return jsonify({'success': True})

@app.route('/api/lastloadedtime', methods=['GET'])
def get_lastloadedtime():
	ts = pd.read_sql('SELECT max(STR_TO_DATE(TIMESTAMP, "%%d-%%M-%%Y")) FROM eq_eod_data', con=engine)
	x = ts.loc[0, 'max(STR_TO_DATE(TIMESTAMP, "%d-%M-%Y"))'] 
	
	return x;

@app.route('/api/momentumlastloadedtime', methods=['GET'])
def get_momentumlastloadedtime():
	ts = pd.read_sql('SELECT max(timestamp) from momentum_scan', con=engine)
	x = ts.loc[0, 'max(timestamp)'] 
	
	return x.strftime('%d-%m-%Y');

@app.route('/api/movingaverage', methods=['GET'])
def get_movingaverage():
	
			# print(len(allsig))
	return jsonify({'data': True})

@app.route('/api/add/portfoliostock', methods=['GET'])
def add_portfolio_stock():
	symbol = request.args.get("symbol") ;
	buydate = request.args.get("buydate") ;
	buyprice = request.args.get("buyprice") ;
	quantity = request.args.get("quantity") ;
	comments = request.args.get("comments") ;

	buyholdsell = request.args.get("buyholdsell") ;
	print(comments, buyholdsell)
	Session = sessionmaker(bind=engine)
	session = Session()
	i = insert(my_portfolio)	
	i = i.values({"symb": symbol, "buydate": datetime.strptime(buydate, "%d-%m-%Y").date(),"buyprice":buyprice,"quantity":quantity, "comments":comments,"buyholdsell":buyholdsell})
	session.execute(i)
	session.commit()
			# print(len(allsig))
	return jsonify({'data': True})

@app.route('/api/delete/portfoliostock', methods=['GET'])
def remove_portfolio_stock():
	symbol = request.args.get("symbol") ;
	Session = sessionmaker(bind=engine)
	session = Session()
	d = my_portfolio.delete(my_portfolio.c.symb == symbol)
	
	d.execute()
	session.commit()
			# print(len(allsig))
	return jsonify({'data': True})


@app.route('/api/getportfolio', methods=['GET'])
def get_portfolio():
	data = pd.read_sql('SELECT e.symbol, p.*,eq.CLOSE,eq.HIGH,eq.LOW, e.last_close_100_ema, e.last_close_50_ema, e.timestamp, e.close_50_ema_xd_close_100_ema, e.close_50_ema_xu_close_100_ema FROM stocks.my_portfolio p , stocks.momentum_scan e, stocks.eq_eod_data eq where e.symbol= p.symb and e.symbol=eq.SYMBOL and STR_TO_DATE(eq.TIMESTAMP, "%%d-%%M-%%Y") = (SELECT MAX(STR_TO_DATE(eq1.TIMESTAMP, "%%d-%%M-%%Y")) FROM stocks.eq_eod_data eq1)', con=engine)
	data = data.sort_values('timestamp', ascending=False).drop_duplicates('symbol')
	data['close_LT_100_ema'] = data['CLOSE'] < data['last_close_100_ema']
	data['close_LT_50_ema'] = data['CLOSE'] < data['last_close_50_ema']
	data['buydate'] =  data['buydate'].apply( lambda x: x.strftime('%Y-%m-%d')  )
	data['timestamp'] =  data['timestamp'].apply( lambda x: x.strftime('%Y-%m-%d')  )
	data['gainpercent'] = (data['CLOSE'] - data['buyprice'])*100/ data['buyprice']
	data.index.name=None

	return jsonify({'data': data.to_json(orient='records')})



@app.route('/api/eoddata/<int:noofdays>', methods=['GET'])
def get_eoddata(noofdays):
	sqlstring = 'SELECT * FROM eod_data where '
	symbol = request.args.get("nse_symbol") ;
	if symbol :
		sqlstring += 'nse_symbol ='+"'"+ symbol + "' and "
	sqlstring += ' nse_date > ' + "'"+(date.today()-timedelta(days=noofdays)).strftime('%Y-%m-%d') + "' order by nse_symbol, nse_date"
	
	data = pd.read_sql(sqlstring, con=engine)


	symboiprice = data[['nse_symbol', 'nse_chg_in_oi', 'nse_fut_change']].copy()

	
		
	symboiprice = symboiprice.groupby('nse_symbol').sum()
	symboiprice.reset_index(level=0, inplace=True);
	
	
	symboiprice.columns=['nse_symbol','tot_chg_oi','tot_priper_chg']

	data = pd.merge(data,symboiprice,	how='inner',		left_on=['nse_symbol'],		right_on=['nse_symbol'])

	# symdatahead
	maxdate = data['nse_date'].max()
	symbols = list(data['nse_symbol'].unique())
	symanalysis = {}
	for j in range(0, len(symbols)):
		symdata = data[data['nse_symbol'] == symbols[j]]

		symdata = symdata.sort_values('nse_chg_in_oi',ascending =False)
		
		symdatahead = symdata.head(3)
		
		symdatahead = symdatahead.reset_index(drop=True)

		symdatatail = symdata.tail(3)
		symdatatail = symdatatail.reset_index(drop=True)
		oitext = ''
		for i in range(0, len(symdatahead)-1):
			futchange = symdatahead.loc[i, 'nse_fut_change'] 
			oichange = symdatahead.loc[i, 'nse_chg_in_oi'] 
			oi = symdatahead.loc[i, 'nse_open_int']
			nsedate = symdatahead.loc[i, 'nse_date'].strftime('%d/%m')
			if (futchange > 0 and oichange > 0):
				
				oitext += " LB>"+ nsedate + "<OI>"+ str(round((oichange/oi)*100, 2)) 
			elif(futchange < 0 and oichange > 0):
				oitext += " SB>"+ nsedate + "<OI>"+ str(round((oichange/oi)*100, 2)) 
		for i in range(0, len(symdatahead)-1):
			futchange = symdatatail.loc[i, 'nse_fut_change'] 
			oichange = symdatatail.loc[i, 'nse_chg_in_oi'] 
			nsedate = symdatatail.loc[i, 'nse_date'].strftime('%d/%m')
			if(futchange < 0 and oichange < 0):
				oitext += " LU>"+ nsedate + "<OI>"	+ str(round((oichange/oi)*100, 2)) 
			elif(futchange > 0 and oichange < 0):
				oitext += " SC>"+ nsedate + "<OI>"	+ str(round((oichange/oi)*100, 2)) 
		
		symanalysis[symbols[j]] = oitext	
		
	
	for i in range(1, len(data)):
		

		# 3 day OI calculation 
		if (i >2 ) :
			# print("inside for",i , data.loc[i,'nse_symbol'], data.loc[i,'nse_symbol'],  data.loc[i,'nse_date'])
			if (data.loc[i,'nse_symbol']  == data.loc[i-2,'nse_symbol']):
				# print("inside if")
				oisum = data.loc[i, 'nse_chg_in_oi'] +  data.loc[i-1, 'nse_chg_in_oi'] + data.loc[i-2, 'nse_chg_in_oi']
				pripersum = data.loc[i, 'nse_fut_change'] +  data.loc[i-1, 'nse_fut_change'] + data.loc[i-2, 'nse_fut_change']
				oi = data.loc[i,'nse_open_int'] 
				data.loc[i, 'oi_3d_sum'] = round((oisum/oi)*100, 2)
				data.loc[i, 'priceper_3d_sum'] = pripersum
				data.loc[i, 'open_int_analysis'] = symanalysis[data.loc[i, 'nse_symbol']]
				if (oisum > 0 and pripersum > 0) :
					data.loc[i,'status'] = 'LB'
				elif(oisum > 0 and pripersum < 0):
					data.loc[i,'status'] = 'SB'
				elif(oisum < 0 and pripersum < 0):
					data.loc[i,'status'] = 'LU'
				elif(oisum < 0 and pripersum > 0):
					data.loc[i,'status'] = 'SC'

	if not symbol :
		data =	data[data['nse_date'] == data['nse_date'].max()]
	data['nse_date'] =  data['nse_date'].apply( lambda x: x.strftime('%Y-%m-%d')  )

	# 

	# data['nse_chg_in_oi_sum'] = data.groupby('nse_symbol')['nse_chg_in_oi']
	# data['nse_chg_in_oi_s'] =  data['nse_chg_in_oi'].apply( lambda x: x.sum() )
	# print(data.nse_symbol.head(3))
	# if (data['nse_symbol'].eq(data['nse_symbol'].shift(3).bfill())) :
	# 	data.oi3daychange = data.nse_chg_in_oi + data.nse_chg_in_oi.shift(1) + data.nse_chg_in_oi.shift(2) + data.nse_chg_in_oi.shift(3) 
	
	
	
	return jsonify({'data': data.to_json(orient='records')})

@app.route('/api/news/<string:symbol>', methods=['GET'])
def getnews(symbol): 
	
	return SentimentAnalysis.get_google_news(symbol)
if __name__ == "__main__":
	# app.run(debug=True)
    app.run(host = '0.0.0.0')