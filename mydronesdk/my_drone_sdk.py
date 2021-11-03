import time
from functionality import CommandSender,VideoReceiverThread,InfoReceiverThread

class MyDroneSDK:
    def __init__(self,uav_id,command_sender=None,video_receiver=None):
        if command_sender is None:
            self.command_sender = CommandSender()
            self.command_sender.start()
            self.video_display_size = (384, 288)  # 640,480 *0.6
            self.video_receiver = VideoReceiverThread(8003, 1, self.video_display_size)
            self.video_receiver.start()
        else:
            self.command_sender=command_sender
            self.video_receiver=video_receiver
        self.uav_id=uav_id

    def prepare(self):
        re=self.command_sender.sendCommandWithResponse(f"setv -p True@{self.uav_id}")
        if not re:
            raise Exception("prepare error")

    def set_velocity_body(self,left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity):
        self.command_sender.sendCommand(f"setv -l {left_right_velocity} -f {for_back_velocity} "
                                        f"-u {up_down_velocity} -y {yaw_velocity}@{self.uav_id}")
        #time.sleep(args[4])

    def land(self):
        self.command_sender.sendCommandWithResponse(f"land@{self.uav_id}")

if __name__=="__main__":
    #sdk=MyDroneSDK(1)
    from mydronesdk.ddpg_yolo_control.script import script
    script(None,None)