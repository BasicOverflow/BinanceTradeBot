from datetime import datetime 
import threading,time 



class DownTrendArray(list):
    '''Upon inititalization, will constantly check (on seperate thread) the time an 
    object has spent in the array. Use add() method to add new objects to the class. 
    Updates itself'''
    
    def __init__(self):
        self.coins_array = []
        self.allotted_time = 120 #In minutes
        threading.Thread(target=self.check_time_gap).start()

    
    def add(self,coin):
        '''Expects DownTrend objects to be inserted'''
        self.coins_array.append(coin)

    
    def check_time_gap(self):
        while True:
            now = datetime.now()
            for coin in self.coins_array:
                time_gap = coin.find_time_spent_in_downtrend(now,return_in_minutes=True)
                if time_gap >= self.allotted_time:
                    self.coins_array.remove(coin)
                else: pass
            time.sleep(10) #Updatees array every 45 seconds



def test():
    #For testing:
    from downtrend_class import Downtrend
    tester = DownTrendArray()
    test_object = Downtrend("BeefSack")
    tester.add(test_object)
    time.sleep(20)
    test_object2 = Downtrend("Guacamole")
    tester.add(test_object2)
    
    while True:
        print(tester.coins_array)
        time.sleep(1)




if __name__=="__main__":
    from downtrend_class import Downtrend
    tester = DownTrendArray()
    test_object = Downtrend("BeefSack")
    tester.add(test_object)
    for i in tester.coins_array:
        print(i.symbol)
    
