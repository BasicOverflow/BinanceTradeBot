# Access_globals.py, used to communicate to globals_server
import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
import socket
import pickle
from custom_errors.errors import GlobalVarsClientError

# {
#         "which_array":"downtrend_array"
#         "action":"append",
#         "item":"symbol to remove/append"
# } <--If the action is to read, then leave item key as an empty string


def client(request,host="localhost",port=3000):
    '''Connects and sends requests to global vars server'''
    action = request["action"]
    address = (host,port)
    try:
        #Create socket:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect(address)
        #Deserialize object into string
        data = pickle.dumps(request)
        sock.send(data)
        #Finish task:
        sock.close() if action == "remove" or action == "append" else None
        #Return data if action 
        if action == "read":
            response = []
            while True:
                packet = sock.recv(4096)
                if not packet: break
                response.append(packet)
            data = pickle.loads(b"".join(response))
            sock.close()
            return data 
    except IndexError:
        raise GlobalVarsClientError("The list your trying to read is empty stupid")
        sock.close()
    except ConnectionRefusedError:
        print("You didnt turn on the global vars server idiot")
        sock.close()
        quit()
    except Exception as e:
        sock.close()
        raise GlobalVarsClientError(f"Error with client connecting to global vars server: {e} | Addr: {host} | Conn: {sock}")
        




def test():
    test_dict_write = {
        "which_array":"in_use",
        "action":"append",
        "item":"Guys Im actually gay"
    }

    # client(test_dict_write)

    test_dict_read = {
        "which_array":"live_candidates",
        "action":"read",
        "item":""
    }

    # x=input("Continue?")
    received_array = client(test_dict_read)
    print(f"Received data: {received_array}")



if __name__ == "__main__":
    test()
