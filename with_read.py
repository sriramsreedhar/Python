#!/usr/bin/python
with open('test.txt') as f:
 #content = f.readlines()
 content = f.read().splitlines()
print content
