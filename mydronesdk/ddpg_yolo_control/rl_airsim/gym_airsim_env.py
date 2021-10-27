import numpy as np
import airsim
import gym
from gym import spaces
import cv2
import os
import json
from mydronesdk.ddpg_yolo_control.yolo.utils import get_yolo_boxes
from mydronesdk.ddpg_yolo_control.yolo.bbox import draw_boxes
from keras.models import load_model
import time
import math
import matplotlib.pyplot as plt
import random
#from gym.utils import seeding

###############################
#   Set some parameter
###############################
net_h, net_w = 416,416 # 416, 416  # a multiple of 32, the smaller the faster
obj_thresh, nms_thresh = 0.1, 0.45
frame_height,frame_width,frame_channel=720,960,3
max_dist=((frame_height//2)**2+(frame_width//2)**2)**0.5
distance_lower=2
z_lower,z_upper=0,-20
alpha_dist,alpha_area,alpha_y=0.4,0.6,0.15
beta_collision,beta_tooclose,beta_reward=10,10,10
evaluate_save_id=6
sim_speed_scale=1
vel_scale=5

class AirsimEnv(gym.Env):
    # metadata = {
    #     'render.modes': ['human', 'rgb_array'],
    #     'video.frames_per_second': 30
    # }

    def __init__(self,render_flag=False,evaluate_cycle=500,evaluate_steps=500,evaluate_flag=False,sim_flag=True):

        if sim_flag:
            # setting config path for YOLO config
            config_path = '../yolo_assets/config_voc.json'
            with open(config_path) as config_buffer:
                self.config = json.load(config_buffer)

            ###############################
            #   Load the model for YOLO detection
            ###############################
            os.environ['CUDA_VISIBLE_DEVICES'] = self.config['train']['gpus']
            self.infer_model = load_model(self.config['train']['saved_weights_name'])

        self.min_action = -1
        self.max_action = 1
        self.min_position = 0
        self.max_positionx = frame_width
        self.max_positiony = frame_height
        self.step_duration=2
        self.center_position=np.array([frame_width//2, frame_height//2])
        self.step_counter=0
        self.evaluate_cycle=evaluate_cycle
        self.evaluate_steps=evaluate_steps
        self.evaluate_counter=self.evaluate_steps+1
        self.evaluate_rewards=[]
        self.evaluate_flag=evaluate_flag
        self.save_path="result"

        self.action_space = spaces.Box(low=self.min_action, high=self.max_action,
                                       shape=(4,), dtype=np.float32)
        print(self.action_space.sample())

        # observation_space:[box.x_min,box.x_max,box.y_min,box.y_max,drone_height]
        self.low_state = np.array([self.min_position]*4+[z_lower])
        self.high_state = np.array([self.max_positionx/frame_width]*2
                                   +[self.max_positiony/frame_height]*2+[1])
        self.observation_space = spaces.Box(low=self.low_state, high=self.high_state,
                                            dtype=np.float32)
        print(self.observation_space.sample())

        self.render_flag=render_flag
        self.state=np.zeros(5)

        if sim_flag:
            #self.seed()
            self.client = airsim.MultirotorClient()
            self.client.confirmConnection()
            self.reset()

    # def seed(self, seed=None):
    #     self.np_random, seed = seeding.np_random(seed)
    #     return [seed]

    def step(self, action):
        done = False
        left_right_velocity, forward_backward_velocity, up_down_velocity,yaw_velocity=action*vel_scale
        reward_collision=0
        reward_tooclose=0
        reward_z=0
        self.moveByRCAsync(
            float(left_right_velocity), float(forward_backward_velocity),
            float(up_down_velocity)/2.5,float(yaw_velocity)*10,self.step_duration)
        timer=time.time()
        while time.time()-timer<self.step_duration/sim_speed_scale:
            target_pst=self.client.simGetObjectPose("ThirdPersonCharacter_5").position
            drone_pst=self.client.simGetVehiclePose().position
            distance=target_pst.distance_to(drone_pst)
            collided=self.client.simGetCollisionInfo().has_collided
            if collided:
                reward_collision=-self.client.getMultirotorState().kinematics_estimated\
                    .linear_velocity.get_length()/7.3*beta_collision
                done = True
            if distance<distance_lower:
                reward_tooclose=-(distance_lower-distance)/distance_lower*beta_collision
                done=True
            if done:
                break
            time.sleep(0.1/sim_speed_scale)
        if not done and (drone_pst.z_val>z_lower or drone_pst.z_val<z_upper):
            done=True
            if drone_pst.z_val>z_lower:
                reward_z=(z_lower-drone_pst.z_val)/0.578*beta_reward
            else:
                reward_z = (drone_pst.z_val-z_upper) /4 * beta_reward
        # print(done,timer-time.time(),drone_pst.z_val)
        while self.client.getMultirotorState().kinematics_estimated.linear_velocity.get_length()>1:
            self.client.moveByVelocityAsync(0,0,0,0.25).join()
        # print(self.client.getMultirotorState().kinematics_estimated.linear_velocity)
        frame_obs = self.get_frame_obs()
        if not done:
            reward=self.reward(frame_obs)
        else:
            reward=reward_collision+reward_tooclose+reward_z
        # print(reward_collision,reward_tooclose,reward)
        if self.evaluate_flag:
            self._evaluate(reward)
        self.state=self.get_current_state(frame_obs)
        print("\naction:",action*vel_scale,"\nreward: ",reward,reward_collision,reward_tooclose,reward_z)
        # print(self.state)

        return self.state, reward, done, {}

    def reset(self):
        self.client.reset()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)
        self.client.moveByVelocityAsync(0,0,-3,2).join()
        self.state = self.get_current_state()
        return np.array(self.state)

    def render(self, mode='human'):
        pass

    def close(self):
        pass

    def _get_frame(self):
        count=0
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])[0]
        while response.height == 0:  # 避免airsim.simGetImages的未知错误(image的高宽都是0)
            response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])[0]
            count+=1
            if count==5:
                return False,None
        # get numpy array
        img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)

        # reshape array to 3 channel image array H X W X 3
        img_rgb = img1d.reshape((response.height, response.width, 3))

        return True, img_rgb

    def get_current_state(self,frame_obs=None):
        if frame_obs is None:
            frame_obs=self.get_frame_obs()
        return np.array([frame_obs[0]/frame_width,frame_obs[1]/frame_width,
                         frame_obs[2]/frame_height,frame_obs[3]/frame_height,
                         (z_lower-self.client.simGetVehiclePose().position.z_val)/(z_lower-z_upper)])

    def get_frame_obs(self):
        success,frame=self._get_frame()
        state=np.zeros(4)
        if not success:
            if self.render_flag:
                cv2.imshow("show", np.zeros((frame_height,frame_width,frame_channel)))
            return state
        # timer=time.time()
        box_list = \
            get_yolo_boxes(self.infer_model, [frame],
                           net_h, net_w, self.config['model']['anchors'], obj_thresh, nms_thresh)[0]
        # print("inner",time.time()-timer)
        for box in box_list:
            if box.get_label() == 14:  # filter on the person class (ID =14)
                if self.render_flag:
                    draw_boxes(frame, [box], self.config['model']['labels'], obj_thresh)
                state=np.array([box.xmin,box.xmax,box.ymin,box.ymax])
                break
        if self.render_flag:
            cv2.imshow("show", frame)
            key = cv2.waitKey(1)  ##等待键盘促发的时间，返回值为ASCII码（无按下键盘时为-1）
            if key == 27:  ##27表示按下Esc
                self.render_flag=False
        return state

    def _convert_vel_to_body_frame(self, left_right_velocity, forward_backward_velocity,up_down_velocity):
        pose = self.client.simGetVehiclePose()
        yaw = airsim.to_eularian_angles(pose.orientation)[2]
        vx = math.sin(yaw) * left_right_velocity + math.cos(yaw) * forward_backward_velocity
        vy = -math.cos(yaw) * left_right_velocity + math.sin(yaw) * forward_backward_velocity
        if left_right_velocity**2+forward_backward_velocity**2+up_down_velocity**2 < 1:
            return vx, vy,-up_down_velocity-0.092/self.step_duration
        return vx, vy,-up_down_velocity

    def moveByRCAsync(self, left_right_velocity, forward_backward_velocity, up_down_velocity,
                      yaw_velocity, duration):
        degree_rate = airsim.YawMode(True, yaw_velocity)
        vx, vy ,vz= self._convert_vel_to_body_frame(left_right_velocity, forward_backward_velocity,up_down_velocity)
        return self.client.moveByVelocityAsync(vx, vy, vz, duration,yaw_mode=degree_rate)

    def reward(self,frame_obs,print_flag=False):
        # ymin>50 ymax<720
        # dist<100
        # 40>area_p >5
        xmin,xmax,ymin,ymax=frame_obs
        if xmin==xmax==ymin==ymax==0:
            return 0
        # print(xmin,xmax,ymin,ymax)
        box_x = int((xmax - xmin) / 2) + xmin
        box_y = int((ymax - ymin) / 2) + ymin
        dist = np.sqrt((np.square(np.array([box_x, box_y]) - self.center_position)).sum())
        reward_dist = math.exp(-dist/max_dist)-0.3678
        area = (xmax - xmin) * (ymax - ymin)
        area_p = area / frame_height/frame_width * 100
        reward_area=math.exp((15-area_p)/85)-0.3678 if area_p>15 else math.exp((area_p-15)/15)-0.3678
        reward_y=0
        if ymin>50:
            reward_y=0.35
        # if ymax<720:
        #     reward_y=-(ymax-720)/50*100
        if print_flag:
            print(f"dist: {box_x,box_y}, area_p: {area_p}, ymin: {ymin}")
            # print("reward",reward_dist , reward_area , reward_y)
            # print(alpha_dist*reward_dist,alpha_area*reward_area,alpha_y*reward_y)
        return alpha_dist*reward_dist+alpha_area*reward_area+alpha_y*reward_y

    def _evaluate(self,reward):
        if self.step_counter%self.evaluate_cycle==0:
            self.sum_rewards = reward
            self.evaluate_counter = 1
        elif self.evaluate_counter<self.evaluate_steps:
            self.sum_rewards+=reward
            self.evaluate_counter+=1
            if self.evaluate_counter==self.evaluate_steps:
                evaluate_reward=self.sum_rewards/self.evaluate_steps
                print('Evaluated reward is ', evaluate_reward)
                self.evaluate_rewards.append(evaluate_reward)
                self.evaluate_counter=self.evaluate_steps+1
                #self.plt(num)
                # plt.figure()
                # plt.axis([0, 10000, 0, 100])
                # plt.cla()

                plt.plot(range(len(self.evaluate_rewards)), self.evaluate_rewards)
                plt.xlabel('step*{}'.format(self.evaluate_cycle))
                plt.ylabel('evaluated_reward')

                plt.savefig(self.save_path + '/plt_{}.png'.format(evaluate_save_id), format='png')
                np.save(self.save_path + '/evaluate_rewards_{}'.format(evaluate_save_id), self.evaluate_rewards)
        self.step_counter+=1


if __name__=="__main__":
    env=AirsimEnv(True)
    timer=time.time()
    while(True):
        _,_,done,_=env.step(np.array([0,0,0,2]))
        # env.client.hoverAsync().join()
        print(time.time()-timer)
        print(env.client.simGetVehiclePose().position.z_val)
        timer=time.time()
    # env.client.moveToPositionAsync(0,0,-20,5).join()
    # print(env.client.simGetVehiclePose().position.z_val)
    # pos = env.client.simGetObjectPose("ThirdPersonCharacter_5")
    # pos.position.x_val = random.randrange(-2500, 1500)
    # pos.position.y_val = random.randrange(-2000, 2000)
    # env.client.simSetObjectPose("ThirdPersonCharacter_5", pos)

    # env.step([0,20,-8,0])
    # env.get_current_state()

    # client = airsim.MultirotorClient()
    # client.confirmConnection()
    # client.enableApiControl(True)
    # client.armDisarm(True)
    # # client.moveByVelocityAsync(1,0,1,3).join()
    # target_pst=client.simGetObjectPose("ThirdPersonCharacter_5").position
    # drone_pst=client.simGetVehiclePose().position
    # distance=target_pst.distance_to(drone_pst)
    # print(distance)
    # print([0] * 4 + [100])
    # print([frame_width/frame_width*7.5]*2
    #                                +[frame_height/frame_height*7.5]*2+[-z_upper/(z_lower-z_upper)*7.5])