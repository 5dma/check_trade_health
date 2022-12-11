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
			print("Trade results:")
			if (trade_info["sell_date"] is None):
				print("Trade is still active")
			elif (trade_info["status"] == Outcome.Both):
				print("Trade went both sold and stopped on {:s}".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y")))
			else:
				if (trade_info["direction"] == Direction.Short) and (trade_info["status"] == Outcome.Stopped):
					print("  Trade closed on {:s} at {:.2f} ({:.2f}).".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y"), trade_info["stop"], trade_info["sell_price"]))
				if (trade_info["direction"] == Direction.Short) and (trade_info["status"] == Outcome.Sold):
					print("  Trade closed on {:s} at {:.2f} ({:.2f}).".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y"), trade_info["target"], trade_info["sell_price"]))
				if (trade_info["direction"] == Direction.Long) and (trade_info["status"] == Outcome.Stopped):
					print("  Trade closed on {:s} at {:.2f} ({:.2f}).".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y"), trade_info["stop"], trade_info["sell_price"]))
				if (trade_info["direction"] == Direction.Long) and (trade_info["status"] == Outcome.Sold):
					print("  Trade closed on {:s} at {:.2f} ({:.2f}).".format(datetime.fromtimestamp(trade_info["sell_date"]).strftime("%m/%d/%Y"), trade_info["target"], trade_info["sell_price"]))
				
		 
		elif (tag == 'tr') and self.in_tbody:
			if (self.current_date_epoch <= trade_info["buy_date_epoch"]):
				self.continue_processing = False
			
		elif self.continue_processing:
			if (tag == 'span'):
				self.in_span = False
				self.span_counter += 1

	def handle_data(self, data):
		if (self.in_tbody and self.in_span and self.continue_processing):

			if ((self.span_counter % 7) == Column.Date.value):
				current_date = datetime.strptime(data,"%b %d, %Y")
				self.current_date_epoch = current_date.timestamp()

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



def evaluate_trade(trade_info):

	r = ''
	if developer_mode:
		html_file = open('/home/abba/programming/python/check_trade_health/apple.html')
		r = html_file.read()
		html_file.close()
	else:
		myheaders = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0', 'Cookie': 'A1=d=AQABBAVXlmMCEC7J7dRDynyO2FyT3ay530IFEgEBAQGol2OgYwAAAAAA_eMAAA&S=AQAAAuNiAkVF_PoX7y_klE5tO_E; A3=d=AQABBAVXlmMCEC7J7dRDynyO2FyT3ay530IFEgEBAQGol2OgYwAAAAAA_eMAAA&S=AQAAAuNiAkVF_PoX7y_klE5tO_E; A1S=d=AQABBAVXlmMCEC7J7dRDynyO2FyT3ay530IFEgEBAQGol2OgYwAAAAAA_eMAAA&S=AQAAAuNiAkVF_PoX7y_klE5tO_E&j=US; PRF=t%3DPLUG; maex=%7B%22v2%22%3A%7B%7D%7D; cmp=t=1670797066&j=0&u=1YNN'}
		yahoo_url = 'https://finance.yahoo.com/quote/{0}/history'.format(trade_info["symbol"])
		print(yahoo_url)
		r = requests.get(yahoo_url, headers=myheaders)

	

	buy_date = datetime.strptime(trade_info["buy_date"],"%m/%d/%Y")
	trade_info["buy_date_epoch"] = buy_date.timestamp()
	print("Trade summary:")
	print(" Symbol: {0}".format(trade_info["symbol"]))
	print(" Direction: {0}".format("Long" if trade_info["direction"] == Direction.Long else "Short"))
	print(" Target: {0}".format(trade_info["target"]))
	print(" Stop: {0}".format(trade_info["stop"]))
	print(" Buy date: {0}".format(trade_info["buy_date"]))

	parser = MyHTMLParser()
	if developer_mode:
		parser.feed(r)
	else:
		parser.feed(r.text)
	parser.close()

def usage():
	print("\nUsage: python3 check_trade_health.py [-d] | <filename.csv>")
	print("  -d indicates developer mode. This option does not require <filename.csv>\n")

try:
	opts, args = getopt.getopt(sys.argv[1:], "hd")
except getopt.GetoptError as err:
	print(err)  # will print something like "option -a not recognized"
	usage()
	sys.exit(2)

developer_mode = False
for o, a in opts:
	if o == '-h':
		usage()
		sys.exit()
	elif o == '-d':
		developer_mode = True

trade_file = 'test_data.csv'
if not developer_mode:
	if (len(sys.argv) < 2):
		usage()
		sys.exit()
	else:
		trade_file = sys.argv[1]

trade_info = {}
with open(trade_file, mode='r') as file:
	csv_file = csv.DictReader(file,None,None, dialect='unix', delimiter='\t', quoting=csv.QUOTE_ALL)
	for lines in csv_file:
		print(lines["Symbol"])
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
		evaluate_trade(trade_info)
		sleep(3)

