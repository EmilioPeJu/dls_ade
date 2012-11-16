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
timeout = 0.1

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
		
	for c in range(1,100):

		time.sleep(0.1)
			
		status = caget(names, timeout=timeout)
					
		if any(s.ok != True for s in status):
			continue

		if all(s == value for s in status):
			return 0
				
	if not all(s == value for s in status):
		print "WaitPV() timeout"

def WaitPV2(names, value1, value2):
	"""Wait for a PV state"""
		
	for c in range(1,100):

		time.sleep(0.1)
			
		status = caget(names, timeout = timeout)
						
		if any(s.ok != True for s in status):
			continue

		if all((s == value1) or (s == value2) for s in status):
			return 0
				
	if not all((s == value1) or (s == value2) for s in status):
		print "WaitPV() timeout"

################################################################################

# remove all VS and DP interlocks and optionally wait
# terminates if any interlocks remain after 40 * 0.25 seconds
# Change this to DropAllVS and DropAllDP

def DropAll():
	"""Remove all Vessel and Dipole Interlocks using the PLC"""
	
	names = []
	names = names + ['SR%(cell)02dC-MP-PLC-01:DROP30' % {'cell' : cell} for cell in range(1,MAXCELL)]
	names = names + ['SR%(cell)02dC-MP-PLC-01:DROP20' % {'cell' : cell} for cell in range(1,MAXCELL)]
	
	caput(names, [[0] for n in range(1,MAXCELL)] + [[0] for n in range(1,MAXCELL)], timeout = timeout)
		
	names = []
	names = names + ['SR%(cell)02dC-MP-VSILK-01:STATE' % {'cell' : cell,} for cell in range(1,MAXCELL)]
	names = names + ['SR%(cell)02dC-MP-DPILK-01:STATE' % {'cell' : cell,} for cell in range(1,MAXCELL)]

	WaitPV(names, ILK_OFF)

# start of main program ########################################################

zeros = [[0] for n in range(1,MAXCELL)]

print "MPS Storage Ring Reset"
print "======================"
print ""

#print "Removing all interlocks"

#DropAll()

print "Resetting all PLC Vessel Flow/Temp Interlocks"

# vessel flow
names = ["SR%(cell)02dC-MP-PLC-01:ILKRST10" % {'cell' : cell} for cell in range(1,MAXCELL)]
caput(names, zeros, timeout = timeout)

# vessel temp
names = ["SR%(cell)02dC-MP-PLC-01:ILKRST20" % {'cell' : cell} for cell in range(1,MAXCELL)]
caput(names, zeros, timeout = timeout)

# wait for vessel flows

print "Waiting for Vessel Flow interlocks"

names = ["SR%(cell)02dC-MP-VSILK-02:ILK00" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV(names, ILK_ON)

# wait for vessel temps

print "Waiting for Vessel Temp interlocks"

names = ["SR%(cell)02dC-MP-VSILK-02:ILK01" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV(names, ILK_ON)

# wait for dipole flows

print "Waiting for Dipole Flow interlocks"

names = ["SR%(cell)02dC-MP-DPILK-01:ILK00" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV(names, ILK_ON)

names = ["SR%(cell)02dC-MP-DPILK-01:ILK02" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV(names, ILK_ON)

print "Waiting for Dipole card interlocks"

names = ["SR%(cell)02dC-MP-DPILK-01:READY" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV2(names, ILK_READY, ILK_GOOD)

print "Resetting Dipole interlocks"
names = ["SR%(cell)02dC-MP-DPRST-01:RESET" % {'cell' : cell} for cell in range(1,MAXCELL)]
caput(names, zeros, timeout = timeout)

names = ["SR%(cell)02dC-MP-DPILK-01:STATE" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV(names, ILK_ON)

print "Resetting Global Dipole interlock"
names = ["SR-MP-DPRST-01:RESET"]
caput(names, [[1]], timeout = timeout)
names = ["SR-MP-DPILK-01:STATE"]
WaitPV(names, ILK_ON)

print "Waiting for Vessel card interlocks"

#names = ["SR%(cell)02dC-MP-VSILK-02:READY" % {'cell' : cell} for cell in range(1,MAXCELL)]
#WaitPV2(names, ILK_READY, ILK_GOOD)

#names = ["SR%(cell)02dC-MP-VSRST-01:RESET" % {'cell' : cell} for cell in range(1,MAXCELL)]
#caput(names, zeros, timeout = timeout)

names = ["SR%(cell)02dC-MP-VSILK-01:READY" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV2(names, ILK_READY, ILK_GOOD)

print "Resetting Vessel interlocks"
names = ["SR%(cell)02dC-MP-VSRST-01:RESET" % {'cell' : cell} for cell in range(1,MAXCELL)]
caput(names, zeros, timeout = timeout)

names = ["SR%(cell)02dC-MP-VSILK-01:STATE" % {'cell' : cell} for cell in range(1,MAXCELL)]
WaitPV(names, ILK_ON)

print "Resetting Global Vessel interlock"
names = ["SR-MP-VSRST-01:RESET"]
caput(names, [[1]], timeout = timeout)
names = ["SR-MP-VSILK-01:STATE"]
WaitPV(names, ILK_ON)

print ""
print "End of script. This window will close in 5 seconds"

time.sleep(5)
