import sys
import sqlite3
import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

class Example(QWidget):
	
	def __init__(self):
		super().__init__()
		
		self.initUI()
		
	def initUI(self):

		self.DisplayType = 0
		#0 = Today
		#1 = This Week
		#2 = This Month
		#3 = All Time

		self.firstRun = True

		labelFont = QFont('Arial', 30)

		(NumString,NameString,SpeedString,TypeString) = self.changeTimeFrame()

		self.typeLabel = QLabel(TypeString, self)
		self.typeLabel.move(140, 10)
		self.typeLabel.setFont(QFont('Arial', 40))

		self.numLabel = QLabel(NumString, self)
		self.numLabel.move(10, 70)
		self.numLabel.setFont(labelFont)

		self.nameLabel = QLabel(NameString, self)
		self.nameLabel.move(65, 70)
		self.nameLabel.setFont(labelFont)

		self.speedLabel = QLabel(SpeedString, self)
		self.speedLabel.move(300, 70)  
		self.speedLabel.setFont(labelFont)   
		
		self.setGeometry(300, 300, 410, 550)
		self.setWindowTitle('Scoreboard')    

		self.show()

	def changeTimeFrame(self):
		now = datetime.datetime.now()

		Month = now.month
		Day = now.day

		NameString = ""
		SpeedString = ""
		NumString = ""

		topResults = 0

		conn = sqlite3.connect('scoreboard.db')
		cursor = conn.execute("SELECT speed, name, day, month  from SCORES ORDER BY speed DESC")
		for row in cursor:
			if topResults < 10:
				if self.DisplayType%4 == 0 and Month == row[3] and Day == row[2]:
					NameString += '{name: <20}\n'.format(name=row[1])
					SpeedString += '{speed: <5}\n'.format(speed=round(row[0],2))
					NumString += str(topResults+1)+".\n"
					topResults += 1
				elif self.DisplayType%4 == 1 and Month == row[3] and Day <= row[2]+7:
					NameString += '{name: <20}\n'.format(name=row[1])
					SpeedString += '{speed: <5}\n'.format(speed=round(row[0],2))
					NumString += str(topResults+1)+".\n"
					topResults += 1
				elif self.DisplayType%4 == 2 and (Month == row[3] or (Month <= row[3]+1 and Day <= row[2])):
					NameString += '{name: <20}\n'.format(name=row[1])
					SpeedString += '{speed: <5}\n'.format(speed=round(row[0],2))
					NumString += str(topResults+1)+".\n"
					topResults += 1
				elif self.DisplayType%4 == 3:
					NameString += '{name: <20}\n'.format(name=row[1])
					SpeedString += '{speed: <5}\n'.format(speed=round(row[0],2))
					NumString += str(topResults+1)+".\n"
					topResults += 1
		
		if self.DisplayType%4 == 0:
			TypeString = "Daily"
		elif self.DisplayType%4 == 1:
			TypeString = "Weekly"
		elif self.DisplayType%4 == 2:
			TypeString = "Monthly"
		elif self.DisplayType%4 == 3:
			TypeString = "All Time"

		conn.close()

		#self.DisplayType += 1

		if self.firstRun:
			self.firstRun = False
		else:
			self.typeLabel.setText(TypeString)
			self.numLabel.setText(NumString)
			self.nameLabel.setText(NameString)
			self.speedLabel.setText(SpeedString)
			self.typeLabel.adjustSize()
			self.numLabel.adjustSize()
			self.nameLabel.adjustSize()
			self.speedLabel.adjustSize()

		return (NumString,NameString,SpeedString,TypeString)
		
if __name__ == '__main__':

	app = QApplication(sys.argv)
	ex = Example()

	timer = QTimer()
	timer.timeout.connect(ex.changeTimeFrame)
	timer.start(3000)

	sys.exit(app.exec_())
