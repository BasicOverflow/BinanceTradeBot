import sys,os
#Add Indicators.py to file's sys.path, to be importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from  api_bridge.binance_client import client
from sms.messaging import send
from binance.enums import *
import binance
import sqlite3
import datetime
import time
import requests
from numpy import mean
from trading_algorithms.tech_indicators import profit
from custom_errors.errors import ExchangeBridgeError,NetworkError,OrderError





class ExchangeBridge(object):
    '''Class that holds any methods that perform actions directly relating to the binance exchange, plus others'''
    def __init__(self,symbol="",trading_interval="1m",init_data_collection=False,websocket_mode=False):
        self.symbol = symbol
        self.trading_interval = trading_interval
        self.websocket_mode = websocket_mode 
        self.base_asset = self.symbol[-3:]
        self.coin=self.symbol[0:(len(self.symbol)-3)]
        #Check if initial data collecton is desired:
        if init_data_collection:
            self.init_data_collection()
        else: pass
        #Create db path
        main_dir = os.path.dirname(os.path.abspath(__file__))
        main_dir = os.path.dirname(os.path.abspath(__file__))
        main_dir,_ = main_dir.split("\Code")
        self.db_path = f"{main_dir}\Databases\{self.symbol}.db" if not self.websocket_mode else f"{main_dir}\Databases\{self.symbol}-websocket.db"
        del main_dir

    
    def init_data_collection(self):
        '''Automatically creates db, and collects first batch of kline data'''
        main_dir = os.path.dirname(os.path.abspath(__file__))
        main_dir = os.path.dirname(os.path.abspath(__file__))
        main_dir,_ = main_dir.split("\Code")
        self.db_path = f"{main_dir}\Databases\{self.symbol}.db" if not self.websocket_mode else f"{main_dir}\Databases\{self.symbol}-websocket.db"
        del main_dir
        self.create_table()
        self.clear_table()
        self.collect_kline_data()
    

    def create_db_connection(self):
        '''Attempts to connect to db, returns connection'''
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.OperationalError:
            raise ExchangeBridgeError(f"Error connecting to {self.symbol} db")


    def create_table(self):
        '''Creates table inside db'''
        try:
            conn = self.create_db_connection()
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS  kline_data(open_price REAL,close_price REAL,volume REAL,close_time BLOB,high_price REAL,low_price REAL)")
            conn.commit()
            conn.close()
        except ExchangeBridgeError as e:
            print("Error creating table: ",e)

    
    def clear_table(self):
        '''Clears the contents of a table'''
        try:
            conn = self.create_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM kline_data")
            conn.commit()
            conn.close()
        except ExchangeBridgeError as e:
            print("Error removing old klines: ",e)
        except sqlite3.OperationalError:
            pass #Just means there was nothing to clear

    
    def collect_kline_data(self,start_str="1 Hour 30 Minutes ago UTC"):
        '''Makes API call, process received data, and stores it in local db'''
        try:
            conn = self.create_db_connection()
            c = conn.cursor()
            #Attempt retreiving kline data from Exchange API
            klines = client.get_historical_klines(symbol=self.symbol,interval=self.trading_interval, start_str=start_str)
            #Parse and store into database:
            for candle in klines: #Each element in klines array is a candle
                open_price,close_price,volume,close_time,high_price,low_price = candle[1],candle[4],candle[5],candle[6],candle[2],candle[3]
                c.execute("INSERT INTO kline_data(open_price,close_price,volume,close_time,high_price,low_price) VALUES (?, ?, ?, ?, ?, ?)",
                (open_price,close_price,volume,close_time,high_price,low_price))
            conn.commit()
            conn.close()
        except ExchangeBridgeError:
            raise ExchangeBridgeError(f"{self.symbol} Error collecting kline data")
        except requests.exceptions.ConnectionError as e:
            #Request took took long and timed out or connection issues
            raise NetworkError(e)
        except requests.exceptions.ReadTimeout:
            #Request took took long and timed out or connection issues
            raise NetworkError(e)
        except Exception as e:
            print(f"{self.symbol} Error collecting klines: ",e)

    
    def record_websocket_data(self,close_price,open_price,close_time,volume):
        '''Inserts given data into db, for websockets'''
        try:
            conn = self.create_db_connection()
            c = conn.cursor()

            c.execute("INSERT INTO kline_data(open_price,close_price,close_time,volume) VALUES (?,?,?,?)", 
            (open_price,close_price,close_time,volume))

            conn.commit()
            conn.close()
        except ExchangeBridgeError:
            raise ExchangeBridgeError(f"Error recording websocket data,couldnt connect to database. {self.symbol}")
        except sqlite3.OperationalError as e:
            raise ExchangeBridgeError(f"{self.symbol} Error recording websocket data to db: {e}")

    
    def select_colum(self,colum):
        '''Returns given colum's contents'''
        try:
            conn = self.create_db_connection()
            c = conn.cursor()
            c.execute("SELECT {} FROM kline_data".format(colum))
            # print(c.fetchall())
            # print([i[0] for i in c.fetchall()])
            data = [i[0] for i in c.fetchall()] 
            #Close connections to the database
            conn.commit()
            conn.close()
            # Return the data
            return data
        except ExchangeBridgeError:
            raise ExchangeBridgeError(f"Error retrieving data,couldnt connect to database. {self.symbol}")
        except sqlite3.OperationalError as e:
            raise ExchangeBridgeError(f"{self.symbol} Error retreiving data: {e}")


    def buy(self,price="",amount="",sms=False):
        '''Makes market buy on Binance exchange'''
        try:
            #Find balance in actual coin 
            amount = str(self.find_symbol_balance(amount))
            #Create actual object that executes buy
            order = client.order_market_buy(symbol=self.symbol, 
                                            quantity=amount)  
            order_id = order["orderId"]
            #If successful:
            send(f"BUY order successful for {self.symbol} at {price} satoshi. Amount: {amount} {self.coin}.") if sms else None     
            #Log Trade:
            # NOTE implement trade logging     

        except binance.exceptions.BinanceAPIException as e:
            raise OrderError(e)
        except Exception as e:
            raise ExchangeBridgeError(e)

    
    def sell(self,entry_price="",exit_price="",amount="",sms=False):
        '''Makes market sell on the binance exchange'''
        try:
            #Find balance in actual coin 
            amount = str(self.find_symbol_balance(amount))
            #Create actual object that executes buy
            order = client.order_market_sell(symbol=self.symbol, 
                                            quantity=amount)  
            order_id = order["orderId"]
            #If successful:
            send(f"SELL order successful for {self.symbol} at {exit_price} satoshi for {amount} {self.coin} making {profit(entry_price,exit_price)}% profit") if sms else None    
            #Log Trade:
            # NOTE implement trade logging       
        except binance.exceptions.BinanceAPIException as e:
            raise OrderError(e)
        except Exception as e:
            raise ExchangeBridgeError(e)

    
    def find_symbol_balance(self,balance):
        '''Takes in base asset balance and converts it to the coin balance. Ex 0.9 ETH returns 50 NANO'''
        latest_satoshi = float(client.get_historical_klines(symbol=self.symbol,interval=self.trading_interval, start_str="5 Minutes Ago UTC")[-1][4])
        return float(balance/latest_satoshi)


    def find_APD(self,time_stamp="1 Hour 30 minutes ago"):
        '''APD=Average Percent difference. Takes all the close prices of the klines in a time frame, records the percent difference between each one, and averages them out'''
        close_prices = [i[4] for i in client.get_historical_klines(symbol=self.symbol,interval=self.trading_interval,start_str=time_stamp)]
        # print(close_prices)
        differences = []
        for price1, price2 in zip(*[iter(close_prices)]*2):
            percent_difference = abs(profit(float(price1),float(price2)))
            differences.append(percent_difference)
            # print(price1,price2,percent_difference)
        #Get rid of small percentages 
        for _ in range(6):
            differences = sorted(differences)[len(differences)//2:]   
        #Weighted modification:
        differences = sorted(differences)[len(differences)//2:] if mean(differences) > 5 else differences
        #Take the average:
        average_difference = mean(differences)  #Result is actual percent (example: 1.34%, 0.5%)
        # print(average_difference)
        return round(average_difference,2)

    
    def log_trade(self,msg):
        ''''''
        #Connect to TCP server and log trade, providing credentials
        pass

    
    def get_24hour_ticker(self,base_asset=True):
        '''Universal method that just returns all exchange symbols. If base_asset is true, will only return the symbols of that base asset '''
        return [i["symbol"] for i in client.get_ticker()] if not base_asset else [i["symbol"] for i in client.get_ticker() if str(self.base_asset) in i["symbol"]]

    
    def get_balance(self,get_base_asset=True):
        '''Retrieves balance of given symbol. If get_base_asset, will return any balace of the base asset, if false, will return the coin's balance'''
        try:
            return str(client.get_asset_balance(asset=self.base_asset if get_base_asset else self.coin)["free"])
        except TypeError:
            raise ExchangeBridgeError(f"There was no balance present for {self.base_asset if get_base_asset else self.coin}.")
        except binance.exceptions.BinanceAPIException as e:
            raise ExchangeBridgeError("Error retreiving balance: ",e)
        except Exception as e:
            raise ExchangeBridgeError("Unknown error: ",e)


    def return_client(self):
        return client










if __name__ == "__main__":
    test = ExchangeBridge(symbol="SCETH",init_data_collection=False,websocket_mode=True)
    # print(test.get_24hour_ticker(base_asset=False))
    print(test.get_balance())
    








