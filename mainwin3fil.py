import wx
import wx.lib.buttons as buttons
import cPickle
import threading
import imframe2fil
import filtrans
from socket import*
import Image
import ImageDraw
import ImageFont
import conference

def findkey(dic, val):
    return [k for k, v in dic.iteritems() if v == val][0]    
def textbutton(flag, text):
        if flag == '0':
                pic = Image.open('buttnonsel.jpg')
        else:
                pic = Image.open('buttnonline.jpg')
        draw = ImageDraw.Draw(pic)
        draw.text((30, 12), text, font=ImageFont.truetype('Twilight.ttf',20), fill='#00f')
        image = apply( wx.EmptyImage, pic.size )
        image.SetData( pic.convert( "RGB").tostring() )
        image.SetAlphaData(pic.convert("RGBA").tostring()[3::4])
        return image

def editframeredraw(x, y, z):
    x.Destroy()
    condatafile = open('condata', 'rb')
    condata = cPickle.load(condatafile)
    app = wx.PySimpleApp()
    frame = conedit(z, condata)
    frame.SetPosition(y)
    frame.Show()        
    app.MainLoop()


def onrecvfil(filsocket, contact):
        print 'got call to recvfil'
        app = wx.PySimpleApp()
        alert = wx.MessageDialog(None, contact+"is to trying to send a file a file", 'Alert', wx.YES_NO|wx.ICON_INFORMATION)
        re = alert.ShowModal()
        if (re == wx.ID_YES):
            filsocket.send('1')
            filname = filsocket.recv(1024)
            app2 = wx.PySimpleApp()
            wildcard = "All Files (*.*)|*.*"
            filesel = wx.FileDialog(None, 'Choose save location', os.getcwd(), filname, wildcard, wx.OPEN)
            filesel.SetFilename(filname)
            if filesel.ShowModal() == wx.ID_OK:
                x = filesel.GetPath()
                app3 = wx.PySimpleApp()
                frame = filtrans.recvfilwin(filsocket, x)
                frame.Show()
                app3.MainLoop()
            else:
                filsocket.send('0')
                filsocket.close()
        else:
            filsocket.send('0')
            filsocket.close()
        alert.Destroy()

class statuscheck(threading.Thread):
    def __init__(self, mainwin, contact):
        threading.Thread.__init__(self)
        self.contact = contact
        self.mainwin = mainwin
        self.condata = condata
    def run(self):
        statussock = socket(AF_INET, SOCK_STREAM)
        statussock.settimeout(2)
        x=statussock.connect_ex((self.condata[self.contact], 4321))
        if x == 0:
            print ('connected to'+self.contact)
            statussock.send('online?') 
            reply = statussock.recv(1024)
            if reply == 'online':
                print (self.contact+'is online\n')
                wx.CallAfter(self.mainwin.butonupdate, self.contact)
        else:
            print (self.contact+'is offline\n')          
        statussock.close()
            
class listner(threading.Thread):
    def __init__(self, mainwin):
        threading.Thread.__init__(self)
        self.mainwin = mainwin
        self.condata = condata
    def run(self):
        port = 5678
        self.listner_socket = socket(AF_INET, SOCK_STREAM)
        self.listner_socket.bind(('', 4321))
        self.listner_socket.listen(20)
        print 'listner on'
        #wx.MessageBox("listner on")
        while 1:
            usocket, uadress = self.listner_socket.accept()
            x = usocket.recv(1024)
            if x == 'aGkgdGhpcyBpcyBsYW4gY2hhdA==':   
                if uadress[0] in self.condata.values():
                    contact = findkey(self.condata, uadress[0])
                    flag = '1'
                    wx.CallAfter(self.mainwin.openim, flag, usocket, uadress[0], contact)
            elif x == 'Y2FuIGkgc2VuZCBhIGZpbGU=':
                print 'got request for file trans\n' 
                contact = findkey(self.condata, uadress[0])
                #wx.MessageBox(contact)
                print 'calling recv fil'
                onrecvfil(usocket, contact)
            elif x == 'online?':
                contact = findkey(self.condata, uadress[0])
                print ('got status chect from'+contact+'\n')
                usocket.send('online')
                wx.CallAfter(self.mainwin.butonupdate, contact)
                usocket.close()
            elif x == 'offline':
                usocket.close()
                wx.CallAfter(self.mainwin.butoffupdate, contact)
            else:
                #wx.MessageBox("bjhgjhgj")
                usocket.close()
    def listnershut(self):
        self.listner_socket.close()
    

class mainwin(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'main wi', size=(280, 500), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.panel = wx.ScrolledWindow(self, -1, style=wx.VSCROLL)
        self.panel.SetScrollbars(1, 1, 0, 1000)
        self.panel.SetBackgroundColour('white')
        self.condata = condata
        self.contacts = self.condata.keys()
        self.online = []
        self.listner = listner(self)
        self.listner.start()
        for contact in self.contacts:
            self.statuscheck = statuscheck(self, contact)
            self.statuscheck.start()
        menu = wx.Menu()
        mexit = menu.Append(-1, "Exit")
        meditcon = menu.Append(-1, "Edit Contacts")
        mconference = menu.Append(-1, "Conference")
        self.Bind(wx.EVT_MENU, self.onclose, mexit)
        self.Bind(wx.EVT_MENU, self.oneditcon, meditcon)
        self.Bind(wx.EVT_CLOSE, self.onclose)
        self.Bind(wx.EVT_MENU, self.onconference)
        menubar = wx.MenuBar()
        menubar.Append(menu, "FILE")
        self.SetMenuBar(menubar)
        
        self.bmp1 = wx.Image("buttnonsel.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bmp2 = wx.Image("buttnonline.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.buttlist = []
        self.textbutton = []
        self.textbuttoff = []
        #for n in range(len(self.contacts))
            #b1 = 
        for x in range(len(self.contacts)):
            b = buttons.GenBitmapButton(self.panel, x, textbutton('0', self.contacts[x]).ConvertToBitmap(), pos=(5,(70*x)+5))
            self.buttlist.append(b) 

        for y in self.buttlist:
            #y.SetBitmapSelected(self.bmp2)
            self.Bind(wx.EVT_BUTTON, self.oncontact, y)
            #self.Bind(wx.EVT_ENTER_WINDOW, self.onmousein, y)
            #self.Bind(wx.EVT_LEAVE_WINDOW, self.onmouseout, y)
    def onclose(self, event):
        for cont in self.online:
            s = socket(AF_INET, SOCK_STREAM)
            print ('sending offline to'+cont)
            s.connect((self.condata[cont], 4321))
            s.send('offline')
            s.close()
        self.listner.listnershut()
        self.Destroy()
    def oncontact(self, event):
        m = event.GetId()
        con = self.contacts[m]
        add = self.condata[con]
        self.panel.Refresh() 
        usocket = socket(AF_INET, SOCK_STREAM)
        flag = '0'
        self.openim(flag, usocket, add, con)
        event.Skip()
        self.panel.Refresh()
        self.SetFocus()
        event.Skip()    
    def openim(self, flag, socket, address, contact):
        imapp = wx.PySimpleApp()
        frame = imframe2fil.imframe(flag, self, socket, address, contact)
        frame.Show()
        imapp.MainLoop()
    def update(self):
        condatafile = open('condata', 'rb')
        self.condata = cPickle.load(condatafile)
        condatafile.close()
        self.contacts = self.condata.keys()
        self.Refresh()

    def butonupdate(self, contact):
        x = self.contacts.index(contact)
        p = self.buttlist[x].GetPosition()
        (m, n) = p
        i = self.buttlist[x].GetId()
        self.buttlist[x].Destroy()
        self.buttlist[x] = buttons.GenBitmapButton(self.panel, i, textbutton('1', self.contacts[x]).ConvertToBitmap(), pos=p)
        self.Refresh()
        self.online.append(contact)

    def butoffupdate(self, contact):
        x = self.contacts.index(contact)
        p = self.buttlist[x].GetPosition()
        self.online.remove(contact)
        (m, n) = p
        i = self.buttlist[x].GetId()
        self.buttlist[x].Destroy()
        self.buttlist[x] = buttons.GenBitmapButton(self.panel, textbutton('0', self.contacts[x]).ConvertToBitmap(), pos=p)
        self.Refresh()
        
        
            
    #def onmousein(self, event):
    #    but = event.GetEventObject()
     #   but.SetBitmapLabel(self.bmp2)
      #  self.panel.Refresh()
    #def onmouseout(self, event):
     #   but = event.GetEventObject()
      #  but.SetBitmapLabel(self.bmp1)
       # self.panel.Refresh()
    def oneditcon(self, event):
        condatafile = open('condata', 'rb')
        condata = cPickle.load(condatafile)
        condatafile.close()
        app = wx.PySimpleApp()
        frame = conedit(self, condata)
        frame.Show()
        app.MainLoop()

    def onconference(self, event):
        app = wx.PySimpleApp()
        frame = conference.confselect(self, self.condata)
        frame.Show()
        app.MainLoop()
        conference.confselect(self, self.condata)
        
        

    def onrecvfil(self, filsocket, contact):
        print 'got call to recv file'
        recvapp = wx.PySimpleApp()
        alert = wx.MessageDialog(self, contact+"is to trying to send a file a file", 'Alert', wx.YES_NO|wx.ICON_INFORMATION)
        reply = alert.ShowModal()
        if (reply == wx.ID_YES):
            filsocket.send('1')
            filname = filsocket.recv(1024)
            app2 = wx.PySimpleApp()
            wildcard = "All Files (*.*)|*.*"
            filesel = wx.FileDialog(None, 'Choose save location', os.getcwd(), filname, wildcard, wx.OPEN)
            filesel.SetFilename(filname)
            if filesel.ShowModal() == wx.ID_OK:
                x = filesel.GetPath()
                app3 = wx.PySimpleApp()
                frame = filtrans.recvfilwin(filsocket, x)
                frame.Show()
                app3.MainLoop()
            else:
                filsocket.send('0')
                filsocket.close()
        else:
            filsocket.send('0')
            filsocket.close()
            
    
class conedit(wx.Frame):
    def __init__(self, parent, condata):
        wx.Frame.__init__(self, parent, -1, 'Edit Contacts', size=(250,300), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.image = wx.Image("test.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        panel = wx.StaticBitmap(self, -1, self.image)
        self.condata = condata
        self.contacts = self.condata.keys()
        self.parent = parent
        self.conlist = wx.ListBox(panel, -1, (20, 20), (150, 150), self.contacts, wx.LB_SINGLE|wx.LB_NEEDED_SB, name='Contacts')
        editbutt = wx.Button(panel, -1, 'Edit', pos=(20, 220))
        deletebutt = wx.Button(panel, -1, 'Delete', pos=(100, 220))
        addbutt = wx.Button(panel, -1, 'Add Contact', pos=(50, 180))

        self.Bind(wx.EVT_BUTTON, self.edit, editbutt)
        self.Bind(wx.EVT_BUTTON, self.delete, deletebutt)
        self.Bind(wx.EVT_BUTTON, self.add, addbutt)
        self.Bind(wx.EVT_CLOSE, self.onclose)
    def edit(self, event):
        app = wx.PySimpleApp()
        frame = contactinput()
        frame.Show()
        app.MainLoop()
        
    def delete(self, event):
        x = self.conlist.GetSelection()
        y = self.contacts[x]
        del(self.condata[y])
        fil = open('condata', 'wb')
        cPickle.dump(self.condata, fil)
        fil.close()
        self.redraw()
    def add(self, event):
        app = wx.PySimpleApp()
        frame = contactinput(self)
        frame.Show()
        app.MainLoop()
        
    def redraw(self):
        p = self.GetPosition()
        editframeredraw(self, p, self.parent) 
    def onclose(self, event):
        #self.parent.update()
        self.Destroy()
        
class contactinput(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "enter details", size=(330, 150), style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU)
        self.image = wx.Image("test.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.parent = parent
        self.backimage = wx.StaticBitmap(self, -1, self.image)
        self.Bind(wx.EVT_CLOSE, self.onclose)
        wx.StaticText(self.backimage, -1, "NAME", (10, 10))
        wx.StaticText(self.backimage, -1, "COMPUTER NAME OR IP", (10, 70))
        self.name = wx.TextCtrl(self.backimage, -1, "", pos=(200, 10), size=(100, -1))
        self.ip = wx.TextCtrl(self.backimage, -1, "", pos=(200, 70), size=(100, -1))
        
        self.ok = wx.Button(self.backimage, -1, "OK", pos=(10, 100))
        self.cancel = wx.Button(self.backimage, -1, "CANCEL", pos=(200,100))

        self.Bind(wx.EVT_BUTTON, self.okclick, self.ok)
        self.Bind(wx.EVT_BUTTON, self.onclose, self.cancel)

        self.ok.SetDefault()
        
        
    def onclose(self, event):
        self.Destroy()
        self.parent.redraw()
    def okclick(self, event):
        self.nameent = self.name.GetValue()
        self.ipent = self.ip.GetValue()
        if self.nameent != '':
            if self.ipent != '':
                fil = open('condata', 'rb')
                y = cPickle.load(fil)
                x = {self.nameent:self.ipent}
                fil.close()
                y.update(x)
                fil2 = open('condata', 'wb')
                cPickle.dump(y, fil2)
                fil2.close()
                self.parent.redraw()
                self.Destroy()
        else:
            wx.MessageBox('u moron enter something')
                


x = []
condatafile = open('condata', 'rb')
condata = cPickle.load(condatafile)
contacts = condata.keys()
app = wx.PySimpleApp()
frame = mainwin()
frame.Show()
app.MainLoop()


