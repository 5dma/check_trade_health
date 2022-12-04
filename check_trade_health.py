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
			#print("Start tag:", tag)

	def handle_endtag(self, tag):
		if (tag == 'tbody'):
			self.in_tbody = False
		if (tag == 'span'):
			self.in_span = False
			self.span_counter += 1
		#print("End tag  :", tag)

	def handle_data(self, data):
		if (self.in_tbody and self.in_span):
			if ((self.span_counter % 7) == Column.Date.value):
				#print("Self {0} {1}".format(self.span_counter, data))
				current_date = datetime.strptime(data,"%b %d, %Y")
				current_date_epoch = current_date.timestamp()
				if (current_date_epoch >= trade_info["buy_date_epoch"]):
					print("Date     :", data)
				else:
					sys.exit()

			#if ((self.span_counter % 7) == Column.Low.value):
			#	current_date = datetime.strptime(data,"%b %d, %Y")
			#	current_date_epoch = current_date.timestamp()
			#	if (current_date_epoch >= buy_date_epoch):
			#		print("Date     :", data)
	#def handle_comment(self, data):
		#print("Comment  :", data)

	#def handle_entityref(self, name):
		#c = chr(name2codepoint[name])
		#print("Named ent:", c)

	#def handle_charref(self, name):
		#if name.startswith('x'):
			#c = chr(int(name[1:], 16))
		#else:
			#c = chr(int(name))
		#print("Num ent  :", c)

	#def handle_decl(self, data):
		#print("Decl     :", data)

myheaders = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0',}
#r = requests.get('https://finance.yahoo.com/quote/AAPL/history', headers=myheaders)
#print(r.text)
html_file = open('apple.html')
r = html_file.read()
html_file.close()



trade_info = {
	"buy_date": "11/03/2022",
	"direction": Direction.Long,
	"stop": 142.00,
	"target": 150.00
}

buy_date = datetime.strptime(trade_info["buy_date"],"%m/%d/%Y")
trade_info["buy_date_epoch"] = buy_date.timestamp()
print(trade_info["buy_date_epoch"])

parser = MyHTMLParser()
parser.feed(r)
parser.close()




