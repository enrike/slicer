from PyQt4 import QtCore, QtGui
from functools import partial
import mirra
import os

app = None
qtwin = None

fileName = None
snapName = None
poolMenu = None
statusbar = None
sndfolders = []



snapshots = os.path.join( mirra.utilities.get_main_dir(), 'snapshots')
sessions = os.path.join( mirra.utilities.get_main_dir(), 'sessions')

def alert(msg):
    # open an alert box with msg (but no alert sound")
    box = QtGui.QMessageBox()
    box.setText(msg)
    box.exec_()
    
def status(st):
    statusbar.showMessage(st)

def do(mainapp, win):
    global app, statusbar, qtwin
    app = mainapp
    qtwin = win
    statusbar = win.statusBar()

    # MENUS ####################
    
    # FILE
    fm = win.menuBar().addMenu("&File")
    fm.addAction(
        QtGui.QAction("O&pen", win, shortcut="Ctrl+O", triggered=openFile)
    )
    fm.addAction(
        QtGui.QAction("S&ave", win, shortcut="Ctrl+S", triggered=save)
    )
    fm.addAction(
        QtGui.QAction("S&ave As", win, shortcut="Ctrl+SHIFT+S", triggered=saveAs)
    )
    fm.addSeparator() #---------
    fm.addAction(
        QtGui.QAction("E&xit", win, shortcut="Ctrl+Q", triggered=app.end)
    )
    
    # SNAPSHOT
    sm = win.menuBar().addMenu("&Snapshot")
    sm.addAction(
        QtGui.QAction("O&pen snapshot", win, triggered=openSnapFile)
    )
    sm.addAction(
        QtGui.QAction("S&ave snapshot", win, triggered=saveSnap)
    )
    sm.addAction(
        QtGui.QAction("S&ave snapshot As", win, triggered=saveSnapAs)
    )
    sm.addSeparator() #---------
    for i in range(10):
        sm.addAction(
            QtGui.QAction("L&OAD snapshot %i" %i, win, triggered=partial(setSnapshot, i))
        )
    sm.addSeparator() #---------
    for i in range(10):
        sm.addAction(
            QtGui.QAction("S&TORE snapshot %i" %i, win, triggered=partial(app.storeSnapshot, i))
        )

    # SOUND POOl
    doPoolMenu()

    # VOLUME
    vm = win.menuBar().addMenu("&Volume")
    vm.addAction( # MUTE
            QtGui.QAction("M&ute", win, shortcut="Ctrl+M", triggered= partial(volChange, 0) )
    )
    for i in xrange(1,11): # 1 to 10
        n = i
        if n == 10: n = 0 # 10 corresponds to key 0
        vm.addAction( 
            QtGui.QAction("V&olume %s" %(i/10.), win, shortcut="Ctrl+%s" % n,
            triggered= partial(volChange, i) )
        )

    # NOL
    nm = win.menuBar().addMenu("&Num of Layers")

    for i in xrange(1,9):
        nm.addAction(
            QtGui.QAction("%s&" % i, win, triggered = partial(app.nol, i))
        )

    # AUTO
    am = win.menuBar().addMenu("&Auto")
    am.addAction( # Auto movement
            QtGui.QAction("A&utomove  toggle", win, triggered=autoNodes )
    )
    am.addAction( # INCREASE Auto movement
        QtGui.QAction("I&ncrease movement", win, shortcut="Ctrl++",
                      triggered=partial(changeAuto, 0.25) )
    )
    am.addAction( # DECRESE Auto movement
        QtGui.QAction("D&ecrease movement", win, shortcut="Ctrl+-",
                      triggered=partial(changeAuto, -0.25) )
    )
    am.addAction( # Auto movement
        QtGui.QAction("B&ounce toggle", win, triggered=bounce )
    )
    am.addSeparator() #--------- 
    am.addAction( # Random
            QtGui.QAction("R&andom situation", win, shortcut="Ctrl+R",
            triggered=app.randomSituation )
        )
    am.addAction( # Random boxes
        QtGui.QAction("R&andom Boxes", win, shortcut="Ctrl+B",
        triggered=app.randomBoxes )
    )
    am.addAction( # Random all nodes
        QtGui.QAction("R&andom ALL nodes", win, shortcut="Ctrl+N",
        triggered=app.randomNodes )
    )
    am.addAction( # Random B/W NO Pitch!
        QtGui.QAction("R&andom B/W nodes", win, shortcut="Ctrl+V",
        triggered=partial(app.randomNodes, 1) )
    )
    am.addAction( # Random White
        QtGui.QAction("R&andom White node", win, shortcut="Ctrl+X",
        triggered=partial(app.randomSingleNode, 'white') )
    )
    am.addAction( # Random White small
        QtGui.QAction("R&andom step White node", win, shortcut="Ctrl+Z",
        triggered=partial(app.randomSingleNode, 'white', 1)  )
    )
    am.addAction( # Random Black
        QtGui.QAction("R&andom Black node", win, shortcut="Ctrl+C",
        triggered=partial(app.randomSingleNode, 'black') )
    )
    am.addAction( # Random Grey
        QtGui.QAction("R&andom Grey node", win,
        triggered=partial(app.randomSingleNode, 'grey') )
    )

    # FREEDOMS
    fm = win.menuBar().addMenu("&Freedom")    
    fm.addAction( 
        QtGui.QAction("T&oggle OSC remote control of handles", win, triggered=app.toggleOSCControl )
    )
    fm.addSeparator() #---------
    fm.addAction( 
        QtGui.QAction("T&oggle pitch block", win, triggered=partial(toggleFreedom, 'pitch') )
    )
    fm.addAction( 
        QtGui.QAction("T&oggle grainshift block", win, triggered=partial(toggleFreedom, 'grainshift') )
    )
    fm.addAction( 
        QtGui.QAction("T&oggle length block", win, triggered=partial(toggleFreedom, 'length') )
    )
    fm.addAction( 
        QtGui.QAction("T&oggle shift block", win, triggered=partial(toggleFreedom, 'shift') )
    )
    fm.addAction( 
        QtGui.QAction("T&oggle start block", win, triggered=partial(toggleFreedom, 'start') )
    )



########################
def openFile():
    global fileName
    
    fileName = str( QtGui.QFileDialog.getOpenFileName(qtwin, 'OpenFile', sessions, "Session files (*.txt)") )
    if fileName == '' or not fileName: return -1
    try :
        rawdata = open(fileName, 'rU').read()
    except  IOError :
        alert( "ERROR : file %s does not exist" % fileName )
        return -1

    app.setSession(rawdata)
    
def save():
    print fileName
    if fileName == None:
        saveAs()
    else:
        app.saveSession(fileName)

def saveAs():
    global fileName
    fileName = str( QtGui.QFileDialog.getSaveFileName(qtwin, 'Save As', sessions) )
    app.saveSession(fileName) 

####################
def openSnapFile():
    global snapName
    snapName = str( QtGui.QFileDialog.getOpenFileName(qtwin, 'OpenFile', snapshots, "Snapshot files (*.txt)") )
    if snapName == '' or not snapName: return -1
    try :
        rawdata = open(snapName, 'rU').read()
    except  IOError :
        alert( "ERROR : snap file %s does not exist" % snapName )
        return -1

    app.loadSnapshots(rawdata)
    
def saveSnap():
    data = app.getSnapshotJSON()
    print snapName
    if snapName == None:
        saveSnapAs()
    else:
        savedata = open(str(snapName), 'w')
        savedata.write(str(data))
        savedata.close()
    
def saveSnapAs():
    global snapName
    snapName = str( QtGui.QFileDialog.getSaveFileName(qtwin, 'Save As', snapshots) )
    if snapName == '' or not snapName: return -1
    saveSnap()

def setSnapshot(index):
    try:
        app.setSnapshot(index)
    except KeyError:
        alert( "snapshot %i not defined yet" % index  )

        
#######################

def toggleFreedom(degree): app.freedom[ degree ] = not app.freedom[ degree ]
def volChange(i): app.vol = i/10.0
def autoNodes(): app.autoNodes = not app.autoNodes
def bounce(): app.bounce = not app.bounce
def changeAuto(i):
    app.boxStep = app.boxStep + i
    app.updateBoxDelta()

def addSnd():
    init = os.path.basename(fileName)
    sndfiles = QtGui.QFileDialog.getOpenFileNames( qtwin,'Open Sound File', init,
                                                   "WAV (*.wav);;FLAC (*.flac);;AIFF (*.aiff);;MP3 (*.mp3)")
    for fil in sndfiles:
        fil = str(fil)
        if fil == '' or not fil: return -1
        name = os.path.basename(fil)
        poolMenu.addAction( 
            QtGui.QAction("&%s" % name, qtwin,triggered=partial(app.loadSnd, fil))
        )
        
##    sndfolders
def addFolder(path=False):
    if path == False:
        init = os.path.basename(fileName)
        path = QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', init,
                                                      QtGui.QFileDialog.ShowDirsOnly)
    # TO DO: THIS dialogue should allow to see the files. otherwise we dont know whats in the dirs
    if os.path.isfile(path): # if selected a file
        path = os.path.dirname(path)

    for root, dirs, files in os.walk( str(path) ) :
        for s in files :
            fpath = os.path.join(root, s)
            if '.wav' in s or '.flac' in s or '.aiff' in s: ## filter no sounds
                poolMenu.addAction( 
                    QtGui.QAction("&%s" % s, qtwin,triggered=partial(app.loadSnd, fpath))
             )

    if not path in sndfolders:
        sndfolders.append(str(path))

def doPoolMenu():
    global poolMenu
##    qtwin.removeMenu(poolMenu)
    poolMenu = qtwin.menuBar().addMenu("&SoundPool")       
    poolMenu.addAction(
            QtGui.QAction("A&dd sound to pool", qtwin, triggered=addSnd)
    )
    poolMenu.addAction(
            QtGui.QAction("A&dd folder to pool", qtwin, triggered=addFolder)
    )
    poolMenu.addAction(
            QtGui.QAction("C&LEAR pool", qtwin, triggered=clearMenu)
    )
    poolMenu.addSeparator() #---------
    filePool = doSndMenu()
    for f in filePool :
        poolMenu.addAction( 
            QtGui.QAction("&%s" % os.path.basename(f), qtwin, triggered=partial(app.loadSnd, f))
    )  

def clearMenu(): print "this should clear the menu from sounds"

####################

def doSndMenu() :
    # in filename alphabetical order please!!
    l = []
    p = os.path.join( mirra.utilities.get_main_dir(), 'sounds')
        
    for dirpath, dirnames, fname in os.walk(p) :
        for f in fname :
            if f[0] != '.' : # mac .DS_Store and other hidden files
##                        if dirname[0]  != '.' : # SVN folders on linux and hidden folders in general
                l.append( os.path.join(dirpath, f) )
    return l



