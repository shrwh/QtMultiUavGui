import pygame
import cv2
import numpy as np
import time
import os
from mydronesdk.ddpg_yolo_control.yolo.utils import get_yolo_boxes
from mydronesdk.ddpg_yolo_control.yolo.bbox import draw_boxes
from keras.models import load_model
import json
from mydronesdk.ddpg_yolo_control.rl_airsim.gym_airsim_env import AirsimEnv
from mydronesdk.ddpg_yolo_control.rl_airsim.ddpg_train import RLAgent
import threading
import copy
from mydronesdk.my_drone_sdk import MyDroneSDK
import sys

# Speed of the drone
S = 0.4
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.
FPS = 15

###############################
#   Set some parameter
###############################
net_h, net_w = 416, 416  # 416, 416  # a multiple of 32, the smaller the faster
obj_thresh, nms_thresh = 0.6, 0.45
frame_height, frame_width, frame_channel = 720, 960, 3
z_lower, z_upper = 0, 1200
step_duration = 2

save_id = 1
vel_scale = 0.55
left_right_velocity_rate = 1  # 0.8
forward_backward_velocity_rate = 1
up_down_velocity_rate = 0.6
yaw_velocity_rate = 70

class FrontEnd:
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations (yaw)
            - W and S: Up and down.
    """

    def __init__(self,drone):
        # Init pygame
        pygame.init()

        # Creat pygame window
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode([frame_width, frame_height])

        # Init Tello object that interacts with the Tello drone
        self.drone = drone

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        # self.speed = 10

        self.send_rc_control = False
        self.should_stop=False
        self.manual_flag=True

        # create update timer
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

    def run(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f'D:\PYCHARMWORKSPACE\PyOneDark_Qt_Widgets_Modern_GUI-master\property/output{save_id}.avi', fourcc, FPS, (frame_width, frame_height))

        frame_read = self.drone.video_receiver

        while not self.should_stop:

            for event in pygame.event.get():
                if self.manual_flag:
                    if event.type == pygame.USEREVENT + 1:
                        self.update()
                    elif event.type == pygame.QUIT:
                        self.should_stop = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.should_stop = True
                        elif event.key == pygame.K_SPACE:
                            self.manual_flag=False
                        else:
                            self.keydown(event.key)
                    elif event.type == pygame.KEYUP:
                        self.keyup(event.key)
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.manual_flag = True

            if frame_read.status!=2:
                continue

            self.screen.fill([0, 0, 0])

            try:
                frame = cv2.resize(frame_read.frame,(frame_width,frame_height))
            except BaseException as e:
                continue
            out.write(frame)
            # text = "Battery: {}%".format(self.tello.get_battery())
            # cv2.putText(frame, text, (5, 720 - 5),
            #     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)

            frame = pygame.surfarray.make_surface(frame)

            self.screen.blit(frame, (0, 0))
            pygame.display.update()

            time.sleep(1 / FPS)

        # Call it always before finishing. To deallocate resources.
        out.release()
        pygame.quit()
        print("ddpg_yolo_control_script ended.")

    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP:  # set forward velocity
            self.for_back_velocity = S
        elif key == pygame.K_DOWN:  # set backward velocity
            self.for_back_velocity = -S
        elif key == pygame.K_LEFT:  # set left velocity
            self.left_right_velocity = -S
        elif key == pygame.K_RIGHT:  # set right velocity
            self.left_right_velocity = S
        elif key == pygame.K_w:  # set up velocity
            self.up_down_velocity = S
        elif key == pygame.K_s:  # set down velocity
            self.up_down_velocity = -S
        elif key == pygame.K_a:  # set yaw counter clockwise velocity
            self.yaw_velocity = -S*50
        elif key == pygame.K_d:  # set yaw clockwise velocity
            self.yaw_velocity = S*50
        # elif key == pygame.K_h:  # set yaw clockwise velocity
        #     print(self.tello.get_height())

    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP or key == pygame.K_DOWN:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_t:  # takeoff
            self.drone.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:  # land
            self.drone.land()
            self.send_rc_control = False
        elif key == pygame.K_p:  # prepare
            try:
                self.drone.prepare()
            except Exception as e:
                pass
            #else:
            self.send_rc_control = True

    def update(self):
        """ Update routine. Send velocities to Tello."""
        if self.send_rc_control:
            # self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity,
            #     self.up_down_velocity, self.yaw_velocity)
            self.drone.set_velocity_body(self.left_right_velocity, self.for_back_velocity,
                self.up_down_velocity, self.yaw_velocity)


def box_thread(drone,front_end,target_id=14):
    """box detection thread function. This function receives a frame every 200ms and return corresponding box and actions in a queue
    input : frame_glob (416x416)
    output : put box and actions in queue.
    """

    # setting config path for YOLO config
    config_path = 'D:\PYCHARMWORKSPACE\PyOneDark_Qt_Widgets_Modern_GUI-master\mydronesdk/ddpg_yolo_control/yolo_assets/config_voc.json'
    with open(config_path) as config_buffer:
        config = json.load(config_buffer)

    ###############################
    #   Load the model for YOLO detection
    ###############################
    os.environ['CUDA_VISIBLE_DEVICES'] = config['train']['gpus']
    infer_model = load_model(config['train']['saved_weights_name'])

    ###############################
    #   Load the model for RL agent
    ###############################
    env = AirsimEnv(False, sim_flag=False)
    agent = RLAgent(env)
    ENV_NAME = 'drone'
    agent.agent.load_weights('D:/PYCHARMWORKSPACE/PyOneDark_Qt_Widgets_Modern_GUI-master/mydronesdk/ddpg_yolo_control/rl_airsim/ddpg_{}_weights_5.h5f'.format(ENV_NAME))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(f'D:\PYCHARMWORKSPACE\PyOneDark_Qt_Widgets_Modern_GUI-master\property/output_box{save_id}.avi', fourcc, 2, (frame_width, frame_height))
    print('YOLO detection ok')

    while not front_end.should_stop:
        try:
            frame_glob=drone.video_receiver.frame
            if frame_glob is not None:
                frame = cv2.resize(frame_glob,(frame_width,frame_height))
                # call prection function of YOLO algorithm to return boxes
                boxes = \
                    get_yolo_boxes(infer_model, [frame],
                                   net_h, net_w, config['model']['anchors'], obj_thresh, nms_thresh)[0]
                # print('YOLO detection ok')
                state = np.zeros(5)
                for box in boxes:
                    if box.get_label() == target_id:  # filter on the person class (ID =14)
                        print("reward:", env.reward([box.xmin, box.xmax, box.ymin, box.ymax]))
                        state = np.array([box.xmin / frame_width, box.xmax / frame_width,
                                          box.ymin / frame_height, box.ymax / frame_height, 0])
                        draw_boxes(frame, [box], config['model']['labels'], obj_thresh)
                        break
                # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # frame = np.rot90(frame)
                # frame = np.flipud(frame)
                cv2.imshow("show", frame)
                cv2.waitKey(1)
                # state[4]=(tello.get_height()-z_lower) / (z_upper - z_lower)
                state[4] = (300 - z_lower) / (z_upper - z_lower)
                action = agent.agent.my_forward_for_test(state) * vel_scale
                #print("action:", action)
                left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity = action
                # tello.send_rc_control(round(-left_right_velocity*left_right_velocity_rate),
                #                       round(forward_backward_velocity*forward_backward_velocity_rate),
                #                       round(up_down_velocity *up_down_velocity_rate),
                #                       round(yaw_velocity / vel_scale * yaw_velocity_rate))
                if not front_end.manual_flag:
                    drone.set_velocity_body(-left_right_velocity*left_right_velocity_rate,
                                            forward_backward_velocity*forward_backward_velocity_rate,
                                            up_down_velocity *up_down_velocity_rate,
                                            yaw_velocity / vel_scale * yaw_velocity_rate)
                timer = time.time()
                text = f"{-left_right_velocity * left_right_velocity_rate}, " \
                       f"{forward_backward_velocity * forward_backward_velocity_rate}, " \
                       f"{up_down_velocity * up_down_velocity_rate}, {yaw_velocity / vel_scale * yaw_velocity_rate}"
                cv2.putText(frame, text, (50, 720 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                out.write(frame)
                while time.time() - timer < step_duration and not front_end.manual_flag:
                    time.sleep(1 / FPS)
                # tello.send_rc_control(0, 0, 0, 0)
                if not front_end.manual_flag:
                    drone.set_velocity_body(0,0,0,0)
            #frame_glob = None
        except Exception as e:
            # print("Exception: "+e.__str__())
            pass
    out.release()
    print("box_thread ended.")


def script(command_sender,video_receiver):
    drone=MyDroneSDK("1",command_sender, video_receiver)
    frontend = FrontEnd(drone)

    thread_box = threading.Thread(target=box_thread, args=(drone,frontend,1))
    # thread_box.setDaemon(True)
    thread_box.start()
    # time.sleep(5)

    # run frontend
    frontend.run()

if __name__=="__main__":
    pass