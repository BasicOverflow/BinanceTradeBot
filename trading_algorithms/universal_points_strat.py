import sys,os
#Add Indicators.py to file's sys.path, to be importable from anywhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
import numpy as np
from trading_algorithms.tech_indicators import *



def point_based_algo(symbol="",close_prices=[],open_prices=[],volume=[],close_times=[]):
    '''Meant for longer-timed trades (hours). Returns a value out of 10 points, the higher the value, the more the conditions to buy were met''' 
    value = 0 

    rsi= rsiFunc(close_prices).tolist()
    curr_rsi = rsi[-1]
    recent_rsi = rsi[-36:]
    bollDate,topBand,bottomBand,middleBand = bollinger_bands(close_times,close_prices)
    try:
        curr_bottomBand = bottomBand[-1]
        recent_bottomBand = bottomBand[-13:]
    except:
        print("Arrays for indicators are 0, most likely a new listing that was just added to the exchange. Not wise to trade {} at this time".format(symbol))
    MA10 =  movingAverage(close_prices,window=10)
    curr_MA10 = MA10[-1]
    macd_line,red_line,histogram = MACD(close_prices)
    curr_MACD_line = macd_line[-1]
    curr_red_line = red_line[-1]
    curr_histogramm = histogram[-1]
    curr_vol = volume[-1]
    recent_vol = volume[-90:]
    curr_close = close_prices[-1]
    recent_close = close_prices[-13:]
    curr_open = open_prices[-1]
    recent_open = open_prices[-13:]

    #Is volume drying up or showing bullish signs? (DOES NOT TAKE INTO CONSIDERATION SELLSIDE VOLUME):

    if curr_vol > np.mean(recent_vol): #If the current volume is above the average for the past 90 hours 
        value += 0.4
    elif ExpMovingAverage(volume,20)[-1] < curr_vol: #If the  20 day Exp moving average is less than the current volume 
        value += 0.5
    elif ExpMovingAverage(volume,20)[-1] > curr_vol or curr_vol < np.mean(recent_vol): #If the 20 Exp moving avg is greater than the current vol or the current vol is less than the average of the past 90 hours
        value =- 1.5
    elif trendline(recent_vol) > 0: #If a positive trend is seen in recent volumes 
        value += 0.8
    elif trendline(recent_vol) < 0: #If a negative trend is seen in recent volumes
        value -=  1.6

    #Does the RSI show potential buy profit?:

    if curr_rsi <= 30: # If the current rsi is below or equal to
        value += 0.8
    elif curr_rsi <= 21:  #If the coin is really oversold 
        value += 1.5
    elif trendline(recent_rsi) < 0: #If recent rsi shows a downtrend
        value += 0.5

    #Did past rsi's that dipped below 30 expirience any increase in price shortly after?
    for index,rsi in reversed(list(enumerate(rsi[:-len(recent_rsi)]))): #For rsi in all the rsi except recent/current rsi starting from the most recents:
        if rsi < 26: #If a past rsi went below 26
        #Check if the price relative to that moment had an increase 
            relative_closep =  close_prices[index]
            trend_index = close_prices[index:index+13] #Small sector of prices from the relative rsi price to 13 candles later, short bull-bursts usually happen at around this length from what i've seen
            if trendline(trend_index) > 0: #If the trend in that time interval showed an overall increase, check how much percentage a profit would have made:
                last_trend_index_price = trend_index[-1] #Last close price of the 13-candle trend
                percent_profit = round(100 - ((relative_closep*100)/last_trend_index_price))
            if percent_profit <= 10 and percent_profit > 0: #Decent profit made
                value += 0.5
            elif percent_profit >= 20: #Interesting!
                value += 0.7
            elif percent_profit >= 60: #Thats insane 
                value += 0.9
            elif percent_profit <= 20 and percent_profit >= 10:
                value += 0.7
            else: #If its a downward trend
                value -= 1.8
                break 
        else: pass

    #Does 10-day moving average show potenial BUY profit?
    if curr_close < curr_MA10:
        value += 0.5
    else: value -= 0.6

    #Does MACD show buy confidence?
    if curr_MACD_line < 0 and curr_red_line < 0: #Are both moving averages under 0?
        value += 0.5
    if abs(curr_histogramm) <= 0.001: #If the macd line is below the red line and they are almost touching 
        value += 0.4

    #Do bollinger bands show profit potential?
    if isBandTouching(curr_open,curr_close,curr_bottomBand): #If the most recent price is touching the most recent bottom band 
        value += 1.7
    else: value = 0 #If the current candle is not touching band, all potential value is reset 
    #Has there already been a downtrend going on?
    if trendline(recent_bottomBand) < 0: 
        value += 0.6
    #Has the downtrend touched or gone under the bottom band?
    for open_,close,band in zip(recent_open,recent_close,recent_bottomBand) :
        if isBandTouching(open_,close,band): #For every candle that haas touched or gone below the bottom band, value is added, 
            value += 0.1
        else: 
            value =- 0.1 #If candle isnt touching it, value is depleted 

    #Has previous support at current level held up?
    for index,close in reversed(list(enumerate(close_prices[13:]))): #For every close price, starting from 13 after the most recent 
        if close == curr_close: #If a price matches the current close price 
            trend_index = close_prices[index:index+13]
            if trendline(trend_index) > 0: #if the previous support level saw a positive trend right after
                value += 0.7
            elif trendline(trend_index) < 0: #If the previous support level saw a neagative trend right after 
                value =- 0.7

    return value




if __name__ == "__main__":
    pass
    
      
