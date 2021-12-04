import sys,os
# Gives file access to parent directory and direct imports from there
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from api_server import exchange_client #exchange_client.client()
from api_server.exchange_client import APIRequest


class Child(object):
    '''Allows for bot to buy or sell into a given symbol with the given amount'''
    def __init__(self,symbol,balance):
        self.symbol = symbol
        self.balance = balance
    
    def buy(self):
        # request = APIRequest(self.symbol,"buy",is_websocket=False,amount=str(self.balance),entry_price="",trade_interval="1m",exit_price="")
        # exchange_client.client(request)
        print(f"Bought {self.balance} of {self.symbol} ")

    
    def sell(self):
        # request = APIRequest(self.symbol,"buy",is_websocket=False,amount=str(self.balance),entry_price="",trade_interval="1m",exit_price="")
        # exchange_client.client(request)
        print(f"Sold {self.balance} of {self.symbol} ")





if __name__ == "__main__":
    pass