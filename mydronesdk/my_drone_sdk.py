import time

class MyDroneSDK:
    def __init__(self,command_sender,video_receiver):
        self.command_sender=command_sender
        self.video_receiver=video_receiver

    def prepare(self):
        self.command_sender.sendCommandWithResponse("setv -p True")

    def set_velocity_body(self,*args):
        self.command_sender.sendCommand(f"setv -f {args[0]} -l {args[1]} -u {args[2]} -y {args[3]}")
        #time.sleep(args[4])

    def land(self):
        self.command_sender.sendCommandWithResponse("land")

if __name__=="__main__":
    sdk=MyDroneSDK(None)
    sdk.set_velocity_body(1,2,3)