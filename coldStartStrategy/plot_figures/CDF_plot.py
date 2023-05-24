# -*- coding: utf-8 -*-

import numpy as np
import statsmodels.api as sm  # recommended import according to the docs
import matplotlib.pyplot as plt
import pandas as pd
import mean as mn
import seaborn as sns
import random

path_1 = "D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\dataSet\\result_3_days.csv"
path_2 = "D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\dataSet\\app_result_14_days.csv"
path_3 = "D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\dataSet\\s&w_set_result_4_days_cov=4.csv"
path_4 = "D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\dataSet\\s&w_set_result_4_days_cov=4_2.csv"
# path = "./dataSet/func_invoc_frequency_per_app.csv"

raw_data_func = pd.read_csv(path_1, header=None)
raw_data_app = pd.read_csv(path_2, header=None)
raw_data_set = pd.read_csv(path_3, header=None)
raw_data_set_2 = pd.read_csv(path_4, header=None)

# 统计每个set包含几个func
app_func_nums = list(pd.read_csv('../dataSet/app_func_nums', header=None).iloc[:, 1])
set_func_nums = []
set_func_nums_2 = []
raw_1 = pd.read_csv('../dataSet/freqSet_s&w_4_days_new.csv', sep=';')
raw_2 = pd.read_csv('../dataSet/freqSet_s&w_4_days_new_2.csv', sep=';')
list1 = []
list2 = []
for s in raw_1['FreqSet']:
    tem = s[1:-1].split(", ")
    tem = [int(i) for i in tem]
    list1.append(tem)
for l in list1:
    set_func_nums.append(len(l))

for s in raw_2['FreqSet']:
    tem = s[1:-1].split(", ")
    tem = [int(i) for i in tem]
    list2.append(tem)
for l in list2:
    set_func_nums_2.append(len(l))

# 去除 1,0,0 值
step = 0
for idx, row in raw_data_set.iterrows():
    if step < mn.scope and row.iloc[0] == 1.0 and row.iloc[1] == 0 and row.iloc[2] == 0:
        raw_data_set = raw_data_set.drop(idx)
        step += 1
step = 0
for idx, row in raw_data_set_2.iterrows():
    if step < mn.scope and row.iloc[0] == 1.0 and row.iloc[1] == 0 and row.iloc[2] == 0:
        raw_data_set_2 = raw_data_set_2.drop(idx)
        step += 1
# for idx, row in raw_data_func.iterrows():
#     if row.iloc[0]==1.0 and row.iloc[1]==0 and row.iloc[2]==0:
#         raw_data_func = raw_data_func.drop(idx)
# for idx, row in raw_data_app.iterrows():
#     if row.iloc[0]==1.0 and row.iloc[1]==0 and row.iloc[2]==0:
#         raw_data_app = raw_data_app.drop(idx)

print(len(app_func_nums))

data_func = raw_data_func.iloc[:, 0]  # 0 冷启动率, 1 内存消耗
data_app_f = list(raw_data_app.iloc[:, 0])
data_app = []
data_set_f = list(raw_data_set.iloc[:, 0])
data_set = []
data_set_2 = list(raw_data_set_2.iloc[:, 0])

# 仅内存时使用，去除app内存的异常负值
for i in range(0, len(data_app_f)):
    if data_app_f[i] > 0:
        data_app.append(data_app_f[i])
for i in range(0, len(data_set_f)):
    if data_set_f[i] > 0:
        data_set.append(data_set_f[i])

# 以set的结果代表其中每个函数的结果
for i in range(0, len(set_func_nums)):
    for j in range(0, set_func_nums[i]):
        data_set.append(data_set[i])
        data_set.append(mn.mean)
for i in range(0, len(set_func_nums_2)):
    for j in range(0, set_func_nums_2[i]):
        data_set_2.append(data_set_2[i])
        data_set_2.append(mn.mean)
for i in range(0, len(app_func_nums)):
    for j in range(0, app_func_nums[i]):
        data_app.append(data_app[i])

# =============绘制cdf图===============
ecdf_func = sm.distributions.ECDF(data_func)
ecdf_app = sm.distributions.ECDF(data_app)
ecdf_set = sm.distributions.ECDF(data_set)
ecdf_set_2 = sm.distributions.ECDF(data_set_2)

# 等差数列，用于绘制X轴数据
x = np.linspace(min(data_func), max(data_func), num=100)
x_app = np.linspace(min(data_app), max(data_app), num=100)
x_set = np.linspace(min(data_set), max(data_set), num=100)
x_set_2 = np.linspace(min(data_set_2), max(data_set_2), num=100)

# x轴数据上值对应的累计密度概率
y = ecdf_func(x)
y_app = ecdf_app(x_app)
y_set = ecdf_set(x_set)
y_set_2 = ecdf_set_2(x_set_2)

# 绘制阶梯图
plt.step(x, y, label='function', where='post')
plt.step(x_app, y_app, label='application', where='post')
plt.step(x_set, y_set, label='Set_strong=10', where='post')
plt.step(x_set_2, y_set_2, label='Set_strong=15', where='post')
plt.legend()

# sns.kdeplot(data_func, cumulative=True, label='function')
# sns.kdeplot(data_app, cumulative=True, label='application')
# sns.kdeplot(data_set, cumulative=True, label='Set')
# plt.step(x, y2)
# plt.step(x, y3)
# plt.step(x, y4)

# plt.figure(figsize=(13, 4))
# plt.bar(xx, d, color=[0.7, 0.81, 0.91])
plt.tick_params(labelsize=12)
# 设置坐标轴名称
plt.xlabel('Memory Cost', fontsize=16)
plt.ylabel('CDF', fontsize=16)

# 设置坐标轴刻度
# my_x_ticks = np.arange(0, 1.2, 0.25)
my_y_ticks = np.arange(0, 1.2, 0.25)
# plt.xticks(my_x_ticks)
plt.yticks(my_y_ticks)

plt.grid()
plt.show()
