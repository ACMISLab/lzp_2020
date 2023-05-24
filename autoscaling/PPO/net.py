# -*- coding: utf-8 -*-

from env import num_action, num_state
import paddle.nn.functional as F
import paddle.nn as nn


class Actor(nn.Layer):
    def __init__(self):
        super(Actor, self).__init__()
        self.fc1 = nn.Linear(num_state, 128)
        self.action_head = nn.Linear(128, num_action)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        action_prob = F.softmax(self.action_head(x), axis=1)
        return action_prob


class Critic(nn.Layer):
    def __init__(self):
        super(Critic, self).__init__()
        self.fc1 = nn.Linear(num_state, 128)
        self.state_value = nn.Linear(128, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        value = self.state_value(x)
        return value