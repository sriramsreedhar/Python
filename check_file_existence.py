#!/usr/bin/python
import os
f="/home/python/scripts/test.txt"
if os.path.isfile(f):
	print "File text.txt exists"
else:
	print "File not found"
