#
#Symbol Start-Date, Direction, Open, Target, Stop, 
#
#
#
#MANU	11/28/22	Short	20.04	15.28	21.63	21.63	-1.59	Gap up too high

import sys
import requests
r = requests.get('https://httpbin.org/')
print(r.text)

print("Hello")
