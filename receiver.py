from accessible_output2.outputs import auto
from webbrowser import open as wopen
from sys import exit
import update
from threading import Thread
import gw
o=auto.Auto()
speak=o.output
g=gw.GW()
#gw.ggwave.enableLog()
g.start()

def threp():
	stat=0
	while True:
		stats=["transmission finished","file transmition","sending","receiving"]
		try:
			if stat!=g.status and g.status<2:
				stat=g.status
				speak(stats[g.status])
		except UnicodeDecodeError:pass
		except KeyboardInterrupt:exit()

t=Thread(target=threp,daemon=True)
t.start()
def command(cmd):
	if not cmd.startswith("/"):
		g.send(cmd,True)
		return "sending"
	c=cmd.split(" ")
	try:
		match c[0]:
			case "/p":
				if int(c[1])<0 or int(c[1])>11:
					return ("specify protocol between 0 and 11")
				g.protocol=int(c[1])
				return ("protocol set to ",g.protocol)
				if len(c)>2:
					if c[2]=="-":
						g.switchinstance(False,-1)
						return ""
					if int(c[2])<4 or int(c[2])>64:
						return ("invalid payload length. it must be between 4 and 64")
					g.switchinstance(False,int(c[2]))
					return ("payload length "+str(c[2]))
				else:
					if int(c[1])>8:
						return ("protocols 9 to 11 needs a payload length. specify a length after the protocol number")
			case "/f":g.sendfile(c[1])
			case "/stop":g.stopcondition=True
			case "/exit":
				return ("exiting")
				exit()
			case "/device":
				gw.test.test()
				return ("program must be restarted. press enter to exit")
				exit()
			case "/whatsnew":
				return ("openning in browser")
				wopen("https://r1oaz.ru/deniz/gw/changelog.html")
			case "/update":
				update.check()
				return ("no updates")
	except Exception as e:return (e)
