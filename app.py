from kiteconnect import KiteConnect, KiteTicker
from flask import Flask, redirect, request
import requests
from datetime import datetime, timedelta, time
import pandas as pd
import sys
import lib

app = Flask(__name__)

configs = {
	"api_key": "lgrjz3jrxt20ldwt",
	"api_secret": "wk3ztbnna4r3gjjpp23z0l6dwkstqrqq"
}

low = sys.argv[1]
int_low = int(low)
high = sys.argv[2]
int_high = int(high)

execute_time = time(9, 21, 5).strftime("%H:%M:%S")
open_time = time(7, 21, 1).strftime("%H:%M:%S")
exit_time = time(15, 15, 0).strftime("%H:%M:%S")

kite = KiteConnect(api_key=configs["api_key"])

@app.route("/")
def hello():
    return redirect("http://localhost:6663/login", code=302)

@app.route("/login")
def login():
	return redirect(kite.login_url(), code=302)

@app.route('/login/callback')
def get_request_token():
	request_token = request.args.get('request_token')
	status = request.args.get('status')
	if status == "success":
		data = kite.generate_session(request_token, api_secret = configs["api_secret"])
		kite.set_access_token(data["access_token"])
		nfo = kite.instruments(exchange="NFO")
		data_nfo = pd.DataFrame(nfo)
		data_nfo.to_csv("nfo.csv")
		lib.selection()
		nse = kite.instruments(exchange="NSE")
		data_nse = pd.DataFrame(nse)
		data_nse.to_csv("nse.csv")
		ohlc_open = 0
		op = 0 
		int_op = 0

		while True:
			current_time = datetime.now().time().strftime("%H:%M:%S")
			if current_time == open_time:
				#ohlc - open
				ohlc_open = kite.ohlc("NSE:NIFTY BANK")
				print(ohlc_open)
				# {'NSE:NIFTY BANK': {'instrument_token': 260105, 'last_price': 29817.85, 'ohlc': {'open': 29844.8, 'high': 29919.75, 'low': 29511, 'close': 29609.05}}}
				op = ohlc_open["NSE:NIFTY BANK"]["ohlc"]["open"]
				int_op = int(op)
				print(int_op)
				break

		if(int_low < int_op and int_op < int_high):
			cepe_dict = {}
			print("Favourable Trade!!!")
			round_of_op = lib.roundof(int_op)
			assets = lib.select_strike(round_of_op)
			print(assets)
			target = 0.0
			sl = 0.0
			sell_counter_ce = 0
			sell_counter_pe = 0
			#get ltp of CE PE on 9:21:05
			while True:
				current_time = datetime.now().time().strftime("%H:%M:%S")
				if current_time == execute_time:
					for asset in assets:
						ltp_asset = kite.ltp("NFO:{ast}".format(ast = asset))
						op_asset = ltp_asset["NFO:{ast}".format(ast = asset)]["last_price"]
						int_op_asset = float(op_asset)
						if asset.endswith("CE"):
							if sell_counter_ce == 0:
								cepe_dict['ce'] = int_op_asset
								sell_ce = kite.place_order(variety = kite.VARIETY_REGULAR, exchange = kite.EXCHANGE_NFO, tradingsymbol = asset, transaction_type = kite.TRANSACTION_TYPE_SELL, quantity = 1, product = kite.PRODUCT_MIS, order_type = kite.ORDER_TYPE_MARKET)
								sell_counter_ce = 1
								print("Sold CE" + sell_ce)
						else:
							if sell_counter_pe == 0:
								cepe_dict['pe'] = int_op_asset
								sell_pe = kite.place_order(variety = kite.VARIETY_REGULAR, exchange = kite.EXCHANGE_NFO, tradingsymbol = asset, transaction_type = kite.TRANSACTION_TYPE_SELL, quantity = 1, product = kite.PRODUCT_MIS, order_type = kite.ORDER_TYPE_MARKET)
								sell_counter_pe = 1
								print("Sold PE" + sell_pe)
				break


			entry = int(cepe_dict['ce'] + cepe_dict['pe'])
			target = entry - (0.1 * entry)
			sl = entry + (0.1 * entry)
			print("taking entry ce pe" + entry)

			asset1 = assets[0]
			asset2 = assets[1]
			buy_counter_ce = 0
			buy_counter_pe = 0
			while True:
				current_time = datetime.now().time().strftime("%H:%M:%S")
				#get ltp's object
				asset1_data = kite.ltp("NFO:{ast}".format(ast = asset1))
				asset2_data = kite.ltp("NFO:{ast}".format(ast = asset2))
				#get ltp's int from object
				asset1_ltp = float(asset1_data['NFO:{ast}'.format(ast = asset1)]['last_price'])
				asset2_ltp = float(asset2_data['NFO:{ast}'.format(ast = asset2)]['last_price'])

				print(asset1_ltp)
				print(asset2_ltp)
				asset_ltp = round(asset1_ltp + asset2_ltp, 2)
				print(asset_ltp)
				if asset_ltp == target or asset_ltp == sl:
					if asset1.endswith("CE"):
						if buy_counter_ce == 0:
							buy_ce = kite.place_order(variety = kite.VARIETY_REGULAR, exchange = kite.EXCHANGE_NFO, tradingsymbol = asset1, transaction_type = kite.TRANSACTION_TYPE_BUY, quantity = 1, product = kite.PRODUCT_MIS, order_type = kite.ORDER_TYPE_MARKET)
							buy_counter_ce = 1
							print("Bought CE" + buy_ce)
					else:
						if buy_counter_pe == 0:
							buy_pe = kite.place_order(variety = kite.VARIETY_REGULAR, exchange = kite.EXCHANGE_NFO, tradingsymbol = asset2, transaction_type = kite.TRANSACTION_TYPE_BUY, quantity = 1, product = kite.PRODUCT_MIS, order_type = kite.ORDER_TYPE_MARKET)
							buy_counter_pe = 1
							print("Bought PE" + buy_pe)
				break

				if current_time == exit_time:
					break


		else:
			print("Not favourable Tarde")

		print("Access Token: {access_token}".format(access_token = data["access_token"]))
		return "Access Token: {access_token}, order has been placed".format(access_token = data["access_token"])
	else:
		return "Unauthorized"






# app config
if __name__ == '__main__':
    app.run(port=6663)