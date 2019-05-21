#!/usr/bin/python3
import re
txt="abc xyz pqr"
#to Search for characters other that abc
print(txt)
x=re.findall("[^abc]",txt)

if (x):
    print(x)
    print("There is a match")
else:
    print(x)
    print("No Match found")
