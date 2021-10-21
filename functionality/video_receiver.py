import socket
import time
import cv2
import numpy
from qt_core import *
import sys


class VideoReceiverThread(QThread):

    updateFrame = Signal(QImage,int)
    streamReceived = Signal(int,int)
    printToCodeEditor = Signal(str)

    def __init__(self, port, uav_id,display_size=(640, 480), parent=None):
        QThread.__init__(self, parent)
        self.status = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.port=port
        self.uav_id=uav_id
        self.display_size=display_size
        self.socket.settimeout(3)

    def run(self):
        while self.status:
            while self.status==1:
                try:
                    self.socket.recvfrom(50000)
                    self.status = 2
                    self.streamReceived.emit(3,self.port)
                except socket.timeout:
                    #print(f'video_receiver: Onboard PC id[{self.uav_id}] timed out!')
                    self.updateFrame.emit(None, self.port)

            start1 = time.time()  # 用于计算帧率信息
            try:
                stringData, addr = self.socket.recvfrom(50000)  # 根据获得的文件长度，获取图片文件
            except socket.timeout:
                self.status = 1
                print(f'video_receiver: Onboard PC id[{self.uav_id}] disconnected!')
                self.updateFrame.emit(None,self.port)
                self.streamReceived.emit(1,self.port)
                self.printToCodeEditor.emit(f"video_receiver: Onboard PC id[{self.uav_id}] disconnected!")
                continue
            # s.setblocking(False)
            # print(len(stringData))
            data = numpy.frombuffer(stringData, numpy.uint8)  # 将获取到的字符流数据转换成1维数组
            start3 = time.time()
            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 将数组解码成图像
            #cv2.imshow('SERVER', decimg)  # 显示图像

            end = time.time()
            #print(end - start1, start3 - start1)
            # seconds = end - start1
            # fps = 1 / seconds
            # conn.send(bytes(str(int(fps)), encoding='utf-8'))
            # k = cv2.waitKey(1) & 0xff
            # if k == 27:
            #     flag_continue = False
            #     break

            # Creating and scaling QImage
            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, frame.strides[0], QImage.Format_BGR888)
            scaled_img = img.scaled(*self.display_size, Qt.KeepAspectRatio)

            # Emit signal
            self.updateFrame.emit(scaled_img,self.port)
        self.socket.close()
        cv2.destroyAllWindows()
        sys.exit(-1)


# if __name__ == '__main__':
#     receiveVideo()