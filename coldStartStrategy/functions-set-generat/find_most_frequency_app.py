# -*- coding: utf-8 -*-
'''
 app的调用次数，寻找高频app
 5442  个app
 0.22419049188432066  的占比
 0.8199885275256394  的贡献

 涉及 20215 个 func

'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

raw = pd.read_csv("./dataSet/appData_invoc_times.csv")
freq = raw['frequency']
hmap = raw['hashApp']
# for ind, row in raw.iterrows():
#     list = row['invoc_time_series'][1: -1].split(", ")
#     # print(list)
#     freq.append(len(list))
#     hmap.append(row['HashApp'])
# res = pd.DataFrame({'hashApp': hmap, 'frequency': freq})
# res.to_csv("./dataSet/appData_invoc_times.csv")

# freq.sort()
# print(str(freq))
# print("mid ", freq[int(len(freq) / 2)])
# print("avg", np.mean(freq))
high = 0
sum = 0
high_sum=0
high_freq_app = []
for i in range(0, len(freq)):
    if freq[i] > 5000:
        # high += 1
        # high_sum += i
        high_freq_app.append(hmap[i])

data = pd.DataFrame({'high_freq_app': high_freq_app})
data.to_csv('./dataSet/high_freq_app_list.csv')

plt.figure(figsize=(13, 7), )

fig, arx = plt.subplots(nrows=2, ncols=1, figsize=(12, 6), tight_layout=True)
arx[0].hist(freq, bins=30, density=0, color=[0.7, 0.81, 0.91])

# [0.7, 0.81, 0.91]
arx[1].hist(freq, bins=30, density=1, color=[0.7, 0.81, 0.91])

arx[0].tick_params(labelsize=18)
arx[1].tick_params(labelsize=18)
# 设置坐标轴名称
arx[0].set_xlabel('App ID', fontsize=22)
arx[0].set_ylabel('Frequency', fontsize=22)

arx[1].set_xlabel('CoV of function histogram ', fontsize=22)
arx[1].set_ylabel('Probability\nDensity', fontsize=22)

arx[0].grid()
arx[1].grid()

plt.show()
