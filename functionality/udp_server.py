import socket
from functionality.onboard_postbox import UDP

server = UDP(8080, "")
server.IsServer()
while True:
    data,_=server.socket.recvfrom(1024)
    print(data)

# while True:
#     msg, client_address = server.getmsg()
#     print(msg.decode())