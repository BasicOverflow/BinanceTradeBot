import sys,os
# Gives file access to parent directory and direct imports from there
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from child import Child #Child()
from scanner import scanner_client #scanner_client.client()
from global_vars_server import globals_client #globals_client.client()
from custom_errors.errors import ChildManagerError,ScannerClientError
from api_bridge.binance_exchange import ExchangeBridge
from global_vars_server import globals_client
from settings import PREFERED_TRADING_ASSET,POSSIBLE_LONG_TRIGGERS,POSSIBLE_SELL_TRIGGERS
import numpy as np 
import time
import random
import threading


def create_trigger_array(prefered_triggers,other_triggers):
    #if prefered_long_triggers isnt populated, raise an Exception:
        if prefered_triggers == []: raise ChildManagerError("Nothing was entered in self.prefered_long_triggers")
        # #Check to see if triggers entered are valid
        # for prefered_trigger in prefered_triggers:
        #     if prefered_trigger not in POSSIBLE_LONG_TRIGGERS or prefered_trigger not in POSSIBLE_SELL_TRIGGERS:
        #         raise ChildManagerError(f"This is not a valid trigger: {prefered_trigger}")
        #     else: pass
        # for other_trigger in other_triggers:
        #     if other_trigger not in POSSIBLE_LONG_TRIGGERS or prefered_trigger not in POSSIBLE_SELL_TRIGGERS:
        #         raise ChildManagerError(f"This is not a valid trigger: {other_trigger}")
        #     else: pass
        #Create triggers array: The items in prefered_long_triggers and other_long_triggers will be added into one array. The items in prefered long triggers
        #will be copied multiple times inside the array so that their chance of being chosen when buying into a stock is higher. If other_long_triggers is empty,
        #the array will only be whatever is in prefered_long_triggers. prefered_long_triggers must be populated 
        triggers = []
        for trigger in prefered_triggers:
            #Items in prefered_long_triggers will be appended twice to increase their chance of getting picked
            triggers.append(trigger)
            triggers.append(trigger)
        for trigger in other_triggers:
            #Items in other_long_triggers will only be appended once
            triggers.append(trigger)
        # print(triggers)
        return triggers



class ChildManager(object):
    '''The main logic of the bot, ties everything all together here and manages all the buying and selling as well as which cryptocurrencies the bot enters and exits.'''
    def __init__(self,threads=4,prefered_long_triggers=[],other_long_triggers=[],prefered_sell_triggers=[],other_sell_triggers=[]):
        '''Initialize all variables'''
        self.threads = threads
        self.symbols_with_scanner_clients = [] #Holds all the symbols that have been assigned scanner clients
        self.taken_symbols = [] #holds the symbols that the bot is currently trading and hasnt exited on. The length of this array is the amount of threads activated
        #Get user's balance from portfolio
        self.total_balance = ExchangeBridge(f"{PREFERED_TRADING_ASSET}").get_balance(get_base_asset=True) #The total amount will be evenly divided among the number of threads defined
        # self.activated_threads = len(self.taken_symbols) #How many threads are active, or how many open postitions there are
        #Produce modified array array of triggers 
        self.long_triggers = create_trigger_array(prefered_long_triggers,other_long_triggers)
        self.sell_triggers = create_trigger_array(prefered_sell_triggers,other_sell_triggers)


    def init_main_loop(self):
        '''Upon Initialzation, will receive, manage, and update all current symbols in the market that have been considered 
        trade ready. With each symbol, a scanner client will be created to start scanning for long entries. When 
        a buy signal is triggered from one of the scanner clients, the bot will buy into that symbol. When a sell signal is triggered
        from the scanner client, the bot will sell that symbol. The maximum number of open positions will be limited by the amount
        of threads defined in the constructor function by self.threads.'''
        while True:
            time.sleep(1)
            try:
                # print("self.symbols_with_scanner_clients: "+", ".join([i for i in self.symbols_with_scanner_clients]))
                # print("self.taken_symbols: "+", ".join([i for i in self.taken_symbols]))
                #Retrieve current live candidates (symbols) from the global vars server via TCP:
                candidates = globals_client.client({"which_array":"live_candidates","action":"read","item":""})
                #FOR TESTING:
                candidates = ["BNBETH"]
                #If nothing was received from the global vars server, then restart the loop and keep trying 
                if candidates == []:
                    print("No candidates received")
                    continue
                #Create a scanner client for each symbol in the array
                for symbol in candidates:
                    #TODO This will fail if a sybmol that has an open order is taken off candidates, fix it
                    #If the symbol is already in self.taken_symbols, then create a scanner client looking to sell:
                    if symbol in self.taken_symbols:
                        threading.Thread(target=self.create_scanner_client,args=[symbol,random.choice(self.sell_triggers),"sell"]).start()
                        # self.create_scanner_client(symbol,random.choice(self.long_triggers),"sell") 
                    else: #if the symbol isnt in self.taken_symbols and also doesnt have a scanner client created from a previous loop:
                        if symbol not in self.symbols_with_scanner_clients:
                            #Then create a scanner client looking to buy and append the symbol to self.symbols_with_scanner_clients
                            threading.Thread(target=self.create_scanner_client,args=[symbol,random.choice(self.long_triggers),"long"]).start()
                            # self.create_scanner_client(symbol,random.choice(self.long_triggers),"long") 
                            
                        else: pass
            except ScannerClientError as e:
                # print("Most likely the scanner has been shut down, restarting main loop")
                # self.init_main_loop()
                print(str(e))
                break
            except Exception as e:
                raise ChildManagerError("Error with main loop: "+str(e))


    def create_scanner_client(self,symbol,trigger,position):
        '''Creates scanner client with given symbol, trigger, and position'''
        print(f"Creating {position} scanner client for {symbol}")
        try:
            scanner_request = {
                "symbol":symbol,
                "trigger":trigger,
                "position":position,
                "buy_level":""
            }
            #define function to be triggered at a buy/sell signal
            trigger_func = self.enter_position if position == "long" else self.exit_position
            #Append:
            self.symbols_with_scanner_clients.append(symbol)
            #Make connection to scanner server:
            scanner_client.client(scanner_request,trigger_func,arg=[symbol])
        except Exception as e:
            try:
                #Try to remove symbol from lists:
                self.symbols_with_scanner_clients.remove(symbol)
            except: 
                pass
            raise ChildManagerError(f"Error creating scanner client for {symbol}: {str(e)}")

        
    def enter_position(self,symbol):
        '''Buys and updates appropriate variables, ONLY if there is a thread available to fill in'''
        #Check to see if all the threads have been filled, if they have, then abort the function entirely
        if len(self.taken_symbols) == self.threads: #If all the threads are activated:
            print("All threads have been filled, aborting this method")
            return #Exit out of function
        elif len(self.taken_symbols) < self.threads: #If they havent all been activated
            #Continue on with rest of function
            try:
                #Calculate amount of currency this thread will trade with based on total balance and number of threads allowed
                balance = float(float(self.total_balance)/self.threads)
                #Enter position into market (actually buy):
                Child(symbol,balance).buy()
                #Update self.taken_symbols
                self.taken_symbols.append(symbol)
                print("self.taken_symbols: "+", ".join([i for i in self.taken_symbols]))
                print("Threads occupied: ",len(self.taken_symbols))
            except Exception as e:
                raise ChildManagerError(f"Error buying {symbol}: {str(e)}")


    def exit_position(self,symbol):
        '''Sells and updates appropriate variables'''
        print("Exiting position for "+symbol)
        #Check to see if all the threads have been filled, if they have, then abort the function entirely
        if len(self.taken_symbols) == 0: #If there have been no threads activated:
            return #Exit out of function, it shouldnt have been called in the first place if there were no entries opened up
        else:
            #Continue on with rest of function
            try:
                #Calculate amount of currency this thread will trade with based on total balance and number of threads allowed
                balance = float(float(self.total_balance)/self.threads)
                #Enter position into market (actually buy):
                Child(symbol,balance).sell()
                #Update self.taken_symbols
                self.taken_symbols.remove(symbol)
            except ValueError:
                pass
            except Exception as e:
                raise ChildManagerError(f"Error selling {symbol}: {str(e)}")





                
if __name__ == "__main__":
    test = ChildManager(threads=4,
                        prefered_long_triggers=["bollband_stochrsi"],
                        other_long_triggers=["ema_crossover"],
                        prefered_sell_triggers=["profit_range","top_bb_band_reached"],
                        other_sell_triggers=["stochastic_peak"])
    test.init_main_loop()

#TODO: When creating scanner client, it activates an infinite loop which only allows one to get created. You might have to do multithreading to create them
#TODO: When a symbol is sold, consider turning the sell client back to a long client to start looking for buy signals again in self.exit_position()
