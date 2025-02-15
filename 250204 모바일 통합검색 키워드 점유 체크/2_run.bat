@echo off
cls

path %path%;c:\python34;c:\python34\scripts;c:\python38;c:\python38\scripts;
python main.py %~n0
pause
exit