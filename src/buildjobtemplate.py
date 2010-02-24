#!/bin/env python2.4

# Template batch script to checkout and build a released
# module in W:\prod\...
#
# This template will be used by the linux dls-release.py 
# scripts to create a build job that can be executed by
# the build server as a scheduled job when dumped in the 
# build servers work queue.
#
# Usage: Substitute the various macros, defined as: $(MACRO)
# The macros will identify module name, version, area and 
# EPICS environment -all things needed to identify a particular
# released module, it's version and build environment.
#
# Ulrik Pedersen 14-07-2009

winbuildscript = r"""
@rem ---------------------------------------------------------
@rem Release build script
@rem module: $(MODULE) version: $(VERSION)
@rem EPICS version: $(DLS_EPICS_RELEASE)
@rem area: '$(AREA)'
@rem -----------------------------------------------------------

set DLS_EPICS_RELEASE=$(DLS_EPICS_RELEASE)
set _area=$(AREA)
set _module=$(MODULE)
set _version=$(VERSION)

set _profile=W:\etc\profile.bat
set _svn_root=http://serv0002.cs.diamond.ac.uk/repos/controls/diamond/release/%_area%
set _dlsprod=W:\prod\%DLS_EPICS_RELEASE%\%_area%\%_module%\%_version%

@rem Configure the environment by loading a profile.
@rem The profile is responsible to set up the build environment:
@rem  - Path to compiler, linker and all necessary environment setup
@rem  - Path to subversion svn commands
@rem  - path to minGW make tool
@rem  - EPICS_BASE and other related EPICS environment variables.
if exist %_profile% (
	call %_profile%
) else (
	echo ### ERROR [%TIME%] ### Could not find profile. Aborting build.
	exit /B 1
)

if not exist %_dlsprod% (
	echo Creating directory %_dlsprod%
	mkdir %_dlsprod%
	if not %ErrorLevel%==0 (
		echo ### ERROR [%TIME%] ### Unable to create directory: %_dlsprod%
		echo                        Aborting build.
		exit /B %ErrorLevel%
	)
	cd %_dlsprod%
	svn checkout  %_svn_root%/%_module%/%_version% .
    if not %ErrorLevel%==0 (
    	echo ### ERROR [%TIME%] ### Unable to access subversion repository. Aborting build.
    	exit /B %ErrorLevel%
    )
) else (
	echo Module has already been released for this version.
	cd %_dlsprod%
)

echo Performing Windows build using mingw32-make.
mingw32-make clean
mingw32-make

"""

