import wx
import os
import threading
class sendfilthread(threading.Thread):
    def __init__(self, sendfilwin, filsocket, sendfil):
        threading.Thread.__init__(self)
        self.sendfilwin = sendfilwin
        self.filsocket = filsocket
        self.sendfil = sendfil

    def run(self):
        c = 0
        for line in self.sendfil:
            self.filsocket.send(line)
            if c == 20:
                update = self.filsocket.recv(4096)
                self.sendfilwin.updategauge(update)
                c = 0
            c = c + 1
        wx.MessageBox('file transfer complete')

class sendfilwin(wx.Frame):
    def __init__(self, filsocket, filpath):
        wx.Frame.__init__(self, window, -1, contact, size=(500, 450), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.image = wx.Image("test.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.panel = wx.StaticBitmap(self, -1, self.image)
        self.filsocket = filsocket
        self.sendfil = open(filpath, 'rb')
        self.filsize = os.path.getsize(filpath)
        self.filsocket.send(os.path.basename(filpath))
        self.filsocket.send(self.filsize)
        self.gauge = wx.Gauge(self.scroll, -1, self.filsize, (20, 20), (250, 25), style=wx.GA_PROGRESSBAR)
        self.gauge.SetBezelFace(3)
        self.gauge.SetShadowWidth(3)
        self.filthread = sendfilthread(self, self.filsocket, self.sendfil)
        self.filthread.start()


    def updategauge(self, update):
        self.gauge.SetValue(int(update))


class recvfilthread(threading.Thread):
    def __init__(self, recvfilwin, filsocket, recvfil, filpath):
        threading.Thread.__init__(self)
        self.recvfilwin = recvfilwin
        self.filsocket = filsocket
        self.recvfil = recvfil
        self.filpath = filpath

    def run(self):
        c = 0
        while 1:
            line = self.filsocket.recv(4096)
            self.recvfil.write(line)
            if c == 20:
                self.recvfil.flush()
                x = os.path.getsize(self.filpath)
                self.filsocket.send(x)
                self.recvfilwin(updategauge(x))
                c = 0
            c = c + 1
    def shut(self):
        self.filsocket.shutdown(SHUT_RDWR)
        self.filsocket.close()


class recvfilwin(wx.Frame):
    def __init__(self, filsocket, filpath):
        wx.Frame.__init__(self, window, -1, contact, size=(300, 50), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.image = wx.Image("test.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.panel = wx.StaticBitmap(self, -1, self.image)
        self.filsocket = filsocket
        self.filpath = filpath
        self.recvfil = open(self.filpath, 'wb')
        self.filsize = self.filsocket.recv(1024)
        self.gauge = wx.Gauge(self.scroll, -1, self.filsize, (20, 20), (250, 25), style=wx.GA_PROGRESSBAR)
        self.gauge.SetBezelFace(3)
        self.gauge.SetShadowWidth(3)
        self.filthread = recvfilthread(self, self.filsocket, self.recvfil, self.filpath)
        self.filthread.start()
        cancelbut = wx.Button(self.panel, -1, 'Canel', pos=(220, 40))
        self.Bind(wx.EVT_BUTTON, self.oncanel, cancelbut)

    def updategauge(self, update):
        self.gauge.SetValue(int(update))

    def oncancel(self, event):
        self.filthread.shut()
        self.Destroy()

