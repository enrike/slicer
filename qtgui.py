from __future__ import print_function
from PyQt5 import QtCore, QtWidgets, QtWidgets
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
    box = QtWidgets.QMessageBox()
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
        QtWidgets.QAction("O&pen", win, shortcut="Ctrl+O", triggered=openFile)
    )
    fm.addAction(
        QtWidgets.QAction("S&ave", win, shortcut="Ctrl+S", triggered=save)
    )
    fm.addAction(
        QtWidgets.QAction("S&ave As", win, shortcut="Ctrl+SHIFT+S", triggered=saveAs)
    )
    fm.addSeparator() #---------
    fm.addAction(
        QtWidgets.QAction("D&raw waveform", win, shortcut="Ctrl+F", triggered=setDrawWave)
    )
    fm.addSeparator() #---------
    fm.addAction(
        QtWidgets.QAction("E&xit", win, shortcut="Ctrl+Q", triggered=app.end)
    )
    
    # SNAPSHOT
    sm = win.menuBar().addMenu("&Snapshot")
    sm.addAction(
        QtWidgets.QAction("O&pen snapshot", win, triggered=openSnapFile)
    )
    sm.addAction(
        QtWidgets.QAction("S&ave snapshot", win, triggered=saveSnap)
    )
    sm.addAction(
        QtWidgets.QAction("S&ave snapshot As", win, triggered=saveSnapAs)
    )
    fm.addSeparator() #---------
    sm.addAction(
        QtWidgets.QAction("Toogle load snap mode", win, triggered=app.toogleLoadSnapMode)
    )
    sm.addSeparator() #---------
    for i in range(10):
        sm.addAction(
            QtWidgets.QAction("L&OAD snapshot %i" %i, win, triggered=partial(setSnapshot, i))
        )
    sm.addSeparator() #---------
    for i in range(10):
        sm.addAction(
            QtWidgets.QAction("S&TORE snapshot %i" %i, win, triggered=partial(app.storeSnapshot, i))
        )

    # SOUND POOl
    doPoolMenu()

    # VOLUME
    vm = win.menuBar().addMenu("&Volume")
    vm.addAction( # MUTE
            QtWidgets.QAction("M&ute", win, shortcut="Ctrl+M", triggered= partial(volChange, 0) )
    )
    for i in range(1,11): # 1 to 10
        n = i
        if n == 10: n = 0 # 10 corresponds to key 0
        vm.addAction( 
            QtWidgets.QAction("V&olume %s" %(i/10.), win, shortcut="Ctrl+%s" % n,
            triggered= partial(volChange, i) )
        )

    # NOL
    nm = win.menuBar().addMenu("&Num of Layers")

    for i in range(1,9):
        nm.addAction(
            QtWidgets.QAction("%s&" % i, win, triggered = partial(app.nol, i))
        )

    # AUTO
    am = win.menuBar().addMenu("&Auto")
    am.addAction( # Auto movement
            QtWidgets.QAction("A&utomove  toggle", win, triggered=autoNodes )
    )
    am.addAction( # INCREASE Auto movement
        QtWidgets.QAction("I&ncrease movement", win, shortcut="Ctrl++",
                      triggered=partial(changeAuto, 0.25) )
    )
    am.addAction( # DECRESE Auto movement
        QtWidgets.QAction("D&ecrease movement", win, shortcut="Ctrl+-",
                      triggered=partial(changeAuto, -0.25) )
    )
    am.addAction( # Auto movement
        QtWidgets.QAction("B&ounce toggle", win, triggered=bounce )
    )
    am.addSeparator() #--------- 
    am.addAction( # Random
            QtWidgets.QAction("R&andom situation", win, shortcut="Ctrl+R",
            triggered=app.randomSituation )
        )
    am.addAction( # Random boxes
        QtWidgets.QAction("R&andom Boxes", win, shortcut="Ctrl+B",
        triggered=app.randomBoxes )
    )
    am.addAction( # Random boxes small
        QtWidgets.QAction("R&andom step Boxes", win, shortcut="Ctrl+D",
        triggered=app.randomBoxesSmall )
    )
    am.addAction( # Random all nodes
        QtWidgets.QAction("R&andom ALL nodes", win, shortcut="Ctrl+N",
        triggered=app.randomNodes )
    )
    am.addAction( # Random B/W NO Pitch!
        QtWidgets.QAction("R&andom B/W nodes", win, shortcut="Ctrl+V",
        triggered=partial(app.randomNodes, 1) )
    )
    am.addAction( # Random White
        QtWidgets.QAction("R&andom White node", win, shortcut="Ctrl+X",
        triggered=partial(app.randomSingleNode, 'white') )
    )
    am.addAction( # Random White small
        QtWidgets.QAction("R&andom step White node", win, shortcut="Ctrl+Z",
        triggered=partial(app.randomSingleNode, 'white', 1)  )
    )
    am.addAction( # Random Black
        QtWidgets.QAction("R&andom Black node", win, shortcut="Ctrl+C",
        triggered=partial(app.randomSingleNode, 'black') )
    )
    am.addAction( # Random Grey
        QtWidgets.QAction("R&andom Grey node", win,
        triggered=partial(app.randomSingleNode, 'grey') )
    )

    # FREEDOMS
    fm = win.menuBar().addMenu("&Freedom & control")
    fm.addAction( 
        QtWidgets.QAction("I&nverse Panning", win, triggered=inversepan )
    )
##    fm.addAction( 
##        QtWidgets.QAction("T&oggle OSC remote control of handles", win, triggered=app.toggleOSCControl )
##    )
##    fm.addAction( 
##        QtWidgets.QAction("R&eset OSC connection", win, triggered=app.setOSC )
##    )
    fm.addSeparator() #---------
    fm.addAction( 
        QtWidgets.QAction("T&oggle pitch block", win, triggered=partial(toggleFreedom, 'pitch') )
    )
    fm.addAction( 
        QtWidgets.QAction("T&oggle grainshift block", win, triggered=partial(toggleFreedom, 'grainshift') )
    )
    fm.addAction( 
        QtWidgets.QAction("T&oggle length block", win, triggered=partial(toggleFreedom, 'length') )
    )
    fm.addAction( 
        QtWidgets.QAction("T&oggle shift block", win, triggered=partial(toggleFreedom, 'shift') )
    )
    fm.addAction( 
        QtWidgets.QAction("T&oggle start block", win, triggered=partial(toggleFreedom, 'start') )
    )



########################
def openFile():
    global fileName
    
    fileName = str( QtWidgets.QFileDialog.getOpenFileName(qtwin, 'OpenFile', sessions, "Session files (*.txt)")[0] )
    if fileName == '' or not fileName: return -1
    try :
        rawdata = open(fileName, 'rU').read()
    except  IOError :
        alert( "ERROR : file %s does not exist" % fileName )
        return -1

    app.setSession(rawdata)
    
def save():
    print(fileName)
    if fileName == None:
        saveAs()
    else:
        app.saveSession(fileName)

def saveAs():
    global fileName
    fileName = str( QtWidgets.QFileDialog.getSaveFileName(qtwin, 'Save As', sessions)[0] )
    app.saveSession(fileName)

def setDrawWave():
    app.setDrawWave()

####################
def openSnapFile():
    global snapName
    snapName = str( QtWidgets.QFileDialog.getOpenFileName(qtwin, 'OpenFile', snapshots, "Snapshot files (*.txt)")[0] )
    if snapName == '' or not snapName: return -1
    try :
        rawdata = open(snapName, 'rU').read()
    except  IOError :
        alert( "ERROR : snap file %s does not exist" % snapName )
        return -1

    app.loadSnapshots(rawdata)
    
def saveSnap():
    data = app.getSnapshotJSON()
    print(snapName)
    if snapName == None:
        saveSnapAs()
    else:
        savedata = open(str(snapName), 'w')
        savedata.write(str(data))
        savedata.close()
    
def saveSnapAs():
    global snapName
    snapName = str( QtWidgets.QFileDialog.getSaveFileName(qtwin, 'Save As', snapshots)[0])
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
def inversepan(): app.inversepan = not app.inversepan
def changeAuto(i):
    app.boxStep = app.boxStep + i
    app.updateBoxDelta()

def addSnd():
    init = os.path.basename(fileName)
    sndfiles = QtWidgets.QFileDialog.getOpenFileNames( qtwin,'Open Sound File', init,
                                                   "WAV (*.wav);;FLAC (*.flac);;AIFF (*.aiff)")[0]
    for fil in sndfiles:
        fil = str(fil)
        if fil == '' or not fil: return -1
        name = os.path.basename(fil)
        poolMenu.addAction( 
            QtWidgets.QAction("&%s" % name, qtwin,triggered=partial(app.loadSnd, fil))
        )
        
##    sndfolders
def addFolder(path=False):
    if path == False:
        init = os.path.basename(fileName)
        path = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder:', init,
                                                      QtWidgets.QFileDialog.ShowDirsOnly)
    # TO DO: THIS dialogue should allow to see the files. otherwise we dont know whats in the dirs
    if os.path.isfile(path): # if selected a file
        path = os.path.dirname(path)

    for root, dirs, files in os.walk( str(path) ) :
        for s in files :
            fpath = os.path.join(root, s)
            if '.wav' in s or '.flac' in s or '.aiff' in s: ## filter out no sounds
                poolMenu.addAction( 
                    QtWidgets.QAction("&%s" % s, qtwin,triggered=partial(app.loadSnd, fpath))
             )

    if not path in sndfolders:
        sndfolders.append(str(path))

def doPoolMenu():
    global poolMenu
    print("rebuilding sound pool menu")
    
    if not poolMenu:    
        poolMenu = qtwin.menuBar().addMenu("&SoundPool")
        
    poolMenu.addAction(
            QtWidgets.QAction("A&dd sound to pool", qtwin, triggered=addSnd)
    )
    poolMenu.addAction(
            QtWidgets.QAction("A&dd folder to pool", qtwin, triggered=addFolder)
    )
    poolMenu.addAction(
            QtWidgets.QAction("C&LEAR pool", qtwin, triggered=clearMenu)
    )
    poolMenu.addSeparator() #---------

    filePool = doSndMenu()
    
    for f in filePool :
        poolMenu.addAction( 
            QtWidgets.QAction("&%s" % os.path.basename(f), qtwin, triggered=partial(app.loadSnd, f))
    )  

def clearMenu():
    poolMenu.clear()
    doPoolMenu()

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



