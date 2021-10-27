import socket
from qt_core import *
import sys
import json


class InfoReceiverThread(QThread):

    infoReceived = Signal(int,dict)

    def __init__(self, port, parent=None):
        QThread.__init__(self, parent)
        self.status = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        #self.socket.settimeout(3)#no use for now
        #self.addr=(port,)#no use for now
        #self.port=port#no use for now

    def run(self):
        while self.status==1:
            try:
                data, addr = self.socket.recvfrom(1024)  # 根据获得的文件长度，获取图片文件
            except socket.timeout:
                print(f'{self.port}: info_receiver timed out!')
                #self.infoReceived.emit(1,None,None)
                continue
            #self.addr=self.addr+addr
            msg = data.decode()
            info = json.loads(msg)
            self.infoReceived.emit(1,info)
            self.status = 2
        while self.status:
            try:
                data, addr = self.socket.recvfrom(1024)  # 根据获得的文件长度，获取图片文件
            except socket.timeout:
                print(f'{self.port}: info_receiver timed out!')
                #self.infoReceived.emit(2,None,None)
                continue
            # s.setblocking(False)
            msg = data.decode()
            info = json.loads(msg)
            # Emit signal
            #print(info)
            self.infoReceived.emit(2,info)
        self.socket.close()
        sys.exit(-1)

# if __name__=="__main__":
#     t=InfoReceiverThread(8001)
#     t.start()