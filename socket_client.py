import socket

host = socket.gethostname() 
port = 8124 

def client_program():
    ClientSocket = socket.socket()  
    print("Waiting for connection...")
    
    try:
        ClientSocket.connect((host, port)) 
    except socket.error as e:
        print(str(e))

    Response = ClientSocket.recv(2048)
    
    while True:
        message = input("-> ")
        ClientSocket.send(message.encode())  
        reply = ClientSocket.recv(2048)
        decoded_reply = reply.decode()
        print(decoded_reply) 
        if message.lower().strip() == "quit":
            break

    ClientSocket.close()  # close the connection


if __name__ == "__main__":
    client_program()
