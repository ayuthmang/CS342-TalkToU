import threading
import sys
import re

from socket import *

from src.Environments import *


class TTUSocketConnection:

    def __init__(self, *args, **kwargs):
        # self.socket_list = []
        self.client_socket = socket.socket(AF_INET, SOCK_STREAM)
        self.client_socket.settimeout(120)
        # self.socket_list.append(self.client_socket)
        self.friend_list = []
        global CLIENT_PORT
        CLIENT_PORT = kwargs['port'] if kwargs['port'] else CLIENT_PORT
        self.user = kwargs['user']
        self.pwd = kwargs['pwd']

        print("Client private %s:%d" % (CLIENT_PRIVATE_IP, CLIENT_PORT))
        print("Login with %s" % self.user)
        self.main()

    def main(self):
        # self.start_virtual_server()
        self.connect(self.client_socket, SERVER_IP, SERVER_PORT)
        self.login(self.user, self.pwd)


        threading.Thread(name="thread_heartbeat", target=self.thread_heartbeat_work).start()
        # threading.Thread(name="thread_accept_connection", target=self.listen_connection()).start()
        print("\n[Menu]")
        print("1. Create room for friend")
        print("2. Join friend's room")
        print("3. Who's online ?")
        print("Ctrl + C or Command + C to exit")
        print()
        select = input("select your menu: ").strip()
        if select == "1":
            print("Creating room with ip: %s port: %d" % (CLIENT_PRIVATE_IP, CLIENT_PORT))
            threading.Thread(name="thread_accept_connection", target=self.listen_connection()).start()
        elif select == "2":
            print("Which friend do you want to join?\n")
            self.print_friend_list()
            print()
            select = input("select friend: ").strip()
            friend = self.friend_list[int(select)].split(":")
            # threading.Thread(target=self.manage_connection, args=(friend[1], friend[2])).start()
            # threading.Thread(name="thread_accept_connection", target=self.listen_connection()).start()
            talk_sock = socket.socket(AF_INET, SOCK_STREAM)
            connSock = talk_sock.connect((friend[1], int(friend[2])))
            threading.Thread(target=self.chat_init(connSock)).start()
        elif select == "3":
            self.print_friend_list()

    def listen_connection(self):
        listenSocket = socket.socket(AF_INET, SOCK_STREAM)
        listenSocket.bind((CLIENT_PRIVATE_IP, CLIENT_PORT))
        listenSocket.listen(10)
        while True:
            connectionSocket, addr = listenSocket.accept()
            print("\nConnection coming from ", addr)
            threading.Thread(target=self.manage_connection, args=(connectionSocket, addr)).start()

    def manage_connection(self, sock, addr):
        self.sock_send(sock, "Type exit() to end chat.\n")
        print("Type exit() to end chat.\n")

        threading.Thread(target=self.send_msg_connection, args=(sock, addr)).start()
        threading.Thread(target=self.listen_msg_connection, args=(sock, addr)).start()

    def sock_send(self, sock, msg):
        try:
            sock.send(msg.encode())
        except Exception as e:
            raise

    def listen_msg_connection(self, sock, addr):
        while True:
            try:
                recv_msg = sock.recv(2048).decode()
                # print(recv_msg.encode())
                if recv_msg:
                    print("%s %s" % (addr, recv_msg.strip()))
                elif recv_msg.strip() == "exit()":
                    print("matched")
                    sock.close()
                    print("Connection closed")
                # else:
                #     sock.close()
                #     print("Connection closed")
            except KeyboardInterrupt:
                sock.close()
                print("Connection closed")
                return
            except Exception as e:
                sock.close()
                print("Connection closed")
                return

    def send_msg_connection(self, sock, addr):
        while True:
            try:
                send_msg = sys.stdin.readline()
                # if send_msg.strip() == 'exit()':
                #     sock.close()
                #     return
                send_msg = "('%s', %d) %s\n" % (CLIENT_PRIVATE_IP, CLIENT_PORT, send_msg.strip())
                self.sock_send(sock, send_msg)
            except Exception as e:
                print("socket are in trouble, please try again")

    # def create_room(self, sock):
    #     sock.bind((CLIENT_PRIVATE_IP, CLIENT_PORT))
    #     sock.listen(1)
    #     listen_sock, addr = sock.accept()
    #     threading.Thread(target=self.keyboard_catch(listen_sock, addr)).start()
    #     print()
    #     print("Chat room connected with ip: %s port: %d" % addr)
    #     print("Use exit() to exit")
    #     print()
    #     while True:
    #         try:
    #             received_msg = listen_sock.recv(2048).decode().strip()
    #             if received_msg == "exit()":
    #                 print("matched")
    #                 sock.close()
    #                 break
    #             print("{}: {}".format(addr, received_msg))
    #         except Exception as e:
    #             print(e)

    # def keyboard_catch(self, sock, display_name):
    #     print("keyboard catch ")
    #     if not display_name:
    #         display_name = self.user
    #     while True:
    #         input_msg = input("Me: ")
    #         input_msg = "{}: {}\n".format(display_name, input_msg)
    #         sock.send(input_msg.encode())

    def connect(self, sock, ip, port):
        try:
           sock.connect((ip, port))
        except Exception as e:
            print(e)

    # def __del__(self):
    #     try:
    #         for sock in self.socket_list:
    #             sock.close()
    #         for job in self.thread_list:
    #             job._stop()
    #     except Exception as e:
    #         print(e)

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
                self.get_friend_list()
                self.print_friend_list()
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
                if match.__contains__(self.user):
                    continue
                friend_list.append(match)
            self.friend_list = friend_list
            return friend_list

    def print_friend_list(self):
        print()
        print("%d online friends" % self.friend_list.__len__())
        for friend in self.friend_list:
            print("%d. %s" % (self.friend_list.index(friend), friend))

    def thread_heartbeat_work(self):
        while True:
            server_msg = self.client_socket.recv(1024).decode()
            if server_msg == "Hello {}".format(self.user):
                self.client_socket.send("Hello Server".encode())

    # def thread_listen(self):
        # self.server_socket.bind((CLIENT_PRIVATE_IP, self.CLIENT_PORT))
        # self.server_socket.listen(1)
        # print()
        # print("Ready to chat with other with port %s" % self.CLIENT_PORT)
        # while 1:
        #     connectionSocket, addr = self.server_socket.accept()
        #     print("Connection from ", addr)
        #     sentence = connectionSocket.recv(2048).decode()
        #     connectionSocket.send('eiei'.encode())
        #     print("{}: {}".format(addr, sentence))
        #     time.sleep(1)

    # def thread_send_msg(self):
    #     print("thread send msg working")
    #     while True:
    #         try:
    #             msg = sys.stdin.readline()
    #             self.server_socket.send(msg.encode())
    #             print("msg is ", msg)
    #         except Exception as e:
    #             print(e)
    #             pass


# if __name__ == '__main__':
#     sock = TTUSocketConnection(user="5809610347", pwd="0347", port=4321)