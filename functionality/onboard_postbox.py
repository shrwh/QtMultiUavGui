import socket
from threading import Thread, Condition
import time
import json
import cv2
import sys
import numpy
import asyncio


class PrintHelper:
    def __init__(self,s):
        self.content=""
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.socket=s
    def set_print_to_content(self,flag):
        #only for getting the prints of argparse
        if flag:
            sys.stdout=self
            sys.stderr=self
        else:
            sys.stdout=self.stdout
            sys.stderr = self.stderr
    def send_content(self):
        if self.content=="":
            self.content="func succeeded."
        self.socket.sendall(self.content.encode())
        self.content=""
    def write(self,str):
        self.content += str
        self.stdout.write(str)
    def flush(self):
        self.content=""
    def __str__(self):
        return self.content+"!!!!"
    def print(self,str,send_flag=True):
        self.write(str)
        if send_flag:
            self.send_content()



class OnboardPostbox:
    def __init__(self,
                 address, video_port, info_port, command_port,
                 # con_comm:Condition,
                 # command: list, info: dict,
                 peer_addresses:tuple,peer_info_port,
                 info_sleep,
                 loop, async_object,
                 video_flip_method):
        super().__init__()
        self.address_video = (address, video_port)
        self.address_info = (address, info_port)
        self.address_command = (address, command_port)
        self.addresses_peer_info=[]
        for each in peer_addresses:
            self.addresses_peer_info.append((each,peer_info_port))
        self.port_peer_info=peer_info_port
        self.info = async_object.Info
        self.info_sleep = info_sleep
        # self.con_comm=con_comm
        # self.command = command
        self.loop = loop
        self.async_object = async_object
        self.video_flip_method=video_flip_method

    def start(self):
        self.t1 = Thread(target=self.info_sender)
        self.t2 = Thread(target=self.video_sender)
        self.t3 = Thread(target=self.command_receiver)
        self.t3.setDaemon(True)
        self.t4 = Thread(target=self.info_receiver)
        self.t4.setDaemon(True)
        self.should_continue = True
        self.t1.start()
        self.t2.start()
        self.t3.start()
        self.t4.start()
        # asyncio.ensure_future(self.command_receiver())

    def close(self):
        self.should_continue = False
        self.t2.join()
        self.t1.join()
        #self.t3.join()
        print(f"onboard_postbox id[{self.async_object.uavId}]: All ended.")

    def info_sender(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while self.should_continue:
            msg = json.dumps(self.info)
            data=msg.encode()
            s.sendto(data, self.address_info)
            for each in self.addresses_peer_info:
                s.sendto(data, each)
            time.sleep(self.info_sleep)
        s.close()
        print(f"onboard_postbox id[{self.async_object.uavId}]: info_sender ended")

    def info_receiver(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', self.port_peer_info))
        while self.should_continue:
            data, addr = s.recvfrom(1024)
            msg = data.decode()
            info = json.loads(msg)
            self.async_object.otheruav_inf[f"{info['uavId']}"]=info
        s.close()

    def command_receiver(self):
        tasks={}
        while self.should_continue:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(self.address_command)
            except Exception as e:
                s.close()
                time.sleep(0.1)
                continue
            s.sendall(str(self.info["uavId"]).encode())
            ph = PrintHelper(s)
            while self.should_continue:
                try:
                    data= s.recv(1024)
                except ConnectionResetError as e:
                    #print("ConnectionResetError")
                    s.close()
                    break
                msg = data.decode()
                command = json.loads(msg)
                print(command)
                #should get all command function but now only 'takeoff'\'stop' written by static code
                import argparse
                parser = argparse.ArgumentParser(description="params for any commands received from remote PC")
                subparsers = parser.add_subparsers()

                # 'takeoff'
                # ///////////////////////////////////////////////////////////////
                parser1 = subparsers.add_parser("takeoff", help="params for the command 'takeoff'")
                import inspect
                full_arg_spec=inspect.getfullargspec(self.async_object.controlUav)
                args_func=full_arg_spec.args
                args_func.remove("self")
                defaults=full_arg_spec.defaults
                for i in range(len(args_func)):
                    try:
                        parser1.add_argument(f'-{args_func[i][:2]}',f'--{args_func[i]}', default=defaults[i])
                    except argparse.ArgumentError as e:
                        parser1.add_argument(f'-{args_func[i][:3]}', f'--{args_func[i]}', default=defaults[i])
                def takeoff(args:argparse.Namespace):
                    delattr(args,"func")
                    print(f"onboard_postbox id[{self.async_object.uavId}]: command received:\n","'takeoff':",args.__dict__)
                    task_takeoff=tasks.get("takeoff")
                    if task_takeoff is None or task_takeoff.done():
                        #self.command.append("takeoff")
                        task = asyncio.run_coroutine_threadsafe(self.async_object.controlUav(**args.__dict__), self.loop)

                        def callback(future):
                            try:
                                result = future.result()
                                # if result is None:
                                #     result = "takeoff succeeded."
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: takeoff succeeded.")
                            except asyncio.CancelledError:
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: takeoff cancelled.")
                            except Exception as e:
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: takeoff error:\n" + str(e))
                            #self.command.remove("takeoff")
                            #tasks.pop("takeoff")

                        task.add_done_callback(callback)
                        tasks["takeoff"]=task
                    else:
                        ph.print(f"onboard_postbox id[{self.async_object.uavId}]: warning: command 'takeoff' is running.")

                parser1.set_defaults(func=takeoff)

                # 'stop'
                # ///////////////////////////////////////////////////////////////
                parser_stop = subparsers.add_parser("stop", help="params for the command 'stop'")

                def stop(args:argparse.Namespace):
                    # stop all for now
                    for task in tasks.values():
                        task.cancel()
                    #tasks.clear()
                    ph.print(f"onboard_postbox id[{self.async_object.uavId}]: all tasks stopped.")

                parser_stop.set_defaults(func=stop)

                # 'setv'
                # ///////////////////////////////////////////////////////////////
                parser_setv = subparsers.add_parser("setv", help="params for the command 'set_velocity'")
                parser_setv.add_argument(f'-f', f'--forward_backward', default=0,type=float)
                parser_setv.add_argument(f'-l', f'--left_right', default=0,type=float)
                parser_setv.add_argument(f'-u', f'--up_down', default=0,type=float)
                parser_setv.add_argument(f'-y', f'--yaw', default=0,type=float)
                parser_setv.add_argument(f'-p', f'--prepare', default=False,type=bool)

                def setv(args: argparse.Namespace):
                    delattr(args, "func")
                    from mavsdk.offboard import VelocityBodyYawspeed
                    async def temp(args):
                        if args.prepare:
                            await self.async_object._prepare_takeoff()
                        await self.async_object.drone.offboard.set_velocity_body(VelocityBodyYawspeed(
                            args.forward_backward, args.left_right, -args.up_down, args.yaw))

                    task = asyncio.run_coroutine_threadsafe(temp(args), self.loop)
                    task_setv = tasks.get("setv")
                    if task_setv is None or task_setv.done():

                        def callback(future):
                            try:
                                result = future.result()
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: setv succeeded.")
                            except asyncio.CancelledError:
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: setv cancelled.")
                            except Exception as e:
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: setv error:\n" + str(e))
                            # self.command.remove("takeoff")
                            # tasks.pop("test")

                        task.add_done_callback(callback)
                        tasks["setv"] = task
                    else:
                        ph.print(f"onboard_postbox id[{self.async_object.uavId}]: warning: command 'setv' is running.")

                parser_setv.set_defaults(func=setv)

                # 'land'
                # ///////////////////////////////////////////////////////////////
                parser_land = subparsers.add_parser("land", help="params for the command 'land'")

                def land(args: argparse.Namespace):
                    delattr(args, "func")
                    task = asyncio.run_coroutine_threadsafe(self.async_object._my_landing(), self.loop)
                    task_land = tasks.get("setv")
                    if task_land is None or task_land.done():

                        def callback(future):
                            try:
                                result = future.result()
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: land succeeded.")
                            except asyncio.CancelledError:
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: land cancelled.")
                            except Exception as e:
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: land error:\n" + str(e))

                        task.add_done_callback(callback)
                        tasks["land"] = task
                    else:
                        ph.print(f"onboard_postbox id[{self.async_object.uavId}]: warning: command 'land' is running.")

                parser_land.set_defaults(func=land)

                # 'test'
                # ///////////////////////////////////////////////////////////////
                parser_test = subparsers.add_parser("test", help="params for the command 'test'")

                def test(args:argparse.Namespace):
                    delattr(args, "func")
                    #task = asyncio.run_coroutine_threadsafe(self.async_object.test(**args.__dict__), self.loop)
                    from mavsdk.offboard import VelocityBodyYawspeed
                    async def temp():
                        await self.async_object.drone.offboard.set_velocity_body(VelocityBodyYawspeed(
                        0, 0, 0, 0))
                    task = asyncio.run_coroutine_threadsafe(temp(),self.loop)
                    task_test = tasks.get("test")
                    if task_test:
                        print(task_test.done(), task_test.cancelled())
                    if task_test is None or task_test.done():

                        def callback(future):
                            try:
                                result=future.result()
                                if result is None:
                                    result="test succeeded."
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: future-done result:\n"+result)
                            except asyncio.CancelledError:
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: test cancelled.")
                            except Exception as e:
                                ph.print(f"onboard_postbox id[{self.async_object.uavId}]: test error:\n"+str(e))
                            # self.command.remove("takeoff")
                            #tasks.pop("test")

                        task.add_done_callback(callback)
                        tasks["test"] = task
                    else:
                        ph.print(f"onboard_postbox id[{self.async_object.uavId}]: warning: command 'test' is running.")

                parser_test.set_defaults(func=test)

                # parse and func
                # ///////////////////////////////////////////////////////////////
                try:
                    ph.set_print_to_content(True)
                    args=parser.parse_args(command)
                except BaseException as e:
                    #print("parse:",e.args)
                    ph.set_print_to_content(False)
                    ph.send_content()
                else:
                    ph.set_print_to_content(False)
                    args.func(args)


                # if command[0] == "takeoff" and "takeoff" not in self.command:
                #
                #     self.command.append(command[0])
                #     task=asyncio.run_coroutine_threadsafe(self.async_object.controlUav(*command[1:]),self.loop)
                #     def callback(future):
                #         try:
                #             print(f"onboard_postbox id[{self.async_object.uavId}]: future-done result\n",future.result())
                #         except Exception as e:
                #             print(f"onboard_postbox id[{self.async_object.uavId}]: future-raised exception\n",e)
                #     task.add_done_callback(callback)
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        print(f"onboard_postbox id[{self.async_object.uavId}]: command_receiver ended")

    def video_sender(self):
        # address = ('192.168.1.103', 8002)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.setblocking(False)

        capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=self.video_flip_method), cv2.CAP_GSTREAMER)
        if not capture.isOpened():
            print("打开摄像头失败")
            sys.exit(-1)
        ret, frame = capture.read()
        # 压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 20]

        while ret and self.should_continue:
            timer1 = time.time()
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            # 建立矩阵
            data = numpy.array(imgencode)
            # 将numpy矩阵转换成字符形式，以便在网络中传输
            stringData = data.tostring()
            s.sendto(stringData, self.address_video)
            ret, frame = capture.read()
            timer8 = time.time()
            while timer8 - timer1 < 0.0666:
                time.sleep(0.006)
                timer8 = time.time()
            # if timer8 - timer1 > 0.09:
            #     print("local", timer8 - timer1)
        capture.release()
        cv2.destroyAllWindows()
        s.close()
        print(f"onboard_postbox id[{self.async_object.uavId}]: video_sender ended")


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


if __name__ == "__main__":
    info1 = {"uavId": 1, "pos": {"longitude": 1, "latitude": 2, "ab_altitude": 3, "rlt_altitude": 4},"angle":10}
    box = OnboardPostbox(address="127.0.0.1", video_port=8003, info_port=8001, command_port=8888,
                         info_sleep=0.1, loop=None, async_object=None,peer_addresses=("127.0.0.1",),peer_info_port=8889,
                         video_flip_method=0)
    box.start()
    info2 = {"uavId": 2, "pos": {"longitude": 1, "latitude": 2, "ab_altitude": 3, "rlt_altitude": 4},"angle":None}
    box = OnboardPostbox(address="127.0.0.1", video_port=8004, info_port=8002, command_port=8889,
                        info_sleep=0.1, loop=None, async_object=None,peer_addresses=("127.0.0.1",),peer_info_port=8889,
                         video_flip_method=0)
    box.start()
    try:
        x=10
        while True:
            info1["pos"]["longitude"]=x
            #info2["pos"]["longitude"] = x-10
            x+=1
            time.sleep(1)
            info1["angle"]=info1["angle"]+2
    except KeyboardInterrupt:
        box.close()
        #pass
    finally:
        #box.close()
        pass



