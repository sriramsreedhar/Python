#!/usr/bin/env python
class MyClass(object):
     i = 123
     def __init__(self):
         self.i = 345

a = MyClass()
print 'Variable inside init => ',a.i
print 'Variable inside class => ',MyClass.i
