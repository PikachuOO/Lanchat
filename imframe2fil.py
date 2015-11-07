import wx
import wx.lib.buttons as buttons
import threading
from socket import*
import cPickle
import os
import filtrans
class netthread(threading.Thread):
    def __init__(self, imwin, usocket, contact):
        threading.Thread.__init__(self)
        self.contact = contact
        self.usocket = usocket
        self.imwin = imwin

    def run(self):
        while 1:
            try :
                indata = self.usocket.recv(1024)
                if indata != '':
                    update = self.contact+' : '+indata+'\n'
                    wx.CallAfter(self.imwin.update, update)
                elif not indata:
                    print 'contact has closed connection no indata'
                    wx.CallAfter(self.imwin.closenet)
            except:
                print 'contact has closed connection error' 
                wx.CallAfter(self.imwin.closenet)
                break
                
                
    def close(self):
        self.usocket.close()


class imframe(wx.Frame):
    def __init__(self, flag, window, usocket, address, contact):
        wx.Frame.__init__(self, window, -1, contact, size=(500, 450), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.image = wx.Image("test.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.panel = wx.StaticBitmap(self, -1, self.image)
        self.parent = window
        self.usocket = usocket
        self.contact = contact
        self.address = address
        self.flag = flag
        if self.flag != '0':
            self.netthread = netthread(self, self.usocket, self.contact) 
            self.netthread.start()
        self.maintext = wx.TextCtrl(self.panel, -1, "", pos=(30,30), size=(400,200), style=wx.TE_LEFT|wx.TE_READONLY|wx.TE_WORDWRAP|wx.TE_MULTILINE)
        self.enttext = wx.TextCtrl(self.panel, -1, "", pos=(30,275), size=(300,55), style=wx.TE_LEFT|wx.TE_WORDWRAP|wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        
        self.bmp1 = wx.Image("sendbut.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        sbutton = buttons.GenBitmapButton(self.panel, -1, self.bmp1, pos=(360,250))
        filbutton = wx.Button(self.panel, -1, 'Send File', pos=(250,235))                
        self.Bind(wx.EVT_BUTTON, self.send, sbutton)
        self.Bind(wx.EVT_CLOSE, self.onclose)
        self.Bind(wx.EVT_BUTTON, self.sendfile, filbutton)
        self.Bind(wx.EVT_TEXT_ENTER, self.send, self.enttext)
        
    def onclose(self, event):
        try:
            self.usocket.shutdown(SHUT_RDWR)
        except:
            pass
        try:
            self.netthread.close()
        except:
            pass
        self.parent.Refresh()
        self.Destroy()


    def send(self, event):
        outdata = self.enttext.GetValue()
        update = 'me  :  '+outdata+'\n'
        self.enttext.Clear()
        self.update(update)
        if self.flag == '0':
            self.usocket.connect((self.address, 4321))
            self.usocket.send('aGkgdGhpcyBpcyBsYW4gY2hhdA==')
            self.netthread = netthread(self, self.usocket, self.contact) 
            self.netthread.start()
            self.flag = '1'
        try:    
            self.usocket.send(outdata)
        except:
            print 'could not send data starting new socket'
            self.netthread.close()
            self.usocket = socket(AF_INET, SOCK_STREAM)
            self.usocket.connect((self.address, 4321))
            self.usocket.send('aGkgdGhpcyBpcyBsYW4gY2hhdA==')
            self.netthread = netthread(self, self.usocket, self.contact) 
            self.netthread.start()
            self.usocket.send(outdata)
        event.Skip()
        
    def update(self, data):
        self.maintext.SetInsertionPointEnd()
        self.maintext.WriteText(data)

    def connect(self):
        self.usocket.connect((self.address, 4321))
        self.usocket.send('aGkgdGhpcyBpcyBsYW4gY2hhdA==')

    def closenet(self):
        self.netthread.close()
    
    def sendfile(self, event):
        app = wx.PySimpleApp()
        wildcard = "All Files (*.*)|*.*"
        filesel = wx.FileDialog(None, 'Choose File', os.getcwd(), "", wildcard, wx.OPEN)
        if filesel.ShowModal() == wx.ID_OK:
            x = filesel.GetPath()
            filsocket = socket(AF_INET, SOCK_STREAM)
            condatafil = open('condata', 'rb')
            condata = cPickle.load(condatafil)
            uadress = condata[self.contact]
            try:
                filsocket.connect((uadress, 4321))
                wx.MessageBox('connected to contact')
                filsocket.send('Y2FuIGkgc2VuZCBhIGZpbGU=')
                print 'sent filtrans request\n'
                reply = filsocket.recv(1024)
                print 'recieved reply'
            except:
                wx.MessageBox('Could not connect to %s' %uadress)
            if reply == '1':
                wx.MessageBox(self.contact+' accepted to share file')
                transapp = PySimpleApp()
                frame = filtrans.sendfilwin(filsocket, x)
                frame.Show()
                transapp.Mainloop()
            elif reply =='0':
                wx.MessageBox(self.contact+' declined to share file')
                filsocket.close()
        
        
    
    

