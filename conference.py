import wx
from socket import*
import threading
import wx.lib.buttons as buttons

class confselect(wx.Frame):
    def __init__(self, parent, condata):
        wx.Frame.__init__(self, parent, -1, 'Select Contacts', size=(375,250), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.image = wx.Image("test.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        panel = wx.StaticBitmap(self, -1, self.image)
        self.condata = condata
        self.contacts = self.condata.keys()
        self.parent = parent
        self.conf = []
        self.conlist = wx.ListBox(panel, -1, (20, 20), (100, 150), self.contacts, wx.LB_NEEDED_SB, name='Contacts')
        self.conflist = wx.ListBox(panel, -1, (245, 20), (100, 150), self.conf, wx.LB_NEEDED_SB, name='Conference')
        addbutt = wx.Button(panel, -1, 'Add', pos=(145, 55))
        removebutt = wx.Button(panel, -1, 'Remove', pos=(145, 85))
        startbutt = wx.Button(panel, -1, 'Start Conference', pos=(50, 180))

        self.Bind(wx.EVT_BUTTON, self.add, addbutt)
        self.Bind(wx.EVT_BUTTON, self.remove, removebutt)
        self.Bind(wx.EVT_BUTTON, self.start, startbutt)
        self.Bind(wx.EVT_CLOSE, self.onclose)

    def add(self, event):
        sel = self.conlist.GetSelections()
        for x in range(len(sel)):
            self.conf.append(self.contacts[sel[x]])
            self.conflist.Append(self.contacts[sel[x]])
        event.Skip()

    def remove(self, event):
        sel = self.conflist.GetSelections()
        for x in range(len(sel)):
            self.conf.remove(self.conf[sel[x]])
            self.conflist.Delete(sel[x])
        event.Skip()

    def start(self, event):
        confstart(self.conf, self.condata)
        
        
    def onclose(self, event):
        self.Destroy()

def confstart(contacts, condata):
    app = wx.PySimpleApp()
    frame = conference(self, condata, contacts)
    frame.Show()
    app.MainLoop()


        
class confrequest(threading.Thread):
    def __init__(self, confwin, address, data):
        threading.Thread.__init__(self)
        self.address = address
        self.data = data

    def run(self):
        resock = socket(AF_INET, SOCK_STREAM)
        print('trying to connect to '+self.address)
        resock.connect((self.address, 4321))
        print ('sent conf request to'+self.address)
        resock.send('start conference')
        resock.send(self.data)
        while 1:
            resock.recv(1024)


class confthread(threading.Thread):
    def __init__(self, confwin, usocket, contact):
        threading.Thread.__init__(self)
        self.usocket = usocket
        self.confwin = confwin
        self.contact = contact

    def run(self):
        while 1:
            try :
                indata = self.usocket.recv(1024)
                if indata != '':
                    update = self.contact+' : '+indata+'\n'
                    wx.CallAfter(self.conference.update, update)
                elif not indata:
                    print 'contact has closed connection no indata'
                    wx.CallAfter(self.conference.contactoff, self.contact, self.usocket)
            except:
                print 'contact has closed connection error' 
                wx.CallAfter(self.conference.contactoff, self.contact, self.usocket)
                break
                
                
    def close(self):
        self.usocket.shutdown(SHUT_RDWR)
        self.usocket.close()
        

class conference(wx.Frame):
    def __init__(self, condata, contacts):
        wx.Frame.__init__(self, None, -1, contact, size=(580, 450), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.image = wx.Image("test.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.panel = wx.StaticBitmap(self, -1, self.image)
        cstring = ''
        for c in contacts:
            cstring = cstring+','+c
        for contact in contacts:
            addr = condata[contact]
            req = confrequest(self , addr, cstring)
            req.start()
        self.condata = condata
        self.conflist = []
        self.confsocks = []
        self.threadlist = []
        self.maintext = wx.TextCtrl(self.panel, -1, "", pos=(30,30), size=(400,200), style=wx.TE_LEFT|wx.TE_READONLY|wx.TE_WORDWRAP|wx.TE_MULTILINE)
        self.enttext = wx.TextCtrl(self.panel, -1, "", pos=(30,275), size=(300,55), style=wx.TE_LEFT|wx.TE_WORDWRAP|wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        
        self.bmp1 = wx.Image("sendbut.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.conflistbox = wx.ListBox(panel, -1, (450, 20), (150, 150), self.contacts, wx.LB_SINGLE|wx.LB_NEEDED_SB, name='Contacts')
        sbutton = buttons.GenBitmapButton(self.panel, -1, self.bmp1, pos=(360,250)                
        self.Bind(wx.EVT_BUTTON, self.send, sbutton)
        self.Bind(wx.EVT_CLOSE, self.onclose)
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
        for socket in self.confsocks:
            socket.send(outdata)
        
    def update(self, data):
        self.maintext.SetInsertionPointEnd()
        self.maintext.WriteText(data)
    
    def contacton(self, contact, socket):
        self.conflist.append(contact)
        self.conflistbox.Append(contact)
        self.confsocks.append(socket)
        netthread = confthread(self, socket, contact)
        netthread.start()
        self.threadlist.append(thread)

    def contactoff(self, contact, socket):
        self.conflist.remove(contact)
        self.conflistbox.Delete(self.conflist.index(contact))
        self.confsocks.remove(socket)

    def onclose(self):
        self.closenet()
        self.Destroy()

    def closenet(self):
        for netthread in self.threadlist:
            netthread.close()
        



        
