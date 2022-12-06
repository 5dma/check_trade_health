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

class MyHTMLParser(HTMLParser):
	in_span = False
	in_tbody = False
	span_counter = 0
	continue_processing = True
	def handle_starttag(self, tag, attrs):
		if self.continue_processing:
			if (tag == 'tbody'):
				self.in_tbody = True
			if (tag == 'tr') and self.in_tbody:
				self.span_counter = 0
			if (tag == 'span'):
				self.in_span = True

	def handle_endtag(self, tag):
		if self.continue_processing:
			if (tag == 'tbody'):
				self.in_tbody = False
			if (tag == 'span'):
				self.in_span = False
				self.span_counter += 1

	def handle_data(self, data):
		if (self.in_tbody and self.in_span and self.continue_processing):
			if ((self.span_counter % 7) == Column.Date.value):
				current_date = datetime.strptime(data,"%b %d, %Y")
				current_date_epoch = current_date.timestamp()
				if (current_date_epoch >= trade_info["buy_date_epoch"]):
					trade_info["current_date"] = current_date
				else:
					print("Trade is still active")
					self.continue_processing = False

			if ((self.span_counter % 7) == Column.Low.value):
				if trade_info["direction"] == Direction.Long:
					if (float(data) < trade_info["stop"]):
						print("Stopped at {0} on {1} (low was {2})".format(trade_info["stop"], trade_info["current_date"].strftime("%Y-%m-%d"), data))
						self.continue_processing = False
				else: # Direction is short
					if (float(data) <= trade_info["target"]):
						print("Sold at {0} on {1} (low was {2})".format(trade_info["target"], trade_info["current_date"].strftime("%Y-%m-%d"), data))
						self.continue_processing = False

			if ((self.span_counter % 7) == Column.High.value):
				if trade_info["direction"] == Direction.Long:
					if (float(data) >= trade_info["target"]):
						print("Sold at {0} on {1} (high was {2})".format(trade_info["target"], trade_info["current_date"].strftime("%Y-%m-%d"), data))
						self.continue_processing = False
				else: # Direction is short
					if (float(data) >= trade_info["stop"]):
						print("Stopped at {0} on {1} (high was {2})".format(trade_info["stop"], trade_info["current_date"].strftime("%Y-%m-%d"), data))
						self.continue_processing = False



def evaluate_trade(trade_info):

	html_file = open('apple.html')
	r = html_file.read()
	html_file.close()


	buy_date = datetime.strptime(trade_info["buy_date"],"%m/%d/%Y")
	trade_info["buy_date_epoch"] = buy_date.timestamp()
	print("Trade summary:")
	print(" Symbol: {0}".format(trade_info["symbol"]))
	print(" Direction: {0}".format("Long" if trade_info["direction"] == Direction.Long else "Short"))
	print(" Target: {0}".format(trade_info["target"]))
	print(" Stop: {0}".format(trade_info["stop"]))
	print(" Buy date: {0}".format(trade_info["buy_date"]))

	#myheaders = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0',}
	#yahoo_url = 'https://finance.yahoo.com/quote/{0}/history'.format(trade_info["symbol"])
	#print(yahoo_url)
	#r = requests.get(yahoo_url, headers=myheaders)

	#print(r.text)
	parser = MyHTMLParser()
	#parser.feed(r.text)
	parser.feed(r)
	parser.close()


with open('/tmp/more_experiments.csv', mode='r') as file:
	csv_file = csv.DictReader(file,None,None, dialect='unix', delimiter='\t', quoting=csv.QUOTE_ALL)
	for lines in csv_file:
		trade_info = {
			"symbol": lines["Symbol"],
			"buy_date": lines["Buy date"],
			"direction": Direction.Short if (lines["Direction"] == "Short") else Direction.Long,
			"stop": float(lines["Stop"]),
			"target": float(lines["Target"])
		}
		evaluate_trade(trade_info)
		#if (lines["Sold"] != ''):
		#	print("Symbol: {0}, sold {1}".format(trade_info['symbol'],lines["Sold"]))
		sleep(3)

