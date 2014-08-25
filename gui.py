


HelpText = 'check the doc/documentation.html for help'
AboutText = 'Slicer by www.ixi-audio.net'

##try:
import wx
import os
import mirra.utilities
from mirra import tools
##    from mirra.tools import *


#-- menus IDs. constants
ID_OPEN	= wx.NewId()
ID_SAVE	= wx.NewId()
ID_SAVEAS        = wx.NewId()
ID_EXIT	= wx.NewId()
ID_HELP	= wx.NewId()
ID_ABOUT	= wx.NewId()

# ssnapshots menu
ID_OPENSNAP	= wx.NewId()
ID_SAVESNAP	= wx.NewId()
ID_SAVEASSNAP       = wx.NewId()

ID_LOAD0 = wx.NewId()
ID_LOAD1 = wx.NewId()
ID_LOAD2 = wx.NewId()
ID_LOAD3 = wx.NewId()
ID_LOAD4 = wx.NewId()
ID_LOAD5 = wx.NewId()
ID_LOAD6 = wx.NewId()
ID_LOAD7 = wx.NewId()
ID_LOAD8 = wx.NewId()
ID_LOAD9 = wx.NewId()

ID_SAVE0 = wx.NewId()
ID_SAVE1 = wx.NewId()
ID_SAVE2 = wx.NewId()
ID_SAVE3 = wx.NewId()
ID_SAVE4 = wx.NewId()
ID_SAVE5 = wx.NewId()
ID_SAVE6 = wx.NewId()
ID_SAVE7 = wx.NewId()
ID_SAVE8 = wx.NewId()
ID_SAVE9 = wx.NewId()

ID_AUTOPANEL = wx.NewId()
ID_FLOCKPANEL = wx.NewId() 
##    ID_AUTOBOX = wx.NewId()
ID_AUTONODE = wx.NewId()
ID_BOUNCE = wx.NewId()

ID_RANDOM = wx.NewId()
ID_RANDOMBOXES = wx.NewId()
ID_RANDOMNODES = wx.NewId()
ID_RANDOMNODESNOPITCH  = wx.NewId()
ID_RANDOMWHITENODE  = wx.NewId()
ID_RANDOMWHITENODESHORT  = wx.NewId()
ID_RANDOMBLACKNODE  = wx.NewId()

ID_VOL1 = wx.NewId()
ID_VOL2 = wx.NewId()
ID_VOL3 = wx.NewId()
ID_VOL4 = wx.NewId()
ID_VOL5 = wx.NewId()
ID_VOL6 = wx.NewId()
ID_VOL7 = wx.NewId()
ID_VOL8 = wx.NewId()
ID_VOL9 = wx.NewId()
ID_VOL10 = wx.NewId()
ID_MUTE = wx.NewId()

ID_ADDSND = wx.NewId()
ID_ADDFOLDER = wx.NewId()

ID_PITCH1 = wx.NewId() # panels
##ID_GAMEPAD = wx.NewId() # panels    
ID_RESET = wx.NewId() # layers
ID_MICROTONES = wx.NewId()
ID_PITCHLOCK = wx.NewId()
ID_STARTLOCK = wx.NewId()
ID_SHIFTLOC = wx.NewId()
ID_GRAINSHIFT = wx.NewId() 
ID_LENGTHLOC = wx.NewId() 
##            ID_PAN2 = wx.NewId()

ID_NOL1 = wx.NewId()
ID_NOL2 = wx.NewId()
ID_NOL3 = wx.NewId()
ID_NOL4 = wx.NewId()
ID_NOL5 = wx.NewId()
ID_NOL6 = wx.NewId()
ID_NOL7 = wx.NewId()
ID_NOL8 = wx.NewId()

import sys
if sys.platform == 'darwin' :
    modKey = '\tAlt-'
##        modKey = '\tCmd-'
    
else:
    modKey = '\tCtrl-'

        

class MyFrame(mirra.utilities.WxMirraFrame) :

    old_vol = 0 ## class var

    def doFrame(self, canvas) :
        self.panels = { 'pitch' : 0, 'auto' : 0, 'flock' : 0 } #, 'effect1' : 0, 'effect2' : 0 } # one for each panel
##        self.doMenu()
        self.doStructure(canvas)

##            self.Bind(wx.EVT_KEY_DOWN, self.KeyDown)
##            self.Bind(wx.EVT_KEY_UP, self.KeyDown)
##            self.Bind(wx.EVT_CHAR, self.KeyDown)
##            self.panel.SetFocus()
##            
##        def KeyDown(self, event=None) :
##            print "--->", event

    def doMenu(self):
        self.filename = 0
        #wx.Frame.__init__(self, parent, ID, strTitle, pos, tplSize,
        #	wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        #--------------- menu ---------------------------------------------

        #--vFile #
        menu = wx.Menu()
        menu.Append(ID_OPEN, "&Open"+modKey+"O", "open file")
        menu.Append(ID_SAVE, "&Save"+modKey+"S", "save file")
        menu.Append(ID_SAVEAS, "&Save as", "save as file")
        menu.AppendSeparator()
##            menu.Append(ID_EXIT, "&Exit"+modKey+"X", "Terminate the program")
        menu.Append(ID_EXIT, "&Exit"+modKey+"Q", "Terminate the program")


        #--SNAPSHOTS #
        menuSnap = wx.Menu()
        menuSnap.Append(ID_OPENSNAP, "&Open snapshot file", "open file")
        menuSnap.Append(ID_SAVESNAP, "&Save current snapshots", "save file")
        menuSnap.Append(ID_SAVEASSNAP, "&Save As current snapshots", "save as file")

        for n in xrange(10):
            arg2 = ("&Load snapshot %i" + '\tShift-'+"%i") % (n,n)
            arg3 = "load snapshot %i" % n
            menuSnap.Append(500+n, arg2, arg3)

        menuSnap.AppendSeparator() # --------

        for n in xrange(10, 20):
            n2 = n-10
            arg2 = ("&Store snapshot %i" +modKey+"%i") % (n2,n2)
            arg3 = "Store snapshot %i" % n2
            menuSnap.Append(500+n, arg2, arg3)
            
        
         #-- Snd pool #
        menuPool = wx.Menu()
        self.filePool = self.doSndMenu()
        sndIndex=0
        for sndIndex, f in enumerate(self.filePool) :
            menuPool.Append(sndIndex+200, "&"+os.path.basename(f), "snd", wx.ITEM_RADIO )# , wx.ITEM_RADIO)
            
        menuPool.AppendSeparator()
        menuPool.Append(ID_ADDSND, "&add snd"+modKey+"A", "snd")
        menuPool.Append(ID_ADDFOLDER, "&add snd folder", "snd")
        
        #-- master vol #
        vol = wx.Menu()
        vol.Append(ID_MUTE, "&Volume 0"+modKey+"M", "Volume 0",  wx.ITEM_RADIO)
        vol.Append(ID_VOL10, "&Volume 10"+modKey+"0", "Volume 10" , wx.ITEM_RADIO)
        vol.Append(ID_VOL9, "&Volume 9"+modKey+"9", "Volume 9" , wx.ITEM_RADIO)
        vol.Append(ID_VOL8, "&Volume 8"+modKey+"8", "Volume 8" , wx.ITEM_RADIO)
        vol.Append(ID_VOL7, "&Volume 7"+modKey+"7", "Volume 7" , wx.ITEM_RADIO)
        vol.Append(ID_VOL6, "&Volume 6"+modKey+"6", "Volume 6" , wx.ITEM_RADIO)
        vol.Append(ID_VOL5, "&Volume 5"+modKey+"5", "Volume 5" , wx.ITEM_RADIO)
        vol.Append(ID_VOL4, "&Volume 4"+modKey+"4", "Volume 4", wx.ITEM_RADIO)
        vol.Append(ID_VOL3, "&Volume 3"+modKey+"3", "Volume 3" , wx.ITEM_RADIO)
        vol.Append(ID_VOL2, "&Volume 2"+modKey+"2", "Volume 2" , wx.ITEM_RADIO)
        vol.Append(ID_VOL1, "&Volume 1"+modKey+"1", "Volume 1", wx.ITEM_RADIO)

##            ## 0 to 9 mute layers without menu
##            exitId = wx.NewId()
##            self.Bind(wx.EVT_MENU, self.mute1, id=exitId )
##            accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('1'), exitId )])
##            self.SetAcceleratorTable(accel_tbl)
        
        
        # num of layers - NOL
        nol = wx.Menu()
        for n in xrange(1,9) : # one to eight
            nolid = eval('ID_NOL'+str(n))
            nol.Append(nolid, '&'+str(n), "NOL" , wx.ITEM_RADIO)
            
        #-- auto
        menuAuto = wx.Menu()
        menuAuto.Append(ID_FLOCKPANEL, "&flock panel", "flock panel", wx.ITEM_CHECK)
        menuAuto.Append(ID_AUTOPANEL, "&box bounce speed panel", "box bounce speed panel", wx.ITEM_CHECK)
##            menuAuto.Append(ID_AUTOBOX, "&box automovement", "box automovement", wx.ITEM_CHECK)
        menuAuto.Append(ID_AUTONODE, "&toggle node automovement", "toggle node automovement", wx.ITEM_CHECK)
        menuAuto.Append(ID_BOUNCE, "&toggle bounce", "toggle bounce", wx.ITEM_CHECK)

        menuAuto.AppendSeparator() # --------
        menuAuto.Append(ID_RANDOM, "&random situation"+modKey+"R", "random")
        menuAuto.Append(ID_RANDOMBOXES, "&random situation of Boxes"+modKey+"B", "random Boxes")
        menuAuto.Append(ID_RANDOMNODES, "&random situation of Nodes"+modKey+"N", "random Nodes")
        menuAuto.Append(ID_RANDOMNODESNOPITCH, "&random Back & White (no pitch)"+modKey+"V", "random B&W")
        menuAuto.Append(ID_RANDOMWHITENODE, "&random White Node"+modKey+"X", "random White Nodes")
        menuAuto.Append(ID_RANDOMWHITENODESHORT, "&small random White Node"+modKey+"C", "small random White Nodes")
        menuAuto.Append(ID_RANDOMBLACKNODE, "&random Black Node"+modKey+"Z", "random Black Nodes")

        #-- panels
        menuPanels = wx.Menu()
        menuPanels.Append(ID_PITCH1, "&pitch control", "pitch panel", wx.ITEM_CHECK)
        menuPanels.AppendSeparator() # --------
        menuPanels.Append(ID_RESET, "&reset playheads", "reset")
        menuPanels.Append(ID_MICROTONES, "&toogle microtones", "microtones", wx.ITEM_CHECK)
        
        menuPanels.Append(ID_PITCHLOCK, "&lock pitch", "pitch", wx.ITEM_CHECK)
        menuPanels.Append(ID_STARTLOCK, "&lock start", "start", wx.ITEM_CHECK)
        menuPanels.Append(ID_SHIFTLOC, "&loc shift", "shift", wx.ITEM_CHECK)
        menuPanels.Append(ID_LENGTHLOC, "&lock length", "length", wx.ITEM_CHECK)
        menuPanels.Append(ID_GRAINSHIFT, "&lock grain shift", "grain shift", wx.ITEM_CHECK)
        
        #-- About
        menuHelp = wx.Menu()
        menuHelp.Append(ID_HELP, "&Help"+modKey+"H", "help!")
        menuHelp.Append(ID_ABOUT, "&About Slicer", "About")
        
        ##########################
        
        #-- add all to menubar
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File")
        menuBar.Append(menuSnap, "&Snapshots")
        menuBar.Append(menuPool, "&Snd Pool")
        menuBar.Append(vol, "&Volume")
        menuBar.Append(nol, "&Num of layers")
        menuBar.Append(menuAuto, "&Movement")
        menuBar.Append(menuPanels, "&General")
        menuBar.Append(menuHelp, "&Help")
        self.SetMenuBar(menuBar) #-- set bar

        
        #-- set IDs and functions
        # file menu
        wx.EVT_MENU(self, ID_OPEN, self.onOpen)
        wx.EVT_MENU(self, ID_SAVE, self.onSave)
        wx.EVT_MENU(self, ID_SAVEAS, self.SaveAs)
        wx.EVT_MENU(self, ID_EXIT,  self.onQuit)

        # snapshots
        wx.EVT_MENU(self, ID_OPENSNAP, self.onOpenSnap)
        wx.EVT_MENU(self, ID_SAVESNAP, self.onSaveSnap)
        wx.EVT_MENU(self, ID_SAVEASSNAP, self.SaveAsSnap)
        self.Bind(wx.EVT_MENU, self.loadSnapshot, id=500, id2=519) # TODO
        
        # snd pool menu
        self.Bind(wx.EVT_MENU, self.loadSnd, id=200, id2=sndIndex+200)
        wx.EVT_MENU(self, ID_ADDSND, self.onAddSnd)
        wx.EVT_MENU(self, ID_ADDFOLDER, self.onAddSndFolder)
        
        # NOL
        wx.EVT_MENU(self, ID_NOL1, self.onNol1)
        wx.EVT_MENU(self, ID_NOL2, self.onNol2)
        wx.EVT_MENU(self, ID_NOL3, self.onNol3)
        wx.EVT_MENU(self, ID_NOL4, self.onNol4)
        wx.EVT_MENU(self, ID_NOL5, self.onNol5)
        wx.EVT_MENU(self, ID_NOL6, self.onNol6)
        wx.EVT_MENU(self, ID_NOL7, self.onNol7)
        wx.EVT_MENU(self, ID_NOL8, self.onNol8)
        
        # auto
        wx.EVT_MENU(self, ID_AUTOPANEL, self.onAutoPanel)
        wx.EVT_MENU(self, ID_FLOCKPANEL, self.onFlockPanel) 
##            wx.EVT_MENU(self, ID_AUTOBOX, self.onAutoBox)
        wx.EVT_MENU(self, ID_AUTONODE, self.onAutoNode)
        wx.EVT_MENU(self, ID_BOUNCE, self.onBounce)

        wx.EVT_MENU(self, ID_RANDOM, self.random)
        wx.EVT_MENU(self, ID_RANDOMBOXES, self.randomBoxes)
        wx.EVT_MENU(self, ID_RANDOMNODES, self.randomNodes)
        wx.EVT_MENU(self, ID_RANDOMNODESNOPITCH, self.randomNodesNoPitch)
        wx.EVT_MENU(self, ID_RANDOMWHITENODE, self.randomWhiteNode)
        wx.EVT_MENU(self, ID_RANDOMWHITENODESHORT, self.randomWhiteNodeShort)
        wx.EVT_MENU(self, ID_RANDOMBLACKNODE, self.randomBlackNode)

        # general
        wx.EVT_MENU(self, ID_PITCH1, self.pitch1)
##        wx.EVT_MENU(self, ID_GAMEPAD, self.gamepad)
        wx.EVT_MENU(self, ID_RESET, self.reset)
        wx.EVT_MENU(self, ID_MICROTONES, self.microtones)

        wx.EVT_MENU(self, ID_PITCHLOCK, self.pitchlock)
        wx.EVT_MENU(self, ID_STARTLOCK, self.startlock)
        wx.EVT_MENU(self, ID_SHIFTLOC, self.shiftlock)
        wx.EVT_MENU(self, ID_LENGTHLOC, self.lengthlock)
        wx.EVT_MENU(self, ID_GRAINSHIFT, self.grainshiftlock)
        
        # help
        wx.EVT_MENU(self, ID_HELP,  self.onHelp)
        wx.EVT_MENU(self, ID_ABOUT, self.onAbout)
        
        # vol
        wx.EVT_MENU(self, ID_MUTE, self.onVol0)
        wx.EVT_MENU(self, ID_VOL1, self.onVol1)
        wx.EVT_MENU(self, ID_VOL2, self.onVol2)
        wx.EVT_MENU(self, ID_VOL3, self.onVol3)
        wx.EVT_MENU(self, ID_VOL4, self.onVol4)
        wx.EVT_MENU(self, ID_VOL5, self.onVol5)
        wx.EVT_MENU(self, ID_VOL6, self.onVol6)
        wx.EVT_MENU(self, ID_VOL7, self.onVol7)
        wx.EVT_MENU(self, ID_VOL8, self.onVol8)
        wx.EVT_MENU(self, ID_VOL9, self.onVol9)
        wx.EVT_MENU(self, ID_VOL10, self.onVol10)

        

    #-------- menu ---------------------------------------------

    # change volume
    def onVol0(self, event): self.app.vol = 0
    def onVol1(self, event): self.app.vol = 0.1 
    def onVol2(self, event): self.app.vol = 0.2 
    def onVol3(self, event): self.app.vol = 0.3 
    def onVol4(self, event): self.app.vol = 0.4
    def onVol5(self, event): self.app.vol = 0.5 
    def onVol6(self, event): self.app.vol = 0.6 
    def onVol7(self, event): self.app.vol = 0.7 
    def onVol8(self, event): self.app.vol = 0.8 
    def onVol9(self, event): self.app.vol = 0.9 
    def onVol10(self, event): self.app.vol = 1

    # change num of layers
    def onNol1(self, event): self.nol(1) 
    def onNol2(self, event): self.nol(2) 
    def onNol3(self, event): self.nol(3)  
    def onNol4(self, event): self.nol(4) 
    def onNol5(self, event): self.nol(5)  
    def onNol6(self, event): self.nol(6)  
    def onNol7(self, event): self.nol(7) 
    def onNol8(self, event): self.nol(8)

##        # mute layers
##        def mute1(self, event): self.app.boxList[0].mute()
##        def mute2(self, event): self.app.boxList[1].mute()
##        def mute3(self, event): self.app.boxList[2].mute()
##        def mute4(self, event): self.app.boxList[3].mute()
##        def mute5(self, event): self.app.boxList[4].mute()
##        def mute6(self, event): self.app.boxList[5].mute()
##        def mute7(self, event): self.app.boxList[6].mute()
##        def mute8(self, event): self.app.boxList[7].mute()


    def nol(self, n) :
        self.app.numOfLayers = n # event.GetId()
        self.app.redoLoopers() 
        self.app.startLayers(n, reset=0)
       

    def onQuit(self, event) :
        self.Close(True)
        self.Destroy()
        
    def onHelp(self, event) :
        dlg = wx.MessageDialog(self, HelpText,
            "Help", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def onAbout(self, event):
        dlg = wx.MessageDialog(self, AboutText,
            "About this app", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    #----
    def startMenus(self) :
        """ make sure that menus display the details from startup proferences
        """
        mb = self.GetMenuBar()
        mb.FindItemById(ID_AUTONODE).Check(self.app.autoNodes) 
        mb.FindItemById(ID_MICROTONES).Check(self.app.microtones)
        mb.FindItemById(eval('ID_NOL'+str(self.app.numOfLayers))).Check(True)
        
        if self.app.vol == 0 : # muted vol was 0
            mb.FindItemById(ID_VOL10).Check(self.app.microtones)
        else :
            mb.FindItemById(eval('ID_VOL'+str(int(self.app.vol*10)))).Check(self.app.microtones)
                
    #-----
    def onOpen(self, event):
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open file", mirra.utilities.get_main_dir(),
            style=wx.OPEN, wildcard = wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.readFile()
            self.insertSnd(self.filename)
        dlg.Destroy()

    

    def readFile(self) :
        print "----> reading session data from file"
        if self.filename == '' or not self.filename: return -1
        
        try :
            f = open(mirra.utilities.getabspath(self.filename), 'rU')
            rawdata = f.read()
        except  IOError :
            print "ERROR : file %s does not exist" % self.filename
            return -1
##            data = data.replace('\n', '') # get rid of possible line breaks in string
##            try : 
##            data = eval(data) # get the dictionary from the string
##            except :
##                print 'there was an error reading the file'
##                return -1
        self.app.setSession(rawdata)

    def onImport(self, event):
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Import file",  mirra.utilities.get_main_dir(),
            style=wx.OPEN, wildcard = wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        dlg.Destroy()

    def onAddSnd(self, event):
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Add sound file",  mirra.utilities.get_main_dir(),
            style=wx.OPEN, wildcard = wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.insertSnd(path)
        dlg.Destroy()

    def insertSnd(self, path) :
        mb = self.GetMenuBar()
##        item = mb.Append(-1, os.path.basename(path))
##        item.SetId( len(self.filePool) + 200 )
##        self.Bind(wx.EVT_MENU, self.loadSnd, item)
####        sndmenu.InsertItem(0, item)
##        self.filePool.append(str(path)) # update snd pool           

        first = mb.FindItemById(200) # get first sound item
        sndmenu = first.GetMenu() # get snd menu
        
        item = wx.MenuItem(sndmenu)# , wx.ITEM_RADIO) # new item
        item.SetId( len(self.filePool) + 200 )
        item.SetText(os.path.basename(path))
        self.Bind(wx.EVT_MENU, self.loadSnd, item)
        sndmenu.InsertItem(0, item)
        self.filePool.append(str(path)) # update snd pool

    def onAddSndFolder(self, event) :
        dlg = wx.DirDialog(self, "Add all sounds in directory",  mirra.utilities.get_main_dir(), style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            for root, dirs, files in os.walk(path) :
                for s in files :
                    self.insertSnd(os.path.join(root, s))
        dlg.Destroy()

    def onSave(self, event):
        if not self.filename:
            self.SaveAs(event)
        else:
            self.SaveFile()

    def SaveAs(self, event):
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Save as", mirra.utilities.get_main_dir(),
            style=wx.SAVE | wx.OVERWRITE_PROMPT,
            wildcard = wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.txt'
            self.filename = filename
            self.SaveFile()
        dlg.Destroy()

    def SaveFile(self) :
        data = self.app.getSessionJSON()
        savedata = open(self.filename, 'w')
        savedata.write(str(data))
        savedata.close()

    def doSndMenu(self) :
        l = []
        p = os.path.join( mirra.utilities.get_main_dir(), 'sounds')
            
        for dirpath, dirnames, fname in os.walk(p) :
            for f in fname :
                if f[0] != '.' : # mac .DS_Store and other hidden files
##                        if dirname[0]  != '.' : # SVN folders on linux and hidden folders in general
                    l.append( os.path.join(dirpath, f) )
        return l

    ## snapshot stuff
    def onOpenSnap(self, event):
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open file", mirra.utilities.get_main_dir(),
            style=wx.OPEN, wildcard = wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            print "----> reading snapshots data from file"
            if self.filename == '' or not self.filename: return -1
            
            try :
                f = open(mirra.utilities.getabspath(self.filename), 'rU')
                rawdata = f.read()
            except  IOError :
                print "ERROR : file %s does not exist" % self.filename
                return -1
            
            self.app.loadSnapshots(rawdata)
##            self.insertSnd(self.filename)
        dlg.Destroy()

    def loadSnapshot(self, e) :
        try :
            if e.GetId()-500 < 10:
                self.app.setSnapshot(e.GetId()-500) #SET
            else :
                self.app.storeSnapshot(e.GetId()-510) # STORE
        except KeyError:
            print "error: sthere is no such snapshot"
        
    def onSaveSnap(self, event):
        if not self.filename:
            self.SaveAsSnap(event)
        else:
            self.SaveSnap()

    def SaveSnap(self) :
        data = self.app.getSnapshotJSON()
        savedata = open(self.filename, 'w')
        savedata.write(str(data))
        savedata.close()

    def SaveAsSnap(self, event):
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Save as", mirra.utilities.get_main_dir(),
            style=wx.SAVE | wx.OVERWRITE_PROMPT,
            wildcard = wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.txt'
            self.filename = filename
            self.SaveSnap()
        dlg.Destroy()

    
    
##    def gamepad(self, e) : print 'open gamepad conf panel'
    def reset(self, e) : self.app.resetplayheads()
    def onAutoNode(self, e) : self.app.autoNodes = not self.app.autoNodes
    def onBounce(self, e) : self.app.bounce = not self.app.bounce  # ; print self.app.bounce
##        def onToggleMove(self, e) : self.app.toogleMove() 
    def random(self, e) : self.app.randomSituation()
    def randomBoxes(self, e) : self.app.randomBoxes()
    def randomNodes(self, e) : self.app.randomNodes()
    def randomNodesNoPitch(self, e) : self.app.randomNodes(1)
    def randomWhiteNode(self, e) : self.app.randomSingleNode('white')
    def randomWhiteNodeShort(self, e) : self.app.randomSingleNode('white', 1)
    def randomBlackNode(self, e) : self.app.randomSingleNode('black')
    
    def swapSnd(self, e) :
        self.app.swapSndPath( str( self.filePool[ e.GetId()-200 ] ) )
    def loadSnd(self, e) :
        print "filepool element", self.filePool[ e.GetId()-200 ] 
        self.app.loadSnd( str( self.filePool[ e.GetId()-200 ] ) )

    def microtones(self, e) :
        self.app.microtones = e.GetInt()
    def pitchlock(self, e) :
        self.app.freedom[ 'pitch' ] = not e.GetInt() #  1 is free, 0 is locked
    def startlock(self, e) :
        self.app.freedom[ 'start' ] = not e.GetInt()
    def shiftlock(self, e) :
        self.app.freedom[ 'shift' ] = not e.GetInt()
    def lengthlock(self, e) :
        self.app.freedom[ 'length' ] = not e.GetInt()
    def grainshiftlock(self, e) :
        self.app.freedom[ 'grainshift' ] = not e.GetInt()



########################
### panels #
########################
    def pitch1(self, e) :
        if not self.panels[ 'pitch' ] : # open only one panel
            p = Panel_1( self,  -1, "pitch", size=(160, 165) )
            p.setProperties(self.app)
            p.Show(True)
            self.panels[ 'pitch' ] = p

    def onAutoPanel(self, e) :
        if not self.panels[ 'auto' ] : # open only one panel
            p = Panel_Auto( self,  -1, "bounce", size=(120, 60) )
            p.setProperties(self.app)
            p.Show(True)
            self.panels[ 'auto' ] = p

    def onFlockPanel(self, e) :
        if not self.panels[ 'flock' ] : # open only one panel
            p = Panel_Flock( self,  -1, "flock", size=(185, 175) )
            p.setProperties(self.app)
            p.Show(True)
            self.panels[ 'flock' ] = p

class MirraWxPanel(wx.Frame) :
    """ general panel
    """
    def __init__(self, *args, **kwds) :
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.STAY_ON_TOP|wx.SYSTEM_MENU|wx.RESIZE_BORDER|wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.doWidgets()

    def doWidgets(self) : pass
    def setProperties(self, a) : self.app = a




class Panel_1(MirraWxPanel) :
    """ controls apllication pitch ranges """
    def doWidgets(self) :
        self.spin_1 = tools.FloatSpin( self, -1, pos=(10, 10), size=(65, -1), min=-50, max=50, increment=0.1, digits=3 )
        self.spin_2 = tools.FloatSpin( self, -1, pos=(10, 40), size=(65, -1), min=-50, max=50, increment=0.1, digits=3 )
        self.spin_3 = tools.FloatSpin( self, -1, pos=(10, 70), size=(65, -1), min=-50, max=50, increment=0.1, digits=3 )
        self.label_1 = wx.StaticText( self, -1, "top",  pos=(80, 10) )
        self.label_2 = wx.StaticText( self, -1, "middle", pos=(80, 40) )
        self.label_3 = wx.StaticText( self, -1, "bottom" , pos=(80, 70) )
        self.button_1 = wx.Button( self, -1, "update values" , pos=(10, 100), size=(120, 30) )

        self.Bind( tools.EVT_FLOATSPIN, self.spinevent1, self.spin_1 )
        self.Bind( tools.EVT_FLOATSPIN, self.spinevent2, self.spin_2 )
        self.Bind( tools.EVT_FLOATSPIN, self.spinevent3, self.spin_3 )
        self.Bind( wx.EVT_BUTTON, self.update, self.button_1 )

    def setProperties(self, a) :
        self.app = a
        self.pitchLimits = [ self.app.pitchLimits[0], self.app.pitchLimits[1], self.app.pitchLimits[2] ]
        for i, p in enumerate(self.pitchLimits) : eval('self.spin_'+str(i+1)).SetValue(p)

    def spinevent1(self, event): # wxGlade: MyPanel.<event_handler>
        n = self.spin_1.GetValue()
        n.set_precision(3)
        self.pitchLimits[0] = n
        event.Skip()

    def spinevent2(self, event): # wxGlade: MyPanel.<event_handler>
        n = self.spin_2.GetValue()
        n.set_precision(3)
        self.pitchLimits[1] = n
        event.Skip()
        
    def spinevent3(self, event): # wxGlade: MyPanel.<event_handler>
        n = self.spin_3.GetValue()
        n.set_precision(3)
        self.pitchLimits[2] = n
        event.Skip()
            
    def update(self, event) :
        self.app.pitchLimits = self.pitchLimits[:] # copy!!
        self.app.updatePitchLimits()
        event.Skip()
        
        

class Panel_Auto(MirraWxPanel) :
    """ controls auto movement variables """
    def doWidgets(self) :
        self.spin_1 = tools.FloatSpin(self, -1, size=(65, -1), pos=(5, 5), min=0, max=999, increment=1, digits=0)
        self.label_1 = wx.StaticText(self, -1, "speed", pos=(80,5))

        self.Bind(tools.EVT_FLOATSPIN, self.spinevent1, self.spin_1)

    def setProperties(self, a) :
        """ set properties of spins externally
        """
        self.app = a
        self.spin_1.SetValue(self.app.boxStep)

    def spinevent1(self, event): # wxGlade: MyPanel.<event_handler>
        n = self.spin_1.GetValue()
        n.set_precision(4)
        self.app.boxStep = n.n*0.0001
        self.app.updateBoxDelta()
        event.Skip()



class Panel_Flock(MirraWxPanel) :
    """ controls Flock movement variables """
    def doWidgets(self) :
        self.toggle = wx.ToggleButton(self,  -1, "flock", pos=(5, 5), size=(165, 25))
        self.spin_1 = tools.FloatSpin(self, -1, size=(65, -1), pos=(5, 35), min=0, max=999, increment=1, digits=0)
        self.label_1 = wx.StaticText(self, -1, "follow flock", pos=(80,40))
        self.spin_2 = tools.FloatSpin(self, -1, size=(65, -1), pos=(5, 55), min=0, max=999, increment=1, digits=0)
        self.label_2 = wx.StaticText(self, -1, "repulsion", pos=(80,60))
        self.spin_3 = tools.FloatSpin(self, -1, size=(65, -1), pos=(5, 75), min=0, max=999, increment=1, digits=0)
        self.label_3 = wx.StaticText(self, -1, "match speed", pos=(80,80))
        self.spin_4 = tools.FloatSpin(self, -1, size=(65, -1), pos=(5, 95), min=0, max=999, increment=1, digits=0)
        self.label_4 = wx.StaticText(self, -1, "follow mouse", pos=(80,100))
        self.spin_5 = tools.FloatSpin(self, -1, size=(65, -1), pos=(5, 115), min=0, max=999, increment=1, digits=0)
        self.label_5 = wx.StaticText(self, -1, "max speed", pos=(80,120))

        self.Bind(wx.EVT_TOGGLEBUTTON, self.toggleevent1, self.toggle)
        self.Bind(tools.EVT_FLOATSPIN, self.spinevent1, self.spin_1)
        self.Bind(tools.EVT_FLOATSPIN, self.spinevent2, self.spin_2)
        self.Bind(tools.EVT_FLOATSPIN, self.spinevent3, self.spin_3)
        self.Bind(tools.EVT_FLOATSPIN, self.spinevent4, self.spin_4)
        self.Bind(tools.EVT_FLOATSPIN, self.spinevent5, self.spin_5)

    def setProperties(self, a) :
        """ set properties of spins externally
        """
        self.app = a
        self.toggle.SetValue(self.app.flock)
        self.spin_1.SetValue(self.app.followtheflockF*100)
        self.spin_2.SetValue(self.app.avoidothersF*10000)
        self.spin_3.SetValue(self.app.matchyrspeedF*1000)
        self.spin_4.SetValue(self.app.followmouse)
        self.spin_5.SetValue(self.app.maxspeed)

    def toggleevent1(self, event) :
        self.app.flock = self.toggle.GetValue()
        if self.app.flock :
            self.toggle.SetBackgroundColour( wx.Colour(255,0,0) )
        else :
            self.toggle.SetBackgroundColour( wx.Colour(210,210,210) )
            self.app.boxStep = 0

    def spinevent1(self, event) : # wxGlade: MyPanel.<event_handler>
        n = self.spin_1.GetValue()
        n.set_precision(4)
        self.app.followtheflockF = n.n*0.01
        event.Skip()
        
    def spinevent2(self, event): # wxGlade: MyPanel.<event_ha\ndler>
        n = self.spin_2.GetValue()
        n.set_precision(4)
        self.app.avoidothersF = n.n*0.0001
        event.Skip()
        
    def spinevent3(self, event): # wxGlade: MyPanel.<event_handler>
        n = self.spin_3.GetValue()
        n.set_precision(4)
        self.app.matchyrspeedF = n.n*0.001
        event.Skip()
        
    def spinevent4(self, event): # wxGlade: MyPanel.<event_handler>
        n = self.spin_4.GetValue()
        n.set_precision(4)
        self.app.followmouse = n.n
        event.Skip()
        
    def spinevent5(self, event): # wxGlade: MyPanel.<event_handler>
        n = self.spin_5.GetValue()
        n.set_precision(4)
        self.app.maxspeed = n.n
        event.Skip()






##except ImportError:
##    print 'Mirra > gui.py : ImportError, no wx.python found.'







