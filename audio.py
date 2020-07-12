from __future__ import print_function
import os, time, sys
from pyo64 import SNDS_PATH, Phasor, Pointer2, SPan, SndTable, Server, Pattern, Mix, Compress, pm_list_devices #, PVShift

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
        print("dir does not exist", p)
    else :
       print("SNDS_PATH set to", p)

    return p


SNDS_PATH = getabspath('sounds')

pyoserver = None
table = "" #filename used to access tables dict
tabrate = None
tables = {}





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
        pyoserver.setJackAuto(True, True) ## False it if error while autoconnecting

    pyoserver.setMidiInputDevice(99) # connect ALL MIDI devices

    pyoserver.boot() 
    pyoserver.start()
    # pyoserver.gui(locals())
    #pm_list_devices()
    
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
        
def createTable( filepath ) :
    global table,tabrate, tables
    table = filepath.split(os.sep)[-1] #filename to access sound dict
    tabrate = None

    if tables.get(table) == None: # not there already
        path = os.path.join( SNDS_PATH, filepath )
        
        if not os.path.isfile(path) :
            print("Error file %s does not exist" % path)
            return -1
        else :
            print('loading sound file %s' % path)
    ##        try
            tables[table] = SndTable(path)
    ##        except :
    ##                print "error loading sound: cannot handle that format?"
    ##                return -1   
        

    tabdur = tables[table].getDur()
    print('length is', tabdur)
    tabrate = tables[table].getRate()
    print('rate is', tabrate)
    
    channels = tables[table].getSize(all=True)
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
##        tabrate = table.getRate() # Return the frequency in cps at which the sound will be read at its original pitch.
        start = 0

        self.phasor = Phasor(freq=(self._pitch*tabrate), add=start, mul=1)
        self.pointer = Pointer2(table=tables[table], index=self.phasor, autosmooth=True, mul=1)
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
        self.phasor.freq = (n * tables[table].getRate()) / self.phasor.mul

    def setDur(self, n) :
        self.phasor.freq = (self._pitch * tables[table].getRate()) / n
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
        self.pointer.setTable(tables[table])
        self.setPitch(self._pitch)

    def stop(self):
        self.pointer.stop()

            
        
        

        


if __name__ == '__main__' :
    
    import time, os.path

    print(SNDS_PATH)    

    startServer(jack=True) #, rate=96000)

    length, stereo = createTable("/home/r2d2/Mahaigaina/audio/feedback/SC_200609_170025_comp.flac")
    num = SlicerPlayer(stereo)
####    b= SlicerPlayer(stereo)
    num.setPitch(1.2)
##    num.setStart(0.2)
##    num.setDur(0.005)
    num.vol(0.1)

    while 1: pass
    
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
    length, stereo = createTable('numeros.wav')
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
    
##    time.sleep(0.5) # required?
##    
    num = SlicerPlayer(stereo)
####    b= SlicerPlayer(stereo)
    num.setPitch(1)
    num.setStart(0.2)
    num.setDur(0.8)
##
##    time.sleep(2)
####    num.vol=0
####    num.setPitch(0)
##    length, stereo = createTable("/home/r2d2/.local/share/SuperCollider/Recordings/SC_200330_173134.flac")
##
##    print(length, stereo)
##    num.updatetable()
##    print("updated table")
    num.vol(0.1)
##    num.setPitch(1)

        
##    import random
##    seed = random.Random()
##    ps = []
##    for i in range(2):
##        ps.append( SlicerPlayer(stereo) )
##        ps[i].setPitch(0.75)
##        ps[i].setStart(seed.random())
##        ps[i].setDur(seed.random())
##        ps[i].vol(0.1)

##    length, stereo = createTable("/home/r2d2/.local/share/SuperCollider/Recordings/SC_200330_173134.flac")
##    for p in ps: p.updatetable()

##    time.sleep(3)
##    length, stereo = createTable('numeros.wav')
##    for p in ps: p.updatetable()

##    time.sleep(3)
##    length, stereo = createTable("/home/r2d2/.local/share/SuperCollider/Recordings/SC_200330_173134.flac")
##    for p in ps: p.updatetable()
        
        
    while 1 :
        time.sleep(0.1)
        print('position is', num.getpos() )
##        pyoserver.gui(locals())
        
