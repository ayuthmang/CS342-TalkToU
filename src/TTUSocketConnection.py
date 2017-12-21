import time
import threading
import sys

import re

from src.SocketConnection import *
from src.Environments import *

from socket import *


class TTUSocketConnection(SocketConnection):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.client_socket.settimeout(60)
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.friend_list = []
        self.thread_list = []
        self.user = kwargs['user']
        self.pwd = kwargs['pwd']
        self.main()

    def main(self):
        self.connect(SERVER_IP, SERVER_PORT)
        self.login(self.user, self.pwd)
        self.get_friend_list()

        thread_heartbeat = threading.Thread(name="Thread_HeartBeat", target=self.thread_heartbeat_work)
        thread_listen = threading.Thread(name="Thread_Listen", target=self.thread_listen)
        thread_send_msg = threading.Thread(name="Thread_SendMSG", target=self.thread_send_msg)
        self.thread_list.append(thread_heartbeat)
        self.thread_list.append(thread_listen)
        self.thread_list.append(thread_send_msg)

        for friend in self.friend_list:
            print(friend)

        for each_thread in self.thread_list:
            each_thread.start()
        # print(self.thread_list)

    def __del__(self):
        super(TTUSocketConnection, self).__del__()
        for job in self.thread_list:
            job._stop()

    def login(self, user, pwd):
        payload = 'USER:{}\n' \
                  'PASS:{}\n' \
                  'IP:{}\n' \
                  'PORT:{}\n'.format(user, pwd, CLIENT_PRIVATE_IP, CLIENT_PORT)

        self.client_socket.send(payload.encode())
        while True:
            server_msg = self.client_socket.recv(1024)
            if server_msg.decode() == SERVER_STATUS['login_success']:
                print("Login success")
                return True
            elif server_msg.decode() == SERVER_STATUS['login_error']:
                print('Login failed, please try again')
                return False
            else:
                print('Unknown error, please try again')
                return False

    def get_friend_list(self):
        while True:
            server_msg = self.client_socket.recv(2048).decode()
            friend_list = []
            for match in re.findall(PATTERN_FRIENDLIST, server_msg):
                friend_list.append(match)
            self.friend_list = friend_list
            return friend_list

    def thread_heartbeat_work(self):
        while True:
            server_msg = self.client_socket.recv(1024).decode()
            if server_msg == "Hello {}".format(self.user):
                self.client_socket.send("Hello Server".encode())
            time.sleep(1)

    def thread_listen(self):
        self.server_socket.bind((CLIENT_PRIVATE_IP, CLIENT_PORT))
        self.server_socket.listen(1)
        print()
        print("Ready to chat with other with port %s" % CLIENT_PORT)
        connectionSocket, addr = self.server_socket.accept()
        print("Connection from ", addr)
        while 1:
            sentence = connectionSocket.recv(2048).decode()
            print("{}: {}".format(addr, sentence))
            time.sleep(1)

    def thread_send_msg(self):
        while True:
            msg = sys.stdin.readline()
            self.server_socket.send(msg.encode())


if __name__ == '__main__':
    sock = TTUSocketConnection(user="5809610347", pwd="0347", port=4321)