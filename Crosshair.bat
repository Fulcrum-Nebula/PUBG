@echo off
setlocal

REM 切换到当前 bat 所在目录，确保相对路径可用
cd /d "%~dp0"

REM 优先用 py 启动器，其次用 python
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "Crosshair.py"
) else (
    python "Crosshair.py"
)

pause
