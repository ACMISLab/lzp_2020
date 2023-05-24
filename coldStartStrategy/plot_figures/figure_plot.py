# -*- coding: utf-8 -*-
import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import random
import seaborn as sns
func_invoc_frequency = pd.read_csv("../dataSet/func_invoc_frequency_per_app_new.csv").iloc[:, 1]

cnt = 0
for i in range(0, len(func_invoc_frequency)):
    if func_invoc_frequency[i] < 0.3:
        cnt += 1

print(cnt/len(func_invoc_frequency))

matplotlib.rcParams['font.sans-serif'] = ['SimHei']   # 用黑体显示中文
# matplotlib.rcParams['axes.unicode_minus'] = False     # 正常显示负号
plt.figure(figsize=(13, 5), dpi=600)
fig, arx = plt.subplots(nrows=2, ncols=1, figsize=(12,6), tight_layout=True)
arx[0].hist(func_invoc_frequency, bins=40, density=1, color=sns.xkcd_rgb["denim blue"], )
num=0
# for i in func_invoc_frequency:
#     if i >= 0.9 and i <=1:
#         num +=1
# print(num/len(func_invoc_frequency))

# arx[1].tick_params(labelsize=20)
# #设置坐标轴名称
# arx[1].set_xlabel('Function ID', fontsize=26)
# arx[1].set_ylabel('Invocation\nFrequency', fontsize=26)
# x = range(0, len(func_invoc_frequency))
# plt.plot(x, func_invoc_frequency, color="blue")
# arx[1].bar(xx, d, color=[0.7, 0.81, 0.91])

arx[0].tick_params(labelsize=20)
#设置坐标轴名称
arx[0].set_xlabel('Invocation Frequency', fontsize=26)
arx[0].set_ylabel('Probability\nDensity', fontsize=26)

#设置坐标轴刻度
my_x_ticks = np.arange(0, 1.1, 0.2)
my_y_ticks = np.arange(0, 15, 2.5)
arx[0].set_xticks(my_x_ticks)
arx[0].set_yticks(my_y_ticks)

# my_x_ticks_1 = np.arange(1, 20, 1)
# my_y_ticks_1 = np.arange(0, 0.5, 0.1)
# arx[1].set_xticks(my_x_ticks_1)
# arx[1].set_yticks(my_y_ticks_1)

# arx[1].grid()
arx[0].grid()
plt.show()
# plt.savefig('func_invoc.png', dpi=600, bbox_inches='tight')

