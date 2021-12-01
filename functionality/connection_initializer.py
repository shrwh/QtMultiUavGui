import socket
from qt_core import *
import sys
import json
import time
import threading


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


class ConnectionInitializer(QThread):

    #infoReceived = Signal(dict)

    def __init__(self, port, info=None, conn_num=2, parent=None):
        super().__init__(parent)
        self.status = 1
        self.port=port
        self.host_ip=get_host_ip()
        self.address_broadcast=(self.host_ip[:self.host_ip.rfind(".")+1]+"255",port)
        if info is None:
            info={}
        info["address"]=self.host_ip
        self.data = json.dumps(info).encode()
        self.status=1

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', self.port))
        s.settimeout(3)
        #count=0
        while self.status:
            s.sendto(self.data,self.address_broadcast)
            while self.status:
                try:
                    _, addr = s.recvfrom(1024)
                    if addr[0]==self.host_ip:
                        continue
                except socket.timeout:
                    break
        s.close()

# if __name__=="__main__":
#     t=InfoReceiverThread(8001)
#     t.start()