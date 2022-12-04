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
	def handle_starttag(self, tag, attrs):
		if (tag == 'tbody'):
			self.in_tbody = True
		if (tag == 'tr') and self.in_tbody:
			self.span_counter = 0
		if (tag == 'span'):
			self.in_span = True

	def handle_endtag(self, tag):
		if (tag == 'tbody'):
			self.in_tbody = False
		if (tag == 'span'):
			self.in_span = False
			self.span_counter += 1

	def handle_data(self, data):
		if (self.in_tbody and self.in_span):
			if ((self.span_counter % 7) == Column.Date.value):
				current_date = datetime.strptime(data,"%b %d, %Y")
				current_date_epoch = current_date.timestamp()
				if (current_date_epoch >= trade_info["buy_date_epoch"]):
					trade_info["current_date"] = current_date
				else:
					print("Trade is still active")
					sys.exit()

			if ((self.span_counter % 7) == Column.Low.value):
				if trade_info["direction"] == Direction.Long:
					if (float(data) < trade_info["stop"]):
						print("Stopped at {0} on {1} (low was {2})".format(trade_info["stop"], trade_info["current_date"].strftime("%Y-%m-%d"), data))
						sys.exit()
				else: # Direction is short
					if (float(data) <= trade_info["target"]):
						print("Sold at {0} on {1} (low was {2})".format(trade_info["target"], trade_info["current_date"].strftime("%Y-%m-%d"), data))
						sys.exit()

			if ((self.span_counter % 7) == Column.High.value):
				if trade_info["direction"] == Direction.Long:
					if (float(data) >= trade_info["target"]):
						print("Sold at {0} on {1} (high was {2})".format(trade_info["target"], trade_info["current_date"].strftime("%Y-%m-%d"), data))
						sys.exit()
				else: # Direction is short
					if (float(data) >= trade_info["stop"]):
						print("Stopped at {0} on {1} (high was {2})".format(trade_info["stop"], trade_info["current_date"].strftime("%Y-%m-%d"), data))
						sys.exit()

myheaders = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0',}
#r = requests.get('https://finance.yahoo.com/quote/AAPL/history', headers=myheaders)
#print(r.text)
html_file = open('apple.html')
r = html_file.read()
html_file.close()



trade_info = {
	"symbol": "AAPL",
	"buy_date": "11/03/2022",
	"direction": Direction.Short,
	"stop": 551.00,
	"target": 55.00
}

buy_date = datetime.strptime(trade_info["buy_date"],"%m/%d/%Y")
trade_info["buy_date_epoch"] = buy_date.timestamp()
print("Trade summary:")
print(" Symbol: {0}".format(trade_info["symbol"]))
print(" Direction: {0}".format("Long" if trade_info["direction"] == Direction.Long else "Short"))
print(" Target: {0}".format(trade_info["target"]))
print(" Stop: {0}".format(trade_info["stop"]))

parser = MyHTMLParser()
parser.feed(r)
parser.close()

