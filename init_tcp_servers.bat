@echo off

REM start "Dynamic Global Vars Environment" python startup/global_vars.py 
REM start "Scanner" python startup/scan_market.py
REM start "Exchange Handler Server" python startup/init_exchange_handler.py 
REM start "Client Manager" python startup/manage_client_threads.py 
REM start "Monitor Global Arrays" python startup/display_globals.py


start "API Server" python api_server/exchange_server.py
start "Globals Server" python global_vars_server/globals_server.py
start "Scanner" python scanner/scanner.py

