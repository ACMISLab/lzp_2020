# -*- coding: utf-8 -*-

from collections import namedtuple
import gym
from autoScaleEnv import myEnv


# Parameters
env_name = 'MountainCar-v0'
gamma = 0.99
render = False
seed = 1
log_interval = 10

# env = gym.make(env_name).unwrapped
env = myEnv()
num_state = env.observation_space.shape[0]
num_action = env.action_space.shape[0]

# env.seed(seed)
Transition = namedtuple('Transition', ['state', 'action', 'action_prob', 'reward', 'next_state'])