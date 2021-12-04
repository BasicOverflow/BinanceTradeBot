import sys,os
#Add Indicators.py to file's sys.path, to be importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from trading_algorithms.tech_indicators import ema,current_crossover
from pandas import Series



def algo(close_prices):
    '''when EMAs 1 (Signal line) and 2 (Baseline) cross - a Long signal is called if the cross is above EMA 3 ( Trendline ), a short if the cross is below EMA3 '''
    ema1 = ema(close_prices,6)
    ema2 = ema(close_prices,9)
    ema3 = ema(close_prices,14)
    crossover = current_crossover(ema1,ema2)
    #conditionals
    if crossover and ema1[-1] > ema3[-1]:
        '''Return the trigger'''
        return True
    else:
        return False





