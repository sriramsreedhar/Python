#!/usr/bin/env python
import MySQLdb
connection = MySQLdb.connect('localhost','sriram','****','test')  # create the connection
cursor = connection.cursor()     # get the cursor
cursor.execute("SELECT * FROM Writers")
rows = cursor.fetchall()
for row in rows:
         	print row
