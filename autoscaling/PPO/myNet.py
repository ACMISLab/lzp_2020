import paddle

from env import num_action, num_state
import paddle.nn.functional as F
import paddle.nn as nn
import torch

LR_v = 2e-5
LR_pi = 2e-5

class Actor(nn.Layer):
    def __init__(self):
        super(Actor, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(num_state, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
        )
        self.mu = nn.Linear(256, num_action)
        self.sigma = nn.Linear(256, num_action)
        # self.optim = torch.optim.Adam(self.parameters(), lr=LR_pi)

    def forward(self, x):
        x = self.net(x)
        mu = paddle.tanh(self.mu(x)) * 2
        sigma = F.softplus(self.sigma(x)) + 0.001
        return mu, sigma


class Critic(nn.Layer):
    def __init__(self):
        super(Critic, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
        )
        # self.optim = torch.optim.Adam(self.parameters(), lr=LR_v)

    def forward(self, x):
        x = self.net(x)
        return x
