import socket
import time
import cv2
import numpy as np
from qt_core import *
import sys
import os


class VideoReceiverThread(QThread):

    updateFrame = Signal(QImage,int)
    streamReceived = Signal(int,int)
    printToCodeEditor = Signal(str)
    printToReminderBox=Signal(str)

    def __init__(self, port, uav_id, info_receiver, display_size, parent=None):
        QThread.__init__(self, parent)
        self.status = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.port=port
        self.uav_id=uav_id
        self.display_size=display_size
        self.socket.settimeout(1)
        self.frame=None
        self.info_receiver=info_receiver
        self.save_flag = False

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

            #start1 = time.time()  # 用于计算帧率信息
            try:
                stringData, addr = self.socket.recvfrom(50000)  # 根据获得的文件长度，获取图片文件
            except socket.timeout:
                self.status = 1
                print(f'video_receiver: Onboard PC id[{self.uav_id}] disconnected!')
                self.updateFrame.emit(None,self.port)
                self.streamReceived.emit(1,self.port)
                self.printToCodeEditor.emit(f"video_receiver: Onboard PC id[{self.uav_id}] disconnected!")
                self.printToReminderBox.emit(f"Onboard PC id[{self.uav_id}] disconnected!")
                self.frame = None
                continue
            # s.setblocking(False)
            #print(len(stringData),type(stringData))
            data = np.frombuffer(stringData, np.uint8)  # 将获取到的字符流数据转换成1维数组
            #start3 = time.time()
            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 将数组解码成图像
            self.frame=frame
            self._save_video()
            # Creating and scaling QImage
            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, frame.strides[0], QImage.Format_BGR888)
            scaled_img = img.scaled(*self.display_size, Qt.KeepAspectRatio)

            # Emit signal
            self.updateFrame.emit(scaled_img,self.port)
        self.socket.close()
        cv2.destroyAllWindows()
        sys.exit(-1)

    def _save_video(self):
        if self.save_flag:
            frame_width, frame_height=self.save_size
            # if self.frame is None:
            #     frame=np.zeros((frame_height,frame_width,3))
            # else:
            frame = cv2.resize(self.frame, (frame_width, frame_height))
            info=self.info_receiver.info.get(str(self.uav_id))
            if info is not None:
                height=20
                for key,value in info.items():
                    text = f"{key}:{value}"
                    cv2.putText(frame, text, (5, height),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    height+=20
            self.out.write(frame)

    def change_save_video_flag(self,flag,frame_width=640, frame_height=480):
        if flag:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            save_id=time.strftime("%Y-%m-%d-%H-%M",time.localtime())
            if not os.path.exists('./properties'):
                os.makedirs("./properties")
            self.out = cv2.VideoWriter(f'properties/{self.uav_id}_{save_id}.avi', fourcc, 15,(frame_width, frame_height))
            self.save_size=(frame_width,frame_height)
            self.save_flag=True
        else:
            self.save_flag = False
            self.out.release()


if __name__ == '__main__':
    print(os.path.exists('../properties'))
    print(time.strftime("%Y-%m-%d_%H:%M",time.localtime()))