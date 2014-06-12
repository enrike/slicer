#!/usr/bin/env python

from mirra import main
from mirra import utilities
from handlers import *

import json
import os


import audio



""" slicer. python interface connected to a supercollider scsyndef
http://www.ixi-software.net
cLicense : GPL ->  Read doc/documentation.html
"""



class Slicer(main.App) :
    """ main appplication class, handles window contains events and graphics manager.
        Subclasses main.App and extends its public methods
    """

    def setUp(self) :
        """ set here the main window properties and characteristics, JUST DEFAUT ONES IN THIS CASE
        """
        self.env = 'wx'
        self.caption = "Slicer" # window name
        self.size = 800, 600 # window size
        self.pos = 10, 10 # window top left location
        self.fullScreen = 0 # if fullScreen is on it will overwrite your pos and size to match the display's resolution
        self.frameRate = 12 # set refresh framerate

        from gui import MyFrame # import the module that contains your custom frame
        self.frameClass = MyFrame # set the class


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
        self.session = self.jsondata['slicer']['session']
##        print "jack?", self.jack
        

    def getSessionJSON(self) : #, filename='slicer.txt') :
        """ returns current state from the application in JSON format
        called from gui.py on saving a session file
        """
        data = { 'layers' : [], 'nodes' : {}}
        
        for b in self.boxList :
             data['layers'].append( (b.x, b.y, b.looper.pointer.mul) )

        data[ 'sndFile' ] = self.sndFile # self.snd[ 'file' ]  ##! CORRECT ??
        data[ 'microtones' ] = self.microtones
        data[ 'vol' ] = self.vol
        data[ 'pitchLimits' ] = self.pitchLimits
        data[ 'nodes' ]['black'] = self.handles['black'].x, self.handles['black'].y
        data[ 'nodes' ]['white'] = self.handles['white'].x, self.handles['white'].y
        data[ 'nodes' ]['grey'] = self.handles['grey'].x, self.handles['grey'].y

        data[ 'boxStep' ] = self.boxStep 
        data[ 'freedom' ] = self.freedom 
        data[ 'initRand' ] = self.initRand  
        data[ 'synthName' ] = self.synthName

        jdata = json.dumps(data)
        print "saving session as json", jdata
        
        return jdata


    def setSession(self, rawdata) :
        """ sets new application state from data taken from session file
        called from gui.py on open session file
        """
        try :
            jdata = json.loads(rawdata) # json decode
        except :
            print "ERROR parsing json session data"
            return -1

        print 'setting json session', jdata

        self.sndFile = str( jdata[ 'sndFile' ] )  #
        self.loadSnd( self.sndFile ) 
        
        # **** display changes in GUI menus as well!! *****
        self.microtones = jdata[ 'microtones' ]  
        self.pitchLimits = jdata[ 'pitchLimits' ]
        self.boxStep = float(jdata[ 'boxStep' ])
        self.numOfLayers = len( jdata['layers'] )
        self.freedom = jdata[ 'freedom' ]
        self.initRand = jdata[ 'initRand' ]
        self.synthName = jdata[ 'synthName' ]
        #####

        self.drawZero() # update display

        self.vol = jdata[ 'vol' ] # !! just before updating volume in loopers, otherwise there is a burst of snd

        self.updatePitchLimits()
        self.redoLoopers() 	 

        self.startLayers( self.numOfLayers )

        for box, d in zip(self.boxList, jdata['layers']) :
            box.x, box.y, box.looper.pointer.mul = d
##            box.x, box.y, box.looper['loop'].mul = d 
##            box.x, box.y, box.looper.mute = d 
            box.updateLooper() # update
            box.moveLabel() 
        
        self.handles['black'].x, self.handles['black'].y = jdata[ 'nodes' ]['black'] 
        self.handles['white'].x, self.handles['white'].y = jdata[ 'nodes' ]['white']
        self.handles['grey'].x, self.handles['grey'].y = jdata[ 'nodes' ]['grey']

        for h in self.handles.values() :
            h.updateVars()
                        
        h.updateDisplays() # last one does the job


        
##########################################################

            
## initialisation stuff ##########################################
        
    def start(self) :
        """ genral application startup
        define properties, read prefs, open audio engine and init audio, create all objects,
        init Wx interface.
        """
##        if sys.platform == 'win32' : #on windows we need to use wx to trigger the SCsynth process and we need a reference to the parent
##            sc.scsynth.process.wxparentwin = self.window 

        # internal variables not set by user
        self.boxList = []
        self.handles = {} # []
        self.displayList = []
        self.selected = 0
        self.joystate = [] # stores joysticks button combinations
        self.joyactions = { "inc" : 4,
                            "dec" : 5,
                            "fast": 6
                           } # maps keyboard buttons to actions
        self.loopers = []
        self.grain = 0 # lenght of layers
        self.grainshift = 0 # shift in the length
        self.sttime = 0 # starting time of first layer
        self.shift = 0 # shift inc delta
        self.pitch = 0 # snd pitch
        self.sndLength = 0 # lenght of sound on PD in millisecs. Just for display purposes
        self.displayPitch = 0 # to display

        # GENERAL APP VARIABLES # MIGHT be owewriten by prefs file !!!!*****
        self.session = 0
##        self.verbose = 0 # print error messages from SC
##        self.spew = 0
        self.snd = {  'file' : '', 'bid' : 0 } # legacy from SCSYNTH??
        self.sndFile = 'numeros.wav' # ??
        self.boxStep = 0  # boxes automovement
        self.autoNodes = 0
        self.microtones = 1
        self.synthName = 'StereoPlayer' # in this case are the same
        self.vol = 1    # volume
        self.numOfLayers = 8 # default to 8
        self.samplerate = 48000 # snd card sample rate for supercollider server
        self.pitchLimits = [ 3.0, 1, -1 ] # top, middle of screen and bottom
        self.selection = 0
        self.initRand = 0
        self.freedom = { 'pitch' : 1, 'length' : 1, 'shift' : 1, 'start' : 1, 'grainshift' : 1} # to lock them
        self.keyPressed = 0
        self.windDir = 0,0
        self.bounce = 1
        self.drawZeroY = 0
        self.drawOneY = 0

        # flock
        self.flock = 0
        self.followtheflockF = 0.01
        self.avoidothersF = 0.0003
        self.matchyrspeedF = 0.001
        self.followmouse = 0
##        self.followmouseF = 0.005  
        self.maxspeed = 7

        ## end declaring variables ############

        # they already were loaded since they are located in the prefs.tx json file
        # so we just need to set them
        self.setSlicerPrefs( ) 

        # trying to load session from prefs.txt
        if self.session != 0 and self.session != '' : # if a session was specified
            self.window.frame.filename = utilities.getabspath( self.session )
##            self.window.frame.filename = os.path.join( utilities.get_cwd(), self.session )
                
        self.launchAudio()
        self.statusbar = StatusBar(self.width*0.5, self.height-6, 1, self.width+2, 27,
                                   color=(0.85,0.85,0.85) )
        
        self.startLayers( self.numOfLayers )

        if self.initRand or self.window.frame.readFile() == -1 :
            print "---> starting random situation"
            self.randomSituation() # not session specified
        
        self.window.frame.doMenu()
        self.window.frame.startMenus() # set initial Wx menus status

        self.setWindowProps() # something wrong in windows does not set the bgcolor


    def launchAudio(self) :
        self.loopers = []

        audio.startServer( self.samplerate, self.jack )

        length, stereo = audio.createTable(self.sndFile)
        
        for b in xrange( self.numOfLayers ) : #buffers 1000-1007
            looper = audio.SlicerPlayer(stereo, b)
            self.loopers.append( looper )        

            
        ################
            

    def startLayers(self, n, reset=1) :
        """ instantiates basic graphical GUI objects
        """        
        try : # kill all interface all instances
            print 'restarting interface'
            for o in self.boxList : o.end()
            for o in self.handles.values() : o.end() # handles is prop list
            for o in self.displayList : o.end()
            self.selection.end()
            self.windCircle.end()
        except :
            print 'starting up, no interface yet'

        self.boxList = []
        self.handles = {}
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
            display.mybox = box # has to remember whos related to
            
            dy += dh+inbetween # y loc for next one

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
        print "-"*15

    def randomBoxes(self) :
        for b in self.boxList :
            b.loc = utilities.randPoint(1, 1, self.width, self.height)
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
            # what about this ? http://code.activestate.com/recipes/576760-brownian-motion-of-stock/
            xrange1, xrange2 = int(self.handles[node].x) - 5, int(self.handles[node].x) + 5
            yrange1, yrange2  =  int(self.handles[node].y) - 5, int(self.handles[node].y )+ 5
        else :
            xrange1, xrange2 = 1, self.width
            yrange1, yrange2 =  1, self.height

        if xrange1 < 1 : xrange1 = 1
        if yrange1 < 1 : yrange1 = 1
        if xrange2 > self.width : xrange1 = self.width
        if yrange2 > self.height : yrange1 = self.height

        print xrange1, yrange1, xrange2, yrange2
            
        self.handles[node].loc = utilities.randPoint(xrange1, yrange1, xrange2, yrange2)
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

        self.compileScreenLines() ## compile again the list
##        self.drawMinusOneY = self.height -  ((self.height - self.drawZeroY) / self.pitchLimits[0]) * (self.pitchLimits[0] - 1)


    def loadSnd(self, filename) :
        self.sndLength, stereo = audio.createTable(filename)
        if self.sndLength > -1 : 
            for p in self.loopers :
                p.updatetable()
        self.sndFile = filename # in case it was triggered from menu

    def resetplayheads(self) :
        for l, d in zip(self.loopers, self.displayList) :
            l.pos = d.calcLimits()[0] # all back to left limit, nomalised to 0-1
        
    def end(self) :
        audio.quitServer()

        
    def step(self) :
        self.statusbar.text = 'snd: %s | pitch: %s | length:%i | shift: %i | start: %i | granshift: %i | vol: %s' \
                              % (self.sndFile, self.pitch,self.grain,self.shift, self.sttime, self.grainshift, self.vol )
        if self.flock :
            self.massCenter = self.averageCenter()
            self.flockSpeed = self.averageSpeed()

    def compileScreenLines(self) :
        glDeleteLists( 9999, 1) # first try to delete it
        # compile call list  	 
        glNewList(9999, GL_COMPILE) # unique int id for each list 	 

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
        
        glEndList()
        
    def render(self) :
        glCallList(9999) # lines marking 0, 1 pitch and middle screen Height
        
    def setVol(self, n) :
        self.__vol = n
        for b in self.boxList : b.updateLooper() #; print b.looper.amp
    def getVol(self) : return self.__vol
    vol = property(getVol, setVol)

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

    # flock
    def averageCenter(self) :
        x = y = 0
        for o in self.boxList : 
            x += o.x
            y += o.y
        num = float(len(self.boxList))  # minus me. note float 1.
        return x/num, y/num 

    def averageSpeed(self) :
        x = y = 0
        for o in self.boxList :
            x += o.delta[0]
            y += o.delta[1]
        num =  float(len(self.boxList))  # minus me. Note float 1.
        return x/num, y/num 


    # joystick and mouse stuff ###########
        
    def mouseDown(self,x,y) :
        self.selection.select(x,y)
            
    def mouseUp(self,x,y) :
        self.selection.stop()






if __name__ == '__main__': Slicer() # init always your main app class that extends main.App
