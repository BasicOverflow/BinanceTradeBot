import sys,os
#Add compile_bot.py to file's sys.path, to be importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from custom_errors.errors import APIServerError
import socket
import pickle



class APIRequest(object):
    '''Based on given arguments, will return an object ready to send to API server'''
    def __new__(self,symbol,request_type,is_websocket=False,amount="",entry_price="",trade_interval="",exit_price=""):
        try:
            return  {
                "symbol":symbol,
                "is_websocket":is_websocket,
                "request_type":request_type,
                "trade_interval":trade_interval,
                "amount":amount,
                "entry_price":entry_price,
                "exit_price":exit_price,
                    }
        except IndexError:
            raise APIServerError(f"Error creating API request for {symbol} {request_type}")


def client(request,host="localhost",port=10000,encryption_mode=False):
    '''Connects and sends requests to global vars server'''
    try:
        #Create socket:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((host,port))
        #Generate encryption key
        key = gen_key() if encryption_mode else None
        # print(key)
        #Serialize the object into a string  and encrytp it so it can be sent over TCP
        request = encrypt(pickle.dumps(request),key) if encryption_mode else pickle.dumps(request)       
        #Send encryption key to server:
        # print("Sending key...")
        sock.send(key) if encryption_mode else None
        # print("Sending message...")
        #Send serialized invoice to exchange handler
        sock.send(request)
        sock.close()
    except Exception as e:
        raise APIServerError(f"Error with client connecting to API server: {e} | Addr: {host}")
        sock.close()


def test():
    request = APIRequest("NANOETH","data",trade_interval="1m")
    client(request)







if __name__ == "__main__":
    test()