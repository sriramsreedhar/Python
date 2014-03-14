#!/usr/bin/env python
f=open('/home/python/scripts/test.txt','r')
modifyme=f.readlines()
print (modifyme)
f.close()
print (modifyme)
modifyme[3]=" This is modified by sriram"
print (modifyme)
f=open('/home/python/scripts/test.txt','w')
f.writelines(modifyme)
f.close()
