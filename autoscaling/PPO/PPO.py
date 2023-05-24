# -*- coding: utf-8 -*-
import logging

from myNet import Actor, Critic
from env import env, gamma, render, Transition
from dataset import RandomDataset

from itertools import count
import os, time

import torch

import paddle
import paddle.nn as nn
import paddle.nn.functional as F
import paddle.optimizer as optim
from paddle.distribution import Normal, Categorical, Multinomial
from paddle.io import RandomSampler, BatchSampler, Dataset
from visualdl import LogWriter


class PPO():
    clip_param = 0.2
    max_grad_norm = 0.5
    ppo_update_time = 10
    buffer_capacity = 8000
    batch_size = 64

    ## 初始化参数
    def __init__(self):
        super(PPO, self).__init__()
        self.actor_net = Actor()
        self.critic_net = Critic()
        self.buffer = []
        self.counter = 0
        self.training_step = 0
        self.writer = LogWriter('./exp')

        clip = nn.ClipGradByNorm(self.max_grad_norm)
        self.actor_optimizer = optim.Adam(parameters=self.actor_net.parameters(), learning_rate=1e-3, grad_clip=clip)
        self.critic_net_optimizer = optim.Adam(parameters=self.critic_net.parameters(), learning_rate=3e-3,
                                               grad_clip=clip)

        if not os.path.exists('./param'):
            os.makedirs('./param/net_param')
            os.makedirs('./param/img')

    # 选择动作
    def select_action_bak(self, state):
        state = paddle.to_tensor(state, dtype="float32").unsqueeze(0)
        with paddle.no_grad():
             action_prob, v2 = self.actor_net(state)
        print("v1 ", action_prob, "v2 ", v2)
        dist = Categorical(action_prob)
        action = dist.sample([1]).squeeze(0)
        action = action.cpu().numpy()[0]
        print("action is ", action)
        return action, action_prob[:, int(action)].numpy()[0]

    # 选择动作
    def select_action(self, state):
        state = paddle.to_tensor(state, dtype="float32").unsqueeze(0)
        with paddle.no_grad():
            mu, sigma = self.actor_net(state)

        # mu = mu[:, int(1)].numpy()[0]
        # sigma = sigma[:, int(1)].numpy()[0]
        print("mu ", mu, "sigma ", sigma)


        # dist = Categorical(action_prob)
        dist = paddle.distribution.Normal(mu, sigma)
        action = dist.sample(shape=[1, 1])
        # action = dist.sample([1]).squeeze(0)
        # action = action.cpu().numpy()[0]
        print("action is ", action)
        return action, mu[:, int(action)].numpy()[0]

    # 评估值
    def get_value(self, state):
        state = paddle.to_tensor(state)
        with paddle.no_grad():
            value = self.critic_net(state)
        return value.numpy()

    def save_param(self):
        paddle.save(self.actor_net.state_dict(), './param/net_param/actor_net' + str(time.time())[:10] + '.param')
        paddle.save(self.critic_net.state_dict(), './param/net_param/critic_net' + str(time.time())[:10] + '.param')

    def store_transition(self, transition):
        self.buffer.append(transition)
        print("trans is ", transition)
        self.counter += 1

    def update(self, i_ep):
        state = paddle.to_tensor([t.state for t in self.buffer], dtype="float32")
        action = paddle.to_tensor([t.action for t in self.buffer], dtype="int64").reshape([-1, 1])
        reward = [t.reward for t in self.buffer]
        # update: don't need next_state

        old_action_prob = paddle.to_tensor([t.action_prob for t in self.buffer], dtype="float32").reshape([-1, 1])

        R = 0
        Gt = []
        for r in reward[::-1]:
            R = r + gamma * R
            Gt.insert(0, R)
        Gt = paddle.to_tensor(Gt, dtype="float32")
        # print("The agent is updateing....")
        for i in range(self.ppo_update_time):
            for index in BatchSampler(sampler=RandomSampler(RandomDataset(len(self.buffer))),
                                      batch_size=self.batch_size, drop_last=False):
                if self.training_step % 1000 == 0:
                    print('I_ep {} ，train {} times'.format(i_ep, self.training_step))
                    self.save_param()

                index = paddle.to_tensor(index)
                Gt_index = paddle.index_select(x=Gt, index=index).reshape([-1, 1])

                # V = self.critic_net(state[index])
                V = self.critic_net(paddle.index_select(state, index))

                delta = Gt_index - V
                advantage = delta.detach()
                # epoch iteration, PPO core!!!
                action_prob = self.actor_net(paddle.index_select(state, index))  # new policy
                action_prob = paddle.concat([action_prob[i][int(paddle.index_select(action, index)[i])] for i in
                                             range(len(action_prob))]).reshape([-1, 1])

                ratio = (action_prob / paddle.index_select(old_action_prob, index))
                surr1 = ratio * advantage
                surr2 = paddle.clip(ratio, 1 - self.clip_param, 1 + self.clip_param) * advantage

                # update actor network
                surr = paddle.concat([surr1, surr2], 1)
                action_loss = -paddle.min(surr, 1).mean()  # MAX->MIN desent
                self.writer.add_scalar('loss/action_loss', action_loss, self.training_step)
                print('loss/action_loss', action_loss, self.training_step)
                self.actor_optimizer.clear_grad()
                action_loss.backward()
                self.actor_optimizer.step()

                # update critic network
                value_loss = F.mse_loss(Gt_index, V)
                self.writer.add_scalar('loss/value_loss', value_loss, self.training_step)
                print('loss/value_loss', value_loss, self.training_step)
                self.critic_net_optimizer.clear_grad()
                value_loss.backward()
                self.critic_net_optimizer.step()
                self.training_step += 1

        del self.buffer[:]  # clear experience


def main():
    agent = PPO()
    for i_epoch in range(1000):
        state = env.reset()
        # if render: env.render()

        for t in count():
            action, action_prob = agent.select_action(state)
            print("action_prob is ", action_prob)
            next_state, reward, done, _ = env.step(action)
            trans = Transition(state, action, action_prob, reward, next_state)
            if render: env.render()
            agent.store_transition(trans)
            state = next_state

            if done:
                if len(agent.buffer) >= agent.batch_size: agent.update(i_epoch)
                agent.writer.add_scalar('Steptime/steptime', t, i_epoch)
                # print("Number of steps to achieve the goal:{} , Steptime:{}".format(t,i_epoch))
                break


if __name__ == '__main__':
    main()
    print("end")
