
import RPi.GPIO as GPIO
import time
import datetime
import numpy as np
import os

#set GPIO numbering mode and define input PIN
pinNum = 8
GPIO.setmode(GPIO.BOARD)      
GPIO.setup(pinNum, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#Set some useful variables
Cir1State = 0 #Tells you the state of the first breakbeam
Cir2State = 0 #Tells you the state of the second breakbeam
r = 0
InitializationTime = time.time()
TimeofBeam1Break = np.arange(100.0)
TimeofBeam2Break = np.arange(100.0)

while True: 
    if GPIO.input(pinNum) ==0:
        print ('unaligned')
    if GPIO.input(pinNum) ==1:
        print ('Sucessfully aligned!')
