@echo off
setlocal
cd /d "%~dp0"
color 0A
python play.py --color green --bg black --new-window --pad-x 0 --pad-y 0 --fit 0.95 --font-size 8 --font-name Consolas
endlocal