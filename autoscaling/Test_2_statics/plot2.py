# -*- coding: utf-8 -*-

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

PPO_thr_path = "./fig_data/PPO_throughput.csv"
PPO_l90_path = "./fig_data/PPO_L_P90.csv"
PPO_avg_path = "./fig_data/PPO_L_avg.csv"

QL_thr_path = "./fig_data/QL_throughput.csv"
QL_l90_path = "./fig_data/QL_lat_p90.csv"
QL_avg_path = "./fig_data/QL_lat_avg.csv"

KPA_path = "D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\main\\java\\qlearning_report\\floating-training\\qlearning-res-1.csv"
KPA_throughput = list(pd.read_csv(KPA_path, header=None).iloc[:, 1])[0:40]

KPA_L_avg = list(pd.read_csv(KPA_path, header=None).iloc[:, 2])[0:40]
KPA_L_p90 = list(pd.read_csv(KPA_path, header=None).iloc[:, 3])[0:40]

limit = 0
PPO_throughput = list(pd.read_csv(PPO_thr_path, header=None).iloc[:, 1])[limit:]
PPO_L_P90 = list(pd.read_csv(PPO_l90_path, header=None).iloc[:, 1])[limit:]
PPO_L_avg = list(pd.read_csv(PPO_avg_path, header=None).iloc[:, 1])[limit:]

print(PPO_L_P90)

QL_throughput = list(pd.read_csv(QL_thr_path, header=None).iloc[:, 1])[limit:]
QL_L_P90 = list(pd.read_csv(QL_l90_path, header=None).iloc[:, 1])[limit:]
QL_L_avg = list(pd.read_csv(QL_avg_path, header=None).iloc[:, 1])[limit:]

PPO_L_P90 = [x * 1000 for x in PPO_L_P90]
PPO_L_avg = [x * 1000 for x in PPO_L_avg]

thr_list = [np.mean(PPO_throughput), np.mean(QL_throughput), np.mean(KPA_throughput)]
avg_list = [np.mean(PPO_L_avg), np.mean(QL_L_avg), np.mean(KPA_L_avg)]
p90_list = [np.mean(PPO_L_P90), np.mean(QL_L_P90), np.mean(KPA_L_p90)]

# print(PPO_list, QL_list)

fig, ax1 = plt.subplots(figsize=(15, 8), dpi=100)
ccur = 1000
# x = np.arange(0, ccur, 1)
name_list = ["PPO", "Q-Learning", "KPA"]
x = list(range(len(name_list)))

total_width, n = 0.3, 2
width = total_width / n

line1 = ax1.bar(x, thr_list, width=width, label="Throughput", color=sns.xkcd_rgb["denim blue"])
for a, b in zip(x, thr_list):  # 柱子上的数字显示
    plt.text(a, b, '%.0f' % b, ha='center', va='bottom', fontsize=12)

for i in range(len(x)):
    x[i] = x[i] + width+0.02

# 吞吐量
# line1, = ax1.plot(x, final_throughput, color=sns.xkcd_rgb["pale red"], )
# p1 = ax1.scatter(x, reward, color=sns.xkcd_rgb["pale red"],  label='reward')

# 时延
ax2 = ax1.twinx()
line2 = ax2.bar(x, avg_list, width=width, label="Latency_avg", tick_label=name_list, color=sns.xkcd_rgb["grey green"])
for a, b in zip(x, avg_list):  # 柱子上的数字显示
    plt.text(a, b, '%.0f' % b, ha='center', va='bottom', fontsize=12)

for i in range(len(x)):
    x[i] = x[i] + width+0.02

line3 = ax2.bar(x, p90_list, width=width, label="Latency_P90", color=sns.xkcd_rgb["pale red"])
for a, b in zip(x, p90_list):  # 柱子上的数字显示
    plt.text(a, b, '%.0f' % b, ha='center', va='bottom', fontsize=12)

# line2, = ax2.plot(x, final_latency_P90, color=sns.xkcd_rgb["denim blue"], linestyle='-', )
# line3, = ax2.plot(x, final_latency_avg, color=sns.xkcd_rgb["medium green"], linestyle='-', )

# p3 = ax2.scatter(x, final_latency_P90, color=sns.xkcd_rgb["denim blue"], marker='s', s=30, label='latency_P90')
# line2, = ax2.plot(x, target, color=sns.xkcd_rgb["denim blue"], )
# p2 = ax2.scatter(x, target, color=sns.xkcd_rgb["denim blue"], label='target')
# line3, = ax2.plot(x, target, color=sns.xkcd_rgb["denim blue"], )
# line4, = ax2.plot(x, util, color='blue', )

# 坐标轴设置
# ax1.set_xticks(range(0, ccur + 1, 50))

ax1.tick_params(axis="x", labelsize=18)
ax1.tick_params(axis="y", labelsize=14)
ax2.tick_params(axis="y", labelsize=14)
# ax1.set_yticks(size=16)
# ax2.set_yticks(size=16)
ax1.set_xlim()
ax1.set_ylim([0, 250])
ax2.set_ylim([0, 700])

# ax1.set_xlabel("Episode", fontsize=20)
# ax1.set_ylabel("Reward", fontsize=20)
ax1.set_ylabel("Throughput (rps)", fontsize=20)
ax2.set_ylabel("Latency(ms)", fontsize=20)

# 双Y轴标签颜色设置
# ax1.yaxis.label.set_color(line1.get_color())
# ax2.yaxis.label.set_color(line2.get_color())
# #
# # # 双Y轴刻度颜色设置
# ax1.tick_params(axis='y', colors=line1.get_color())
# ax2.tick_params(axis='y', colors=line2.get_color())

plt.grid()
plt.legend(handles=[line1, line2, line3], loc=0,
           fontsize=16)  # 显示图例
# plt.legend(loc="upper left")  # 图例
plt.show()
