#!/usr/bin/env python

##from __future__ import print_function
from mirra import main
from mirra import utilities
from handlers import *

from time import sleep
import json
import os

from pyo import OscDataReceive, RawMidi

import audio
import qtgui # QT GUI menus



""" slicer
http://www.ixi-software.net
License : GPL ->  Read doc/documentation.html
"""



class Slicer(main.App) :
    """ main appplication class, handles window contains events and graphics manager.
        Subclasses main.App and extends its public methods
    """

    def setUp(self) :
        """ set here the main window properties and characteristics, JUST DEFAUT ONES IN THIS CASE
        """
        self.caption = "Slicer" # window name
        #self.inversepan = 0

        self.readSetUpPrefs()

##    def toggleOSCControl(self):
##        self.remoteControl = not self.remoteControl

    def toogleLoadSnapMode(self):
        self.loadsnapshotboxes = not self.loadsnapshotboxes

##    # OSC control nodes
##    def greyJump(self, address, *args):
##        self.handles['grey'].jump(args[1][0], args[1][1])
##
##    def greyPos(self, address, *args):
##        self.handles['grey'].pos(args[1][0], args[1][1])
##
##    def whiteJump(self, address, *args):
##        self.handles['white'].jump(args[1][0], args[1][1])
##
##    def whitePos(self, address, *args):
##        self.handles['white'].pos(args[1][0], args[1][1])
##
##    def blackJump(self, address, *args):
##        self.handles['black'].jump(args[1][0], args[1][1])
##
##    def blackPos(self, address, *args):
##        self.handles['black'].pos(args[1][0], args[1][1])
##        
    def setOSC(self):
        OscDataReceive(port=9001, address='/grey/jump', function=self.greyJump)
        
##        initOSCServer('127.0.1', 9001) # takes args : ip, port, mode --> 0 for basic server, 1 for threading server, 2 for forking server
##
##        setOSCHandler('/grey/jump', self.greyJump)
##        setOSCHandler('/grey/pos', self.greyPos)
##        setOSCHandler('/white/jump', self.whiteJump)
##        setOSCHandler('/white/pos', self.whitePos)
##        setOSCHandler('/black/jump', self.blackJump)
##        setOSCHandler('/black/pos', self.blackPos)

##        setOSCHandler('/axis/1',    self.hid_vertical_0)
##        setOSCHandler('/axis/0',    self.hid_horizontal_0)
##        setOSCHandler('/axis/3',    self.hid_vertical_1)
##        setOSCHandler('/axis/2',    self.hid_horizontal_1)
##        setOSCHandler('/buttonDown/0',        self.hid_down_1)
##        setOSCHandler('/buttonDown/2',        self.hid_down_3)
##        setOSCHandler('/buttonDown/9',        self.hid_down_9)        

##        startOSCServer() # and now set it into action

##    # OSC messages to control de handles from HID device
##    def hid_vertical_0(self, addr, tags, data, source):
##        self.handles['black'].delta[1] = data[0] * 2.5
##    def hid_horizontal_0(self, addr, tags, data, source):
##        self.handles['black'].delta[0] = data[0] * 2.5
##    def hid_vertical_1(self, addr, tags, data, source):
##        self.handles['white'].delta[1] = data[0] * 2.5
##    def hid_horizontal_1(self, addr, tags, data, source):
##        self.handles['white'].delta[0] = data[0] * 2.5

# MIDI
    def midievent(self, status, channel, value):
        print("midi", channel, value)
        if channel==16:
            print(value)
        
    def hid_down_1(self, addr, tags, data, source):
        self.randomSingleNode('white', 1)
    def hid_down_3(self, addr, tags, data, source):
        self.randomSingleNode('black', 1)
    def hid_down_9(self, addr, tags, data, source):
        self.remoteControl = not self.remoteControl
            
    # change number of layers
    def nol(self, n) :
        self.numOfLayers = n 
        self.redoLoopers()
        self.startLayers(n, reset=0)
        self.startHandlers()
        self.forceUpdate()

    def saveSession(self, filepath=None) :
        """ saves the sesion data as json into a txt file with the time name
        """
        data = self.getSessionJSON()
        print("save session", filepath)
        savedata = open(filepath, 'w')
        savedata.write(str(data))
        savedata.close()
        
######## open and save session files #############################


    def setSlicerPrefs(self) :
        ''' read from the variable the prefs that were already loaded by mirra
        {"setup": {"fullscreen": false, "framerate": 8, "pos": [0, 0], "size": [1024, 768]},
        "start": {"bgColor": [0.7, 0.7, 0.7], "mouseVisible": true}, "slicer": {"session": "long1.txt"},
        "audio": {"jack": false, "samplerate": 44100}}
        '''
        # it is already loaded by mirra
##        self.verbose =  self.jsondata['scsynth']['verbose']  # print msgs to audio engine True / False
##        self.spew =  self.jsondata['scsynth']['spew']  # print audio engine answers True / False
        self.jack = self.jsondata['audio']['jack'] 
        self.samplerate = self.jsondata['audio']['samplerate'] 
        qtgui.fileName = self.jsondata['slicer']['session']
        self.constrain = self.jsondata['slicer']['constrain']


    # SNAPSHOTS
    def getCurrentSnapshot(self):
        # but not json in this case
        data = { 'layers' : [], 'nodes' : {}}
        
        for b in self.boxList :
             data['layers'].append( (b.x, b.y, b.looper.pointer.mul) )

        data[ 'nodes' ]['black'] = self.handles['black'].x, self.handles['black'].y
        data[ 'nodes' ]['white'] = self.handles['white'].x, self.handles['white'].y
        data[ 'nodes' ]['grey'] = self.handles['grey'].x, self.handles['grey'].y

        print("current snapshot", data)
        
        return data


    def getSnapshotJSON(self):
        """ returns json of the current snapshot set in memory
        """
        return json.dumps(self.snapshotData)


    def loadSnapshots(self, rawdata):
        """ loads json data containing 10 snapshots into self.snapshotData for later access
        """
        try :
            jdata = json.loads(rawdata) # json decode
        except :
            print("ERROR parsing json snapshot data")
            return -1

        self.snapshotData = jdata
##        print 'load json snapshots from file', self.snapshotData

    def storeSnapshot(self, index):
        """ sets selected snapshot from currently loaded snapshots
        """
        self.snapshotData["snapshot%s" % index] = self.getCurrentSnapshot()
        
        
    def setSnapshot(self, index):
        """ sets selected snapshot from currently loaded snapshots
        """
        jdata = self.snapshotData["snapshot%s" % index]
        
        self.numOfLayers = len( jdata['layers'] )

        if self.loadsnapshotboxes:
            for box, d in zip(self.boxList, jdata['layers']) :
                box.x, box.y, box.looper.pointer.mul = d
                box.updateLooper() # update
                box.moveLabel() 
 
        self.handles['white'].x, self.handles['white'].y = jdata[ 'nodes' ]['white']
        self.handles['grey'].x, self.handles['grey'].y = jdata[ 'nodes' ]['grey']

        self.forceUpdate()


    # SESSIONS

    def getSessionJSON(self):
        """ returns current state from the application in JSON format
        called from gui.py on saving a session file
        """
        data = { 'layers' : [], 'nodes' : {}}
        
        for b in self.boxList :
             data['layers'].append( (b.x, b.y, b.looper.pointer.mul) )

        data[ 'sndFile' ] = self.sndFile # self.snd[ 'file' ]  ##! CORRECT ??
        data[ 'sndPath' ] = self.sndPath
        data[ 'microtones' ] = self.microtones
        data[ 'vol' ] = self.vol
        data[ 'pitchLimits' ] = self.pitchLimits
        data[ 'nodes' ]['black'] = self.handles['black'].x, self.handles['black'].y
        data[ 'nodes' ]['white'] = self.handles['white'].x, self.handles['white'].y
        data[ 'nodes' ]['grey'] = self.handles['grey'].x, self.handles['grey'].y
        data[ 'boxStep' ] = self.boxStep 
        data[ 'freedom' ] = self.freedom 
        data[ 'initRand' ] = self.initRand
        data['autoNodes'] = self.autoNodes

        data['sndfolders'] = qtgui.sndfolders

        data['winSize'] = self.size
                
        return json.dumps(data)

    def setSession(self, rawdata) :
        """ sets new application state from data taken from session file
        called from gui.py on open session file
        """
        try :
            jdata = json.loads(rawdata) # json decode
        except :
            print("ERROR parsing json session data")
            return -1

        #print 'setting json session', jdata

        self.sndFile = str( jdata[ 'sndFile' ] )  #
        self.loadSnd( self.sndFile )

        try:
            self.sndPath = str( jdata[ 'sndPath' ] )
        except :
            self.sndPath = ""
            print("no sndPath in session file")
        
        # **** display changes in GUI menus as well!! *****
        self.microtones = jdata[ 'microtones' ]  
        self.pitchLimits = jdata[ 'pitchLimits' ]
        self.boxStep = float(jdata[ 'boxStep' ])
        self.numOfLayers = len( jdata['layers'] )
        self.freedom = jdata[ 'freedom' ]
        self.initRand = jdata[ 'initRand' ]

        try:
            self.loadsnapshotboxes = jdata[ 'loadsnapshotboxes' ]
        except:
            print("no loadsnapshotsboxes in session file")

        try :
            self.autoNodes =  jdata[ 'autoNodes' ]
        except :
            print("no autoNodes set in this session.. skiping...")

        try:
            if jdata['winSize'] != self.size :
                print("WARNING: this session works well with a window size of %" % jdata['winSize'])
        except:
            pass # silently skip. for backwards compatibility
            
        self.drawZero() # update display

        self.vol = jdata[ 'vol' ] # !! just before updating volume in loopers, otherwise there is a burst of snd

        self.updatePitchLimits()
        self.redoLoopers() 	 

        self.startLayers( self.numOfLayers )
        self.startHandlers()

        for box, d in zip(self.boxList, jdata['layers']) :
            box.x, box.y, box.looper.pointer.mul = d
            box.updateLooper() # update
            box.moveLabel() 
        
        self.handles['black'].x, self.handles['black'].y = jdata[ 'nodes' ]['black'] 
        self.handles['white'].x, self.handles['white'].y = jdata[ 'nodes' ]['white']
        self.handles['grey'].x, self.handles['grey'].y = jdata[ 'nodes' ]['grey']

        self.forceUpdate()
     
        try:
            for folder in jdata[ 'sndfolders' ]:
                qtgui.addFolder(folder)
        except :
            print("no sndfolders stored in this session.. skiping...")

    def forceUpdate(self):
        for h in self.handles.values() :
            h.updateVars()
                        
        h.updateDisplays() # last one does the job


        
##########################################################

            
## initialisation stuff ##########################################
        
    def start(self) :
        """ general application startup
        define properties, read prefs, open audio engine and init audio, create all objects,
        init qt interface.
        """
        qtgui.do(self, self.window)

        # internal variables not set by user
        self.boxList = []
        self.handles = {} # []
        self.displayList = []
        self.selected = 0
##        self.joystate = [] # stores joysticks button combinations
##        self.joyactions = { "inc" : 4,
##                            "dec" : 5,
##                            "fast": 6
##                           } # maps keyboard buttons to actions
        self.loopers = []
        self.grain = 0 # lenght of layers
        self.grainshift = 0 # shift in the length
        self.sttime = 0 # starting time of first layer
        self.shift = 0 # shift inc delta
        self.pitch = 0 # snd pitch
        self.sndLength = 0 # lenght of sound in millisecs. Just for display purposes
        self.displayPitch = 0 # to display

        # GENERAL APP VARIABLES # MIGHT be owewriten by prefs file !!!!*****
##        self.session = 0
        self.sndFile = 'numeros.wav' # ??
        self.sndPath = ""
        self.boxStep = 0  # boxes automovement
        self.autoNodes = 0
        self.microtones = 1
        self.vol = 1    # volume
        self.numOfLayers = 8 
        self.samplerate = 48000 # snd card sample rate 
        self.pitchLimits = [ 3.0, 1, -1 ] # top, middle of screen and bottom
        self.selection = 0
        self.initRand = 0
        self.freedom = { 'pitch' : 1, 'length' : 1, 'shift' : 1, 'start' : 1, 'grainshift' : 1} # to lock them
        self.keyPressed = 0
        self.windDir = 0,0
        self.bounce = 1
        self.drawZeroY = 0
        self.drawOneY = 0

        self.constrain = 0, 0, self.size[0], self.size[1]
        self.remoteControl = False
        self.inversepan = 0

##        # flock
##        self.flock = 0
##        self.followtheflockF = 0.01
##        self.avoidothersF = 0.0003
##        self.matchyrspeedF = 0.001
##        self.followmouse = 0
##        self.maxspeed = 7

        self.snapshotData = {}
        self.loadsnapshotboxes = True

        ## end declaring variables ############

        # they already were loaded since they are located in the prefs.tx json file
        # so we just need to set them
        self.setSlicerPrefs( ) # general window prefs

        self.launchAudio()

        self.startLayers( self.numOfLayers )
        self.startHandlers()

        self.setWindowProps() # becausesomething wrong in windows does not set the bgcolor

        # trying to load session from prefs.txt
        if qtgui.fileName != 0 and qtgui.fileName != None : # if a session was specified
            filename = utilities.getabspath( qtgui.fileName )
            qtgui.fileName = utilities.getabspath(filename) #FOR QT
            print("----> reading session data from file", filename)
            try :
                rawdata = open(utilities.getabspath(filename), 'tr').read()
                self.setSession(rawdata)
            except  IOError :
                print("ERROR : file %s does not exist" %  filename)

        self.doSndList()
##        self.setOSC()
        RawMidi(self.midievent)
        print("done init ----------------------")

        
    def launchAudio(self) :
        self.loopers = []

        audio.startServer( self.samplerate, self.jack )
        print("starting audio server: samplerate %s, jack %s" % ( self.samplerate, self.jack ))
##        self.loadSnd(self.sndFile)
        audio.amp(0)
        length, stereo = audio.createTable(self.sndFile)

        for b in range( self.numOfLayers ) : #buffers 1000-1007
            looper = audio.SlicerPlayer(stereo, b)
            looper.vol(0)
            self.loopers.append( looper )
        print("done lauching audio server")
        audio.amp(self.vol)


    def loadSnd(self, filename) : # from launchAudio and from setSession        
        self.sndFile = filename # in case it was triggered from menu
        audio.amp(0)
        self.sndLength, stereo = audio.createTable(filename)
        for p in self.loopers :
            p.updatetable()
        audio.amp(self.vol)
            

    def startLayers(self, n, reset=1) :
        """ instantiates basic graphical GUI objects
        """        
        try : # kill all interface all instances
            print('restarting interface')
            for o in self.boxList : o.end()
            for o in self.handles.values() : o.end() # handles is prop list
            for o in self.displayList : o.end()
            self.selection.end()
            self.windCircle.end()
        except :
            print('starting up, no interface yet')

        self.boxList = []
##        self.handles = {}
        self.displayList = []
        self.selection = 0
        self.windCircle = 0
        # prepare margins and distances for initialization block
        dw = self.width - 40 # width . 10 px margin on left and right
        dh = self.height / (n + (n / 6.9) ) # 65 # height.
        inbetween = self.height / ( ( n + (n/dh) ) * 10 ) # 5
        dx = self.width * 0.5 # x loc: centered on stage
        dy = self.height / (n * 2) # y loc for first one

        for z in range(self.numOfLayers) :
            c = utilities.randRGB()
            # displays
            display = Display(dx, dy, z, dw, dh, c)
            self.displayList.append(display) # displays, same color as correspondant box
            # small boxes
            x = z*20 -50 + self.width*0.5
            y = self.height*0.3
            box = MovingSmallBox(display, x, y, z+20, 9, 9, c) # z+20 to go on top of displays and other stuff
            self.boxList.append(box)
            box.constrainRect = self.constrain #
            display.mybox = box # has to remember whos related to
            
            dy += dh+inbetween # y loc for next one

    def startHandlers(self):
        # one black handle
        x,y = self.width, self.height*0.5 # left
        self.handles['black'] = BlackHandle( x,y, 11, 11,11,  (0,0,0, 1)) 

        # one white handle
        x,y = 1, self.height*0.5 # right
        self.handles['white'] = WhiteHandle( x,y, 10, 11,11, (1,1,1,1) )

        # one grey handle
        x,y = self.width*0.5, self.height*0.5 # centered
        self.handles['grey'] = GreyHandle( x,y, 10, 11,11, (0.4, 0.4, 0.4, 1) )
     
        # selection object
        if self.selection == 0 :
            self.selection = Selection(self.boxList) # selection object, it needs to know whos selectable
            self.selected = self.boxList[0] # I need to keep track of this, just initialising.

        if self.windCircle == 0 :
            self.windCircle = WindHandle(self.width/2, self.height/2, 100, 10, color=(1,0,0, 1))

## END initialisation methods ###########################################################
        
    def randomSituation(self) :
        self.randomNodes()
        self.randomBoxes()

    def randomBoxes(self) :
        for b in self.boxList :
            b.loc = utilities.randPoint(1, 1, self.width, self.height)
            b.updateLooper()
            b.moveLabel()

    def randomBoxesSmall(self) :
        for b in self.boxList :
            b.loc = utilities.randPoint(int(b.x-5), int(b.y-5), int(b.x+5), int(b.y+5))
            b.updateLooper()
            b.moveLabel() 
            
    def randomNodes(self, flag=0) :
        for h in self.handles.values() : # prop list {}
            if not flag : 
                h.loc = utilities.randPoint(1, 1, self.width, self.height)
                h.updateVars()
            else :
                if h is not self.handles['grey'] :  ## no pitch change in this case
                    h.loc = utilities.randPoint(1, 1, self.width, self.height)
                    h.updateVars()
        h.updateDisplays() # last one does the job

    def randomSingleNode(self, node, mode=0) :
        if mode :
            # what about this ? http://code.activestate.com/recipesy/576760-brownian-motion-of-stock/
            xrange1, xrange2 = int(self.handles[node].x) - 5, int(self.handles[node].x) + 5
            yrange1, yrange2  =  int(self.handles[node].y) - 5, int(self.handles[node].y )+ 5
        else :
            xrange1, xrange2 = 1, self.width
            yrange1, yrange2 =  1, self.height

        if xrange1 < 1 : xrange1 = 1
        if yrange1 < 1 : yrange1 = 1
        if xrange2 > self.width : xrange1 = self.width
        if yrange2 > self.height : yrange1 = self.height
        
        self.handles[node].loc = utilities.randPoint(xrange1, yrange1, xrange2, yrange2)
        if node == 'grey': self.handles[node].x = self.width/2
        self.handles[node].updateVars()
        self.handles[node].updateDisplays()
        

    def redoLoopers(self) :
        """ disables the ones not needed
        """
        for i, l in enumerate(self.loopers) : # current to max
##            ## FIX ME##
            l.vol( int( i < self.numOfLayers) ) # convert true/false to 1/0
##            if  i < self.numOfLayers :
##                l.looper.pitch = 0
##            l['loop'].mul = ( int( i < self.numOfLayers) ) # convert true/false to 1/0
##            l.run( int( i < self.numOfLayers) ) # convert true/false to 1/0
            

    def drawZero(self) : # top, mid, bottom
        """ calcs the Y post of the 0 pitch line
        """
        if self.pitchLimits[1] < 0 : #is on top side
            self.drawZeroY = (self.height*0.5) - ( (self.height*0.5) / (self.pitchLimits[0] + abs(self.pitchLimits[1]))  )  * abs(self.pitchLimits[1])        
        else : #is on bottom???
            self.drawZeroY= self.height - ( (self.height*0.5) / (self.pitchLimits[1] + abs(self.pitchLimits[2]))  )  * abs(self.pitchLimits[2])
            
        self.drawOneY = int (self.drawZeroY / self.pitchLimits[0]) * (self.pitchLimits[0] - 1)

    def doSndList(self) :
        self.sndPool = []    
        for dirpath, dirnames, fname in os.walk( self.sndPath ) :
            for f in fname :
                if f[0] != '.' : # mac .DS_Store and other hidden files
##                        if dirname[0]  != '.' : # SVN folders on linux and hidden folders in general
                    self.sndPool.append( os.path.join(dirpath, f) )
        print(self.sndPool)
        
    def resetplayheads(self) :
        for l, d in zip(self.loopers, self.displayList) :
            l.pos = d.calcLimits()[0] # all back to left limit, nomalised to 0-1
        
    def end(self) :
##        closeOSC()
        audio.quitServer()
        super(Slicer, self).end()
 
    def step(self) :
        qtgui.status('snd: %s | pitch: %s | length:%i | shift: %i | start: %i | granshift: %i | vol: %s | step: %s | session: %s' \
                              % (os.path.basename(self.sndFile), self.pitch,self.grain,self.shift,
                                 self.sttime, self.grainshift, self.vol, self.boxStep,
                                 os.path.basename(qtgui.fileName) ) )
##        if self.flock :
##            self.massCenter = self.averageCenter()
##            self.flockSpeed = self.averageSpeed()

    def render(self):
        # draw zero line #
        glPushMatrix()
        glTranslatef(self.width2, self.drawZeroY, -999) # translate to GL loc point

        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0xF0F0)
        glLineWidth(1)

        glBegin(GL_LINES)
        glVertex2f( -self.width2, 0 )
        glVertex2f( self.width2, 0 ) 
        glEnd()
        
        glPopMatrix()
        
        # draw one line #
        if self.drawOneY != self.height/2 :
            glPushMatrix()
            glTranslatef(self.width2,  self.drawOneY, -999) # translate to GL loc point
            
            glLineStipple(1, 0xFAF0)
            
            glBegin(GL_LINES)
            glVertex2f( -self.width2, 0 )
            glVertex2f( self.width2, 0 ) 
            glEnd()
            
            glPopMatrix()
        ####################
        glPushMatrix()
        glTranslatef(self.width2, self.height/2, -999) # translate to GL loc point
        
        glLineStipple(1, 0x1C47)
        glColor4fv( (0.3,0.3, 0.7,1) ) # kind of blue
        glBegin(GL_LINES)
        glVertex2f( -self.width2, 0 )
        glVertex2f( self.width2, 0 ) 
        glEnd()
        glDisable(GL_LINE_STIPPLE)
        glPopMatrix()
        
        
    def setVol(self, n) :
        if n > 1 : n = 1
        if n < 0 : n = 0
        self.__vol = n
        for b in self.boxList : b.updateLooper() #; print b.looper.amp
        print("vol set to %s" % n)
    def getVol(self) : return self.__vol
    vol = property(getVol, setVol)

    def volUp(self):
        self.vol = self.vol + 0.1
    def volDown(self):
        self.vol = self.vol - 0.1
    
    def setPitchL(self, l) :
        n = self.size[1]*0.5 # half the height of the window
        self.__pitchLimits = l # items 0,1,2 (top, midd, bottom)
        self.__pitchLimits.append( (l[0] - l[1]) / n) # sub 3
        self.__pitchLimits.append( (l[1] - l[2]) / n) # sub 4
        self.drawZero() # try draw line displaying 0 crossing
    def getPitchL(self) : return self.__pitchLimits
    pitchLimits = property(getPitchL, setPitchL)

    def updatePitchLimits(self) :
        self.handles['black'].updateVars()
##        self.handles[0].updateDisplays()

    def updateBoxDelta(self) :
        for b in self.boxList :
            b.delta = b.calcDelta()
            b.updateLooper()

##    # flock
##    def averageCenter(self) :
##        x = y = 0
##        for o in self.boxList : 
##            x += o.x
##            y += o.y
##        num = float(len(self.boxList))  # minus me. note float 1.
##        return x/num, y/num 
##
##    def averageSpeed(self) :
##        x = y = 0
##        for o in self.boxList :
##            x += o.delta[0]
##            y += o.delta[1]
##        num =  float(len(self.boxList))  # minus me. Note float 1.
##        return x/num, y/num 


    # joystick and mouse stuff ###########
        
    def mouseDown(self,x,y) :
        self.selection.select(x,y)
            
    def mouseUp(self,x,y) :
        self.selection.stop()






if __name__ == '__main__': Slicer() # init always your main app class that extends main.App
