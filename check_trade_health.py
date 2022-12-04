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

class MyHTMLParser(HTMLParser):
	write_data = False
	in_tbody = False
	span_counter = 0
	def handle_starttag(self, tag, attrs):
		if (tag == 'tbody'):
			self.in_tbody = True
			self.span_counter = 0
		if (tag == 'span'):
			self.write_data = True
			#print("Start tag:", tag)

	def handle_endtag(self, tag):
		if (tag == 'tbody'):
			self.in_tbody = False
		if (tag == 'span'):
			self.write_data = False
			self.span_counter  += 1
		#print("End tag  :", tag)

	def handle_data(self, data):
		if (self.in_tbody and self.write_data):
			print("Self {0}".format(self.span_counter))
			if (self.span_counter % 7 == 0):
				current_date = datetime.strptime(data,"%b %d, %Y")
				current_date_epoch = current_date.timestamp()
				if (current_date_epoch >= buy_date_epoch):
					print("Date     :", data)

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

buy_date = datetime.strptime("11/28/2022","%m/%d/%Y")
buy_date_epoch = buy_date.timestamp()
print(buy_date_epoch)

parser = MyHTMLParser()
parser.feed(r)




