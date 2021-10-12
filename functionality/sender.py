import socket
import cv2
import numpy
import time
import sys
 
def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=640,
    display_height=480,
    framerate=15,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )
 



def SendVideo():
    #建立sock连接
    #address要连接的服务器IP地址和端口号
    address = ('192.168.1.103', 8002)
    # try:
    #     #建立socket对象，参数意义见https://blog.csdn.net/rebelqsp/article/details/22109925
    #     #socket.AF_INET：服务器之间网络通信 
    #     #socket.SOCK_STREAM：流式socket , for TCP
    #     sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #     #开启连接
    #     sock.connect(address)
    # except socket.error as msg:
    #     print(msg)
    #     sys.exit(1)
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #s.setblocking(False)

    #建立图像读取对象
    #capture = cv2.VideoCapture(0)
    #读取一帧图像，读取成功:ret=1 frame=读取到的一帧图像；读取失败:ret=0
    #ret, frame = capture.read()
    capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    if not capture.isOpened():
        print("打开摄像头失败")
        sys.exit(-1)
    ret, frame = capture.read()
    #压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),20]

    # result, imgencode = cv2.imencode('.jpg', frame, encode_param)

    # data = numpy.array(imgencode)

    # stringData = data.tostring()

    # sock.send(str.encode(str(len(stringData)).ljust(16)))

    # ret, frame = capture.read()

    while ret:
        timer1=time.time()
        #停止0.1S 防止发送过快服务的处理不过来，如果服务端的处理很多，那么应该加大这个值
        #time.sleep(0.01)
        #cv2.imencode将图片格式转换(编码)成流数据，赋值到内存缓存中;主要用于图像数据格式的压缩，方便网络传输
        #'.jpg'表示将图片按照jpg格式编码。
        #timer2=time.time()
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        #建立矩阵
        data = numpy.array(imgencode)
        #将numpy矩阵转换成字符形式，以便在网络中传输
        stringData = data.tostring()
        
        #timer3=time.time()
        #先发送要发送的数据的长度
        #ljust() 方法返回一个原字符串左对齐,并使用空格填充至指定长度的新字符串
        #s.sendto(str.encode(str(len(stringData)).ljust(16)),address);
        #print(str.encode(str(len(stringData)).ljust(16)))
        timer4=time.time()
        #发送数据
        #print(len(stringData))
        s.sendto(stringData,address)
        
        timer5=time.time()
        #读取服务器返回值
        #receive = sock.recv(1024)
        #if len(receive):print(str(receive,encoding='utf-8'))
        #timer6=time.time()
        #读取下一帧图片
        ret, frame = capture.read()
        # timer7=time.time()
        # cv2.imshow("sender",numpy.ones((100,100)))
        # if cv2.waitKey(1) == 27:
        #     break
        timer8=time.time()
        while timer8-timer1<0.0666:
            time.sleep(0.006)
            timer8=time.time()
        if timer8-timer1>0.09:
            print("local",timer5-timer4,timer8-timer1)
    capture.release()
    cv2.destroyAllWindows()
    s.close()

def func_a(con):
    print("func_a")
    with con:
        con.wait()
    print("func_a ending")

def func_b(con):
    print("func_b")
    with con:
        con.wait()
    print("func_b ending")

SHOULD_CONTINUE=True

def func_c():
    x=0
    while SHOULD_CONTINUE:
        x+=1
        print(x)
        time.sleep(1)

def func_d(l):
    l[0]=1
    print(l)
    l[1]=2

if __name__ == '__main__':
    from threading import Thread
    from functionality import *
    t1=CommandSender()
    t1.start()
    #Thread(target=func_c).start()




