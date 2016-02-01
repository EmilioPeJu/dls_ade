#! /bin/env dls-python
import sys

var1 = sys.argv[1]

print("I am not the " + var1 + "?")


class Error(Exception):
    pass

raise Error("I am the message.")

