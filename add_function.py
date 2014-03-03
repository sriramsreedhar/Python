#!/usr/bin/env python
def add(a,b):   
    return int(a) + int(b)

print "The first number you want to add?"
#a = int(raw_input("First no: "))
a = raw_input("First no: ")
print "What's the second number you want to add?"
#b = int(raw_input("Second no: "))
b = raw_input("Second no: ")

result = add(a, b)

print "The result is: %r." % result 
