import socket
from qt_core import *
import sys
import json
import struct


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


class InfoReceiverThread(QThread):

    infoReceived = Signal(dict)

    def __init__(self, multicast_ip,multicast_port, parent=None):
        QThread.__init__(self, parent)
        self.status = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.bind(('', multicast_port))
        # 加入组播组
        #mreq = struct.pack("=4sl", socket.inet_aton("234.2.2.2"), socket.INADDR_ANY)
        group=socket.inet_aton(multicast_ip)
        iface=socket.inet_aton(get_host_ip())
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, group+iface)

    def run(self):
        while self.status!=0:
            data, addr = self.socket.recvfrom(1024)
            msg = data.decode()
            info = json.loads(msg)
            self.infoReceived.emit(info)
            self.status = 2
        self.socket.close()
        sys.exit(-1)

# if __name__=="__main__":
#     t=InfoReceiverThread(8001)
#     t.start()