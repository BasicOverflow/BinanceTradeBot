import sys,os
#Add compile_bot.py to file's sys.path, to be importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
import socket 
import pickle
from custom_errors.errors import ScannerClientError


request_example = {
    "symbol":"BNBBTC",
    "trigger":"volume_spike",
    "position":"sell", #sell or long
    "buy_level":"0.000123" #If position is long, this key should only hold an empty string
}

def client(request,trigger_function,arg=[],host="localhost",port=12000):
    '''Connects to scanner via TCP and keeps constant stream of tigger alerts for a given symbol'''
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((host,port))
        # Send Initial request with symbol and trigger option
        sock.send(pickle.dumps(request))
        # Init loop
        while True:
            # print(str(sock))
            # signal = pickle.loads(signal)
            response = sock.recv(4096)
            signal = pickle.loads(response)





    except Exception as e:
        pass



def test_trigger(text):
    print(text)






if __name__=="__main__":
    client(request_example,test_trigger)
