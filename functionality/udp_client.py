import socket
import time
from functionality.onboard_postbox import UDP

i = 0

client = UDP(8080, "127.0.0.1")
client.IsClient()

# while True:
#     uav_1 = UAV(1)
#     client.IsClient(msg)
#     time.sleep(1)
#     msg, _= client.getmsg()
#     client.getdata(msg)
#     i = i+1