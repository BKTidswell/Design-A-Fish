import RPi.GPIO as GPIO
import time
import datetime
import numpy as np
import os
import sys
from PyQt5.QtWidgets import (QWidget, QLabel,
    QComboBox, QApplication,QPushButton)
from PyQt5.QtGui import QPainter, QColor, QBrush
import PyQt5.QtGui as QtGui
import colorsys


#The purpose of this code is to make it so that you can have as many
# different beams as you like. Simply add the pin number where you have
# plugged in the new IR detector to beamPins and you should be good to go.

# Sets the beam pin numbers
beamPins = [8,10,12,16,18,22]

#The distances here are in centimeters, and should be the
# distances between the different IR recievers in order to
# correctly calculate the speeds
distArray = [5.5,64.5,8,67,8.5]

# Sets GPIO numbering mode and defines input PIN
GPIO.setmode(GPIO.BOARD)
for b in beamPins:
    GPIO.setup(b, GPIO.IN, pull_up_down = GPIO.PUD_UP)

class BeamGUI(QWidget):

    def __init__(self, materialType, bodyType, spineType):
        super().__init__()
        self.materialType = materialType
        self.bodyType = bodyType
        self.spineType = spineType
        self.firstData = True
        self.initUI()
        self.last_call = 0
        
        self.maxSpeed = 30
        self.R = 255
        self.G = 255
        self.B = 255

    def initUI(self):     
        #Creates the labels for the drop downs
        self.lbl1 = QLabel("Body Type", self)
        self.lbl2 = QLabel("Material Type", self)
        self.lbl3 = QLabel("Spine Type", self)
        self.lbl1.move(10, 5)
        self.lbl2.move(100, 5)
        self.lbl3.move(200, 5)

        #Creates the body drop down menu
        bodyCombo = QComboBox(self)
        bodyCombo.addItem("- - -")
        bodyCombo.addItem("Long")
        bodyCombo.addItem("Normal")
        bodyCombo.addItem("Tall")

        #Creates the material drop down menu
        materialCombo = QComboBox(self)
        materialCombo.addItem("- - -")
        materialCombo.addItem("Pink")
        materialCombo.addItem("Orange")
        materialCombo.addItem("Yellow")

        #Creates the spine drop down menu
        spineCombo = QComboBox(self)
        spineCombo.addItem("- - -")
        spineCombo.addItem("Long")
        spineCombo.addItem("Normal")
        spineCombo.addItem("Tall")

        #Sets the location of drop downs
        bodyCombo.move(10, 25)
        materialCombo.move(100, 25)
        spineCombo.move(200, 25)

        #Attaches the functions to the drops downs
        bodyCombo.activated[str].connect(self.changeBody)
        materialCombo.activated[str].connect(self.changeMaterial)
        spineCombo.activated[str].connect(self.changeSpine)

        #Creates the buttons to check the beams and start the trial
        self.trialButton = QPushButton("Run Trial", self)
        self.trialButton.move(400, 25)

        setupButton = QPushButton("Check Beams", self)
        setupButton.move(300, 25)

        cancelButton = QPushButton("Cancel Run", self)
        cancelButton.setStyleSheet("background-color: red")
        cancelButton.move(500, 25)

        #Connects the buttons the functions
        self.trialButton.clicked.connect(self.runTrials)
        setupButton.clicked.connect(self.beamSetup)
        cancelButton.clicked.connect(self.cancelRun)

        #Creates the status string label
        self.status = QLabel("", self)
        self.status.move(300, 60)

        #Makes font
        newfont = QtGui.QFont("Times", 40, QtGui.QFont.Bold)

        #Creates Time Label
        self.time = QLabel("Time:",self)
        self.time.move(10, 75)
        self.time.setFont(newfont)

        #Creates Speed Label
        self.speed = QLabel("Speed:",self)
        self.speed.move(10, 175)
        self.speed.setFont(newfont)

        #Creates Speed Label
        self.accel = QLabel("Accel:",self)
        self.accel.move(10, 275)
        self.accel.setFont(newfont)
        
        #Makes the window
        self.setGeometry(300, 300, 600, 350)
        self.setWindowTitle('Build-A-Fish')
        self.show()

    def changeMaterial(self, text):
        #Changes the material type string
        self.materialType = text

    def changeBody(self, text):
        #Changes the body type string
        self.bodyType = text

    def changeSpine(self, text):
        #Changes the body type string
        self.spineType = text

    def cancelRun(self):
        self.status.setText("Run Canceled!")
        self.status.adjustSize()
        self.trialButton.setEnabled(True)
        self.state = -2
        app.processEvents()

    def runTrials(self):
        #Don't run if material and body haven't been set
        if self.materialType == "- - -" or self.bodyType == "- - -" or self.spineType == "- - -":
            print(self.materialType+self.bodyType)
            self.status.setText("Please set Body, Spine, and Material")
            self.status.adjustSize()
        else:
            #prevent button from being clicked too much
            if time.time() - self.last_call < 1:
                return
            #If they have set the material and enough time has passed
            else:
                self.trialButton.setEnabled(False)
                self.status.setText("Ready to run!")
                self.status.adjustSize()
                #Update to show ready to run
                app.processEvents()
                app.processEvents()
                self.beamBreakSpeed()
                self.trialButton.setEnabled(True)
                self.last_call = time.time()

    # Defines a function to print alignments
    def printAlignString(self,beam_a):
        outString = "Please align these beams:"
        brokenBeams = np.where(beam_a == 0)
        #if the length of the list of broken beams is greater than 0
        if len(brokenBeams[0]) != 0:
            #print out the number of those beams so it's clear which
            # need to be realigned
            for b in brokenBeams:
                outString += " " + str(b+1)[1:-1]
            self.status.setText(outString)
            self.status.adjustSize()
            return(False)
        else:
        #Otherwise let the person know that the beams are aligned
            self.status.setText("All beams are aligned")
            self.status.adjustSize()
            return(True)

    #Checks that the beams are in alignment, and lets you know
    # which need to be aligned
    def beamSetup(self):
        #Updates the status string
        self.status.setText("Checking Setup")
        self.status.adjustSize()
        #gets the input for each beam
        beamState = np.asarray([GPIO.input(b) for b in beamPins])
        #Show the new beam state
        aligned = self.printAlignString(beamState)

    #This function is for getting the times of the breaks and the speeds
    # from that and the distance
    def beamBreakSpeed(self):
        #Sets up the time and the filepath
        InitializationTime = time.time()

        if self.firstData:
            timeCSV = open("/home/pi/Desktop/beamBreaks.csv","w")
            #Writes the CSV headers
            startStr = "Body,Material,Spine"
            for p in range(1,len(beamPins)+1):
                startStr += "B"+str(p)+"Time,"
            for p in range(1,len(beamPins)):
                startStr += "Speed"+str(p)+","
            for p in range(1,int(len(beamPins)/2)):
                startStr += "Accel"+str(p)+","

            timeCSV.write(startStr[:-1]+"\n")
            print(startStr[:-1])

            self.firstData = False
        else:
            timeCSV = open("/home/pi/Desktop/beamBreaks.csv","a")

        #Sets up the time and speed arrays
        timeArray = [0]*len(beamPins)
        speedArray = [0]*(len(beamPins)-1)
        accelArray = [0]*(int(len(beamPins)/2)-1)

        #Starts the state at zero
        self.state = 0

        #What this does is step through the different IR receivers
        # one by one, and moves onto the next one once one beam has been
        # broken.
        while self.state >= 0:
            state = self.state
            app.processEvents()
            if(GPIO.input(beamPins[state]) == 0):
            #Get the time of the beam break
                timeArray[state] = time.time() - InitializationTime
                self.status.setText("Beam "+str(state+1)+" Broken")
                self.status.adjustSize()
                app.processEvents()
                #If the beam broken is at or past the second....
                if state >= 1:
                #Calculate the speed between the two beams
                    speedArray[state-1] = distArray[state-1]/(timeArray[state]-timeArray[state-1])

                #If the beam broken is at or past the fourth....
                #States are 0 indexed recall
                if state > 1 and state % 2 == 1:
                    #Calculate the acceleration between the two beams
                    accelArray[int(state/2)-1] = (speedArray[state-1]-speedArray[state-3])/(timeArray[state]-timeArray[state-2])
                    print(accelArray[int(state/2)-1])
                    
                #If the last beam has been broken
                if state == len(beamPins)-1:
                #Create a string to write out to the CSV
                    outStr = str(self.bodyType)+","+str(self.materialType)+","+str(self.spineType)+","
                    for p in timeArray+speedArray+accelArray:
                        outStr += str(p) + ","
                    print(outStr[:-1])
                    #Write that string
                    timeCSV.write(outStr[:-1]+"\n")
                    #sets the state to -1
                    state = -1

                #Otherwise increase the state by 1
                else:
                    state += 1

        #Closes the CSV file
        timeCSV.close()

        if self.state != -2:
            #Gets the rounded values
            roundTime = round(timeArray[-1] - timeArray[0],2)
            roundSpeed = round(speedArray[-1],2)
            roundAccel = round(accelArray[0],2)

            #change color of rectangle by going from HSV to RGB
            # will circle around to red at > 50 cm/s but the top
            # speed can be better calibrated later 
            h = roundSpeed/self.maxSpeed
            rgb = colorsys.hsv_to_rgb(h,1,1)
            self.R = rgb[0]*255
            self.G = rgb[1]*255
            self.B = rgb[2]*255
            
            #Changes the text
            self.time.setText("Time: " + str(roundTime) + " secs")
            self.speed.setText("Speed: " + str(roundSpeed) + " cm/s")
            self.accel.setText("Accel: " + str(roundAccel) + " cm/s^2")
            self.status.setText("Done Running")
            
            self.time.adjustSize()
            self.speed.adjustSize()
            self.accel.adjustSize()
            self.status.adjustSize()

    #These draw the squares
    def paintEvent(self, e):
        self.qp = QPainter()
        self.qp.begin(self)
        self.drawRectangles()
        self.qp.end()

    def drawRectangles(self):
        self.qp.setBrush(QColor(self.R, self.G, self.B))
        self.qp.drawRect(510, 100, 60, 150)

        self.update()

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = BeamGUI(bodyType = "- - -", materialType = "- - -", spineType = "- - -")
    sys.exit(app.exec_())
