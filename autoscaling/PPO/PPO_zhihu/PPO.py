import jpype
import numpy as np
import torch
from matplotlib import pyplot as plt
from main import EP_MAX, EP_LEN, env, Switch, GAMMA, BATCH
from net import Actor, Critic
import pandas as pd


if Switch == 0:
    print('PPO2训练中...')
    actor = Actor()
    critic = Critic()
    # checkpoint_aa = torch.load("./res/1671108823340/PPO2_model_actor.pth")
    # actor.old_pi.load_state_dict(checkpoint_aa['net'])
    # checkpoint_cc = torch.load("./res/1671108823340/PPO2_model_critic.pth")
    # critic.critic_v.load_state_dict(checkpoint_cc['net'])

    all_ep_r = []  # 每轮ep reward
    all_ep_target = []  # 每轮ep target
    all_ep_util = []  # 每轮ep utilization


    for episode in range(EP_MAX):
        observation = env.reset()  # 环境重置
        buffer_s, buffer_a, buffer_r, buffer_a_logp = [], [], [], []
        reward_totle = 0

        for timestep in range(EP_LEN):
            action, action_logprob = actor.choose_action(observation)
            print("action ", action, ", action_logprob ", action_logprob)
            observation_, reward, done, info = env.myStep(action, 10, episode)

            all_ep_target.append(action[0])
            all_ep_util.append(action[1])
            buffer_s.append(observation)
            buffer_a.append(action)
            buffer_r.append((reward + 8) / 8)  # normalize reward, find to be useful
            buffer_a_logp.append(action_logprob)

            observation = observation_
            reward_totle += reward
            # reward = (reward - reward.mean()) / (reward.std() + 1e-5)

            # PPO 更新
            if (timestep + 1) % BATCH == 0 or timestep == EP_LEN - 1:
                v_observation_ = critic.get_v(observation_)
                discounted_r = []
                for reward in buffer_r[::-1]:
                    v_observation_ = reward + GAMMA * v_observation_
                    discounted_r.append(v_observation_.detach().numpy())
                discounted_r.reverse()
                bs, ba, br, bap = np.vstack(buffer_s), np.vstack(buffer_a), np.array(discounted_r), np.vstack(
                    buffer_a_logp)
                buffer_s, buffer_a, buffer_r, buffer_a_logp = [], [], [], []
                advantage = critic.learn(bs, br)            # critic部分更新
                actor.learn(bs, ba, advantage, bap)         # actor部分更新
                actor.update_oldpi()                        # pi-new的参数赋给pi-old
                # critic.learn(bs,br)

        if episode == 0:
            all_ep_r.append(reward_totle)
        else:
            all_ep_r.append(all_ep_r[-1] * 0.9 + reward_totle * 0.1)

        print("Ep: {} | rewards: {}".format(episode, reward_totle))
        pd_res = pd.DataFrame([[all_ep_target], [all_ep_util], [all_ep_r]])
        pd_res.to_csv(env.resPath+"train_info.csv", header=False, index=False)

        # 保存神经网络参数
        if episode % 5 == 0:  # 保存神经网络参数
            save_data = {'net': actor.old_pi.state_dict(), 'opt': actor.optimizer.state_dict(), 'i': episode}
            torch.save(save_data, env.resPath + "PPO2_model_actor.pth")
            save_data = {'net': critic.critic_v.state_dict(), 'opt': critic.optimizer.state_dict(), 'i': episode}
            torch.save(save_data, env.resPath + "PPO2_model_critic.pth")

    env.close()
    jpype.shutdownJVM()

    plt.plot(np.arange(len(all_ep_r)), all_ep_r)
    plt.xlabel('Episode')
    plt.ylabel('Moving averaged episode reward')
    plt.show()

else:
    print('PPO2测试中...')
    aa = Actor()
    cc = Critic()
    checkpoint_aa = torch.load(".\model\PPO2_model_actor.pth")
    aa.old_pi.load_state_dict(checkpoint_aa['net'])
    checkpoint_cc = torch.load(".\model\PPO2_model_critic.pth")
    cc.critic_v.load_state_dict(checkpoint_cc['net'])
    for j in range(10):
        state = env.reset()
        total_rewards = 0
        for timestep in range(EP_LEN):
            env.render()
            action, action_logprob = aa.choose_action(state)
            new_state, reward, done, info = env.step(action)  # 执行动作
            total_rewards += reward
            state = new_state
        print("Score：", total_rewards)
    env.close()
