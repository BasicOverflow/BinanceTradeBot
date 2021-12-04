import numpy as np
import pandas as pd
import math
import time,decimal
from pyti.function_helper import fill_for_noncomputable_vals
from statistics import mean
from array import array
from pyti import catch_errors
from pyti.function_helper import fill_for_noncomputable_vals
from pyti.simple_moving_average import (
    simple_moving_average as sma
    )
from six.moves import range
import warnings
warnings.filterwarnings("ignore")



def standard_deviation(tf,close_prices,date): # tf,prices
    sd=[]
    sddate=[]
    x=tf
    while x <= len(close_prices): 
        array2consider = close_prices[x-tf:x]
        standev = np.std(array2consider)
        sd.append(standev)
        sddate.append(date[x])
        x+=1
    return sddate,sd


def movingAverage(values,window=25):
    weigths = np.repeat(1.0, window)/window
    smas = np.convolve(values, weigths, 'valid')
    return smas # as a numpy array


def ema(values,window): #values = close prices
    weights = np.exp(np.linspace(-1.,0.,window))
    weights /= weights.sum()
    a = np.convolve(values,weights,mode="full")[:len(values)]
    a[:window] = a[window]
    return a


def MACD(prices,slow=26,fast=12):
    '''
    macd line (blue line) = 12ema - 26ema 
    signal line (red line) = 9ema of the macd line 
    bars (histogram) = macd line - signal line 
    '''
    emaslow = ema(prices,slow)
    emafast = ema(prices,fast)

    macd_line = emafast - emaslow 
    signal_line = ema(macd_line,9)
    historgram = macd_line - signal_line

    return macd_line,signal_line,historgram


def rsiFunc(prices, n=14): # prices
    prices = [float(i) for i in prices]
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi
    

def bollinger_bands(date,closep,tff=21,mult=2): 
    #date = [''.join(i) for i in date]
    bDate = []
    topBand = []
    botBand = []
    midBand = []

    x = tff
    while x < len(date):
        curSMA = movingAverage(closep[x-tff:x],tff)[-1]
        d,curSD = standard_deviation(tff,closep[x-tff:x],date) #closep[x-tff:x]
        curSD = curSD[-1]

        TB = curSMA + (curSD*mult)
        BB = curSMA - (curSD*mult)
        D = date[x]

        topBand.append(TB)
        bDate.append(D)
        botBand.append(BB)
        midBand.append(curSMA)
        x+=1
    return bDate,topBand,botBand,midBand


def stochrsi(close_prices, period=14):
    '''%K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
        %D = 3-day SMA of %K

        Lowest Low = lowest low for the look-back period
        Highest High = highest high for the look-back period'''
    
    rsi = rsiFunc(close_prices, period)
    stochrsi = [100 * ((rsi[idx] - np.min(rsi[idx+1-period:idx+1])) / (np.max(rsi[idx+1-period:idx+1]) - np.min(rsi[idx+1-period:idx+1]))) for idx in range(period-1, len(rsi))]
    # stochrsi = fill_for_noncomputable_vals(close_prices, stochrsi)
    return stochrsi


def percent_k(data, period=14):
    """
    %K.
    Formula:
    %k = data(t) - low(n) / (high(n) - low(n))
    """
    catch_errors.check_for_period_error(data, period)
    percent_k = [((data[idx] - np.min(data[idx+1-period:idx+1])) /
         (np.max(data[idx+1-period:idx+1]) -
          np.min(data[idx+1-period:idx+1]))) for idx in range(period-1, len(data))]
    percent_k = fill_for_noncomputable_vals(data, percent_k)

    return percent_k


def percent_d(data, period=3):
    """
    %D.
    Formula:
    %D = SMA(%K, 3)
    """
    p_k = percent_k(data, period)
    percent_d = sma(p_k, 3)
    return percent_d


def trendline(data):  
    '''returns value based on wether a trend in the data is going up or down'''
    trend = [b - a for a, b in zip(data[::1], data[1::1])]
    return np.mean(trend)


def isBandTouching(open_price,close_price,band):
    if open_price > close_price: #If the open is on top of the close 
        if float(band) >= float(close_price): #If the close price is touching or under the boll band
            return True
        else: return False
    elif close_price > open_price: #IF the close price is above the open price 
        if float(band) >= float(open_price):
            return True
        else: return False 


def profit(buy,sell):
    increase = sell-buy
    return (increase/buy*100)


def smoothed_rsi(prices,length=10):
    pass


def current_crossover(list1,list2):
    '''The `list1`-series is defined as having crossed over `list2`-series if the value of `list1` 
    is greater than the value of `list2` and the value of `list1` was less than the value of `list2` on the bar immediately preceding the current bar.'''
    return True if list1[-1] > list2[-1] and list1[-2] < list2[-2] else False


def softmax():
    ''''''
    pass






if __name__ == "__main__":
    data = [0.004698, 0.004698, 0.004698, 0.004698, 0.004703, 0.00469, 0.00469, 0.00469, 0.00469, 0.004721, 0.00469, 0.00469, 0.00469, 0.004703, 0.004703, 0.004687, 0.004687, 0.004687, 0.004687, 0.004687, 0.004683, 0.004683, 0.004683, 0.004683, 0.004683, 0.00469, 0.00469, 0.004693, 0.004697, 0.0047, 0.0047, 0.004734, 0.004734, 0.004734, 0.004734, 0.004697, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.00471, 0.00471, 0.00471, 0.00471, 0.004726, 0.0047, 0.0047, 0.0047, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004701, 0.004702, 0.004702, 0.004702, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.0047, 0.004726, 0.004726, 0.004726, 0.004726, 0.004726, 0.004726, 0.004726, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004731, 0.004715, 0.004715, 0.004715, 0.004726, 0.004726, 0.004726, 0.004726, 0.004726, 0.004726, 0.00473, 0.004723, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004696, 0.004687, 0.004707, 0.004707, 0.004697, 0.004695, 0.004697, 0.004697, 0.004697, 0.004697, 0.004697, 0.004709, 0.004709, 0.004709, 0.004709, 0.004709, 0.004725, 0.004725, 0.004725, 0.004725, 0.004725, 0.004725, 0.004725, 0.004723, 0.004723, 0.004723, 0.004723, 0.004723, 0.004723, 0.004723, 0.004723, 0.0047, 0.0047, 0.004725, 0.004725, 0.004725, 0.004725, 0.004725, 0.00471, 0.00471, 0.004712, 0.004712, 0.004711, 0.004694, 0.004694, 0.004694, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004695, 0.004709, 0.004725, 0.004725, 0.004725, 0.004725, 0.004725, 0.004725, 0.004726, 0.004711, 0.004711, 0.004711, 0.004711, 0.004711, 0.004711, 0.004711, 0.004711, 0.004737, 0.004733, 0.004738, 0.004738, 0.004738, 0.004738, 0.004715, 0.004693, 0.004693, 0.004688, 0.00468, 0.00468, 0.00468, 0.004716, 0.004716, 0.004716, 0.004719, 0.004719, 0.004719, 0.004719, 0.004702, 0.004702, 0.004703, 0.004703, 0.004703, 0.004703, 0.004703, 0.004703, 0.004703, 0.004703, 0.004719, 0.004719, 0.004719, 0.004719, 0.004719, 0.004719, 0.004719, 0.004719, 0.004719, 0.004719, 0.004719, 0.004687, 0.004687, 0.004687, 0.004687, 0.004687, 0.004687,
0.004687, 0.004687, 0.004687, 0.004687, 0.004687, 0.004687, 0.004687, 0.004687, 0.004687, 0.004687, 0.004687, 0.0047, 0.0047, 0.0047, 0.0047, 0.004659, 0.004632, 0.004632, 0.00462, 0.004645, 0.00462, 0.004645, 0.004645, 0.004645, 0.004628, 0.004643, 0.004643, 0.004643, 0.004628, 0.004643, 0.00462, 0.00462, 0.004613, 0.004613, 0.004613, 0.004613, 0.004606, 0.004605, 0.004605, 0.004626, 0.004626, 0.004626, 0.004615, 0.004615, 0.004615, 0.004615, 0.004624, 0.004624, 0.004631, 0.004631, 0.004631, 0.004631, 0.00464, 0.004612, 0.004612, 0.004647, 0.004622, 0.004622, 0.00465, 0.00465, 0.00465, 0.004634, 0.004662, 0.004635, 0.004635, 0.004635, 0.004635, 0.004635, 0.00463, 0.004626, 0.004635, 0.004635, 0.004635, 0.004637, 0.004637, 0.004637, 0.004637, 0.004618, 0.004604, 0.004589, 0.00462, 0.00462, 0.004626, 0.004626, 0.004632, 0.004634, 0.004631, 0.004609, 0.004612, 0.004612, 0.004612, 0.004612, 0.00464, 0.00464, 0.00464, 0.00464, 0.004646, 0.004646, 0.004648, 0.004648, 0.004648, 0.004621, 0.004616, 0.004597, 0.004597, 0.00461, 0.00461, 0.00461, 0.004626, 0.004626, 0.004612, 0.004612, 0.004612, 0.004616, 0.004617, 0.004617, 0.00462, 0.00462, 0.004649, 0.004636, 0.004636, 0.004636, 0.004636, 0.004636, 0.004636, 0.00462, 0.00461, 0.00461, 0.00461, 0.00461, 0.00461, 0.004626, 0.004622, 0.00461, 0.00461, 0.004604, 0.004638, 0.00464, 0.00464, 0.00464, 0.00464, 0.004617, 0.004617, 0.004625, 0.004625, 0.004625, 0.004619, 0.004622, 0.004622, 0.004607, 0.004615, 0.004627, 0.004627, 0.004627, 0.004638, 0.004638, 0.004617, 0.004617, 0.004617, 0.004617, 0.004638, 0.004612, 0.004612, 0.004612, 0.004612, 0.004612, 0.004624, 0.004624, 0.004624, 0.004626, 0.004626, 0.004612, 0.004612, 0.004612, 0.004612, 0.004612, 0.004605, 0.004605, 0.004598, 0.004622, 0.004596, 0.004596, 0.004624, 0.004624, 0.004624, 0.004624, 0.004593, 0.004573, 0.004573, 0.004572, 0.004569, 0.004576, 0.004581, 0.004579, 0.004579, 0.004571, 0.00457, 0.004558, 0.004548, 0.00456, 0.004553, 0.004546, 0.004557, 0.004556, 0.00456, 0.00456, 0.004526, 0.00455, 0.004549, 0.004549, 0.004551, 0.004531, 0.004547, 0.004574, 0.00458, 0.00458, 0.004572, 0.004589, 0.004589, 0.004564, 0.004558, 0.004558, 0.004585, 0.004585, 0.004585, 0.004585, 0.004555, 0.004578, 0.004578, 0.004585, 0.004585, 0.004567, 0.004567, 0.00457, 0.00457, 0.004587, 0.00456, 0.00456, 0.004559, 0.004559, 0.004559, 0.004556, 0.004556, 0.004556, 0.004556, 0.004556, 0.004567, 0.004567, 0.004567, 0.004567, 0.004567, 0.004567, 0.004567, 0.004567, 0.004567, 0.004567, 0.004564, 0.004559, 0.004559, 0.004559, 0.004559, 0.004528, 0.004539, 0.004514, 0.004493, 0.00449, 0.004508, 0.004508, 0.004526, 0.004527, 0.004527, 0.004534, 0.004534, 0.004495, 0.004465, 0.004485, 0.004493, 0.0045, 0.004504, 0.004514, 0.004544, 0.004522, 0.004522, 0.004522, 0.00452, 0.00452, 0.004499, 0.004499, 0.004499, 0.004499, 0.004499, 0.004545, 0.004545, 0.004545, 0.004545, 0.004545, 0.004514, 0.004514, 0.004514, 0.004514, 0.004514, 0.0045, 0.0045, 0.00449, 0.004513, 0.004513, 0.004479, 0.004511, 0.004514,
0.004514, 0.004514, 0.004485, 0.004485, 0.004509, 0.004509, 0.004509, 0.004508, 0.004508, 0.004508, 0.004488, 0.004495, 0.00448, 0.004468, 0.004467, 0.004497, 0.004497, 0.004471, 0.004478, 0.004516, 0.004516, 0.004516, 0.004484, 0.004484, 0.004484, 0.004484, 0.004484, 0.004484, 0.004484, 0.004484, 0.004484, 0.004507, 0.004488, 0.004505, 0.004505, 0.004505, 0.004486, 
0.004486, 0.004486, 0.004484, 0.004483, 0.004483, 0.004483, 0.004494, 0.004481, 0.004481, 0.004481, 0.0045, 0.0045, 0.0045, 0.004476, 0.004476]
    

