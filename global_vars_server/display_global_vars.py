import sys,os
#Add compile_bot.py to file's sys.path, to be importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print(lib_path)
from global_vars_server.globals_client import client
import time




def display_arrays():
    '''Displays contents of global vars in real time'''
    previous_downtrend = client({"which_array":"downtrend","action":"read","item":""},host="localhost",port=3000)    
    previous_in_use = client({"which_array":"in_use","action":"read","item":""})
    #Init loop
    while True:
        time.sleep(1)
        current_downtrend = client({"which_array":"downtrend","action":"read","item":""},host="localhost",port=3000)    
        current_in_use = client({"which_array":"in_use","action":"read","item":""})

        if current_downtrend != previous_downtrend:
            os.system("cls")
            print(f"Symbols on a downtrend: {[i.symbol for i in current_downtrend]}")
            previous_downtrend = current_downtrend
        else: pass
        if current_in_use != previous_in_use:
            os.system("cls")
            print(f"Symbols in use: {current_in_use}")
            previous_in_use = current_in_use
        else: pass





if __name__ == "__main__":
    display_arrays()