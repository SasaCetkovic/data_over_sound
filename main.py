import wx
import receiver
from threading import Thread

class Wnd(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="Default Frame")
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.title = wx.TextCtrl(panel,style=wx.TE_PROCESS_ENTER)
		self.title.Bind(wx.EVT_TEXT_ENTER, self.enter)
		self.text = wx.TextCtrl(panel, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL)
		sizer.Add(self.title, 0, wx.ALL | wx.EXPAND, 5)
		sizer.Add(self.text, 1, wx.ALL | wx.EXPAND, 5)
		panel.SetSizer(sizer)

		filemenu=wx.Menu()
		filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
		filemenu.AppendSeparator()
		filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
		self.Bind(wx.EVT_MENU, exit, id=wx.ID_EXIT)
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&Program")
		self.SetMenuBar(menuBar)
		self.Show()

	def enter(self,event):
		ms= str(self.title.GetValue())
		receiver.speak(str(receiver.command(ms)))
		self.title.SetValue("")
		self.text.write("me: "+ms+"\n")

	def loop(self):
		while True:
			if not receiver.g.q.empty():
				r=receiver.g.q.get()
				self.text.write("received: "+r+"\n")
				receiver.speak(r)




if __name__ == "__main__":
	app = wx.App(False)
	receiver.update.check()
	frame = Wnd()
	t=Thread(target=frame.loop,daemon=True)
	t.start()
	app.MainLoop()