import sys,os
#Add compile_bot.py to file's sys.path, to be importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from api_bridge.binance_exchange import ExchangeBridge
from custom_errors.errors import APIServerError,ExchangeBridgeError
import socket
import pickle
import threading



class Server(object):
    '''Basic part client-server system where it waits for incoming requests to execute actions directly relating to the Binance Exchange API'''
    def __init__(self,host="localhost",port=10000,MAX_CLIENTS=50,encryption_mode=False): 
        self.server_address = (host,port)
        self.MAX_CLIENTS = MAX_CLIENTS #Given value is assuming each bot will have its own instance of this server, in any other case is will need to listen to much more clients
        self.encryption_mode = encryption_mode
        #Set up TCP socket
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #For notifying of a client shutdown:
        # self.termination_symbol = None
        # self.termination_msg = None

    def listen(self):
        '''Listens for incoming clients, processes their requests'''
        self.listening = True
        self.sock.bind(self.server_address)
        self.sock.listen(self.MAX_CLIENTS)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Init loop:
        while self.listening:
            try:
                #Accept client socket, get connection and address
                conn,addr = self.sock.accept()
                print(f"Connected with client: {addr} | {conn}")
                #Receive encryption key from client:
                key = conn.recv(1024) if self.encryption_mode else None
                # print(key)
                #Receive data from client:
                data = conn.recv(1024)
                #Decrypt data:
                data = decrypt(data,key) if self.encryption_mode else data
                #Send request to be processes by another method:
                threading.Thread(target=self.process_request,args=[conn,data]).start()
            except Exception as e:
                #Abandon connection, raise Exception
                conn.close() 
                raise APIServerError(e)

        
    def process_request(self,conn,data):
        '''Processes requests and calls appropriate mthods to execute the action. Eventually ends the connection with client once task is completed'''
        request = pickle.loads(data)
        print("Request: ",request)
        #Extract data:
        symbol = request["symbol"]
        is_websocket = request["is_websocket"]
        request_type = request["request_type"]
        trade_interval = request["trade_interval"]
        amount = request["amount"]
        entry_price = request["entry_price"]
        exit_price = request["exit_price"]
        #Send data to methods to execute task:
        if request_type == "buy":
            self.buy(symbol,entry_price,amount,conn)
        elif request_type == "sell":
            self.sell(symbol,entry_price,exit_price,amount,conn)
        elif request_type == "data":
            self.collect_klines(symbol,trade_interval,is_websocket,conn)


    def buy(self,symbol,entry_price,amount,conn):
        '''Makes market buy on API exchange'''
        try:
            ExchangeBridge(symbol=symbol).buy(price=entry_price,amount=amount,sms=True)
            #If successful:
            conn.close()
        except ExchangeBridgeError as e:
            conn.close()
            raise APIServerError("Something went wrong with ExchangeBridge buy: ",e)

    
    def sell(self,symbol,entry_price,exit_price,amount,conn):
        '''Makes market sell on API Exchange'''
        try:
            ExchangeBridge(symbol=symbol).sell(price=entry_price,exit_price=exit_price,amount=amount,sms=True)
            #If successful:
            conn.close()
        except ExchangeBridgeError as e:
            raise APIServerError("Something went wrong with ExchangeBridge sell: ",e)
            conn.close()


    def collect_klines(self,symbol,trade_interval,is_websocket,conn):
        '''Collects klines and puts them in database'''
        try:
            exchangeBridge = ExchangeBridge(symbol=symbol,trading_interval=trade_interval,init_data_collection=True,websocket_mode=is_websocket)
            #If successful:
            del exchangeBridge
            conn.close()
        except ExchangeBridgeError as e:
            conn.close()
            raise APIServerError("Something went wrong with exchangeBridge kline collection: ",e)
            

    






if __name__ == "__main__":
    test = Server(encryption_mode=False)
    print("Listening...")
    test.listen()