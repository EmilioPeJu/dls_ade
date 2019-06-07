:: ****************************************************************************
:: 
:: Script to build EPICS base as a Diamond production module
::
:: This is a partial script which builds EPICS base for the dls-release system.
:: The script is prepended with a list of variables before invocation by the
:: dls-release mechanism. These variables are:
::
::   _profile   : Optional override of the profile batch script
::   _email     : The email address of the user who initiated the build
::   _epics     : The DLS_EPICS_RELEASE to use
::   _build_dir : The parent directory in the file system in which to build the
::                module. This does not include module or version directories.
::   _git_dir   : The directory in git where the module is located.
::   _module    : The module name
::   _version   : The module version
::   _area      : The build area
::   _force     : Force the build (i.e. rebuild even if already exists)
::   _build_name: The base name to use for log files etc.
::

setlocal enabledelayedexpansion enableextensions

:: Set up environment
set DLS_EPICS_RELEASE=%_epics%
if defined _profile (
    call %_profile%
) else (
    call W:\etc\profile.bat
)
echo on
if errorlevel 1 (
    call :ReportFailure %ERRORLEVEL% Could not find profile. Aborting build.
    exit /b %ERRORLEVEL%
)

if "%_module%"=="base" (
    set "build_dir=%_build_dir:/=\%\%_epics:_64=%"
) else if "%_module%"=="extensions" (
    set "build_dir=%_build_dir:/=\%\%_epics:_64=%"
) else (
    set "build_dir=%_build_dir:/=\%\%_epics:_64=%\extensions\src"
)

:: Checkout module
mkdir "%build_dir%"
if errorlevel 1 (
    call :ReportFailure %ERRORLEVEL% Can not mkdir %build_dir%
)

cd /d "%build_dir%"
if errorlevel 1 (
    call :ReportFailure %ERRORLEVEL% Can not cd to %build_dir%
    exit /b %ERRORLEVEL%
)

if "%_force%"=="true" (
    rmdir /s/q %_version%
)

if not exist %_module% (
    git clone --depth=100 %_git_dir% %_module%
    if errorlevel 1 (
        call :ReportFailure %ERRORLEVEL% Can not check out %_git_dir%
        exit /b %ERRORLEVEL%
    )
)

cd %_module%
git fetch --depth=1 origin tag %_version% && git checkout %_version%
if errorlevel 1 (
    call :ReportFailure %ERRORLEVEL% Can not switch to %_git_dir%
    exit /b %ERRORLEVEL%
)

:: Build
set error_log=%_build_name%.err
set build_log=%_build_name%.log

%_make% clean
:: make
%_make% 1>%build_log% 2>%error_log%
set make_status=%ERRORLEVEL%
echo %make_status% > %_build_name%.sta
if NOT "%make_status%"=="0" (
    call :ReportFailure %make_status% Build Errors for %_module% %_version%
    exit /b %ERRORLEVEL%
)

goto :EOF

:ReportFailure
    if exist "%build_dir%\%_version%" echo %1 > "%build_dir%\%_version%\%_build_name%.sta"
    echo #### ERROR [%DATE% %TIME%] ### Error code: %*

:: This exit code doesn't seem to work, caught by Ulrik 20-07-2015
::    exit /B %1
::    goto :EOF
