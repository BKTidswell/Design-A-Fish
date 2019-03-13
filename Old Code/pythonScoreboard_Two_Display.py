import csv
import sys
import sqlite3
import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

class Example(QWidget):
	
	def __init__(self):
		super().__init__()
		
		self.initUI()
		
	def initUI(self):

		self.rows = [10,100,150,227,304,381,458,535,612,689,766,843,920]
		self.cols = [30,80,230,380,700,750,900,1050]

		self.fishSize = 80
		self.firstRun = True
		self.textSize = 25

		labelFont = QFont('Arial', 30)

		(TopNameStr,TopSpeedStr,TopNumStr,RecentNameStr,RecentSpeedStr,RecentNumStr) = self.UpdateBoard()

		self.ColLabels = [QLabel("Top", self),QLabel("Recent", self)]
		for lbl in self.ColLabels:
			lbl.setFont(QFont('Arial', 50))
			
		self.ColLabels[0].move(self.cols[2], self.rows[0])
		self.ColLabels[1].move(self.cols[6]-50, self.rows[0])

		#add the place numbers
		self.numLabels = [QLabel(TopNumStr, self),QLabel(RecentNumStr, self)]
		for lbl in self.numLabels:
			lbl.setFont(QFont('Arial', self.textSize))

		self.numLabels[0].move(self.cols[0], self.rows[1])
		self.numLabels[1].move(self.cols[4], self.rows[1])

		#make name labels
		self.nameLabels = [QLabel(TopNameStr, self),QLabel(RecentNameStr, self)]
		for lbl in self.nameLabels:
			lbl.setFont(QFont('Arial', self.textSize))

		self.nameLabels[0].move(self.cols[1], self.rows[1])
		self.nameLabels[1].move(self.cols[5], self.rows[1])

		#make speed labels
		self.speedLabels = [QLabel(TopSpeedStr, self),QLabel(RecentSpeedStr, self)]
		for lbl in self.speedLabels:
			lbl.setFont(QFont('Arial', self.textSize))

		self.speedLabels[0].move(self.cols[2], self.rows[1])
		self.speedLabels[1].move(self.cols[6], self.rows[1])

		
		self.setGeometry(20, 75, 1250, 925)
		self.setWindowTitle('Scoreboard')    

		self.show()

	def UpdateBoard(self):
		data = ['Name','Body','Material','Spine','TailShape','FinShape','Special','Speed5','Time']

		with open('beamBreaksTESTER.csv','r',newline='') as f_input:
		    csv_input = csv.DictReader(f_input)
		    speedData = sorted(csv_input, key = lambda row: (float(row['Speed5'])), reverse = True)

		with open('beamBreaksTESTER.csv','r',newline='') as f_input:
		    csv_input = csv.DictReader(f_input)
		    timeData = sorted(csv_input, key = lambda row: (row['Time']), reverse = True)

		TopNameStr= "Name\n\n"
		TopSpeedStr = "Speed (cm/s)\n\n"
		TopNumStr = "\n\n"

		RecentNameStr = "Name\n\n"
		RecentSpeedStr = "Speed (cm/s)\n\n"
		RecentNumStr = "\n\n"

		maxResults = 10

		for i in range(len(speedData)):
			if i < maxResults:
				TopNameStr += '{name: <20}\n\n'.format(name=speedData[i]['Name'])
				TopSpeedStr += '{speed: <20}\n\n'.format(speed=round(float(speedData[i]['Speed5']),2))
				TopNumStr += str(i+1)+".\n\n"

				RecentNameStr += '{name: <20}\n\n'.format(name=timeData[i]['Name'])
				RecentSpeedStr += '{speed: <20}\n\n'.format(speed=round(float(timeData[i]['Speed5']),2))
				RecentNumStr += str(i+1)+".\n\n"
		
		speedFishPix = []
		recentFishPix = []

		for i in range(min(len(speedData),maxResults)):
			speedFishPix.append([QLabel(self),QLabel(self),QLabel(self)])
			recentFishPix.append([QLabel(self),QLabel(self),QLabel(self)])

		pix = [speedFishPix,recentFishPix]
		data = [speedData,timeData]

		for h in range(2):
			for i in range(min(len(speedData),maxResults)):
				body = data[h][i]['Body']
				color = data[h][i]['Material']
				fin = data[h][i]['FinShape']
				tail = data[h][i]['TailShape']
				
				bodyPix = QPixmap('Medium_Fish/'+body+color+'.png').scaledToHeight(self.fishSize)
				finPix = QPixmap('Medium_Fish/'+body+'Dorsal'+fin+'.png').scaledToHeight(self.fishSize)
				tailPix = QPixmap('Medium_Fish/'+body+'Tail'+tail+'.png').scaledToHeight(self.fishSize)

				pixes = [bodyPix,finPix,tailPix]
					
				for j in range(3):
					pix[h][i][j].setPixmap(pixes[j])
					pix[h][i][j].move(self.cols[3+h*4], self.rows[i+2])

		if self.firstRun:
			self.firstRun = False
		else:
			self.numLabels[0].setText(TopNumStr)
			self.numLabels[1].setText(RecentNumStr)
			self.nameLabels[0].setText(TopNameStr)
			self.nameLabels[1].setText(RecentNameStr)
			self.speedLabels[0].setText(TopSpeedStr)
			self.speedLabels[1].setText(RecentSpeedStr)
			
			self.numLabels[0].adjustSize()
			self.numLabels[1].adjustSize()
			self.nameLabels[0].adjustSize()
			self.nameLabels[1].adjustSize()
			self.speedLabels[0].adjustSize()
			self.speedLabels[1].adjustSize()

		return (TopNameStr,TopSpeedStr,TopNumStr,RecentNameStr,RecentSpeedStr,RecentNumStr)
		
if __name__ == '__main__':

	app = QApplication(sys.argv)
	ex = Example()

	timer = QTimer()
	timer.timeout.connect(ex.UpdateBoard)
	timer.start(3000)

	sys.exit(app.exec_())
