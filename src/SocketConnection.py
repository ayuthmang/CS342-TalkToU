from socket import *


class SocketConnection:

    def __init__(self):
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    def connect(self, ip, port):
        try:
            self.client_socket.connect((ip, port))
        except Exception as e:
            print(e)
            sys.exit(-1)

    def send_message(self, sock, msg):
        sock.send(msg.encode())

    def __del__(self):
        try:
            self.client_socket.close()
        except Exception as e:
            print(e)
            sys.exit(-1)

