import os, time, sys
from pyo import SNDS_PATH, Phasor, Pointer, SPan, SndTable, Server, Pattern


SNDS_PATH = os.path.join( os.getcwd(), 'sounds' )


pyoserver = None
table = None
##freeverb = None
##mix = None


##class ThreadServer(threading.Thread):
##    def run(self):
####        freev.ctrl(title='Freeverb')
##        pyoserver.gui(timer=True)


def startServer(rate=44100, audio='jack',  channels=2):
        global pyoserver
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
        pyoserver.boot()
        pyoserver.start()

##        freeverb = Freeverb(pointer, size=0.50, damp=0.50, bal=0.50)
##        mix = Mix(freev, voices=2).out()
##        t = ThreadServer()
##        t.start()
##        t.join()

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
        print "Error file %s does not exist" % path
        return -1
    else :
        print 'loading sound file %s' % path
        try :
                table = SndTable(path)
        except :
                print "error loading sound: cannot handle that format?"
                return -1

    tabdur = table.getDur()
    print 'length is', tabdur
    
    return tabdur

class SlicerPlayer(object) :
        
    def __init__(self, index=0) :
        self._storedmul= None
        self.pos = 0
        self.index= index

        self._pitch = 1
        tabrate = table.getRate() # Return the frequency in cps at which the sound will be read at its original pitch.
        start = 0

##        env = LinTable([(0,0),(300,1),(1000,.3),(8191,0)])
##        env = CosTable([(0,0),(100,1),(500,.5),(8192,0)])
# trig the amplitude envelope (no mix to keep the polyphony and not truncate an envelope)
##        amp = TrigEnv(seq, table=env, dur=dur, mul=.3)

##Fader(fadein=0.01, fadeout=0.10, dur=0, mul=1, add=0)

##f = Adsr(attack=.01, decay=.2, sustain=.5, release=.1, dur=2, mul=.5)
##a = BrownNoise(mul=f).mix(2).out()


        self.phasor = Phasor(freq=(self._pitch*tabrate), add=start, mul=1)
        self.pointer = Pointer(table=table, index=self.phasor, mul=1)
        self.pan = SPan(self.pointer, outs=2, pan=0.5)
        self.pan.out()

        # poll phasor
        self.pat = Pattern(function=self.findpos, time=1/12).play()

    def findpos(self) :
        self.pos = self.phasor.get() # * table.getDur() # position in seconds (.getSize() for samples)

    def setPitch(self, n) :
        self._pitch = n # store
        self.phasor.freq = (n * table.getRate()) / self.phasor.mul

    def setDur(self, n) :
        self.phasor.freq = (self._pitch * table.getRate()) / n
        self.phasor.mul = n

    def setStart(self, n) :
        self.phasor.add = n

    def gomute(self, flag) :
        if flag : # go mute
            self._storedmul = self.pointer.mul
            self.pointer.mul = 0
        else :
            self.pointer.mul = self._storedmul
            self._storedmul = None

    def vol(self, n) :
        if self._storedmul is not None : # muted
            self._storedmul = n # apply later
        else :
            self.pointer.mul = n # directly

    def updatetable(self) :
        self.pointer.table = table
        self.setPitch(self._pitch)
            
        
        

        


if __name__ == '__main__' :
        
        import time
                    
        startServer()
        createTable('numeros.wav')
        sl = SlicerPlayer()
        sl.setPitch(0.75)
        sl.setStart(0.2)
        sl.setDur(0.3)
        
        while 1 :
            time.sleep(0.1)
            print 'position is', sl.pos
##        pyoserver.gui(locals())
        
