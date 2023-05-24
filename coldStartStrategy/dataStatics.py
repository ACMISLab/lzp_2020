# -*- coding: utf-8 -*-
import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

raw = pd.read_csv("./dataSet/resData_2019_all.csv", sep=';')
dict_app = {}
dict_trigger = {}

for index, row in raw.iterrows():
    if row['HashApp'] not in dict_app:
        dict_app[row['HashApp']] = [row]
    else:
        dict_app[row['HashApp']].append(row)

    if row['Trigger'] not in dict_trigger:
        dict_trigger[row['Trigger']] = 1
    else:
        dict_trigger[row['Trigger']] += 1

print(str(dict_trigger))
print("app nums ", len(dict_app))
func_num_per_app = []
for app, val in dict_app.items():
    func_num_per_app.append(len(val))
print("func_num_per_app ", str(func_num_per_app))

# app中，每个函数的调用次数占app调用次数之比
func_invoc_frequency = []
# app中，所有函数的调用频率的cov
cov_per_app = []


def coefficient_of_variation(data):
    mean = np.mean(data)  # 计算平均值
    std = np.std(data, ddof=0)  # 计算标准差
    cv = std / mean
    return cv

for app, val in dict_app.items():
    func_nums = []
    app_nums = 0
    for v in val:
        func_invoc = len(v["invoc_time_series"])
        app_nums = max(app_nums, func_invoc)
        func_nums.append(func_invoc)
    for i in func_nums:
        func_invoc_frequency.append(i / app_nums)
    cov_per_app.append(coefficient_of_variation(func_invoc_frequency))





# print(str(func_invoc_frequency))
# res = pd.DataFrame({})
# res['cov_per_app'] = cov_per_app
# res.to_csv("./dataSet/funcInvoc_Freq_cov_per_app.csv")

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号
plt.figure(figsize=(13, 4))
plt.hist(cov_per_app, bins=40, density=1, color=sns.xkcd_rgb["denim blue"])
# plt.bar(xx, d, color=[0.7, 0.81, 0.91])
plt.tick_params(labelsize=20)
# 设置坐标轴名称
plt.xlabel('区间', fontsize=22)
plt.ylabel('频率', fontsize=28)

# 设置坐标轴刻度
my_x_ticks = np.arange(0, 1, 0.1)
my_y_ticks = np.arange(0, 50, 10)
plt.xticks(my_x_ticks)
plt.yticks(my_y_ticks)

plt.grid()
plt.show()



