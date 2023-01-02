#
#Symbol Start-Date, Direction, Open, Target, Stop, 
#
#
#
#MANU	11/28/22	Short	20.04	15.28	21.63	21.63	-1.59	Gap up too high

import sys
import requests
from html.parser import HTMLParser
from datetime import datetime
from enum import Enum
import csv
from time import sleep
import getopt

class Column(Enum):
	Date = 0
	Open = 1
	High = 2
	Low = 3
	Close = 4
	AdjClose = 5
	Volume = 6

class Direction(Enum):
	Long = 0
	Short = 1

class Outcome(Enum):
	Open = 0
	Sold = 1
	Stopped = 2
	Both = 3

class MyHTMLParser(HTMLParser):
	in_span = False
	in_tbody = False
	span_counter = 0
	continue_processing = True
	current_date_epoch = 0
	def handle_starttag(self, tag, attrs):
		if self.continue_processing:
			if (tag == 'tbody'):
				self.in_tbody = True
			if (tag == 'tr') and self.in_tbody:
				self.span_counter = 0
			if (tag == 'span'):
				self.in_span = True

	def handle_endtag(self, tag):
		if (tag == 'tbody'):
			self.in_tbody = False
			result=""
			if (trade_info["sell_date"] is None):
				result = "Trade is still active"
			elif (trade_info["status"] == Outcome.Both):
				result = "Trade went both sold and stopped on {:s}".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y"))
			else:
				if (trade_info["direction"] == Direction.Short) and (trade_info["status"] == Outcome.Stopped):
					result = "Trade closed on {:s} at {:.2f} ({:.2f}).".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y"), trade_info["stop"], trade_info["sell_price"])
				if (trade_info["direction"] == Direction.Short) and (trade_info["status"] == Outcome.Sold):
					result = "Trade closed on {:s} at {:.2f} ({:.2f}).".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y"), trade_info["target"], trade_info["sell_price"])
				if (trade_info["direction"] == Direction.Long) and (trade_info["status"] == Outcome.Stopped):
					result = "Trade closed on {:s} at {:.2f} ({:.2f}).".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y"), trade_info["stop"], trade_info["sell_price"])
				if (trade_info["direction"] == Direction.Long) and (trade_info["status"] == Outcome.Sold):
					result = "Trade closed on {:s} at {:.2f} ({:.2f}).".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y"), trade_info["target"], trade_info["sell_price"])
				
		 
			row_data = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>".format(trade_info["symbol"], trade_info["direction"].name, trade_info["target"], trade_info["stop"],trade_info["buy_date"],result)
			output_file.write(row_data)
			
		elif self.continue_processing:
			if (tag == 'span'):
				self.in_span = False
				self.span_counter += 1

	def handle_data(self, data):
		if (self.in_tbody and self.in_span and self.continue_processing):

			if ((self.span_counter % 7) == Column.Date.value):
				current_date = datetime.strptime(data,"%b %d, %Y")
				self.current_date_epoch = current_date.timestamp()
				if (self.current_date_epoch <= trade_info["buy_date_epoch"]):
					self.continue_processing = False
				if verbose_mode:
					print("Current line's date/epoch: {0} / {1}".format(data, self.current_date_epoch))

			if ((self.span_counter % 7) == Column.Low.value):
				if trade_info["direction"] == Direction.Long:
					if (float(data) <= trade_info["stop"]):
						trade_info["sell_date"] = self.current_date_epoch
						trade_info["status"] = Outcome.Both if trade_info["status"] == Outcome.Sold else Outcome.Stopped
						trade_info["sell_price"] = float(data)
						
				else: # Direction is short
					if (float(data) <= trade_info["target"]):
						trade_info["sell_date"] = self.current_date_epoch
						trade_info["status"] = Outcome.Both if trade_info["status"] == Outcome.Stopped else Outcome.Sold
						trade_info["sell_price"] = float(data)

			if ((self.span_counter % 7) == Column.High.value):
				if trade_info["direction"] == Direction.Long:
					if (float(data) >= trade_info["target"]):
						trade_info["sell_date"] = self.current_date_epoch
						trade_info["status"] = Outcome.Both if trade_info["status"] == Outcome.Stopped else Outcome.Sold
						trade_info["sell_price"] = float(data)
				else: # Direction is short
					if (float(data) >= trade_info["stop"]):
						trade_info["sell_date"] = self.current_date_epoch
						trade_info["status"] = Outcome.Both if trade_info["status"] == Outcome.Sold else Outcome.Stopped
						trade_info["sell_price"] = float(data)



def trade_input(trade_info):
	print("Trade input:")
	print("  Symbol: {0}".format(trade_info["symbol"]))
	print("  Buy date: {0}".format(trade_info["buy_date"]))
	print("  Direction: {0}".format(trade_info["direction"]))
	print("  Stop: {0}".format(trade_info["stop"]))
	print("  Target: {0}".format(trade_info["target"]))


def evaluate_trade(trade_info):

	r = ''
	if developer_mode:
		html_file = open('/home/abba/programming/python/check_trade_health/apple.html')
		r = html_file.read()
		html_file.close()
	else:
		myheaders = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate, br',
			'Accept-Language':'en-US,en;q=0.5',
			'Connection':'keep-alive',
			'Host':'finance.yahoo.com',
			'Sec-Fetch-Dest':'document',
			'Sec-Fetch-Mode':'navigate',
			'Sec-Fetch-Site':'same-origin',
			'Sec-Fetch-User':'?1',
			'TE':'trailers',
			'Upgrade-Insecure-Requests':'1',
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0', 
			'Cookie': 'A1=d=AQABBAVXlmMCEC7J7dRDynyO2FyT3ay530IFEgEBAQGol2OgYwAAAAAA_eMAAA&S=AQAAAuNiAkVF_PoX7y_klE5tO_E; A3=d=AQABBAVXlmMCEC7J7dRDynyO2FyT3ay530IFEgEBAQGol2OgYwAAAAAA_eMAAA&S=AQAAAuNiAkVF_PoX7y_klE5tO_E; A1S=d=AQABBAVXlmMCEC7J7dRDynyO2FyT3ay530IFEgEBAQGol2OgYwAAAAAA_eMAAA&S=AQAAAuNiAkVF_PoX7y_klE5tO_E&j=US; PRF=t%3DPLUG; maex=%7B%22v2%22%3A%7B%7D%7D; cmp=t=1670797066&j=0&u=1YNN'
		}
		yahoo_url = 'https://finance.yahoo.com/quote/{0}/history'.format(trade_info["symbol"])
		r = requests.get(yahoo_url, headers=myheaders)

	

	buy_date = datetime.strptime(trade_info["buy_date"],"%m/%d/%Y")
	trade_info["buy_date_epoch"] = buy_date.timestamp()
	if verbose_mode:
		print("  Buy date epoch: {0}".format(trade_info["buy_date_epoch"]))

	parser = MyHTMLParser()
	if developer_mode:
		parser.feed(r)
	else:
		parser.feed(r.text)
	parser.close()

def usage():
	print("\nUsage: python3 check_trade_health.py [-d] | [-v] <filename.csv>")
	print("       python3 check_trade_health.py -h")
	print("       -d indicates developer mode. This option ignores <filename.csv>")
	print("       -v verbose mode\n")

try:
	opts, args = getopt.getopt(sys.argv[1:], "hdv")
except getopt.GetoptError as err:
	print(err)  # will print something like "option -a not recognized"
	usage()
	sys.exit(2)

developer_mode = False
verbose_mode = False
for o, a in opts:
	if o == '-h':
		usage()
		sys.exit()
	elif o == '-d':
		developer_mode = True
	elif o == '-v':
		verbose_mode = True

trade_file = 'test_data.csv'
if not developer_mode:
	if (len(sys.argv) < 2):
		usage()
		sys.exit()
	else:
		trade_file = sys.argv[len(sys.argv)-1]

output_file = open("/tmp/trade_health.html", "w")
start_html = """
<!DOCTYPE html>
<html lang="en">
<head>
	<title>Trade health</title>
	<meta charset="utf-8">
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
</head>
<body class="p-5">
	
	<table class="table">
		<thead>
			<tr><td>Symbol</td><td>Direction</td><td>Target</td><td>Stop</td><td>Buy date</td><td>Result</td></tr>

		</thead>
		<tbody>
"""
output_file.write(start_html)
trade_info = {}
with open(trade_file, mode='r') as file:
	csv_file = csv.DictReader(file,None,None, dialect='unix', delimiter='\t', quoting=csv.QUOTE_ALL)
	for lines in csv_file:
		if (lines["Sold"] == ""):
			print("Processing {0}".format(lines["Symbol"]))
			trade_info.clear()
			trade_info = {
				"symbol": lines["Symbol"],
				"buy_date": lines["Buy date"],
				"direction": Direction.Short if (lines["Direction"] == "Short") else Direction.Long,
				"stop": float(lines["Stop"]),
				"target": float(lines["Target"]),
				"status": Outcome.Open,
				"sell_date": None,
				"sell_price": 0
			}
			if verbose_mode:
				trade_input(trade_info)
			evaluate_trade(trade_info)
			if not developer_mode:
				sleep(3)

end_html = """
</tbody>
	</table>
</body>
</html>
"""
output_file.write(end_html)
output_file.close()
