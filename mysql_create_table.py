#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb as mdb

con = mdb.connect('localhost', 'sriram', '****', 'test');

with con:
    
    cur = con.cursor()
    #cur.execute("DROP TABLE IF EXISTS Writers")
    cur.execute("CREATE TABLE riters(Id INT PRIMARY KEY AUTO_INCREMENT, \
                 Name VARCHAR(25))")
    cur.execute("INSERT INTO riters(Name) VALUES('Jack London')")
    cur.execute("INSERT INTO riters(Name) VALUES('Honore de Balzac')")
    cur.execute("INSERT INTO riters(Name) VALUES('Lion Feuchtwanger')")
    cur.execute("INSERT INTO riters(Name) VALUES('Emile Zola')")
    cur.execute("INSERT INTO riters(Name) VALUES('Truman Capote')")
