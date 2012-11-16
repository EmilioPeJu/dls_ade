#! /usr/bin/env dls-python2.6
# Reset Local and then Global VS + DP interlocks
# PH 11/05/06

from pkg_resources import require
require('cothread==2.8')
from cothread.catools import *

import time
import sys

ILK_ON    = 1
ILK_OFF   = 0
ILK_BAD   = 0
ILK_READY = 1
ILK_GOOD  = 2

MAXCELL = 25

# default timeout in seconds
timeout = 1.0

################################################################################

# any and all reducers for boolean lists

def any(S):
	for x in S:
		if x:
			return True
	return False
        
def all(S):
	for x in S:
		if not x:
			return False
	return True

################################################################################

def WaitPV(names, value):
	"""Wait for a PV state"""
		
	for c in range(1, 20):

		time.sleep(0.1)
		
		status = caget(names, timeout = timeout)
						
		if any(s.ok != True for s in status):
			continue
						
		if all(s == value for s in status):
			return 0
				
	if not all(s == value for s in status):
		print "WaitPV() timeout"

def WaitPV2(names, value1, value2):
	"""Wait for a PV state"""
		
	for c in range(1, 20):

		time.sleep(0.1)
			
		status = caget(names, timeout = timeout)
						
		if any(s.ok != True for s in status):
			continue

		if all((s == value1) or (s == value2) for s in status):
			return 0
				
	if not all((s == value1) or (s == value2) for s in status):
		print "WaitPV() timeout"

# start of main program ########################################################

zeros = [[0] for n in range(1,MAXCELL)]

print "MPS Storage Ring Fast Vessel Reset"
print "=================================="
print ""

print "Waiting for Vessel card interlocks"

names = ["SR%(cell)02dC-MP-VSILK-02:READY" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV2(names, ILK_READY, ILK_GOOD)

print "Resetting Vessel interlocks"

# This PV resets Interlock B, waits a bit, and then resets Interlock A
names = ["SR%(cell)02dC-MP-VSRST-01:RESET" % {'cell' : cell} for cell in range(1,MAXCELL)]
caput(names, zeros, timeout = timeout)

# Wait for up to 2 seconds for all 24 local Vessel interlocks to be set
names = ["SR%(cell)02dC-MP-VSILK-01:STATE" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV(names, ILK_ON)

print "Resetting Global Vessel interlock"

# reset the Global Vessel Interlock
names = ["SR-MP-VSRST-01:RESET"]
caput(names, [[1]], timeout = timeout)

#names = ["SR-MP-VSILK-01:STATE"]
#WaitPV(names, ILK_ON)
