import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from custom_errors.errors import GlobalVarsServerError
from downtrend_tracker import instance,modified_array
import pickle
import socket
import threading



class DynamicArrayEnvironment(object):
    '''''Holds global variables and allows for them to be read and updated 
    from different scripts through TCP connections'''
    def __init__(self,host="localhost",port=3000,MAX_CLIENTS=300):
        self.server_address = (host,port)
        self.MAX_CLIENTS = MAX_CLIENTS
        #Init socket bindings and stuff
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #Init arrays:
        self.downtrend_array = modified_array.DownTrendArray() #NOTE: This might not be as important because new strategies I found require a tight stop 
        self.live_candidates = []
        self.in_use = []
        self.thread_num = 0 #Default number of live threads created #TODO: Consider having child manager track this

    
    def listen(self):
        '''Listens for incoming clients to accept and process'''
        self.sock.bind(self.server_address)
        self.sock.listen(self.MAX_CLIENTS)
        self.listening = True
        #Init loop
        print("Listening...")
        while self.listening:
            try:
                #Accept incoming client:
                connection,addr = self.sock.accept()
                print(f"Connected! Connection: {str(connection)} | Address: {addr}")
                #Recieve data sent from client:
                data = connection.recv(4096) 
                #Process the request:
                threading.Thread(target=self.process_request,args=[data,connection]).start()
            except Exception as e:
                connection.close()
                raise GlobalVarsServerError(f"Error with client {addr}: {e}")
                


    def process_request(self,data,connection):
        '''Extracts data from requests and sends conn + data to appropriate methods'''
        data = pickle.loads(data)
        # print(f"Data: {data}")
        try:
            var = data["which_array"]
            action = data["action"]
            item = data["item"]
            #Call Methods corresponding to request type:
            if action == "read":
                self.read_array(var,connection)
            elif action == "append":
                self.append_array(var,item,connection)
            elif action == "remove":
                self.remove_array(var,item,connection)
            elif action == "clear":
                self.clear_array(var,connection)
            else: raise GlobalVarsServerError("You didnt name one of the actions right retard. Conn: ",connection)
        except IndexError:
            connection.close()
            raise GlobalVarsServerError("Request formatted incorrectly. Client conn: ",connection)
            
        except Exception as e:
            connection.close()
            raise GlobalVarsServerError(f"Unknown error with processing request: {e} | Connection: {connection}")
            

    
    def read_array(self,var,conn):
        '''Returns the current state of one of the arrays in the class'''
        try:
            if var == "downtrend":
                data = self.downtrend_array.coins_array
                data = pickle.dumps(data)
                conn.send(data)
            elif var == "in_use":
                data = self.in_use
                data = pickle.dumps(data)
                conn.send(data)
            elif var == "live_candidates":
                data = self.live_candidates
                data = pickle.dumps(data)
                conn.send(data)
            elif var == "thread_num":
                data = str(self.thread_num)
                data = pickle.dumps(data)
                conn.send(data)
            #Close connection
            conn.close()
        except Exception as e:
            conn.close()
            raise GlobalVarsServerError(f"Error sending read data to client: {e} | Connection: {conn}")
            

    
    def append_array(self,var,item,conn):
        '''Will append elements to the given array'''
        try:
            if var == "downtrend":
                downtrend_object = instance.Downtrend(str(item))
                self.downtrend_array.add(downtrend_object)
            elif var == "in_use":
                self.in_use.append(item)
            elif var == "live_candidates":
                self.live_candidates.append(item)
            elif var == "thread_num":
                self.thread_num += 1
            else: conn.close()
        except Exception as e:
            conn.close()
            raise GlobalVarsServerError(f"Error appending array: {e} | Connection: {conn}")
            

    
    def remove_array(self,var,item,conn):
        '''Will remove an element from a given array. Wont remove item from downtrend array because it is designed to do that itself.'''
        try:
            if var == "downtrend":
                del var
                del item
                raise Exception("Attempting to delete an item from an array that doesnt allow manual removes, you idiot")
            elif var == "in_use":
                self.in_use.remove(item)
            elif var == "live_candidates":
                self.live_candidates.remove(item)
            elif var == "thread_num":
                self.thread_num -= 1
            #Close connection:
            conn.close()
        except Exception as e:
            conn.close()
            raise GlobalVarsServerError(f"Error removing from array: {e} | Connection: {conn}")
            

    
    def terminate_listening(self):
        self.listening = False

    
    def restart_connection(self):
        self.terminate_listening()
        self.listen()

    
    def clear_array(self,var,conn):
        ''''''
        self.live_candidates = []
        conn.close()




if __name__ == "__main__":
    Server = DynamicArrayEnvironment()
    Server.listen()


# Format for requesting to the Array server:
# {
#     "which_array":"downtrend_array"
#     "action":"append",
#     "item":"symbol to remove/append"
# } <--If the action is to read, then leave item key as an empty string