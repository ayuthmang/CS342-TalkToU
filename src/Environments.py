#======================================================
# ENV
#======================================================

import socket

SERVER_IP = '128.199.83.36'
SERVER_PORT = 34260

CLIENT_PORT = 12345
CLIENT_PRIVATE_IP = my_ip = socket.gethostbyname(socket.gethostname())

PAYLOAD_ORIGIN = {
    "USER": '',
    "PASS": '',
    "IP": '',
    "PORT": ''
}

SERVER_STATUS = {
    'login_error': '404 ERROR',
    'login_success': "200 SUCCESS\n"
}

PATTERN_FRIENDLIST = r"\d{10}:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}"
