# -*- coding: utf-8 -*-
import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


func_invoc_frequency = pd.read_csv("../dataSet/funcInvoc_Freq_cov_per_app.csv")
func_invoc_frequency = func_invoc_frequency["cov_per_app"]


plt.figure(figsize=(13, 6))
# [0.7, 0.81, 0.91]
colors = sns.xkcd_rgb["denim blue"]
plt.hist(func_invoc_frequency, bins=int(len(func_invoc_frequency)/6), density=0, color=sns.xkcd_rgb["denim blue"])

plt.axvline(0.9, c=sns.xkcd_rgb["pale red"], ls='--', linewidth='2')
plt.axvline(0.96, c=sns.xkcd_rgb["pale red"], ls='--', linewidth='2')


plt.tick_params(labelsize=18)
#设置坐标轴名称
plt.xlabel('CoV of Function Invocations', fontsize=22)
plt.ylabel('Frequency', fontsize=22)

#设置坐标轴刻度
my_x_ticks = np.arange(0.8, 1.21, 0.1)
my_y_ticks = np.arange(0, 201, 25)
plt.xticks(my_x_ticks)
plt.yticks(my_y_ticks)

plt.grid()
plt.show()


