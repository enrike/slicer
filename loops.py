        
from audio import *


loops = []


grain = 0           # lenght of layers
grainshift = 0   # shift in the length
sttime = 0         # starting time of first layer
shift = 0            # shift inc delta
pitch = 0           # snd pitch

# individual pan, vol, and calc loopst loopend for each of the loops
                
startServer()
createTable('oren2.wav')


for n in xrange(8) :
    sl = SlicerPlayer()
    sl.setPitch(0.75)
    sl.setStart(0.2)
    sl.setDur(0.1)
    loops.append(sl)

    
while 1 :
    time.sleep(0.1)
##    print 'position is', sl.pos
##        pyoserver.gui(locals())
