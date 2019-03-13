import csv
import sys
import sqlite3
import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGridLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

class Example(QWidget):
	
	def __init__(self):
		super().__init__()
		
		self.initUI()
		
	def initUI(self):

		#Sets up the grid layout
		self.grid_layout = QGridLayout()
		self.setLayout(self.grid_layout)

		#Sets the sizes for things
		self.fishSize = 70
		self.textSize = 25
		self.maxResults = 10

		#Add the titles and then adds them to the grid
		self.ColLabels = [QLabel("Top", self),QLabel("Recent", self)]
		for lbl in self.ColLabels:
			lbl.setFont(QFont('Arial', self.textSize*2))

		#Adds the titles to the grid
		self.grid_layout.addWidget(self.ColLabels[0],0,1)
		self.grid_layout.addWidget(self.ColLabels[1],0,5,1,2)

		#Makes the column labels for the text and fish
		self.nameLabels = [[QLabel("",self) for y in range(2)] for x in range(self.maxResults+1)]
		self.speedLabels = [[QLabel("",self) for y in range(2)] for x in range(self.maxResults+1)]
		self.fishLabels = [[[QLabel(self) for z in range(3)] for y in range(self.maxResults)] for x in range(2)]

		for j in range(2):
			self.nameLabels[0][j].setText("Name")
			self.speedLabels[0][j].setText("Speed (cm/s)")

		#Sets fonts and places the labels on the grid
		for i in range(len(self.nameLabels)):
			for j in range(2):
				self.grid_layout.addWidget(self.nameLabels[i][j],i+1,j*4)
				#lets speed label span
				if i == 0:
					self.grid_layout.addWidget(self.speedLabels[i][j],i+1,1+j*4,1,2)
				else:
					self.grid_layout.addWidget(self.speedLabels[i][j],i+1,1+j*4)

		#Adds fish labels to grid
		for i in range(2):
			for j in range(self.maxResults):
				for k in range(3):
					self.grid_layout.addWidget(self.fishLabels[i][j][k],j+2,2+i*4)

		#Add middle space and line
		self.spaceLabels = [QLabel("       |       ",self) for x in range(self.maxResults+2)]
		for i in range(len(self.spaceLabels)):
			self.spaceLabels[i].setFont(QFont('Arial', self.textSize))
			self.grid_layout.addWidget(self.spaceLabels[i],i,3)

		#updates the board
		self.UpdateBoard()

		#Creates the window
		self.setGeometry(20, 75, 1250, 900)
		self.setWindowTitle('Scoreboard')    

		self.show()

	def UpdateBoard(self):
		self.fishSize = int(0.075*self.height())
		self.textSize = int(0.02*self.width())

		#Resets Top label size
		for lbl in self.ColLabels:
			lbl.setFont(QFont('Arial', self.textSize*2))
		
		#Gets the data from the CSV
		with open('beamBreaksTESTER.csv','r',newline='') as f_input:
		    csv_input = csv.DictReader(f_input)
		    speedData = sorted(csv_input, key = lambda row: (float(row['Speed5'])), reverse = True)

		with open('beamBreaksTESTER.csv','r',newline='') as f_input:
		    csv_input = csv.DictReader(f_input)
		    timeData = sorted(csv_input, key = lambda row: (row['Time']), reverse = True)

		data = [speedData,timeData]

		#Adds all the text to the name and speed columns
		for i in range(len(speedData)):
			if i < self.maxResults:
				TopNameStr = '{num}.  {name}'.format(num=i+1,name=speedData[i]['Name'])
				TopSpeedStr = '{speed}'.format(speed=round(float(speedData[i]['Speed5']),2))
				RecentNameStr = '{num}.  {name}'.format(num=i+1,name=timeData[i]['Name'])
				RecentSpeedStr = '{speed}'.format(speed=round(float(timeData[i]['Speed5']),2))

				nameStrs = [TopNameStr,RecentNameStr]
				speedStrs = [TopSpeedStr,RecentSpeedStr]

				#Sets the text
				for j in range(2):
					self.nameLabels[i+1][j].setText(nameStrs[j])
					self.speedLabels[i+1][j].setText(speedStrs[j])

		#Adjusts the size of all the text boxes
		for i in range(len(self.nameLabels)):
			for j in range(2):
				self.nameLabels[i][j].setFont(QFont('Arial', self.textSize))
				self.speedLabels[i][j].setFont(QFont('Arial', self.textSize))

				self.nameLabels[i][j].adjustSize()
				self.speedLabels[i][j].adjustSize()

		#Adds the pictures to the fish columns
		for i in range(2):
			for j in range(min(len(speedData),self.maxResults)):
				#Gets the values for each body, color, fin, and tail
				body = data[i][j]['Body']
				color = data[i][j]['Material']
				fin = data[i][j]['FinShape']
				tail = data[i][j]['TailShape']

				#Gets the png from based on the name of each
				bodyPix = QPixmap('Medium_Fish/'+body+color+'.png').scaledToHeight(self.fishSize)
				finPix = QPixmap('Medium_Fish/'+body+'Dorsal'+fin+'.png').scaledToHeight(self.fishSize)
				tailPix = QPixmap('Medium_Fish/'+body+'Tail'+tail+'.png').scaledToHeight(self.fishSize)

				pixes = [bodyPix,finPix,tailPix]

				#Sets each pixmap
				for k in range(3):
					self.fishLabels[i][j][k].setPixmap(pixes[k])
		
if __name__ == '__main__':

	app = QApplication(sys.argv)
	ex = Example()

	timer = QTimer()
	timer.timeout.connect(ex.UpdateBoard)
	timer.start(3000)

	sys.exit(app.exec_())
