import socket
import time
import cv2
import numpy as np
from qt_core import *
import sys
import os
import threading


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
        # self.socket.settimeout(3)
        self.frame=None
        self.info_receiver=info_receiver
        self.save_flag = False
        self.condition=threading.Condition()
        t1=threading.Thread(target=self._save_video_thread)
        t1.setDaemon(True)
        t1.start()

    def run(self):
        while self.status:
            while self.status==1:
                try:
                    self.socket.recvfrom(50000)
                    self.status = 2
                    self.streamReceived.emit(3,self.port)
                except socket.timeout:
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
            # Creating and scaling QImage
            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, frame.strides[0], QImage.Format_BGR888)
            scaled_img = img.scaled(*self.display_size, Qt.KeepAspectRatio)

            # Emit signal
            self.updateFrame.emit(scaled_img,self.port)
        self.socket.close()
        cv2.destroyAllWindows()
        sys.exit(-1)

    def _put_text_to_frame(self,frame,text,width,height):
        cv2.putText(frame, text, (width, height),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        height += 20
        if height > self.save_size[1] - 20:
            width, height = self.save_size[0] - 200, 20
        return width,height

    def _save_video_thread(self):
        while self.status:
            with self.condition:
                self.condition.wait()
            while self.save_flag and self.status!=0:
                timer = time.time()
                frame_width, frame_height=self.save_size
                frame=self.frame
                if frame is None:
                    frame=np.zeros((frame_height,frame_width,3),dtype = np.uint8)
                else:
                    frame = cv2.resize(frame, (frame_width, frame_height))
                info=self.info_receiver.info.get(str(self.uav_id))
                #info={"uavId":1,"pos":{"pos1":1,"pos2":2}}
                if info is not None:
                    width,height=5,20
                    for key,value in info.items():
                        if value is None or type(value) != dict:
                            text = f"{key}:{value}"
                            width,height=self._put_text_to_frame(frame,text,width,height)
                        else:
                            for _key,_value in value.items():
                                text = f"{_key}:{_value}"
                                width, height = self._put_text_to_frame(frame, text, width, height)
                self.out.write(frame)
                while time.time()-timer<0.066:
                    time.sleep(0.006)
        self.out.release()

    def change_save_video_flag(self,flag,frame_width=640, frame_height=480):
        if flag:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            save_id=time.strftime("%Y-%m-%d-%H-%M",time.localtime())
            if not os.path.exists('./properties'):
                os.makedirs("./properties")
            self.out = cv2.VideoWriter(f'properties/{self.uav_id}_{save_id}.avi', fourcc, 15,(frame_width, frame_height))
            self.save_size=(frame_width,frame_height)
            self.save_flag=True
            with self.condition:
                self.condition.notify_all()
        else:
            self.save_flag = False
            self.out.release()


if __name__ == '__main__':
    print(os.path.exists('../properties'))
    print(time.strftime("%Y-%m-%d_%H:%M",time.localtime()))