from accessible_output2.outputs import auto
from webbrowser import open as wopen
from sys import exit
# import update
from threading import Thread
import gw

o=auto.Auto()
first=o.get_first_available_output().name
speak=o.output
if first=="SAPI5" or first=="SAPI4" or first=="SpeechDispatcher": speak=lambda x:None

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
				toreturn=f"protocol set to {str(g.protocol)}. "
				if len(c)>2:
					if c[2]=="-":
						g.switchinstance(False,-1)
						return toreturn
					if int(c[2])<4 or int(c[2])>64:
						return ("invalid payload length. it must be between 4 and 64")
					g.switchinstance(False, int(c[2]))
					return toreturn+(" payload length "+str(c[2]))
				else:
					if int(c[1])>8:
						return ("protocols 9 to 11 needs a payload length. specify a length after the protocol number")
			case "/f":		
				if len(c)>1 and os.path.exists(c[1]):
					g.sendfile(c[1])
				else: return "!no file specified. please enter a file name into the text field before clicking send file" if len[c]>1 else "this file doesn't ever existed and will not exist in the future!"

			case "/stop":g.stopcondition=True
			case "/exit":
				return ("exiting")
				exit()
			case "/device":
				gw.test.test()
				return ("!Program must be restarted. Press enter to exit")
				exit()
			case "/whatsnew":
				# wopen("https://r1oaz.ru/deniz/gw/changelog.html")
				return ("changelog currently unavailable.")
			case "/update":
				return ("no updates")
	except Exception as e:return (e)
