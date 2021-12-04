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
            # print(signal["trigger_bool"])
            # print("Triggered?: ",signal["trigger_bool"])
            if signal["trigger_bool"]:
                # print("WE GOT TRIGGERED FOR ",request["symbol"])
                trigger_function() if arg==[] else trigger_function(arg[0])
                #If a signal has been triggered and the function has been activated, then
                #break this loop so that a new long or sell client can be started
                sock.close()
                break
            else: 
                symbol = request["symbol"]
                print(f"{symbol} Not triggered")     
        return
    except Exception as e:
        #NOTE: When the trigger_bool comes up as True from the scanner server, the client raises an EOF error for some reason. So when this error is caught,
        #it means that a trigger has been detected and to execute the given function
        if "Ran out of input" in str(e):
            trigger_function() if arg==[] else trigger_function(arg[0])
            #If a signal has been triggered and the function has been activated, then
            #break this loop so that a new long or sell client can be started
            sock.close()
            return
        else:
            raise ScannerClientError(str(e)) 



def test_trigger(text):
    print(text)






if __name__=="__main__":
    client(request_example,test_trigger)
