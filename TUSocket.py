import socket
import re
import threading
import sys
from Environments import *


class TUSocket:

    def __init__(self, *args, **kwargs):
        self.USER = kwargs['user']
        self.PWD = kwargs['pwd']
        self.PORT = int(kwargs['port'])

        print("USER: %s" % self.USER)
        print("PRIVATE IP: %s" % CLIENT_PRIVATE_IP)
        print("PORT: %s" % self.PORT)
        self.friend_list = []
        self.server_authen()
        self.main()

    def main(self):
        print("\n[Menu]")
        print("1. Create room")
        print("2. Join friend's room")

        select = input("select: ").strip()

        if select == "1":
            print("\nCreating room %s %s" % (CLIENT_PRIVATE_IP, self.PORT))
            threading.Thread(target=self.wait_for_connection).start()
        elif select == "2":
            print("\nWhich friend you want to join ?")
            self.print_friend_list()
            select = int(input("\nselect friend: ").strip())
            friend = self.friend_list[select].split(":")
            ip = friend[1]
            port = int(friend[2])
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))

            threading.Thread(self.chat_connection(client_socket)).start()
            threading.Thread(self.wait_for_connection).start()

    def wait_for_connection(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((CLIENT_PRIVATE_IP, self.PORT))
        listen_socket.listen(10)
        while True:
            connection_socket, addr = listen_socket.accept()
            print("\nConnected to", addr)
            threading.Thread(target=self.listen_connection, args=(connection_socket, addr)).start()
            threading.Thread(target=self.chat_connection(connection_socket)).start()

    def chat_connection(self, sock):
        while True:
            try:
                payload = sys.stdin.readline()
                if payload.strip() == 'exit()':
                    sock.close()
                    return
                payload = "('%s', %d) %s\n" % (CLIENT_PRIVATE_IP, self.PORT, payload.strip())
                self.sock_send(sock, payload)
            except Exception as e:
                print("socket are in trouble, please try again")
        pass

    def listen_connection(self, sock, addr):
        while True:
            try:
                recv_msg = self.sock_recv(sock)
                if recv_msg:
                    print("%s %s" % (addr, recv_msg.strip()))
                elif recv_msg.strip() == "exit()":
                    print("Connection closed")
            except Exception as e:
                sock.close()
                print("Connection closed")
                return

    def server_authen(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        self.server_login(client_socket, self.USER, self.PWD)
        self.server_get_friend_list(client_socket)
        self.print_friend_list()

    def server_login(self, sock, user, pwd):
        payload = 'USER:{}\n' \
                  'PASS:{}\n' \
                  'IP:{}\n' \
                  'PORT:{}\n'.format(user, pwd, CLIENT_PRIVATE_IP, self.PORT)

        self.sock_send(sock, payload)
        while True:
            server_msg = sock.recv(1024)
            if server_msg.decode() == SERVER_STATUS['login_success']:
                print("Connected to server")
                return True
            elif server_msg.decode() == SERVER_STATUS['login_error']:
                print('Login failed, please try again')
                return False
            else:
                print('Unknown error, please try again')
                return False

    def server_get_friend_list(self, sock):
        while True:
            server_msg = sock.recv(2048).decode()
            friend_list = []
            for match in re.findall(PATTERN_FRIENDLIST, server_msg):
                if match.__contains__(self.USER):
                    continue
                friend_list.append(match)
            self.friend_list = friend_list
            return friend_list

    def print_friend_list(self):
        print("\n%d online friends" % self.friend_list.__len__())
        for friend in self.friend_list:
            print("%d. %s" % (self.friend_list.index(friend), friend))

    def sock_send(self, sock, payload):
        try:
            sock.send(payload.encode())
        except Exception as e:
            raise

    def sock_recv(self, sock):
        try:
            return sock.recv(2048).decode()
        except Exception as e:
            raise

