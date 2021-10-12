#can add image info:
import json
import datetime
#import bluetooth
import yaml
import logging
import cv2
import numpy
import time
import asyncio
import socket
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityNedYaw)

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

def logger_config(log_path, logging_name):
    '''
    配置log
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :return:
    '''
    '''
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    '''
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger

class BluetoothConnection:
    def __init__(self):
        # 是否找到到设备
        self.find = False
        # 附近蓝牙设备
        self.nearby_devices = None

    def find_nearby_devices(self, logger):
        logger.info("Detecting nearby Bluetooth devices...")
        # 可传参数 duration--持续时间 lookup-name=true 显示设备名
        # 大概查询10s左右
        # 循环查找次数
        loop_num = 3
        i = 0
        try:
            self.nearby_devices = bluetooth.discover_devices(lookup_names=True, duration=5)
            while self.nearby_devices.__len__() == 0 and i < loop_num:
                self.nearby_devices = bluetooth.discover_devices(lookup_names=True, duration=5)
                if self.nearby_devices.__len__() > 0:
                    break
                i = i + 1
                time.sleep(2)
                logger.warning("No Bluetooth device around here! trying again {}...".format(str(i)))
            if not self.nearby_devices:
                logger.error("There's no Bluetooth device around here. Program stop!")
            else:
                logger.info("{} nearby Bluetooth device(s) has(have) been found:".format(self.nearby_devices.__len__()),
                      self.nearby_devices) # 附近所有可连的蓝牙设备s
        except Exception as e:
            logger.error("There's no Bluetooth device around here. Program stop(2)!")

    def find_target_device(self, target_name, target_address, logger):
        self.find_nearby_devices(logger=logger)
        if self.nearby_devices:
            for addr, name in self.nearby_devices:
                if target_name == name and target_address == addr:
                    logger.info("Found target bluetooth device with address:{} name:{}".format(target_address, target_name))
                    self.find = True
                    break
            if not self.find:
                logger.warning("could not find target bluetooth device nearby. "
                      "Please turn on the Bluetooth of the target device.")

class UAV(BluetoothConnection):
        def __init__(self,uavId,address, port):
                super(UAV,self).__init__()
                self.uavId = uavId
                self.pos = None
                self.vel = None
                self.Info = {"uavId": uavId, "pos":None, "vel": None, "angle":None,"command":None}
                self.sendtoAddress = (address,port)
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.frame  = None
                self.encode_param = None
                self.command=[]
                
        def run_bluetooth(self):
                logger = logger_config(log_path='log.txt', logging_name='水平仪参数记录')
                yamlPath = 'config.yaml'
                f = open(yamlPath, 'r', encoding='utf-8')
                data = yaml.load(f)
                target_name = data.get('ble').get('name')
                target_address = data.get('ble').get('address')
                  # target_name = "BT04-A"
                 # target_address = "98:DA:20:02:F9:3C"
                self.connect_target_device(target_name=target_name, target_address=target_address, logger=logger)

        async def connect_target_device(self, target_name, target_address, logger):
                self.find_target_device(target_name=target_name, target_address=target_address, logger=logger)
                if self.find:
                        logger.info("Ready to connect")
                        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                try:
                        sock.connect((target_address, 1))
                        logger.info("Connection successful. Now ready to get the data")
                        data_dtr = ""
                        while True:
                        # sock.send("123124\n")
                                data = sock.recv(1024)
                                data_dtr += data.decode()
                                if '\n' in self.data.decode():
                                        # data_dtr[:-2] 截断"\t\n",只输出数据
                                        logger.info(datetime.datetime.now().strftime("%H:%M:%S") + "->" + data_dtr[:-2])
                                        data_dtr = ""
                                self.Info["angle"] = data

                except Exception as e:
                        logger.error("connection fail\n", e)
                        sock.close()

        async def run(self):

                # capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
                # if not capture.isOpened():
                #         print("打开摄像头失败")
                # _, self.frame = capture.read()
                # #压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
                # self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]

                self.drone = System()
                await self.drone.connect(system_address="serial:///com7")
                # print("Waiting for drone to connect...")
                # async for state in self.drone.core.connection_state():
                #         if state.is_connected:
                #                 print(f"Drone discovered!")
                #                 break

                # print("-- Arming")
                # await self.drone.action.arm()
                # #await self.drone.action.reboot()
                # print("-- Setting initial setpoint")
                # await self.drone.offboard.set_velocity_ned(
                #         VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
                #
                # print("-- Starting offboard")
                # try:
                #         await self.drone.offboard.start()
                # except OffboardError as error:
                #         print(f"Starting offboard mode failed with error code: \
                #         {error._result.result}")
                #         print("-- Disarming")
                #         await self.drone.action.disarm()
                #         return
                asyncio.ensure_future(self.GetPos())
                asyncio.ensure_future(self.GetVel())
                asyncio.ensure_future(self.print_imu())
                #asyncio.ensure_future(self.controlUav())


                # await self.set_vel_ned(0,0,-1,0)
                #
                # print("-- Wait for a bit")
                # await self.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
                # await asyncio.sleep(8)

                #print("-- Stopping offboard")
                # try:
                #         await self.drone.offboard.stop()
                # except OffboardError as error:
                #         print(f"Stopping offboard mode failed with error code: \
                #         {error._result.result}")

        async def print_imu(self):
            async for imu in self.drone.telemetry.imu():
                print(f"Position: {imu.angular_velocity_frd}")
                temp=imu.angular_velocity_frd
                self.Info["agl_vel"] = {"forward": temp.forward_rad_s,
                                        "right": temp.right_rad_s,
                                        "up": temp.down_rad_s}
                print('sendInfo')
                self.Info["uavId"]=1
                msg = json.dumps(self.Info)
                self.socket.sendto(msg.encode(), self.sendtoAddress)
                self.Info["uavId"] = 2
                msg = json.dumps(self.Info)
                self.socket.sendto(msg.encode(), ("127.0.0.1",8002))
                await asyncio.sleep(1)
                
        async def GetPos(self):
            async for pos in self.drone.telemetry.position():
                self.pos = pos
                self.Info["pos"] = {"longitude":pos.longitude_deg,
                                    "latitude":pos.latitude_deg,
                                    "ab_altitude":pos.absolute_altitude_m,
                                    "rlt_altitude":pos.relative_altitude_m}

            await asyncio.sleep(0.25)


        async def GetVel(self):
            async for vel in self.drone.telemetry.velocity_ned():
                self.vel = vel
                self.Info["vel"] = {"vel_n":vel.north_m_s,
                                    "vel_e":vel.east_m_s,
                                    "vel_up":-vel.down_m_s}

        async def get_position_ned(self):
            async for position_velocity in self.drone.telemetry.position_velocity_ned():
                print(f"position_velocity_ned: {position_velocity}")
                temp=position_velocity.position
                self.Info["pos_ned"]={"pos_n":temp.north_m,"pos_e":temp.east_m,"pos_d":temp.down_m}

        
        async def set_vel_ned(self, north_v, east_v, down_v, yaw):
                await self.drone.offboard.set_velocity_ned(VelocityNedYaw(north_v, east_v, down_v, yaw))
                #await self.send()
                await asyncio.sleep(5)
        
        def getImage(self,):
                _, imgencode = cv2.imencode('.jpg', self.frame, self.encode_param)
        #建立矩阵
                data = numpy.array(imgencode)
         #将numpy矩阵转换成字符形式，以便在网络中传输
                stringData = data.tostring()
                return stringData

        async def getOtherInfo(self):
                othermsg, _= self.socket.recvfrom(1024)
                msg = othermsg.decode()
                #otherInfo = json.loads(msg) #the type of Info is dict
                #print(otherInfo)
                #return otherInfo
                self.Info["command"]=msg
        async def controlUav(self):
            # while True:
            #     if "takeoff" in self.command:
            #         print("takeoff start")
            #         await asyncio.sleep(3)
            #         print("takeoff end")
            #         self.command.remove("takeoff")
            #     else:
            #         await asyncio.sleep(0.05)
            print("takeoff start")
            await asyncio.sleep(3)
            print("takeoff end")
            self.command.remove("takeoff")

if __name__=='__main__':
        a = UAV(1,"127.0.0.1",8001)
        '''info = a.SetToString()
        print(info)
        infotype = info.split(" ",1)[0]
        print(infotype)
        infoc = info.split(" ",1)[1]
        num = re.findall(r"\d+\.?\d*",infoc)'''

        from functionality.onboard_postbox import OnboardPostbox



        asyncio.ensure_future(a.run())

        # Runs the event loop until the program is canceled with e.g. CTRL-C
        loop=asyncio.get_event_loop()
        info = {"uavId": 1, "pos": {"longitude": 1, "latitude": 2, "ab_altitude": 3, "rlt_altitude": 4}}
        box = OnboardPostbox(address="127.0.0.1", video_port=8002, info_port=8001, host_port=8888,
                             info=info, info_sleep=0.1,async_object=a,loop=loop,command=a.command)

        loop.run_forever()
        



