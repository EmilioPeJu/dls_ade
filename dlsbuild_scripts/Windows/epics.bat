:: ******************************************************************************
:: 
:: Script to build a Diamond production module.in the support or ioc areas
::
:: This is a partial script which builds a module in for the dls-release system.
:: The script is prepended with a list of variables before invocation by the
:: dls-release mechanism. These variables are:
::
::   _email     : The email address of the user who initiated the build
::   _epics     : The DLS_EPICS_RELEASE to use
::   _build_dir : The parent directory in the file system in which to build the
::                module. This does not include module or version directories.
::   _svn_dir   : The directory in subversion where the module is located.
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
)
set SVN_ROOT=http://serv0002.cs.diamond.ac.uk/repos/controls

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
)

if "%_force%"=="true" (
    rmdir /s/q %_version%
)

if not exist %_module% (
    svn checkout %_svn_dir% %_module%
    if errorlevel 1 (
        call :ReportFailure %ERRORLEVEL% Can not check out %_svn_dir%
    )
    cd %_module%
) else (
    cd %_module%
    svn switch %_svn_dir%
    if errorlevel 1 (
        call :ReportFailure %ERRORLEVEL% Can not switch to %_svn_dir%
    )
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
)

goto :EOF

:ReportFailure
    if exist "%build_dir%\%_version%" echo %1 > "%build_dir%\%_version%\%_build_name%.sta"
    echo #### ERROR [%DATE% %TIME%] ### Error code: %*
    exit /B %1
    goto :EOF
