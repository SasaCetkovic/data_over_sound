import test
from threading import Thread
from time import sleep,time
from queue import Queue
from base64 import b64encode,b64decode
import numpy as np
import ggwave
ggwave.disableLog()
import sounddevice as sd
# import json
rate=48000
ch=1
frames=1024
slp=0.5


class GW:
	def __init__(self,**kwargs):
		self.sendthr=None
		self.recvthr=None
		self.thr=None
		self.q=Queue()
		self.fileq=Queue()
		self.protocol=2
		self.recving=False
		self.pars=ggwave.getDefaultParameters()
		for k,v in kwargs.items():
			self.pars[k]=v
		self.filelength=64
		self.filepars=ggwave.getDefaultParameters()
		#self.filepars["payloadLength"]=self.filelength

		self.instance = ggwave.init(self.pars)
		self.stream=sd.InputStream(samplerate=rate, blocksize=frames, dtype='float32', channels=ch, callback=self.callback,device=test.devs[1])
		self.started=False
		self.stopcondition=False

	def thractive(self,thr):
		if thr is None or not thr.is_alive():return False
		t=time()
		while time()-t<3:
			if not thr.is_alive():return False
			return thr.is_alive()

	def callback(self,indata, frames, time, status):
		if self.stopcondition: self.stopcondition=False
		res = ggwave.decode(self.instance, bytes(indata))
		if res is not None:
			res=trytoutf8(res)
			if self.recving:self.fileq.put(res)
			else:self.q.put(res)
		if type(res)==str and res.startswith("$$$"):
			res=res.replace("$$$","").split(":")
			if self.thractive(self.thr):return 1
			self.thr=Thread(target=self.receivefile,args=(res[0],res[1]),daemon=True)
			self.thr.start()


	def start(self):
		if self.started:return
		self.started=True
		self.stream.start()
	def stop(self):
		if not self.started:return
		self.started=False
		self.stream.stop()

	def send(self, data, start=False):
		#print("sending",data)
		self.stop()
		wf=np.frombuffer(ggwave.encode(data,protocolId =self.protocol, instance=self.instance),dtype="float32")		
		def wr():
			with sd.OutputStream(samplerate=rate, blocksize=frames, dtype='float32', channels=ch, device=test.devs[0]) as st:st.write(wf)
		self.sendthr=Thread(target=wr,daemon=True)
		self.sendthr.start()
		if start:self.start()

	def switchinstance(self, r=False, leng=-1):
		self.recving=r
		ggwave.free(self.instance)
		if r:
			self.instance=ggwave.init(self.filepars)
		else:
			if leng is not None:self.pars["payloadLength"]=leng

			self.instance=ggwave.init(self.pars)

	def receive(self,recvtime=10,wait=0):
		self.start()
		if self.recving:qq=self.fileq
		else:qq=self.q
		t=time()
		while time()-t<recvtime and qq.empty() and not self.stopcondition:
			continue
		if qq.empty():
			return ...
		self.stop()
		if wait>0:sleep(wait)
		r=qq.get()
		qq.task_done()
		return r


	def sendfilethr(self,filename):
		with open(filename,"rb") as f:r=b64encode(f.read())
		n=self.filelength-4
		lst=[r[i:i+n] for i in range(0, len(r), n)]
		del(r) #optimize memory incase
		self.send("$$$"+filename+":"+str(len(lst)))
		self.sendwait()
		sleep(slp)
		self.switchinstance(True)
		unheard=list(range(len(lst)))
		while unheard!=[] and not self.stopcondition:
			for i,block in enumerate(lst):
				if not i in unheard:continue
				s=str(i)+":"+block.decode("UTF-8")
				self.send(s)
				self.sendwait()
				sleep(slp)
			unheard=""
			count=0
			while unheard=="" and count<3:
				self.send("EOF")
				self.sendwait()
				unheard=self.receive(10,slp)
				if unheard=="":return
				count+=1

			if unheard==...:
				print("connection error")
				self.stopcondition=True
				break
			if "@all" in unheard:return 0
			unheard=unheard.replace("@","").split(",")
			print(unheard)
			unheard=[int(i) for i in unheard]
		self.switchinstance(False)

	def sendfile(self,filename):
		if self.thractive(self.thr):return ...
		self.thr=Thread(target=self.sendfilethr, args=(filename,),daemon=True)
		self.thr.start()

	def sendwait(self):
		self.sendthr.join()

	@property
	def status(self):
		if self.thr is not None and self.thr.is_alive(): return 1 #sending or recving file
		if self.sendthr is not None and self.sendthr.is_alive(): return 2 #sending
		if self.recvthr is not None and self.recvthr.is_alive(): return 3 #recving
		return 0

	def receivefile(self,filename,size):
		size=int(size)
		filearr=[None]*size
		self.switchinstance(True)
		unheard=list(range(len(filearr)))
		while not self.stopcondition and unheard!=[]:
			c=self.receive(30)
			if c!=... and "finish" in c:
				unheard = [i for i, x in enumerate(filearr) if x == None]
				sleep(slp)
				if unheard!=[]:
					self.send("@"+(",".join(map(str,[i for i,x in enumerate(filearr) if x==None]))))
					self.sendwait()
				else:
					self.send("@all")
					return self.savefile(filename,filearr)
				continue

			elif c==... or c=="" or not ":" in c:continue
			c=c.split(":")
			filearr[int(c[0])]=c[1]
		else:
			if self.stopcondition:
				self.stopcondition=False
				return

	def savefile(self, filename, filearr):
		self.switchinstance(False)
		rec=""
		for item in filearr:rec+=item
		with open("files/"+filename,"wb") as f:f.write(b64decode(rec))
		print("ended!")




	def __del__(self):
		ggwave.free(self.instance)

def trytoutf8(val):
	try:
		return val.decode("UTF-8").replace("\x00","")
	except:return val