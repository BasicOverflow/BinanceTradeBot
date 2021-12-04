import sys,os
# Gives file access to parent directory and direct imports from there
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor
from trading_algorithms import bollband_stochrsi_strat,ema_crossover
from trading_algorithms.tech_indicators import profit,isBandTouching,stochrsi,bollinger_bands,rsiFunc
# from trading_algorithms.tech_indicators import percent_k,percent_d
from api_bridge.binance_exchange import ExchangeBridge
from global_vars_server.globals_client import client 
from api_server.exchange_client import APIRequest,client
import custom_errors
from custom_errors.errors import WebsocketScannerError,APIServerError
from settings import POSSIBLE_LONG_TRIGGERS,POSSIBLE_SELL_TRIGGERS
import time
import threading
import pickle
import socket
from datetime import datetime



class Scanner(object): 
    '''Uses websockets to scan desired symbols and looks for technical indocators set in place by progamer'''
    long_triggers = POSSIBLE_LONG_TRIGGERS
    sell_triggers = POSSIBLE_SELL_TRIGGERS

    def __init__(self,updateGlobalVars=False,trading_interval="1m",host="localhost",port=12000,MAX_CLIENTS=350):
        self.updateGlobalVars = updateGlobalVars
        self.trading_interval = trading_interval
        self.server_address = (host,port)
        self.MAX_CLIENTS = MAX_CLIENTS
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #Init pool to accept symbol requests
        threading.Thread(target=self.init_pool).start()
        #Init TCP server to receive and process client requests
        threading.Thread(target=self.init_server).start()

    
    def init_server(self):
        '''Communicates to client and sends constant stream of info on wether a trigger was hit for the client's symbol'''
        self.sock.bind(self.server_address)
        self.sock.listen(self.MAX_CLIENTS)
        self.listening = True
        #Init loop
        print("Listening...")
        while self.listening:
            # Dont create a method to process the request, do everything here since its just calling self.add_symbol or self.remove_symbol
            try:
                conn,addr = self.sock.accept()
                print(f"Connected with client: {addr} | {conn}")
                # Receive client request:
                request = pickle.loads(conn.recv(1024))
                print("Request received: ",request)
                #Process request:
                self.add_symbol(request["symbol"],request["trigger"],request["position"],request["buy_level"],conn)
            except IndexError:
                raise WebsocketScannerError("Error with receiving TCP request: "+str(e))
            except Exception as e:
                print(f"Error receving request: {str(e)}")


    def add_symbol(self,symbol,trigger,position,buy_level,tcp_conn):
        '''Allows for a symbol to be added to the pool. If an attempt is made to connect with a symbol that is alread connected, then the current TCP object and other new parameters will be switched out and the incoming client will be given the data stream'''
        # self.websocket_symbols.append({"symbol":symbol,"trigger":trigger,"position":position,"buy_level":buy_level,"tcp_conn":tcp_conn}) if symbol not in [i["symbol"] for i in self.websocket_symbols] else None
        if symbol not in [i["symbol"] for i in self.websocket_symbols]: #If there is no client already present for the given symbol:
            #Add the client to the pool
            self.websocket_symbols.append({"symbol":symbol,"trigger":trigger,"position":position,"buy_level":buy_level,"tcp_conn":tcp_conn,"trailing_stop_price":""})
        else: #If there is already a client with the given symbol
            # Take that client and replace all its other attributes with the new given ones, including the TCP connection 
            for i in self.websocket_symbols:
                if i["symbol"] == symbol:
                    i["tcp_conn"] == tcp_conn
                    i["trigger"] == trigger
                    i["position"] == position
                    # i["buy_level"] == buy_level


    def remove_symbol(self,symbol):
        '''Allows for a symbol to be removed from the pool'''
        try:
            for i in self.websocket_symbols:
                if i["symbol"] == symbol:
                    self.websocket_symbols.remove(i)
            for i in self.activated_connections:
                if i["symbol"] == symbol:
                    self.bm.stop_socket(i["conn_key"])
                    self.activated_connections.remove(i)
        except IndexError: 
            #Symbol not present in pool anyway
            pass

    
    def init_pool(self):
        '''Holds an array of symbols to receive websockets. Two arrays: websocket_symbols and self.activated_connections
        -when a new symbol is added to the pool, it is appended to websocket_symbols,
        -to activate a websocket stream for it, a key is created and appended to self.activated_connections
        -this way it is possible to remove and deactivate select symbols'''
        self.websocket_symbols = []
        self.listening = True
        self.bm = BinanceSocketManager(ExchangeBridge().return_client())
        self.activated_connections = [] 
        #Start loop:
        print("Initializing pool...")
        while self.listening: 
            try:
                time.sleep(0.6)
                # print([i["symbol"] for i in self.activated_connections])
                # print("-------------------------------------")
                if self.websocket_symbols == []: continue
                for i in self.websocket_symbols:
                    if bool([conn for conn in self.activated_connections if conn["symbol"] == i["symbol"]]): #If there is a key for the symbol present in self.activated_connections
                        pass
                    elif bool([conn for conn in self.activated_connections if conn["symbol"] == i["symbol"]]) == False: # If there isnt,
                        #Activate it
                        conn_key = self.bm.start_kline_socket(i["symbol"],self.process_response_long if i["position"] == "long" else self.process_response_sell, interval=self.trading_interval)
                        #Gather historical klines: Make data request to server:
                        request = APIRequest(i["symbol"],"data",is_websocket=True,trade_interval=self.trading_interval)
                        #Send request to server:
                        client(request,host="localhost",port=10000,encryption_mode=False) 
                        bm = BinanceSocketManager(ExchangeBridge().return_client())
                        #Append it to activate connections
                        self.activated_connections.append({"symbol":i["symbol"],"conn_key":conn_key,"bm":bm})
                        bm.start()
                    if bool([conn for conn in self.activated_connections if conn["symbol"] not in self.websocket_symbols]):
                        #If a symbol has been removed from self.websocket symbols but is still in self.activated_connections, then deactivate the websocket:
                        # print("Removing...")
                        [(self.bm.stop_socket(conn["conn_key"]),self.activated_connections.remove(conn)) for conn in self.activated_connections if conn["symbol"] not in [i["symbol"] for i in self.websocket_symbols]]    
            except APIServerError as e:
                # The API server isnt activated
                print("API server isn't activated stupid: ",e)
                break 
            except Exception as e:
                raise WebsocketScannerError("Error in self.init_pool: ",e)

    
    def notify(self,symbol,trigger,trigger_bool):
        '''Send packet of data with trigger type, symbol, current datetime, and the boolean '''
        notification = {
            "symbol":symbol,
            "trigger":trigger,
            "trigger_bool":trigger_bool,
            "datetime":datetime.now()
        }
        try:
            tcp_conn = [i["tcp_conn"] for i in self.websocket_symbols if i["symbol"] == symbol][0]
            tcp_conn.send(pickle.dumps(notification))
        except ConnectionAbortedError:
            #If the client has disconnected with the scanner server, than its symbol's webscoket stream will be removed and this function will abort
            self.remove_symbol(symbol)
            return
        except ConnectionResetError:
            #If the client has manually disconnected with the scanner server, than its symbol's webscoket stream will be removed and this function will abort
            self.remove_symbol(symbol)
            return


    def process_response_long(self,data):
        '''Processes websocket data and sends it off formatted to be analyzed '''
        try:
            #Check to see if websocket API error has occured:
            if data["e"] == "error":
                raise WebsocketScannerError("Error receiving websocket data: ",data["m"])
            else: pass
            #Parse response:
            symbol = data["s"]
            open_price = data["k"]["o"]
            close_price = data["k"]["c"]
            close_time = data["k"]["T"]
            final_bar = data["k"]["x"]
            volume = data["k"]["v"]
            print(f"Data: {symbol},{open_price},{close_price},{close_time},{final_bar},{volume}, long")
            #Prep data for analysis:
            exchangeBridge = ExchangeBridge(symbol=symbol,trading_interval=self.trading_interval,init_data_collection=False,websocket_mode=True)
            # Receive data into arrays
            if final_bar: #If the current response is the closing of a bar
                #Add the data into the websocket db and gather all the klines
                exchangeBridge.record_websocket_data(close_price,open_price,close_time,volume)
                #Gather rest of klines:
                open_prices  = exchangeBridge.select_colum("open_price")
                close_prices = exchangeBridge.select_colum("close_price")
                close_times = exchangeBridge.select_colum("close_time")
                volumes = exchangeBridge.select_colum("volume")
            else: #If the current response is not the close of a bar Gather all klines in db and append this response data to arrays without actually storing it in db
                open_prices  = exchangeBridge.select_colum("open_price")
                close_prices = exchangeBridge.select_colum("close_price")
                close_times = exchangeBridge.select_colum("close_time")
                volumes = exchangeBridge.select_colum("volume")
                #Append current data to historic arrays:
                open_prices.append(float(open_price))
                close_prices.append(float(close_price))
                close_times.append(close_time)
                volumes.append(float(volume))
            # Find desired trigger:
            trigger = [i["trigger"] for i in self.websocket_symbols if i["symbol"] == symbol][0] 
            # print(f"Trigger for {symbol}: ",trigger)
            # Assign to appropriate method:
            if trigger == "volume_spike":
                is_met = self.volume_spike(volumes)
            elif trigger == "price_spike":
                is_met = self.price_spike(close_prices)
            elif trigger == "bollband_stochrsi":
                is_met = self.bollband_stochrsi(close_prices,open_prices,close_times)
            elif trigger == "ema_crossover":
                is_met = self.ema_crossover(close_prices)
            # For testing:
            print(f"{symbol} {trigger} was triggered at {datetime.now()} at {close_price} satoshi") if is_met else None
            #Send notification to appropriate scanner client:
            self.notify(symbol,trigger,is_met)
            #Update the symbol's buy level if a buy signal was triggered
            if is_met:
                for i in self.websocket_symbols:
                    if i["symbol"] == symbol:
                        i["buy_level"] == close_price
            else: pass
        except WebsocketScannerError:
            # Abort function:
            print("Hit exception, aborting...")
            return 
        except custom_errors.errors.ExchangeBridgeError:
            print("Couldn't access all of data needed in database, aborting...")
            return
        except IndexError as e:
            print(f"Collecting historical klines for {symbol} probably failed on the exchange server side or cant compute technical indicators: "+str(e))
            return
        except Exception as e:
            print(f"{symbol} Error: {str(e)}") 
            return

        
    def process_response_sell(self,data):
        ''''''
        try:
            #Check to see if websocket API error has occured:
            if data["e"] == "error":
                raise WebsocketScannerError("Error receiving websocket data: ",data["m"])
            else: pass
            #Parse response:
            symbol = data["s"]
            open_price = data["k"]["o"]
            close_price = data["k"]["c"]
            close_time = data["k"]["T"]
            final_bar = data["k"]["x"]
            volume = data["k"]["v"]
            #For testing:
            print(f"Data: {symbol},{open_price},{close_price},{close_time},{final_bar},{volume}, sell")
            #Gather and prep data:
            exchangeBridge = ExchangeBridge(symbol=symbol,trading_interval=self.trading_interval,init_data_collection=False,websocket_mode=True)
            # Receive data into arrays
            if final_bar: #If the current response is the closing of a bar
                #Add the data into the websocket db and gather all the klines
                exchangeBridge.record_websocket_data(close_price,open_price,close_time,volume)
                #Gather rest of klines:
                open_prices  = exchangeBridge.select_colum("open_price")
                close_prices = exchangeBridge.select_colum("close_price")
                close_times = exchangeBridge.select_colum("close_time")
                volumes = exchangeBridge.select_colum("volume")
            else: #If the current response is not the close of a bar Gather all klines in db and append this response data to arrays without actually storing it in db
                open_prices  = exchangeBridge.select_colum("open_price")
                close_prices = exchangeBridge.select_colum("close_price")
                close_times = exchangeBridge.select_colum("close_time")
                volumes = exchangeBridge.select_colum("volume")
                #Append current data to historic arrays:
                open_prices.append(float(open_price))
                close_prices.append(float(close_price))
                close_times.append(close_time)
                volumes.append(float(volume))
            #Retreive desired trigger
            trigger = [i["trigger"] for i in self.websocket_symbols if i["symbol"] == symbol][0]
            #Retreive buy level:
            buy_level = [i["buy_level"] for i in self.websocket_symbols if i["symbol"] == symbol][0]
            # Assign to appropriate method:
            if trigger == "profit_range":
                profit_range = exchangeBridge.find_APD()
                is_met = self.profit_range(buy_level,close_price,profit_range)
            elif trigger == "stochastic_peak":
                is_met = self.stochastic_peak(buy_level,close_prices)
            elif trigger == "rsi_peak":
                is_met = self.rsi_peak(buy_level,close_prices)
            elif trigger == "has_reached_top_bb":
                is_met = self.has_reached_top_bb(buy_level,open_prices[-1],close_prices,close_times)
            # For testing:
            print(f"{symbol} {trigger} was triggered at {datetime.now()} at {close_price} satoshi") if is_met else None
            #Send notification to appropriate scanner client:
            self.notify(symbol,trigger,is_met)
        except WebsocketScannerError:
            # Abort function:
            print("Hit exception, aborting...")
            return 
        except custom_errors.errors.ExchangeBridgeError:
            print("Couldn't access all of data needed in database, aborting...")
            return
        except IndexError as e:
            print(f"Collecting historical klines for {symbol} probably failed on the exchange server side or cant compute technical indicators: "+str(e))
            return
        except Exception as e:
            print(f"{symbol} Error: {str(e)}") 
            return

    
    def volume_spike(self,volumes,min_percentage=2000):
        '''Detects recent spikes in volume for long position'''
        #NOTE: Not good to use if the overall quote asset volume is low to begin with, and when its not, try using a min percentage of 200
        volumes = volumes[-4:]
        differences = []
        for volume1, volume2 in zip(*[iter(volumes)]*2):
            percent_difference = abs(profit(float(volume1),float(volume2)))
            differences.append(percent_difference)
            # print(price1,price2,percent_difference)
        #Get rid of small percentages 
        for _ in range(4):
            differences = sorted(differences)[len(differences)//2:]   
        # print(average_difference)
        # Take highest value:
        result = differences[-1]
        # Check if trigger condition is met:
        if result >= min_percentage:
            return True
        else: return False

    
    def price_spike(self,close_prices,min_percentage=5):
        '''Detects any recent parabolic movements in price for long position'''
        close_prices = close_prices[-20:]
        # print(close_prices)
        differences = []
        for price1, price2 in zip(*[iter(close_prices)]*2):
            percent_difference = abs(profit(float(price1),float(price2)))
            differences.append(percent_difference)
            # print(price1,price2,percent_difference)
        #Get rid of small percentages 
        for _ in range(4):
            differences = sorted(differences)[len(differences)//2:]   
        # print(average_difference)
        # Take highest value:
        result = differences[-1]
        # Check if trigger condition is met:
        if result >= min_percentage:
            return True
        else: return False

    
    def bollband_stochrsi(self,close_prices,open_prices,close_times):
        '''Detects when stoch_rsi and bollingerbands signal align and trigger together for long position'''
        return bollband_stochrsi_strat.algo(close_prices=close_prices,open_prices=open_prices,close_times=close_times) #old method using stochrsi algo

    
    def ema_crossover(self,close_prices):
        '''Detects the crossing over of three ema's to generate a long position'''
        return ema_crossover.algo(close_prices)
    

    def stochastic_peak(self,buy_level,close_prices,peak_value=85):
        '''Calculates the stochastic rsi of the current close and if it has reached a certain level while still remaining profitable, a signal wil be triggered for a sell'''
        curr_stochrsi = stochrsi(close_prices)[-1]
        curr_close = close_prices[-1]
        percent_profit = profit(buy_level,curr_close)
        if curr_stochrsi >= peak_value and percent_profit > 0:
            return True
        else: return False

    
    def profit_range(self,buy_level,current_close,profit_range):
        '''With a given percent range will determine if the current close it that much above the buy price and will send a sell signal if it is'''
        percent_profit = profit(buy_level,current_close)
        if percent_profit >= profit_range:
            return True
        else: return False

    
    def rsi_peak(self,buy_level,close_prices,peak_value=65):
        '''Returns True if the rsi of the current close price has reached or passed a certain level and there is still profit to be made based on the given buy level. Returns signal for sell'''
        curr_close = close_prices[-1]
        curr_rsi = rsiFunc(close_prices)[-1]
        percent_profit = profit(buy_level,curr_close)
        if curr_rsi >= peak_value and percent_profit > 0:
            return True
        else: return False

    
    def has_reached_top_bb(self,buy_level,curr_open,close_prices,close_times):
        '''Returns True if if the close price has reached the top bollinger band of the current close and profitablity is still reachable. Returns signal for sell'''
        curr_close = close_prices[-1]
        _,top_band,_,_ = bollinger_bands(close_times,close_prices)
        curr_top_band = top_band[-1]
        percent_profit = profit(buy_level,curr_close)
        if isBandTouching(curr_open,curr_close,curr_top_band) and percent_profit > 0:
            return True
        else: return False

    
    def stoploss(self,buy_level,current_close,stoploss_range,trailing=False):
        '''Checks to see if price has fallen a certain percent below the bought price.'''
        if not trailing:
            decrease =  abs(round(100 - ((buy_level*100)/current_close),2)) #Assuming that the profit is already negative
            if decrease > stoploss_range:
                '''Stop loss has been hit'''
                return True
            else: return False #Stoploss hasn't been hit
        else:
            # If a trailing stop price hasn't been set, set it as the current close if its higher than the original buy price:
            for i in self.websocket_symbols:
                if i["buy_level"] == buy_level:
                    if i["trailing_stop_price"] == "":
                        i["trailing_stop_price"] = str(current_close) if current_close > buy_level else buy_level
                        #Set the stop price
                        stop_price = current_close if current_close > buy_level else buy_level 
                    else: #If a stop price has been set, than check to see if the current price is higher, if so set the stop price to the current close
                        for i in self.websocket_symbols:
                            if i["buy_level"] != "":
                                recorded_stop_price = i["trailing_stop_price"]
                                i["trailing_stop_price"] = str(current_close) if current_close > recorded_stop_price else recorded_stop_price
                                #Set the stop price
                                stop_price = current_close if current_close > recorded_stop_price else recorded_stop_price
            # Calculate percent decrease from stop price
            decrease =  abs(round(100 - ((stop_price*100)/current_close),2)) #Assuming that the profit is already negative
            if decrease > stoploss_range: #If the percent range from the stop price to the current is greater than the specified stoploss range,
                #Trailing stop has been hit
                return True 
            else: return False #Trailing stop hasn't been hit


    def terminate_tcp_accepter(self):
        self.listening = False






if __name__ == "__main__":
    test = Scanner()
    # coins = ['ETHBTC', 'LTCBTC', 'BNBBTC', 'NEOBTC', 'QTUMETH',"ADAETH","MFTETH","XRPUSDT","XRPBTC","ZILETH"]
    

#NOTE: for calculating APD, find the range between the top and bottom bollinger bands of the current close price, then maybe calculate 80% of it or something like that
#NOTE: possible long strategy: combine the rsi,stochastic rsi, and stochastic





