import wx
from socket import*
import threading
import wx.lib.buttons as buttons
import random
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
        confstart(self.parent, self, self.conf, self.condata)
        self.Destroy()
        
    def onclose(self, event):
        self.Destroy()

def confstart(mainwin, confselectwin, contacts, condata):
    confselectwin.Destroy
    confid = str(random.randrange(5500, 11500))
    app = wx.PySimpleApp()
    frame = conference(mainwin, confselectwin, '0', confid, condata, contacts, '', '', '')
    frame.Show()
    app.MainLoop()
    
        
class confrequest(threading.Thread):
    def __init__(self, confwin, contact, address, confid):
        threading.Thread.__init__(self)
        self.address = address
        self.confwin = confwin
        self.contact = contact
        self.confid = confid
    def run(self):
        resock = socket(AF_INET, SOCK_STREAM)
        print('trying to connect to '+self.contact+'\n')
        try:
            resock.connect((self.address, 4321))
        except:
            print ('could not connect to '+self.contact)
        resock.send('start conference')
        print ('sent conf request to'+self.contact+'\n')
        resock.send(self.confid)
        #resock.send(self.data)
        #print('sent '+self.data+' to '+self.contact)
        while 1:
            print ('waiting for reply from '+self.contact)
            indata = resock.recv(1024)
            if indata == 'yes':
                print(self.contact+' accepted conf starting data sock')
                datasocket = socket(AF_INET, SOCK_STREAM)
                datasocket.connect((self.address, 4321))
                datasocket.send('start conference')
                datasocket.send(self.confid)
                #wx.CallAfter(self.confwin.newcon, self.contact, self.address)
                wx.CallAfter(self.confwin.contacton, self.contact, self.address, resock, datasocket)
                break
            else:
                print (self.contact+' refused the conference request')
                break
            
class connectionthread(threading.Thread):
    def __init__(self, confwin, confid, contact, address):
        threading.Thread.__init__(self)
        self.confwin = confwin
        self.contact = contact
        self.address = address
        self.confid = confid

    def run(self):
        connsock = socket(AF_INET, SOCK_STREAM)
        print('trying to connect to '+self.contact+'\n')
        try:
            connsock.connect((self.address, 4321))
        except:
            print ('could not connect to '+self.contact+self.address)
        connsock.send('start conference')
        print ('sent conf request to'+self.contact+'\n')
        connsock.send(self.confid)
        conndatasock = socket(AF_INET, SOCK_STREAM)
        try:
            conndatasock.connect((self.address, 4321))
        except:
            print ('could not connect to '+self.contact)
        conndatasock.send('start conference')
        print ('sent conf request to'+self.contact+'\n')
        conndatasock.send(self.confid)
        wx.CallAfter(self.confwin.contacton, self.contact, self.address, connsock, conndatasock)
            
class confdatathread(threading.Thread):
    def __init__(self, confwin, datasocket, contact):
        threading.Thread.__init__(self)
        self.confwin = confwin
        self.datasocket = datasocket
        self.contact = contact

    def run(self):
        print('started dataconnection with '+self.contact)
        while 1: 
            conname = self.datasocket.recv(1024)
            conaddress = self.datasocket.recv(1024)
            wx.CallAfter(self.confwin.makeconn, conname, conaddress)
            print(conname+conaddress)
               


class confthread(threading.Thread):
    def __init__(self, confwin, usocket, contact, address):
        threading.Thread.__init__(self)
        self.usocket = usocket
        self.confwin = confwin
        self.contact = contact
        self.address = address

    def run(self):
        while 1:
            try :
                indata = self.usocket.recv(1024)
                if indata != '':
                    update = self.contact+' : '+indata+'\n'
                    wx.CallAfter(self.confwin.update, update)
                elif not indata:
                    print 'contact has closed connection no indata'
                    wx.CallAfter(self.confwin.contactoff, self.contact, self.usocket)
                    break
            except:
                
                print 'contact has closed connection error' 
                wx.CallAfter(self.confwin.contactoff, self.contact, self.usocket)
                break
                
                
    def close(self):
        self.usocket.shutdown(SHUT_RDWR)
        self.usocket.close()
        

class conference(wx.Frame):
    def __init__(self, mainwin, confreqwin, flag, confid, condata, contacts, contact, address, confsocket):
        wx.Frame.__init__(self, mainwin, -1, 'Conference', size=(583, 450), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.image = wx.Image("test.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.panel = wx.StaticBitmap(self, -1, self.image)
        confreqwin.Destroy()
        self.mainwin = mainwin
        self.condata = condata
        self.confid = confid
        if flag == '0':
            cstring = ''
            for c in contacts:
                cstring = cstring+','+c
            for contact in contacts:
                addr = condata[contact]
                req = confrequest(self, contact, addr, self.confid)
                req.start()
        self.datasocks = []
        self.conflist = []
        self.confsocks = []
        self.datalist = []
        self.threadlist = []
        self.confs = {}
        self.maintext = wx.TextCtrl(self.panel, -1, "", pos=(20,30), size=(400,200), style=wx.TE_LEFT|wx.TE_READONLY|wx.TE_WORDWRAP|wx.TE_MULTILINE)
        self.enttext = wx.TextCtrl(self.panel, -1, "", pos=(20,275), size=(300,55), style=wx.TE_LEFT|wx.TE_WORDWRAP|wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.bmp1 = wx.Image("sendbut.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.conflistbox = wx.ListBox(self.panel, -1, (430, 30), (120, 150), self.conflist, wx.LB_SINGLE|wx.LB_NEEDED_SB, name='Contacts')
        sbutton = buttons.GenBitmapButton(self.panel, -1, self.bmp1, pos=(360,250))
        addbutton = wx.Button(self.panel, -1, 'Add Contacts', pos=(430, 190))
        self.Bind(wx.EVT_BUTTON, self.send, sbutton)
        self.Bind(wx.EVT_CLOSE, self.onclose)
        self.Bind(wx.EVT_TEXT_ENTER, self.send, self.enttext)
        self.Bind(wx.EVT_BUTTON, self.add, addbutton)
        if flag == '1':
            self.conflist.append(contact)
            self.conflistbox.Append(contact)
            self.confsocks.append(confsocket)
            confsocket.send('yes')
            netthread = confthread(self, confsocket, contact, address)
            netthread.start()
            self.threadlist.append(netthread)

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
        
    def startdata(self, datasocket, contact, address):
        if contact in self.conflist:
            if contact not in self.datalist:
                self.datalist.append(contact)
                self.datasocks.append(datasocket)
                print('starting dataconn with '+contact)
                netthread = confdatathread(self, datasocket, contact)
                netthread.start()
        elif contact not in self.conflist:
            print ('got req to datasock from '+contact+'already connected')
            netthread = confthread(self, datasocket, contact, address)
            netthread.start()
            dit = {contact:address}
            self.confs.update(dit)
            self.conflist.append(contact)
            self.conflistbox.Append(contact)
            self.confsocks.append(datasocket)
            self.threadlist.append(netthread)

    def send(self, event):
        outdata = self.enttext.GetValue()
        update = 'me  :  '+outdata+'\n'
        self.enttext.Clear()
        self.update(update)
        for confsocket in self.confsocks:
            confsocket.send(outdata)
        
    def update(self, data):
        self.maintext.SetInsertionPointEnd()
        self.maintext.WriteText(data)
    
    def contacton(self, contact, address, confsocket, datasocket):
        cons = self.confs.keys()
        for con in cons:
            datasocket.send(con)
            datasocket.send(self.confs[con])
            
        netthread = confthread(self, confsocket, contact, address)
        netthread.start()
        self.datalist.append(contact)
        self.datasocks.append(datasocket)
        datathread = confdatathread(self, datasocket, contact)
        datathread.start()
        self.conflist.append(contact)
        dit = {contact:address}
        self.confs.update(dit)
        self.conflistbox.Append(contact)
        self.confsocks.append(confsocket)
        self.threadlist.append(netthread)
        

    def contactoff(self, contact, confsocket):
        self.conflistbox.Delete(self.conflist.index(contact))
        self.conflist.remove(contact)
        self.confsocks.remove(confsocket)

    def add(self, event):
        app = wx.PySimpleApp()
        frame = confadd(self, self.condata)
        frame.Show()
        app.MainLoop()

    def makeconn(self, conname, conaddress):
        thread = connectionthread(self, self.confid, conname, conaddress)
        thread.start()

    def newcon(self, contact, address):
        for sock in self.datasocks:
            try:
                sock.send(contact)
                sock.send(address)
            except:
                pass

    def invitecontacts(self, contacts):
        for contact in contacts:
            addr = self.condata[contact]
            req = confrequest(self, contact, addr, self.confid)
            req.start()

    def onclose(self, event):
        del(self.mainwin.confids[self.confid])
        self.closenet()
        self.Destroy()

    def closenet(self):
        for netthread in self.threadlist:
            netthread.close()
        
        
class confadd(wx.Frame):
    def __init__(self, parent, condata):
        wx.Frame.__init__(self, parent, -1, 'Select Contacts', size=(375,250), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.image = wx.Image("test.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        panel = wx.StaticBitmap(self, -1, self.image)
        self.condata = condata
        self.contacts = self.condata.keys()
        self.confwin = parent
        self.conf = []
        self.conlist = wx.ListBox(panel, -1, (20, 20), (100, 150), self.contacts, wx.LB_NEEDED_SB, name='Contacts')
        self.conflist = wx.ListBox(panel, -1, (245, 20), (100, 150), self.conf, wx.LB_NEEDED_SB, name='Conference')
        addbutt = wx.Button(panel, -1, 'Add', pos=(145, 55))
        removebutt = wx.Button(panel, -1, 'Remove', pos=(145, 85))
        invitebutt = wx.Button(panel, -1, 'Invite', pos=(50, 180))

        self.Bind(wx.EVT_BUTTON, self.add, addbutt)
        self.Bind(wx.EVT_BUTTON, self.remove, removebutt)
        self.Bind(wx.EVT_BUTTON, self.invite, invitebutt)
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

    def invite(self, event):
        self.confwin.invitecontacts(self.conf)
        self.Destroy()
        
    def onclose(self, event):
        self.Destroy()
        



        
