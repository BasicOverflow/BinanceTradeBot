import sys,os
# Gives file access to parent directory and direct imports from there
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from trading_algorithms.tech_indicators import percent_k,percent_d,bollinger_bands,isBandTouching,smoothed_rsi,stochrsi



def algo(close_prices=[],open_prices=[],close_times=[]):
    '''Algorithm used to trade by the minute, returns boolean for wether condition is set up or not'''
    try:
        curr_open = open_prices[-1]
        curr_close = close_prices[-1]
        curr_stoch_rsi = stochrsi(close_prices)[-1]
        # curr_smoothed_rsi = smoothed_rsi(close_prices)
        # curr_smoothed_rsi = round(curr_smoothed_rsi,3)
        _,_,bottomBand,middleBand = bollinger_bands(close_times,close_prices)
        curr_bottomBand = bottomBand[-1]
        # print("Curr bottom band: ",curr_bottomBand)
        # print("Curr stoch rsi: ",curr_stoch_rsi)
    except IndexError:
        return False

    except Exception as e:
        print("algo didnt work: ",e)
        return False

    if isBandTouching(curr_open,curr_close,curr_bottomBand) and curr_stoch_rsi <= 14: #IF the current candle is touching the bottom band and the stochastic rsi is <= 15 and smooth rsi is 0:
        '''Optimum time to enter is found'''
        return True 
    elif isBandTouching(curr_open,curr_close,curr_bottomBand) == False or curr_stoch_rsi > 14:
        '''Optimum time to enter is not found'''
        return False



if __name__ == "__main__":
    pass

