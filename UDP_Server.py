import socket
import sys

serverName = '127.0.0.1'        # MY_SERVER_ADDRESS
serverPort = 12000          # PORT

# socket() : 소켓 객체 생성
# 1) 주소 체계(family)
# - AF_INET : IPv4
# - AF_INET6 : IPv6 (V)
# 2) 타입(type)
# - SOCK_STREAM : TCP
# - SOCK_DGRAM : UDP (V)

server_address = ((serverName, serverPort))      # MY_SERVER_ADDRESS, PORT
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print('Starting up on {} port {}'.format(*server_address))
serverSocket.bind(server_address)

while True:
    print('\nwaiting to receive message')
    data, address = serverSocket.recvfrom(1024)

    print('received {} bytes from {}'.format(len(data), address))
    print(data.decode())