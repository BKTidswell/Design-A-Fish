import sqlite3
from random import *

conn = sqlite3.connect('scoreboard.db')
print("Opened database successfully")

conn.execute("DROP TABLE SCORES")

conn.execute('''CREATE TABLE SCORES
         (ID INT PRIMARY KEY     NOT NULL,
         NAME           TEXT    NOT NULL,
         SPEED            REAL     NOT NULL,
         DAY            INTEGER   NOT NULL,
         MONTH          INTEGER  NOT NULL,
         YEAR         INTEGER);''')
print("Table created successfully")


nameList = ["Alice","Bob","Carol","Dan","Eve","Frank","Grace","Heidi","Ivan","Judy",\
            "Michael","Olivia","Peggy","Sybil","Trent","Victor","Ben","Janne","Cassandra",\
            "Jerry","Mike"]

for i in range(len(nameList)):
   conn.execute("INSERT INTO SCORES (ID,NAME,SPEED,DAY,MONTH,YEAR) \
         VALUES (?, ?, ?, ?, ?, ?)",(i, nameList[i], random()*20+10, randint(0,30), randint(10,12), 2018));
   
conn.commit()

cursor = conn.execute("SELECT speed, name from SCORES ORDER BY speed DESC")
for row in cursor:
   print('{name: <15}{speed: <5}'.format(name=row[1],speed=round(row[0],2)))

print("Operation done successfully")

conn.close()

