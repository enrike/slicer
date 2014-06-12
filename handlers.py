
from mirra import main
from mirra import utilities
from mirra import engine # is it worth?
from mirra.tools import *

import time

from OpenGL.GL import * # i am using opengl calls in slicer.
from OpenGL.GLUT import GLUT_BITMAP_8_BY_13, glutBitmapCharacter




class SmallBox(SRect) :
    """ Base for draggable box that controls volume and pan for each layer
    """
    def __init__(self, display, x,y,z,w,h,c) :
        SRect.__init__(self, x,y,z,w,h, c)

        self.display = display
        #self.constrainRect = 0, 0, self.app.width, self.app.height
        self.oldcolor = c[0],c[1],c[2],1
        self.interactiveState = 2
        self.delta = [0,0]

        self.label = Text(str(self.z-20), self.x + 5 + self.width2, self.y+5 + self.height2, self.z,
                          'helvetica', 10, (0.2,0.2,0.2))
        
        self.looper = self.app.loopers[self.z-20] # just keep a reference to it
        self.updateLooper()

    def end(self) :
        self.label.end()
##        self.looper.free() # ???
        super(SmallBox, self).end()
        
    def rightMouseDown(self,x,y) :
        self.display.mute() # pass event to display, they both need to react
        self.mute()

    def mute(self) :
        if self.blend == 1 : #or self.getBlend() == 0 : # coz blend returns 0 if none
            self.blend = 0.3
            self.label.text = str(self.z-20)+ ' muted' # OSC #
            self.looper.gomute(1)
        else:
            self.blend = 1
            self.label.text = str(self.z-20) # OSC #
            self.looper.gomute(0)

    def moveLabel(self) : #, x,y) :
        self.label.loc = self.x + 5 + self.width2, self.y + 5 + self.height2

    def drag(self,x,y) :
        SRect.drag(self, x,y)
        self.moveLabel() 
        self.updateLooper()

    def updateLooper(self) :
        self.looper.setPan( self.calcPan() )
        self.looper.vol( self.calcVol() )

    def calcPan(self) : # range 0 to 1 for eg. 
        return self.x/float(self.app.width)
##        left = self.x/float(self.app.width)
##        right = abs(left - 1)
##        return  [left, right] # (self.x*(2.0/self.app.width)) -1

    def calcVol(self) :
        if not self.app.vol : return 0 # to avoid /0 when no volume
        return (((self.app.height - self.y) * (1.0 / self.app.height))) * self.app.vol

    def render(self) : 
##        if glGetFloatv(GL_CURRENT_COLOR) != self.color :
        glColor4fv(self.color)
        glPushMatrix()
        glTranslatef(self.x, self.y, -self.z)
        glRectf(-self.width2, -self.height2 , self.width2, self.height2)

        # Marquee 
##        glColor4fv((0,0,0,1)) # black
##        glLineWidth(1)
##        glBegin(GL_LINE_LOOP)
##        glVertex2f(-self.width2, -self.height2)
##        glVertex2f(self.width2, -self.height2)
##        glVertex2f(self.width2, self.height2)
##        glVertex2f(-self.width2, self.height2)
##        glEnd()
        glPopMatrix()

    def mouseDown(self,x,y) :
        SRect.mouseDown(self,x,y)
        if len(Selectable.selection.selected)==1 :
            self.doSelect()

    def mouseUp(self,x,y) :
        SRect.mouseUp(self,x,y)
        if len(Selectable.selection.selected)==1 : #and not Selectable.selection.selected.index(self) : # from tools module
            self.doDeselect()

    def doSelect(self) :
        self.color = 1,0,0 # mark as red when selected
        self.display.color = self.color
        self.display.selected = 1
##        self.app.selection.selected.append(self) ## !!

    def doDeselect(self) :
        self.color = self.oldcolor
        self.display.color = self.display.oldcolor
        self.display.selected = 0
##        self.app.selection.selected.remove(self) ##!!
##        self.delta = [0,0]




class MovingSmallBox(SmallBox) :
    """ draggable box that wanders around
        max step possible / limiting factor
    """
    def __init__(self, display, x,y,z,w,h,c) :
        SmallBox.__init__(self, display, x,y,z,w,h, c) 
        self.timeOut = self.doTimeOut()
        self.delta = self.calcDelta()
        self.constrainRect = 0, 0, self.app.size[0], self.app.size[1]  / 2 ## /2 temp hack
        self.oldloc = 0
        self.mates = []
        # flock
        self.f1 = 0
        self.f2 = 0
        self.f3 = 0

##        self.move = 1

    def step(self) :
##        if not self.move : return # individual movement switch
##        if not self.app.flock and self.app.boxStep <= 0 : return
        
        if self.app.flock : # Flocking #
##            print self.app.flock
            self.f1 = (self.app.massCenter[0] - self.x)* self.app.followtheflockF, (self.app.massCenter[1] - self.y)* self.app.followtheflockF 
            
            c,d = self.avoidOthers()
            self.f2 =  c * self.app.avoidothersF, d * self.app.avoidothersF

            self.f3 = (self.app.flockSpeed[0] - self.delta[0])* self.app.matchyrspeedF,  (self.app.flockSpeed[1] - self.delta[1])* self.app.matchyrspeedF
            
    ##        if self.app.followmouse :
    ##            mouse = self.tend_to_point(self.app.mouseLoc)
    ##        else:
    ##            mouse = self.avoid_point(self.app.mouseLoc)

            x = self.delta[0] + self.f1[0] + self.f2[0] + self.f3[0]  #\
    ##          + mouse[0] + self.app.wind[0]
            y = self.delta[1] + self.f1[1] + self.f2[1] + self.f3[1]  #\
    ##            + mouse[1] + self.app.wind[1] + self.app.gravityF
            
            self.delta = self.limitSpeed( [x,y] )  #limit if too fast 
            
            nextx = self.x + self.delta[0]
            nexty = self.y + self.delta[1]  # calc new step

            self.rotation = utilities.getAng( self.loc, (self.x + self.delta[0], self.y + self.delta[1]) )
            limitedX, limitedY =  utilities.constrainToRect( (nextx+self.app.windDir[0]), \
                                                             (nexty+self.app.windDir[1]),\
                                                             (0,0,self.app.width, self.app.height))
            self.loc = limitedX, limitedY # here we go
##            self.moveLabel() # self.x, self.y
##            self.looper.pan = self.calcPan()
##            self.looper.amp = self.calcVol()
            
        elif self.app.autoNodes : # self.app.boxStep > 0 : # Moving but not flocking #
            self.checkTimeOut()
            self.loc = constrainToRect( ( self.x + self.delta[0] + self.app.windDir[0] ) , \
                                        ( self.y + self.delta[1] + self.app.windDir[1] ) , self.constrainRect )
            if self.app.bounce : 
                if self.x >= self.constrainRect [2] or self.x <= 0 : self.delta[0] *= -1
                if self.y >= self.constrainRect [3] or self.y <= 0 : self.delta[1] *= -1
                # should WRAP UP here
##            else : # stay in border
##                if self.x > self.app.width :  self.delta[0] = self.app.width
##                if self.x < 0 : self.delta[0] = 0
##                if self.y > self.app.height :  self.delta[1] = self.app.height
##                if self.y < 0 : self.delta[1] = 0

        # finally update sounds and label
        self.moveLabel() # self.x, self.y
        self.looper.setPan( self.calcPan() )
        self.looper.vol( self.calcVol() )
        self.looper._mute = self.display.amp = self.calcVol()
            

    def doTimeOut(self) :
        return time.time() + utilities.randint(60, 120) #secs

    def checkTimeOut(self) :
        if time.time() >= self.timeOut :
            self.delta = self.calcDelta()
            self.timeOut = self.doTimeOut() # again

    def calcDelta(self) :
        """ return new delta vector
        """
        deltax = utilities.choice( (-self.app.boxStep, self.app.boxStep) ) / 20.0
        deltay = utilities.choice( (-self.app.boxStep, self.app.boxStep) ) / 20.0
        return [ deltax, deltay ] # needs to be an array because it changes individually

    def limitSpeed(self, speed) :
        if self.app.maxspeed == 0 : self.app.maxspeed = 1 # avoid 0
        if speed[0] != 0 :
            if abs(speed[0]) > self.app.maxspeed :
                speed[0] = (speed[0]/abs(speed[0])) * self.app.maxspeed
        if speed[1] != 0 :
            if abs(speed[1]) > self.app.maxspeed :
                speed[1] = (speed[1]/abs(speed[1])) * self.app.maxspeed
        return speed

    def tend_to_point(self, p) :
        return (p[0] - self.x)*self.app.followmouseF, (p[1] - self.y)*self.app.followmouseF
    
    def avoid_point(self, p):
        return (self.x - p[0])*self.app.followmouseF, (self.y - p[1])*self.app.followmouseF

    def avoidOthers(self) :
        x = y = 0
        for o in self.app.boxList :
            if o is not self :
                if utilities.distance(self.loc, o.loc) < 100:
                    x -= (o.x - self.x)
                    y -= (o.y - self.y)
        return x,y

    def mouseDown( self, x,y ) :
        if self.app.keyPressed == 308 : # CTL
            self.delta = self.calcDelta() # new delta
##        if self.app.keyPressed == 308 : # M ?
##            self.move = not self.move # toggle
        else :
            if self.app.keyPressed == 74 : # J pressed
                self.mates = self.app.selection.selected[:]
                self.mates.append(self)
                for o in self.mates : # my mates
                    o.color = 0,1,0
                    o.oldloc = o.loc

            SmallBox.mouseDown( self, x,y ) # pass event

    def mouseUp(self, x, y) :
        if self.oldloc : # come back to where you where before the click
            for o in self.mates : # me and my mates
                if o.oldloc : # in case
                    o.loc = o.oldloc # jumpback
                    o.oldloc = 0 # forget about it
                o.color = 1,0,0 # still selected
                if self.display.selected :
                    self.color = 1,0,0 # still selected
                else :
                    self.color = self.oldcolor
            self.mates = []
##            self.loc = self.oldloc # jumpback
##            self.oldloc = 0 # forget about it
##            if self.selected :
##                self.color = 1,0,0 # still selected
##            else :
##                self.color = self.oldcolor
        SmallBox.mouseUp( self, x,y ) # pass event





class WindHandle( Circle ) :
    # rotate to increase strenght?, right click to disable?
    def start(self) :
        self.interactiveState = 2
        self.label = Text( '0,0', self.x+10, self.y+10, self.z+1, 'helvetica', 10, (0.2,0.2,0.2) )
        self.w = self.app.width/2
        self.h = self.app.height/2
        self.dir = self.app.windDir

    def drag(self, x, y) :
        Circle.drag(self, x,y)
        self.label.loc = self.x + 10 , self.y + 10
        self.dir = ( x - self.w ) *0.025, ( y - self.h ) *0.025
        self.label.text = "%.1f, %.1f" % (round(self.dir[0], 1), round(self.dir[1], 1))
        if self.blend ==1 :
            self.app.windDir = self.dir # update only if active

    def rightMouseUp( self, x, y ) :
        if self.blend == 0.5 : #was inactive
            self.blend = 1
            self.app.winDir = self.dir #restore
        else : # was active
            self.blend = 0.5
            self.app.windDir = 0,0 # disable
            
    def end(self) :
        self.label.end()
        Circle.end(self)

        super(ImageBlob, self).render()
        self.sq += 1

#    def render(self):
##        super(WindHandle, self).render()
##        engine.drawLine(self.loc, (self.app.width/2,  self.app.height/2), self.z, (1,0,0,1), 1, 0, 0xAAAA)

##        glEnable(GL_LINE_STIPPLE)
##        glPushMatrix()
##        glTranslatef(self.x, self.y, -self.z) # translate to GL loc ppint
##            
##        glBegin(GL_LINES)
##        glVertex2f( self.x, self.y) # draw relative pixel points
##        glVertex2f(self.app.width/2,  self.app.height/2)
##        glEnd()
##        glPopMatrix()
##        glDisable(GL_LINE_STIPPLE)
        
        


class HandleBase(Rect) :
    """ base for handles, dragable rect that controls displays with its loc.
    it is connected to each smallbox with a line
    """
    def __init__(self, x,y,z,w,h, color=(0,0,0)) :
        self.style = 0 # line style
        Rect.__init__(self, x,y,z,w,h, color) # super
        self.interactiveState = 2 #
        self.updateVars()
        self.updateDisplays()
        self.constrainRect = 0, 0, self.app.width, self.app.height
        self.style = 0xF0F0 # dashed

    def render(self) : #,e) :
        glPushMatrix()
        glTranslatef(self.x, self.y, -self.z)
        # colored box #
        glColor4fv(self.color)
##        try :
##            glRectfv(self.v2[0], self.v2[2])
##        except: # pyopengl3 bug 
        glBegin(GL_QUADS)
        glVertex2fv(self.v2[0])
        glVertex2fv(self.v2[1])
        glVertex2fv(self.v2[2])
        glVertex2fv(self.v2[3])
        glEnd()
##            print 'render error on HandleBase render'
        # Marquee starts #
##        glColor4fv((0,0,0,1)) # black
##        glLineWidth(1)
##        glBegin(GL_LINE_LOOP)
##        glVertex2fv(self.v2[0])
##        glVertex2fv(self.v2[1])
##        glVertex2fv(self.v2[2])
##        glVertex2fv(self.v2[3])
##        glEnd()
        glPopMatrix()
        
        #Draw my lines #
##        glLineWidth(1)

        # dont need this here, it is already set
##        glColor4fv(self.color)

        if self.style :
                glEnable(GL_LINE_STIPPLE)
                glLineStipple(1, 0xAAAA)
                
        for b in self.app.boxList :
            x = abs(self.x + (b.x - self.x) * 0.5) # calc loc point
            y = abs(self.y + (b.y - self.y) * 0.5) 
            
            glPushMatrix()
            glTranslatef(x, y, -self.z) # translate to GL loc ppint
            
            glBegin(GL_LINES)
            glVertex2f( x - self.x,  y - self.y) # draw relative pixel points
            glVertex2f(x - b.x,  y - b.y)
            glEnd()
            glPopMatrix()
            
        if self.style : glDisable(GL_LINE_STIPPLE)

    def drag(self,x,y) :
        Rect.drag(self, x, y) # super
        self.updateDisplays() # if dragged

    def updateDisplays(self) :
        for d in self.app.displayList :
            d.update()#self.x, self.y)






# old black
class GreyHandle(HandleBase) :
    def __init__(self, x,y,z,w,h, color=(0.4, 0.4, 0.4)) :
        self.rev = self.app.height*0.5 # to reverse values from mouseY
        super(GreyHandle, self).__init__(x,y,z,w,h, color)
        self.style = 0xAAAA # dotted?

    def updateVars(self) :
##        self.app.grain = self.x
        self.setPitch(self.y) # +1) # plus 1 to avoid 0
##        super(GreyHandle,self).updateDisplays()

    def setPitch(self, i) :
        if i < self.app.height*0.5 : # top. mouse range 0 to middle 300
            if i == 0 : # very top'
                self.app.pitch = self.app.pitchLimits[0] # fix float rounding problem
            else:
                self.app.pitch = self.app.pitchLimits[1] + ( self.app.pitchLimits[3] * abs(self.rev - i) ) # scale to mid to max
        elif i == self.app.height*0.5 :# middle
            self.app.pitch = self.app.pitchLimits[1]
        else : # bottom. the difference is that mouse range is 300 to 600 here
##            self.app.pitch = self.app.pitchLimits[1] - (self.app.pitchLimits[1] - ( self.app.pitchLimits[4] * abs(self.app.size[1] - i) ) )
            self.app.pitch = self.app.pitchLimits[2] + ( self.app.pitchLimits[4] * abs(self.app.height - i) )

        if not self.app.microtones :
            self.app.pitch = int(self.app.pitch)
        else :
            self.app.pitch = round(self.app.pitch, 4) # four digits

        for l in self.app.loopers :
            l.setPitch(self.app.pitch) 
                

    def drag(self, x, y) :
        if self.app.freedom[ 'pitch' ] : # y unlocked
            self.loc = constrainToRect( self.x, y + self.mouseoffset[1], self.constrainRect )
##        if self.app.freedom[ 'length' ] : # x unlocked
        self.loc = constrainToRect( x + self.mouseoffset[0], self.y, self.constrainRect)

        self.updateVars()
        self.updateDisplays() # if dragged


# old grey
class BlackHandle(HandleBase) :
    def __init__(self, x,y,z,w,h, color=(0, 0, 0)) :
        self.rev = self.app.height*0.5 # to reverse values from mouseY
        super(BlackHandle, self).__init__(x,y,z,w,h, color)

    def updateVars(self) :
        self.app.grain = self.x
        self.app.grainshift = self.y - self.app.height/2
##        self.setPitch(self.y) # +1) # plus 1 to avoid 0
##        super(BlackHandle,self).updateDisplays()

    def drag(self, x, y) :
        if self.app.freedom[ 'grainshift' ] : # y unlocked
            self.loc = constrainToRect( self.x, y + self.mouseoffset[1], self.constrainRect )
        if self.app.freedom[ 'length' ] : # x unlocked
            self.loc = constrainToRect( x + self.mouseoffset[0], self.y, self.constrainRect)

        self.updateVars()
        self.updateDisplays() # if dragged





class WhiteHandle(HandleBase) :
    """ special handle that jumps once in a while to a close new loc
    """
##    def __init__(self, x,y,z,w,h, color=(0,0,0)) :
##        super(WhiteHandle, self).__init__(x,y,z,w,h, color)
##        self.constrainRect = 0, 0, self.app.width, self.app.height

    def updateVars(self) :
        self.app.sttime = self.x
        self.app.shift = int( (self.y - self.app.height*0.5) / 1.33) # limit it a bit
##        super(WhiteHandle, self).updateDisplays()

    def start(self) :
        self.timeOut = self.doTimeOut()
        self.delta = self.calcDelta()

    def doTimeOut(self) :
        return time.time()+ utilities.randint(120, 240) # 120, 240) # 2 to 4 min

##    def step(self) :
##        if self.app.autoNodes  and time.time() >= self.timeOut :
##            self.x += self.delta[0]
##            self.y += self.delta[1]
##            if self.x >= self.app.width or self.x <= 0 : self.delta[0] *= -1
##            if self.y >= self.app.height or self.y <= 0 : self.delta[1] *= -1
##            self.updateVars()
##            self.updateDisplays() # if dragged
##            self.timeOut = self.doTimeOut() # again

    def calcDelta(self) :
        deltax = deltay = 0
        i = 4 # max step
        while deltax == 0 : deltax = utilities.randint(-i, i)#/300.0
        while deltay == 0 : deltay = utilities.randint(-i, i)#/300.0
        return [deltax, deltay] # needs to be an array because it changes
    

    def drag(self,x,y) :
        if self.app.freedom[ 'shift' ] : # y unlocked
            self.loc = constrainToRect( self.x, y + self.mouseoffset[1] , self.constrainRect)
        if self.app.freedom[ 'start' ] : # x unlocked
            self.loc = constrainToRect( x + self.mouseoffset[0], self.y , self.constrainRect)

        self.updateVars()
        self.updateDisplays() # if dragged

##    def render(self):
##        super(WhiteHandle, self).render()
##        engine.drawLine( (self.loc[0]+20, 0), (self.loc[0]+20,  self.app.height), self.z, (1,0,0,1), 1, 0, 0xAAAA)








class Display(Rect) :
    """ long rect that displays the lenght of selected sample that corresponds to its layer of sound
    """
    def __init__(self, x,y,z,w,h,forecolor) :#bgcolor,forecolor) :
        Rect.__init__(self, x,y,z,w,h, stroke=1)
        self.interactiveState = 1 # mouseable
        self.forecolor = forecolor[0],forecolor[1],forecolor[2],1
        self.color = 0.4, 0.4, 0.4, 1 # marquee color
        self.oldcolor = self.color
        self.limits = [0, self.width]
        self.selected = 0
        self.textcolors = (0.2,0.2,0.2), (1,0,0,1)
        self.amp = 0
        
        font = 10 # font size
        labelx = 3 + self.x - self.width2
        labely = self.y + (self.height2) - 2
        self.label = Text('dummytext', labelx, labely, self.z+1, 'helvetica', font, self.textcolors[0])
        self.num = Text(str(z), labelx, (self.y-self.height2+font+2), self.z+1, 'helvetica', font, self.textcolors[0]) # number, doesnt change

        self.mybox = 0 # to store ref to box where i am related to
        self.playhead = self.x - self.width2 # left position

        # compile call list  	 
        glNewList(self.z+1, GL_COMPILE) # unique int id for each list 	 
##        glColor4fv(0.7, 0.7, 0.7, 1) # black? 	 
        glPushMatrix()
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0x1111) # 0x0101 dotted # 0x00FF  dashed #0x1C47  dash/dot/dash
        glTranslatef(self.x, self.y, -self.z) # translate to GL loc ppint 	 
        glLineWidth(1) 	 
        glBegin(GL_LINE_LOOP) 	 
        glVertex2f(-self.width2, -self.height2) 	 
        glVertex2f(self.width2, -self.height2) 	 
        glVertex2f(self.width2, self.height2) 	 
        glVertex2f(-self.width2, self.height2) 	 
        glEnd()
        glDisable(GL_LINE_STIPPLE)
        glPopMatrix() 	 
        glEndList()

   
    def end(self) : # extending end
        self.label.end()
        self.num.end()
        glDeleteLists( self.z+1, 1)
        super(Display, self).end() #

    def update(self) :#, x,y) :
        """ update selected area, check for limits
        """
        mysttime = self.app.sttime + self.z * self.app.shift
##        myendtime = self.app.grain + self.z * self.app.grainshift
        myendtime = mysttime + self.app.grain + self.z * self.app.grainshift
        
        # it does work but took me time ...
        if mysttime > self.width: # wrap on right
            mysttime = mysttime % self.width
            myendtime = mysttime + self.app.grain
            if myendtime > self.width : # cut on right
                myendtime = self.width
        elif myendtime > self.width : # cut on right
            myendtime = self.width
        elif myendtime < 0: # wrap on left
            mysttime = self.width - (-mysttime % self.width) # positive modulo from right
            myendtime = mysttime + self.app.grain #+ self.z * self.app.grainshift
            if myendtime > self.width : # cut on right
                myendtime = self.width

        if mysttime < 0 : #now cut on left
            mysttime = 0
            
        if mysttime == myendtime : 
            myendtime = mysttime+1
        
        self.limits = mysttime, myendtime
        
        #self.app.loopers[self.z].start, self.app.loopers[self.z].end = self.calcLimits()
        st = ( mysttime/float(self.width) ) #* self.app.sndLength
        dur =  ((myendtime-mysttime)/float(self.width) ) #*  self.app.sndLength 
        
##        if self.app.pitch > 0 :
##            self.app.loopers[self.z].looper.start = st # forwards. start from beginning
##        else :
##            self.app.loopers[self.z].looper.start = st + dur # start from end. backwards

        self.app.loopers[self.z].setStart( st ) 
            
        self.app.loopers[self.z].setDur( dur )
        self.label.text = '%f : %f' % (st*self.app.sndLength , dur*self.app.sndLength )

    def calcLimits(self) :
        #v = 1.0/self.width # from 0 to 1 per pixel
        #return self.limits[0]*v, self.limits[1]*v #l # start and end of slice
        return self.limits[0]/self.width, self.limits[1]/self.width
    
    def render(self) : #,e) :
        if self.blend < 1:
            glColor3fv( (1,0,0) ) # dark grey this one
        else :
            glColor3fv(self.textcolors[0]) # 
        
        # marquee
        glCallList(self.z+1)

        bgleft = self.x - self.width2  # display's marquee left side
        w = (self.limits[1] - self.limits[0] + 1)*0.5 # half width of color area
        x = bgleft + self.limits[0] + w # x loc of color rect
        
        # colored selection area #
        glColor4fv(self.forecolor) # black? 
        glPushMatrix()
        glTranslatef(x, self.y, -self.z) # translate to GL loc ppint
        glRectf(-w, -self.height2+1, w, self.height2)
        glPopMatrix()

        # marquee
##        glCallList(self.z+1)
        self.playhead = (self.app.loopers[self.z].pos * self.width) + bgleft

        # reference line
        glColor4fv( self.forecolor ) 
        glPushMatrix()
        glTranslatef( x, 0, -self.z ) # translate to GL loc ppint
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex2f( -w, 0) # line ends
        glVertex2f( -w, self.app.height )
        glVertex2f( w, 0) # line ends
        glVertex2f( w, self.app.height )
        glEnd()
        glPopMatrix()
        
        # playhead line
        glColor4fv( (1,0,0,1) ) ### EVERYTHING below goes red but normal volume ###
        glPushMatrix()
        glTranslatef( self.playhead, self.y, -self.z ) # translate to GL loc ppint
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex2f( 0, self.height2 ) # line ends
        glVertex2f( 0, -self.height2 )
        glEnd()
        glPopMatrix()

        # red mark # already drawing red at this point
        if self.selected : # mark as selected
            glPushMatrix()
            glTranslatef(20, self.y, -self.z)
            glRectf(-7,-7,7,7)
            glPopMatrix()

        # amp/MUTED label #
        if self.blend < 1:
            glColor3fv( (1,0,0) ) # dark grey this one
            txt ='MUTED' 
        else :
            glColor3fv(self.textcolors[0]) # dark grey this one
            txt =  'amp: %.2f' % round(self.amp, 2)

        glRasterPos3f(self.left + 25, self.top + 13, -self.z)
        
        for c in txt : 
            glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(c))

    def updateLabel(self) :
        self.label.text = '%f : %f' % self.calcLimits() # start and end point

    def rightMouseDown(self,x,y) :
        self.mybox.mute() # small box too
        self.mute() #

    def mouseDown(self,x,y) : return -1 # pass event to background
    def mouseUp(self,x,y) : return -1 # pass event to background

    def mute(self) :
        if self.blend == 1 : #or self.getBlend() == 0 : # coz blend returns 0 if none
            self.blend = 0.3
            self.forecolor = self.forecolor[0], self.forecolor[1], self.forecolor[2], self.blend
            self.label.color = self.num.color = self.textcolors[1]
        else:
            self.blend = 1
            self.forecolor = self.forecolor[0], self.forecolor[1], self.forecolor[2], self.blend
            self.label.color = self.num.color = self.textcolors[0]

##    def setplayhead(self, f) : # range 0 to 1 # left side + position in sound * how many px is the sound
##        self.playhead = (self.x-self.width2) + f * self.width    #



