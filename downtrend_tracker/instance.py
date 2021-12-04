from datetime import datetime
import time


class Downtrend(object):
    '''For stocks that are considered in a downtrend and should not be traded with (at least with the hypertrade algorithm).'''
   
    def __init__(self,symbol):
        '''Has attribute that tracks amount of time spent '''
        self.symbol = symbol
        self.timestamp_from_start = datetime.now()
    

    def find_time_spent_in_downtrend(self,current_timestamp,return_in_minutes=True): #If return in minutes is False, will return in seconds 
        '''Compares self.timestamp to a current timestamp to find how much time has elapsed in *timeframe*.'''
        #Get rid of miliseconds:
        starting_time = self.timestamp_from_start.strftime("%Y-%m-%d %H:%M:%S")
        current_time = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        fmt = '%Y-%m-%d %H:%M:%S'
        starting_time = datetime.strptime(str(starting_time), fmt)    
        current_time = datetime.strptime(str(current_time), fmt)
        
        #Convert to unix timestamps:
        starting_time = time.mktime(starting_time.timetuple())
        current_time = time.mktime(current_time.timetuple())

        if return_in_minutes:
            return float(current_time-starting_time) / 60
        else:
            return int(current_time-starting_time)








if __name__=="__main__":
    tester = Downtrend("EggSackStock")
    time.sleep(5)
    time_gap = datetime.now()
    mins = str(tester.find_time_spent_in_downtrend(time_gap))
    secs = str(tester.find_time_spent_in_downtrend(time_gap,return_in_minutes=False))

    print("Time difference in minutes: "+mins)
    print("Time difference in seconds: "+secs)
    print(id(tester))    