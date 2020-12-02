import pandas as pd

def roundof(no):
	str_no = str(no)
	index = [-2, -1]
	ass = map(str_no.__getitem__, index)
	al = list(ass)
	s = ""
	joined = s.join(al)
	intj = int(joined)
	imp = 100 - intj
	if intj > 50:
		no = no + imp
		return no
	else:
		no = no - intj
		return no


def selection():
	file = pd.read_csv("nfo.csv")
	file.set_index("name", inplace = True)
	result = file.loc["BANKNIFTY"]
	result.to_csv("banknifty.csv")

def select_strike(sr):
	asset_arr = []
	file = pd.read_csv("banknifty.csv")
	file.set_index("strike", inplace =  True)
	result = file.loc[sr]

	exp = result['expiry'].min()
	result.set_index('expiry',inplace=True)
	exp_result = result.loc[exp]

	for l in exp_result['tradingsymbol']:
		asset_arr.append(l)

	return asset_arr