import RPi.GPIO as GPIO
import time
import datetime
import numpy as np
import os
import sys
from PyQt5.QtWidgets import (QWidget, QLabel,
    QComboBox, QApplication,QPushButton,QGridLayout,QLineEdit)
from PyQt5.QtGui import QPainter, QColor, QBrush
import PyQt5.QtGui as QtGui
import sqlite3

#The purpose of this code is to make it so that you can have as many
# different beams as you like. Simply add the pin number where you have
# plugged in the new IR detector to beamPins and you should be good to go.

# Sets the beam pin numbers
#beamPinsArray = [[8,10,12,16,18,22],[3,5,7,11,13,15]]
beamPinsArray = [[22,18,16,12,10,8],[15,13,11,7,5,3]]

#The distances here are in centimeters, and should be the
# distances between the different IR recievers in order to
# correctly calculate the speeds
#distArrays = [[8.5,52.5,11.5,39.5,7],[8.5,52.5,11.5,39.5,7]]
distArrays = [[7,39.5,11.5,52.5,8.5],[7,39.5,11.5,52.5,8.5]]

# Setting position Values
rows = [10,75,125,175,225,350,475]
cols = [10,100,200,300,425,525,615]

# Sets GPIO numbering mode and defines input PIN
GPIO.setmode(GPIO.BOARD)
for beamPins in beamPinsArray:
    for b in beamPins:
        GPIO.setup(b, GPIO.IN, pull_up_down = GPIO.PUD_UP)

class BeamGUI(QWidget):

    def __init__(self, materialType, bodyType, spineType):
        super().__init__()
        #initializes varibles that will be needed in different
        # functions and places
        self.materialTypes = [materialType,materialType]
        self.bodyTypes = [bodyType,bodyType]
        self.spineTypes = [spineType,spineType]
        self.names = ["",""]
        self.firstData = True
        self.initUI()
        self.last_call = 0

        #Time data for the SQL
        now = datetime.datetime.now()
        self.month = now.month
        self.day = now.day
    
##        self.maxSpeed = 30
##        self.R = 255
##        self.G = 255
##        self.B = 255

        self.states = [0,0]

    def initUI(self):
        
        #Creates the labels for the drop downs
        comboLbls = [QLabel("Body Type", self),QLabel("Material Type", self),QLabel("Spine Type", self),
                     QLabel("Body Type", self),QLabel("Material Type", self),QLabel("Spine Type", self)]
        
        for x in range(len(comboLbls)):
            if x < 3:
                comboLbls[x].move(cols[x], rows[0])
            else:
                comboLbls[x].move(cols[x+1], rows[0])

        #Creates the body drop down menu
        bodyCombos = [QComboBox(self),QComboBox(self)]
        for bc in bodyCombos:
            bc.addItem("- - -")
            bc.addItem("Long")
            bc.addItem("Normal")
            bc.addItem("Tall")

        bodyCombos[0].move(cols[0], rows[0]+15)
        bodyCombos[1].move(cols[4], rows[0]+15)

        #Creates the material drop down menu
        materialCombos = [QComboBox(self),QComboBox(self)]
        for mc in materialCombos:
            mc.addItem("- - -")
            mc.addItem("Pink")
            mc.addItem("Yellow")
            mc.addItem("Blue")

        materialCombos[0].move(cols[1], rows[0]+15)
        materialCombos[1].move(cols[5], rows[0]+15)

        #Creates the spine drop down menu
        spineCombos = [QComboBox(self),QComboBox(self)]
        for sc in spineCombos:
            sc.addItem("- - -")
            sc.addItem("Long")
            sc.addItem("Normal")
            sc.addItem("Tall")

        spineCombos[0].move(cols[2], rows[0]+15)
        spineCombos[1].move(cols[6], rows[0]+15)

        #adds textbox for name entry
        self.nameBoxes = [QLineEdit(self),QLineEdit(self)]

        self.nameBoxes[0].move(cols[0], rows[1])
        self.nameBoxes[1].move(cols[4], rows[1])

        #adds buttons to enter names

        self.nameButtons = [QPushButton('Enter Name',self),QPushButton('Enter Name',self)]
        for i in range(2):
            self.nameButtons[i].clicked.connect(lambda state, x=i: self.enterName(x))

        self.nameButtons[0].move(cols[2], rows[1])
        self.nameButtons[1].move(cols[6], rows[1])

        #Attaches the functions to the drops downs
        for i in range(2):
            bodyCombos[i].activated[str].connect(lambda str, x=i: self.changeBody(str, x))
            materialCombos[i].activated[str].connect(lambda str, x=i: self.changeMaterial(str, x))
            spineCombos[i].activated[str].connect(lambda str, x=i: self.changeSpine(str, x))

        #Creates the buttons to check the beams and start the trial
        self.goButtons = [QPushButton("GO Floaty 1", self),QPushButton("GO Floaty 2", self),
                          QPushButton("GO ALL", self)]

        for gb in self.goButtons:
            gb.setStyleSheet("background-color: green")
            
        self.goButtons[0].move(cols[0],rows[2])
        self.goButtons[1].move(cols[4],rows[2])
        self.goButtons[2].move(cols[3],rows[4])

        self.cancelButtons = [QPushButton("Cancel Floaty 1", self),QPushButton("Cancel Floaty 2", self),
                          QPushButton("CANCEL ALL", self)]

        for cb in self.cancelButtons:
            cb.setStyleSheet("background-color: red")
            
        self.cancelButtons[0].move(cols[0],rows[3])
        self.cancelButtons[1].move(cols[4],rows[3])
        self.cancelButtons[2].move(cols[3],rows[5])

        setupButton = QPushButton("Check Beams", self)
        setupButton.move(cols[3],rows[0])

        #Connects the buttons the functions
        setupButton.clicked.connect(self.beamSetup)
        
        for i in range(2):
            self.goButtons[i].clicked.connect(lambda state, x=[i]: self.runTrials(x))
            self.cancelButtons[i].clicked.connect(lambda state, x=[i]: self.cancelRun(x))

        self.goButtons[2].clicked.connect(lambda state, x=[0,1]: self.runTrials(x))
        self.cancelButtons[2].clicked.connect(lambda state, x=[0,1]: self.cancelRun(x))

        #Creates the status string label
        self.statusLbls = [QLabel("", self),QLabel("", self)]
        self.statusLbls[0].move(cols[1], rows[3])
        self.statusLbls[1].move(cols[5], rows[3])

        #Makes font
        newfont = QtGui.QFont("Times", 40, QtGui.QFont.Bold)

        #Creates Time Labels
        self.timeLbls = [QLabel("Time:",self),QLabel("Time:",self)]
        self.timeLbls[0].move(cols[0], rows[4])
        self.timeLbls[0].setFont(newfont)
        self.timeLbls[1].move(cols[4], rows[4])
        self.timeLbls[1].setFont(newfont)

        #Creates Speed Labels
        self.speedLbls = [QLabel("Speed:",self),QLabel("Speed:",self)]
        self.speedLbls[0].move(cols[0], rows[5])
        self.speedLbls[0].setFont(newfont)
        self.speedLbls[1].move(cols[4], rows[5])
        self.speedLbls[1].setFont(newfont)
        
        #Makes the window
        self.setGeometry(200, 200, 725, 550)
        self.setWindowTitle('Build-A-Fish')
        self.show()

    def changeMaterial(self, text, n):
        #Changes the material type string
        self.materialTypes[n] = text

    def changeBody(self, text, n):
        #Changes the body type string
        self.bodyTypes[n] = text

    def changeSpine(self, text, n):
        #Changes the body type string
        self.spineTypes[n] = text

    def enterName(self,n):
        self.names[n] = self.nameBoxes[n].text()
        self.statusLbls[n].setText("Name set to "+self.names[n])
        self.statusLbls[n].adjustSize()

    def cancelRun(self, a):
        for n in a:
            self.statusLbls[n].setText("Run Canceled!")
            self.statusLbls[n].adjustSize()
            self.goButtons[n].setEnabled(True)
            self.states[n] = -2
        app.processEvents()

    def runTrials(self, a):
        run = False

        for n in a:
            #Don't run if material and body haven't been set
            if self.materialTypes[n] == "- - -" or self.bodyTypes[n] == "- - -" \
               or self.spineTypes[n] == "- - -" or self.names[n] == "":
                self.statusLbls[n].setText("Set Body, Spine, Material, and Name")
                self.statusLbls[n].adjustSize()
                run = False
            else:
                self.statusLbls[n].setText("Set other side")
                self.statusLbls[n].adjustSize()
                run = True
            
        if run:
            #prevent button from being clicked too much
            if time.time() - self.last_call < 1:
                return
            #If they have set the material and enough time has passed
            else:
                for n in a:
                    self.goButtons[n].setEnabled(False)
                    self.statusLbls[n].setText("Ready to run!")
                    self.statusLbls[n].adjustSize()
                    
                #Update to show ready to run
                app.processEvents()
                app.processEvents()
                self.beamBreakSpeed(a)
                
                for n in a:
                    self.goButtons[n].setEnabled(True)
                    
                self.last_calls = time.time()

    # Defines a function to print alignments
    def printAlignString(self,beam_a):
        outString = "Align these beams:"
        brokenBeams = np.where(beam_a == 0)
        #if the length of the list of broken beams is greater than 0
        if len(brokenBeams[0]) != 0:
            #print out the number of those beams so it's clear which
            # need to be realigned
            for b in brokenBeams:
                outString += " " + str(b+1)[1:-1]
            self.statusLbls[0].setText(outString)
            self.statusLbls[0].adjustSize()
            return(False)
        else:
        #Otherwise let the person know that the beams are aligned
            self.statusLbls[0].setText("All beams are aligned")
            self.statusLbls[0].adjustSize()
            return(True)

    #Checks that the beams are in alignment, and lets you know
    # which need to be aligned
    def beamSetup(self):
        #Updates the status string
        self.statusLbls[0].setText("Checking Setup")
        self.statusLbls[0].adjustSize()
        #gets the input for each beam
        beamState = np.asarray([GPIO.input(b) for b in beamPins])
        #Show the new beam state
        aligned = self.printAlignString(beamState)

    #This function is for getting the times of the breaks and the speeds
    # from that and the distance
    def beamBreakSpeed(self,a):
        #Sets up the time and the filepath
        InitializationTime = time.time()

        numPins = len(beamPinsArray[0])
        
        if self.firstData:
            timeCSV = open("/home/pi/Desktop/beamBreaks.csv","w")
            #Writes the CSV headers
            startStr = "Body,Material,Spine"
            for p in range(1,numPins+1):
                startStr += "B"+str(p)+"Time,"
            for p in range(1,numPins):
                startStr += "Speed"+str(p)+","
            for p in range(1,int(numPins/2)):
                startStr += "Accel"+str(p)+","

            timeCSV.write(startStr[:-1]+"\n")
            print(startStr[:-1])

            self.firstData = False
            
        else:
            timeCSV = open("/home/pi/Desktop/beamBreaks.csv","a")

        conn = sqlite3.connect("scoreboard.db")

        try:
            conn.execute('''CREATE TABLE SCORES
                         (ID INT PRIMARY KEY    NOT NULL,
                         NAME            TEXT   NOT NULL,
                         SPEED           REAL   NOT NULL,
                         DAY             INTEGER NOT NULL,
                         MONTH           INTERGER NOT NULL,
                         YEAR            INTERGER);''')
        except:
            pass
            
        #Sets up the time and speed arrays
        timeArrays = [[0]*numPins,[0]*numPins]
        speedArrays = [[0]*(numPins-1),[0]*(numPins-1)]
        accelArrays = [[0]*(int(numPins/2)-1),[0]*(int(numPins/2)-1)]

        self.states = [0,0]

        for n in np.setdiff1d([0,1],a):
            print(n)
            self.states[n] = -3

        #What this does is step through the different IR receivers
        # one by one, and moves onto the next one once one beam has been
        # broken.
        while self.states[0] >= 0 or self.states[1] >= 0:
            states = self.states
            app.processEvents()
            for n in a:
                state = states[n]
                
                if(GPIO.input(beamPinsArray[n][state]) == 0):
                #Get the time of the beam break
                    timeArrays[n][state] = time.time() - InitializationTime
                    self.statusLbls[n].setText("Beam "+str(state+1)+" Broken")
                    self.statusLbls[n].adjustSize()
                    app.processEvents()
                    #If the beam broken is at or past the second....
                    if state >= 1:
                    #Calculate the speed between the two beams
                        speedArrays[n][state-1] = distArrays[n][state-1]/\
                                                  (timeArrays[n][state]-timeArrays[n][state-1])

                    #If the beam broken is at or past the fourth....
                    #States are 0 indexed recall
                    if state > 1 and state % 2 == 1:
                        #Calculate the acceleration between the two beams
                        accelArrays[n][int(state/2)-1] = (speedArrays[n][state-1]-speedArrays[n][state-3])\
                                                         /(timeArrays[n][state]-timeArrays[n][state-2])
                        
                    #If the last beam has been broken
                    if state == len(beamPins)-1:
                    #Create a string to write out to the CSV
                        outStr = str(self.bodyTypes[n])+","+str(self.materialTypes[n])+","+str(self.spineTypes[n])+","
                        for p in timeArrays[n]+speedArrays[n]+accelArrays[n]:
                            outStr += str(p) + ","
                        #Write that string
                        timeCSV.write(outStr[:-1]+"\n")
                        #Writes to SQL datebase
                        cursor = conn.execute("SELECT MAX(ID) FROM SCORES")
                        for idNum in cursor:
                            try:
                                newID = idNum[0]+1
                            except:
                                newID = 0
                        conn.execute("INSERT INTO SCORES (ID,NAME,SPEED,DAY,MONTH,YEAR) \
                                    VALUES (?, ?, ?, ?, ?, ?)",\
                                    (newID, self.names[n],speedArrays[n][-1], self.day, self.month, 2019));
                        conn.commit()
                        #sets the state to -4
                        self.states[n] = -4

                    #Otherwise increase the state by 1
                    else:
                        self.states[n] += 1

        #Closes the CSV and SQL files
        timeCSV.close()
        conn.close()

        for n in a:
            if self.states[n] != -2:
                #Gets the rounded values
                roundTime = round(timeArrays[n][-1] - timeArrays[n][0],2)
                roundSpeed = round(speedArrays[n][-1],2)
                
                #Changes the text
                self.timeLbls[n].setText("Time: \n" + str(roundTime) + " secs")
                self.speedLbls[n].setText("Speed: \n" + str(roundSpeed) + " cm/s")
                self.statusLbls[n].setText("Done Running")
                
                self.timeLbls[n].adjustSize()
                self.speedLbls[n].adjustSize()
                self.statusLbls[n].adjustSize()

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = BeamGUI(bodyType = "- - -", materialType = "- - -", spineType = "- - -")
    sys.exit(app.exec_())
