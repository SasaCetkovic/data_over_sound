import os
import dlgs
from webbrowser import open as wopen
from sys import exit
import requests
error=0
vid=2
def check():
	global error
	r=requests.get("https://r1oaz.ru/deniz/gw/v.txt")
	if r:v=int(r.text)
	else:
		error=1
		v=vid
	if v>vid:
		process()

def process():
	url="https://r1oaz.ru/deniz/gw/receiver.exe"
	total_length = int(requests.head(url).headers["Content-Length"])
	dlgs.progressstart("updating","downloading update",total_length)
	canceled=False
	with requests.get(url,stream=True) as response,open("receiver.dl","wb") as f:
		dl = 0
		for data in response.iter_content(chunk_size=4096):
			dl+=f.write(data)
			canc=dlgs.progressset(dl)
			if canc:
				canceled=True
				dlgs.progressclose()
				break
	if not canceled:
		os.remove("receiver.exe")
		os.rename("receiver.dl","receiver.exe")
		dlgs.progressset(total_length,"update finished. press enter and launch your app again.")
		dlgs.progressclose()
		wopen("https://r1oaz.ru/deniz/gw/changelog.html")
		exit()
	else:
		os.remove("receiver.dl")