from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input, Concatenate, Lambda
from keras.optimizers import Adam
from keras.initializers import RandomUniform
from rl.agents import DDPGAgent
from rl.memory import SequentialMemory
from rl.random import OrnsteinUhlenbeckProcess
from mydronesdk.ddpg_yolo_control.rl_airsim.gym_airsim_env import AirsimEnv


class RLAgent:

    def __init__(self, env):
        self.env = env
        # np.random.seed(123)
        # self.env.seed(123)
        assert len(self.env.action_space.shape) == 1
        nb_actions = self.env.action_space.shape[0]

        # Next, we build a very simple model.
        self.actor = Sequential()
        self.actor.add(Flatten(input_shape=(3,) + self.env.observation_space.shape))
        self.actor.add(Dense(128))
        self.actor.add(Activation('relu'))
        self.actor.add(Dense(64))
        self.actor.add(Activation('relu'))
        self.actor.add(Dense(32))
        self.actor.add(Activation('relu'))
        self.actor.add(Dense(nb_actions, activation='tanh', kernel_initializer=RandomUniform(minval=-0.001, maxval=0.001)))
        # self.actor.add(Lambda(lambda x: x * 5))
        print(self.actor.summary())

        action_input = Input(shape=(nb_actions,), name='action_input')
        observation_input = Input(shape=(3,) + self.env.observation_space.shape, name='observation_input')
        flattened_observation = Flatten()(observation_input)
        x = Concatenate()([action_input, flattened_observation])
        x = Dense(256)(x)
        x = Activation('relu')(x)
        x = Dense(128)(x)
        x = Activation('relu')(x)
        x = Dense(64)(x)
        x = Activation('relu')(x)
        x = Dense(1)(x)
        x = Activation('linear')(x)
        critic = Model(inputs=[action_input, observation_input], outputs=x)
        print(critic.summary())

        # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
        # even the metrics!
        memory = SequentialMemory(limit=100000, window_length=3)
        random_process = OrnsteinUhlenbeckProcess(size=nb_actions, theta=.15, mu=0.,sigma=.3,sigma_min=0.05,n_steps_annealing=50000)
        self.agent = DDPGAgent(nb_actions=nb_actions, actor=self.actor, critic=critic, critic_action_input=action_input,
                               memory=memory, nb_steps_warmup_critic=1000, nb_steps_warmup_actor=1000,
                               random_process=random_process, gamma=.99, target_model_update=1e-3,train_interval=8,batch_size=32)
        self.agent.compile(Adam(lr=5e-4), metrics=['mae'])

if __name__ == "__main__":
    env = AirsimEnv(True,evaluate_flag=False)
    agent = RLAgent(env)
    ENV_NAME = 'drone'
    agent.agent.load_weights('ddpg_{}_weights_5.h5f'.format(ENV_NAME))
    # agent.agent.fit(env, nb_steps=50000, verbose=1,log_interval=500,nb_max_episode_steps=100)

    #After training is done, we save the final weights.
    # agent.agent.save_weights('ddpg_{}_weights.h5f'.format(ENV_NAME), overwrite=True)
    # agent.agent.load_weights('ddpg_{}_weights.h5f'.format(ENV_NAME))
    # Finally, evaluate our algorithm for 5 episodes.
    agent.agent.test(env, nb_episodes=1, nb_max_episode_steps=30)