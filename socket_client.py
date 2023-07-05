import socket


def client_program():
    host = socket.gethostname()  # as both code is running on the same pc
    port = 8124  # socket server  port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = input(" -> ")  # take input

    while message.lower().strip() != "quit":
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(2048).decode()  # receive response

        print(data)  # show in terminal

        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection


if __name__ == "__main__":
    client_program()
