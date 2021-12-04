import socket
import pickle



def receive_key(user_password,addr="*public ip*",port=1105):
    '''Connects to user data server and attempts to receive exchange account API key
    and secret with given credentials'''
    request_packet = {
        "action":"GET",
        "datatype":"api_key",
        "proof":"password",
        "item":user_password
    }
    #Create socket object
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # Connect to server
    sock.connect((addr,port))
    # Serialze request packet
    request_packet = pickle.dumps(request_packet)
    #send credentials
    sock.send(request_packet)
    #Receive data if any is provided
    received_key = (sock.recv(1024)).decode()
    print(received_key)
    #Close the connection
    sock.close()
    #Request API secret:
    request_packet = {
        "action":"GET",
        "datatype":"api_secret",
        "proof":"password",
        "item":user_password
    }
    sock.connect((addr,port))
    # Serialze request packet
    request_packet = pickle.dumps(request_packet)
    #send credentials
    sock.send(request_packet)
    #Receive data if any is provided
    received_secret = (sock.recv(1024)).decode()
    print(received_secret)
    #Close the connection
    sock.close()
    return received_key,received_secret


receive_key("ImG123")