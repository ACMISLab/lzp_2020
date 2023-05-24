import torch
import torch.nn as nn
import torch.nn.functional as F

from main import max_action, max_action_1, min_action_1, state_number, A_LR, action_number, min_action, METHOD, \
    A_UPDATE_STEPS, C_LR, C_UPDATE_STEPS

'''由于PPO也是基于A-C框架，所以我把PPO的编写分为两部分，PPO的第一部分 Actor'''
'''PPO的第一步  编写A-C框架的网络，先编写actor部分的actor网络，actor的网络有新与老两个网络'''


class ActorNet(nn.Module):
    def __init__(self, inp, outp):
        super(ActorNet, self).__init__()
        self.in_to_y1 = nn.Linear(inp, 64)
        self.in_to_y1.weight.data.normal_(0, 0.1)

        self.mean_out = nn.Linear(64, outp)
        self.mean_out.weight.data.normal_(0, 0.1)

        self.std_out = nn.Linear(64, outp)
        self.std_out.weight.data.normal_(0, 0.1)

    '''生成均值与标准差，PPO必须这样做，一定要生成分布（所以需要mean与std），不然后续学习策略里的公式写不了，DDPG是可以不用生成概率分布的'''

    def forward(self, input_state):
        print("input_state ", input_state)
        input_state = self.in_to_y1(input_state)
        input_state = F.relu(input_state)
        # print("input_state_after_relu ", input_state)

        mean = torch.tanh(self.mean_out(input_state))  # 输出概率分布的均值mean
        # mean = max_action * torch.tanh(self.out(inputstate))  # 输出概率分布的均值mean
        std = F.softplus(self.std_out(input_state))  # softplus 激活函数的值域>0

        print("mean is", mean, " std is ", std)

        return mean, std


'''再编写critic部分的critic网络，PPO的critic部分与AC算法的critic部分是一样，PPO不一样的地方只在actor部分'''


class CriticNet(nn.Module):
    def __init__(self, input, output):
        super(CriticNet, self).__init__()
        self.in_to_y1 = nn.Linear(input, 64)
        self.in_to_y1.weight.data.normal_(0, 0.1)
        self.out = nn.Linear(64, output)
        self.out.weight.data.normal_(0, 0.1)

    def forward(self, inputstate):
        inputstate = self.in_to_y1(inputstate)
        inputstate = F.relu(inputstate)
        Q = self.out(inputstate)
        return Q


class Actor():
    def __init__(self):
        self.old_pi, self.new_pi = ActorNet(state_number, action_number), ActorNet(state_number,
                                                                                   action_number)  # 这只是均值mean
        self.optimizer = torch.optim.Adam(self.new_pi.parameters(), lr=A_LR, eps=1e-5)

    '''第二步 编写根据状态选择动作的函数'''

    def choose_action(self, s):
        inputstate = torch.FloatTensor(s)
        mean, std = self.old_pi(inputstate)

        # 对均值进行范围缩放，两个维度范围不一样
        # mean[0] = (mean[0]+1) * ((max_action - min_action) / 2)
        # mean[1] = (mean[1]+1) * ((max_action_1 - min_action_1) / 2)
        # mean[0] = min_action + (max_action-min_action)*(mean[0]+1)/2
        # mean[1] = min_action_1 + (max_action_1 - min_action_1) * (mean[1] + 1) / 2
        print("now mean ", mean)
        # std[0] = std[0] * max_action
        # std[1] = std[1] * max_action_1

        std = std * torch.eye(2)  # 为了适配 MultivariateNormal
        # print("mean {}, std {}".format(mean, std))
        # dist = torch.distributions.Normal(mean, std)
        dist = torch.distributions.MultivariateNormal(mean, std)

        action = dist.sample()
        action_logprob = dist.log_prob(action)

        print("ori_act ", action)
        action[0] = min_action + (max_action - min_action) * (action[0] + 1) / 2
        action[1] = min_action_1 + (max_action_1 - min_action_1) * (action[1] + 1) / 2
        print("adj_act ", action)
        action[0] = torch.clamp(action[0], min_action, max_action)
        action[1] = torch.clamp(action[1], min_action_1, max_action_1)


        return action.detach().numpy(), action_logprob.detach().numpy()

    '''第四步  actor网络有两个策略（更新old策略）————————把new策略的参数赋给old策略'''

    def update_oldpi(self):
        self.old_pi.load_state_dict(self.new_pi.state_dict())

    '''第六步 编写actor网络的学习函数，采用PPO2，即OpenAI推出的clip形式公式'''

    def learn(self, bs, ba, adv, bap):
        bs = torch.FloatTensor(bs)
        ba = torch.FloatTensor(ba)
        adv = torch.FloatTensor(adv)
        bap = torch.FloatTensor(bap)
        print("bs ", bs)
        print("ba ", ba)
        print("adv ", adv)
        print("bap ", bap)

        for _ in range(A_UPDATE_STEPS):

            mean, std = self.new_pi(bs)
            std = std * torch.eye(2)  # 为了适配 MultivariateNormal

            dist_new = torch.distributions.MultivariateNormal(mean, std)
            # dist_new = torch.distributions.Normal(mean, std)
            action_new_logprob = dist_new.log_prob(ba)
            print("action_new_logprob ", action_new_logprob)
            ratio = torch.exp(action_new_logprob - bap.detach())
            print("ratio", ratio)
            surr1 = ratio * adv
            surr2 = torch.clamp(ratio, 1 - METHOD['epsilon'], 1 + METHOD['epsilon']) * adv
            print("surr1 ", surr1)
            print("surr2 ", surr2)
            # loss = - torch.min(surr1, surr2)
            loss = -surr2
            print("loss0 ", loss)
            loss = torch.mean(loss, dim=1)
            # loss = loss.mean(dim=0)
            print("loss1 ", loss)
            self.optimizer.zero_grad()
            loss.sum().backward()

            nn.utils.clip_grad_norm_(self.new_pi.parameters(), 0.5)
            self.optimizer.step()


class Critic():
    def __init__(self):
        self.critic_v = CriticNet(state_number, 1)  # 改网络输入状态，生成一个Q值
        self.optimizer = torch.optim.Adam(self.critic_v.parameters(), lr=C_LR, eps=1e-5)
        self.lossfunc = nn.MSELoss()

    '''第三步  编写评定动作价值的函数'''

    def get_v(self, s):
        inputstate = torch.FloatTensor(s)
        return self.critic_v(inputstate)

    '''第五步  计算优势——————advantage，后面发现第五步计算出来的adv可以与第七步合为一体，所以这里的代码注释了，但是，计算优势依然算是可以单独拎出来的一个步骤'''
    # def get_adv(self,bs,br):
    #     reality_v=torch.FloatTensor(br)
    #     v=self.get_v(bs)
    #     adv=(reality_v-v).detach()
    #     return adv
    '''第七步  编写actor-critic的critic部分的learn函数，td-error的计算代码（V现实减去V估计就是td-error）'''

    def learn(self, bs, br):
        bs = torch.FloatTensor(bs)
        reality_v = torch.FloatTensor(br)
        for _ in range(C_UPDATE_STEPS):
            v = self.get_v(bs)
            td_e = self.lossfunc(reality_v, v)
            self.optimizer.zero_grad()
            td_e.backward()
            nn.utils.clip_grad_norm_(self.critic_v.parameters(), 0.5)
            self.optimizer.step()
        return (reality_v - v).detach()
