import socket

HOST = '192.168.137.10'
PORT = 8123

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    while True:
        msg = input(">>> enter cmd: ")
        s.sendall((msg + '\r\n').encode())
