import wx
app = wx.App()
frame = wx.Frame(None, -1,"win.py")
frame.SetSize	(0,0,200,50)

progress=None

def onButton(event):
	print("Button pressed.")

def inputbox(header,msg,defaultval):
	val=""
	# Create text input
	dlg = wx.TextEntryDialog(frame, header,msg)
	dlg.SetValue(defaultval)
	btnr=dlg.ShowModal()
	if btnr== wx.ID_OK:
		val=dlg.GetValue()
	dlg.Destroy()
	return val

def progressstart(header, message, max=100):
	global progress
	progress = wx.ProgressDialog(header, message, maximum=max, style = wx.PD_CAN_ABORT|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_REMAINING_TIME)

def progressset(per,txt=""):
	global progress
	progress.Update(per,txt)
	return progress.WasCancelled()

def progressclose():
	global progress
	progress.Destroy()
	progress=None
