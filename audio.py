from __future__ import print_function
import os, time, sys
from pyo import SNDS_PATH, Phasor, Pointer, SPan, SndTable, Server, Pattern, Mix, Compress #, PVShift


def getabspath(f=''):
    p = ''
    print(os.getcwd(), f, sys.executable)
    if getattr(sys, 'frozen', False) :
        if sys.platform == 'darwin' :
##            p = os.path.join(sys.executable, "../../../", f)
            p = "/"
            for st in sys.executable.split("/")[1:-4]:
                p = os.path.join(p, st)
            p = os.path.join(p, f)
        elif sys.platform == "win32":
            # get the exe directory and append the prefs file name
            p = os.path.join(sys.executable[:-len(os.path.basename(sys.executable))], f)
        else :
            p = os.path.join(os.getcwd(), f)
    else :
        p = os.path.join(os.getcwd(), f)

    if not os.path.isdir( p ) :
        print("file does not exist", p)
    else :
       print("SNDS_PATH set to", p)

    return p


SNDS_PATH = getabspath('sounds')

pyoserver = None
table = None



def startServer(rate=44100, jack=True,  channels=2):
    global pyoserver
    
    if jack :
        audio= 'jack'
    else:
        audio = 'portaudio' # alsa?
        
    if sys.platform == 'win32' :
        pyoserver = Server(
                               sr=rate,
                               nchnls=channels,
                               duplex=0,
                               )
    else :
        pyoserver = Server(
                               sr=rate,
                               nchnls=channels,
                               duplex=0,
                               audio=audio,
                               jackname="Slicer"
                               )
    if audio == 'jack':
        pyoserver.setJackAuto(False, False)## ERROR in laptop while autoconnecting

    pyoserver.boot() 
    pyoserver.start()

def quitServer() :
    pyoserver.shutdown()

def amp(amp):
    ''' global amp '''
    pyoserver.setAmp(amp)

def recstart() :
    filename = 'slicer_%s_%s_%s_%s_%s_%s.aif' % time.localtime()[:6]
    pyoserver.recstart( filename )

def recstop() :
    pyoserver.recstop()
    
##recstart(str) : Begins recording of the sound sent to output. 
##        This method creates a file called `pyo_rec.aif` in the 
##        user's home directory if a path is not supplied.
##    recstop()
        
def createTable( filename ) :
    global table
    path = os.path.join( SNDS_PATH, filename )
    
    if not os.path.isfile(path) :
        print("Error file %s does not exist" % path)
        return -1
    else :
        print('loading sound file %s' % path)
##        try :
        table = SndTable(path)
##        except :
##                print "error loading sound: cannot handle that format?"
##                return -1

    tabdur = table.getDur()
    print('length is', tabdur)
    
    channels = table.getSize(all=True)
    stereoflag = isinstance(channels, list)        
    print("stereo?", stereoflag)
    
    return tabdur, stereoflag





class SlicerPlayer(object) :
        
    def __init__(self, stereo=False, index=0) :
        self._storedmul= None
        self.pos = 0
##        self.index= index
        self.stereo = stereo
        print("Am I an stereo player?", stereo)

        self._pitch = 1
        # table is global but it could be a class variable
        tabrate = table.getRate() # Return the frequency in cps at which the sound will be read at its original pitch.
        start = 0

        self.phasor = Phasor(freq=(self._pitch*tabrate), add=start, mul=1)
        self.pointer = Pointer(table=table, index=self.phasor, mul=1)
##        self.pointer.mix(1).out(index) #  each channel to one output. for an 8 multichanel setup
        
        if self.stereo :
            signal = self.pointer
        else :
            self.pan = SPan(self.pointer, outs=2, pan=0.5)
            signal = self.pan

        self.mix = Mix(signal, voices=2, mul=1)
##        PVShift(self.mix, shift=500).out()
##        self.mix = Compress(self.mix, thresh = -14, ratio = 6, risetime = 0.01,
##                            falltime = 0.2, knee = 0.5)
        self.mix.out()

        # poll phasor
        self.pat = Pattern(function=self.findpos, time=1/10.0).play()

    def findpos(self) :
        self.pos = self.phasor.get() 

    def setPitch(self, n) :
        self._pitch = n # store
        self.phasor.freq = (n * table.getRate()) / self.phasor.mul

    def setDur(self, n) :
        self.phasor.freq = (self._pitch * table.getRate()) / n
        self.phasor.mul = n

    def setStart(self, n) :
        self.phasor.add = n

    def setPan(self, n) :
        if self.stereo:
            self.pointer.mul = [abs(n - 1), n]
        else :
            self.pan.pan = n
        
    def gomute(self, flag) :
        if flag : 
            self._storedmul = self.pointer.mul
            self.mix.mul = 0
        else :
            self.mix.mul = self._storedmul
            self._storedmul = None

    def vol(self, n) :
        if self._storedmul is not None : # muted
            self._storedmul = n # apply later
        else :
            self.mix.mul = n # directly

    def updatetable(self) :
        self.pointer.table = table
        self.setPitch(self._pitch)

    def stop(self):
        self.pointer.stop()
            
        
        

        


if __name__ == '__main__' :
    
    import time
                
    startServer(jack=True) #, rate=96000)
    
##        # mono sound
##        length, stereo = createTable('mono_test.wav')
##        print length, stereo
##        sm = SlicerPlayer(stereo)
##
##        sm.setPan(0.5) # mono tables
##        time.sleep(1)
##        sm.setPan(1) # mono tables
##        time.sleep(1)
##        sm.setPan(0) # mono tables
##        time.sleep(1)
##
##        sm.stop()
##        
##        # stereo sound
    length, stereo = createTable('stereo_test.wav')
##        print length, stereo
##        st = SlicerPlayer(stereo)
##        
##        st.setPan(0.5)
##        time.sleep(1)
##        st.setPan(0) 
##        time.sleep(1)
##        st.setPan(1) 
##        time.sleep(1)
##
##        st.stop()

    # other options
##    length, stereo = createTable('numeros.wav')
    print(length, stereo)
    
    time.sleep(0.5) # required
    
    num= SlicerPlayer(stereo)
##    b= SlicerPlayer(stereo)
##    num.setPitch(0.75)
##    num.setStart(0.2)
##    num.setDur(0.8)
    
    import random
    seed = random.Random()

##    ps = []
##    for i in xrange(2):
##        ps.append( SlicerPlayer(stereo) )
##        ps[i].setPitch(0.75)
##        ps[i].setStart(seed.random())
##        ps[i].setDur(seed.random())
##        ps[i].vol(0.1)
        
        
    while 1 :
        time.sleep(0.1)
##        print 'position is', num.pos
        pyoserver.gui(locals())
        
