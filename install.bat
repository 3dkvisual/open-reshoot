@echo off
rem Open Reshoot installer. Put this repo folder next to (or inside) your ComfyUI folder and double-click,
rem or run:  install.bat "C:\path\to\ComfyUI"
cd /d "%~dp0"
set PY=
for %%P in ("..\python_embeded\python.exe" "..\..\python_embeded\python.exe" "..\ComfyUI_windows_portable\python_embeded\python.exe") do if exist %%P if not defined PY set PY=%%~P
if not defined PY set PY=python
"%PY%" -s install.py %*
pause
