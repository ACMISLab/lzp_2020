# -*- coding: utf-8 -*-
import random

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from figPlot import min_max_range


def smooth(old_data, weight):
    new_data = []
    last = old_data[0]

    for point in old_data:
        smoothed_val = last * weight + (1 - weight) * point
        new_data.append(smoothed_val)
        last = smoothed_val
    return new_data


PPO_rew_path = "./fig_data/PPO_reward_6.csv"
PPO_thr_path = "./fig_data/PPO_throughput.csv"
PPO_l90_path = "./fig_data/PPO_L_P90.csv"
PPO_avg_path = "./fig_data/PPO_L_avg.csv"

QL_rew_path = "./fig_data/QL_reward.csv"
QL_thr_path = "./fig_data/QL_throughput.csv"
QL_l90_path = "./fig_data/QL_lat_p90.csv"
QL_avg_path = "./fig_data/QL_lat_avg.csv"

fig, ax1 = plt.subplots(figsize=(15, 8), dpi=100)

# reportData = pd.read_csv(reportPath, header=None)


PPO_reward = list(pd.read_csv(PPO_rew_path, header=None).iloc[:, 1])
PPO_throughput = list(pd.read_csv(PPO_thr_path, header=None).iloc[:,1])
PPO_L_P90 = list(pd.read_csv(PPO_l90_path, header=None).iloc[:,1])
PPO_L_avg = list(pd.read_csv(PPO_avg_path, header=None).iloc[:,1])

# PPO_reward = []
# for i in range(0,len(PPO_throughput)):
#     PPO_reward.append(PPO_throughput[i]/(0.8*PPO_L_avg[i]+0.2*PPO_L_P90[i]))


QL_reward = list(pd.read_csv(QL_rew_path, header=None).iloc[:, 1])
QL_throughput = list(pd.read_csv(QL_thr_path, header=None).iloc[:,1])
QL_L_P90 = list(pd.read_csv(QL_l90_path, header=None).iloc[:,1])
QL_L_avg = list(pd.read_csv(QL_avg_path, header=None).iloc[:,1])
QL_L_avg = [x / 1000 for x in QL_L_avg]
QL_L_P90 = [x / 1000 for x in QL_L_P90]

# QL_reward = []
# for i in range(0,len(QL_throughput)):
#     QL_reward.append(QL_throughput[i]/(0.8*QL_L_avg[i]+0.2*QL_L_P90[i]))


PPO_reward_s = smooth(PPO_reward, 0.75)
QL_reward_s = smooth(QL_reward, 0.75)
PPO_throughput_s = smooth(PPO_throughput, 0.75)
QL_throughput_s = smooth(QL_throughput, 0.75)
PPO_L_P90_s = smooth(PPO_L_P90, 0.75)
QL_L_P90_s = smooth(QL_L_P90, 0.75)
PPO_L_avg_s = smooth(PPO_L_avg, 0.75)
QL_L_avg_s = smooth(QL_L_avg, 0.75)

ccur = 1000


x = np.arange(0, ccur, 1)


# 吞吐量
line2, = ax1.plot(x, QL_L_P90_s, color=sns.xkcd_rgb["denim blue"], )
line1, = ax1.plot(x, PPO_L_P90_s, color=sns.xkcd_rgb["pale red"], )
line4, = ax1.plot(x, QL_L_P90, color=sns.xkcd_rgb["denim blue"], alpha=0.25)
line3, = ax1.plot(x, PPO_L_P90, color=sns.xkcd_rgb["pale red"], alpha=0.25)

# p1 = ax1.scatter(x, reward, color=sns.xkcd_rgb["pale red"],  label='reward')

# 时延
# ax2 = ax1.twinx()
# line2, = ax2.plot(x, final_latency_P90, color=sns.xkcd_rgb["denim blue"], linestyle='-',)
# line3, = ax2.plot(x, final_latency_avg, color=sns.xkcd_rgb["medium green"], linestyle='-',)

# p3 = ax2.scatter(x, final_latency_P90, color=sns.xkcd_rgb["denim blue"], marker='s', s=30, label='latency_P90')
# line2, = ax2.plot(x, target, color=sns.xkcd_rgb["denim blue"], )
# p2 = ax2.scatter(x, target, color=sns.xkcd_rgb["denim blue"], label='target')
# line3, = ax2.plot(x, target, color=sns.xkcd_rgb["denim blue"], )
# line4, = ax2.plot(x, util, color='blue', )

# 坐标轴设置
ax1.set_xticks(range(0, ccur+1, 50))
# ax1.set_xlim(fontsize=15)
# ax1.set_ylim([0, 100])
ax1.set_ylim([0, 2])
# ax2.set_ylim([0, 4])

ax1.set_xlabel("Timestamp", fontsize=20)
ax1.set_ylabel("Reward", fontsize=20)
# ax1.set_ylabel("Throughput (rps)", fontsize=20)
# ax2.set_ylabel("Latency (s)", fontsize=20)

# 双Y轴标签颜色设置
# ax1.yaxis.label.set_color(line1.get_color())
# ax2.yaxis.label.set_color(line2.get_color())
#
# # 双Y轴刻度颜色设置
# ax1.tick_params(axis='y', colors=line1.get_color())
# ax2.tick_params(axis='y', colors=line2.get_color())

plt.grid()
plt.legend(handles=[line1, line2], labels=['PPO', 'QL'], loc = 0, fontsize = 20) #显示图例
# plt.legend(loc="upper left")  # 图例
plt.show()
