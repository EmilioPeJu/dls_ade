#! /bin/env dls-python
import sys

var1 = sys.argv[1]

print("I am not the message?")

class Error(Exception):
    pass

print("Do you liek: " + var1 + "?")

raise Error("I am the message.")

