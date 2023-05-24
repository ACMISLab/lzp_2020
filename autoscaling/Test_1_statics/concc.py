# -*- coding: utf-8 -*-
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

dictPath = "D:/Seepen/ACMIS/MyGraduation/cold-2/src/main/java/Jmeter_report"

# plt.figure(figsize=(16, 8), dpi=600)
fig, ax1 = plt.subplots(figsize=(8, 4), dpi=100)


def getProcessAvg(list_0, list_1):
    for i in range(0, 19):
        tem = []
        for j in range(0, 5):
            # if latency_max[j][i] < 20000:
            tem.append(list_0[j][i])
        if len(tem) > 3:
            tem.sort()
            tem.pop()
            tem.pop(0)
        # print(str(tem))
        list_1.append(np.mean(tem))


target = []
throughput = []
latency_avg = []
latency_P90 = []
latency_max = []

ccur = 200
for i in range(1, 6):
    # csvPath = dictPath + "/ccur=" + str(ccur) + "/round_" + str(i)
    csvPath = dictPath + "/round_" + str(i)
    reportCsvPath = csvPath + "/report_all.csv"
    report = pd.read_csv(reportCsvPath, header=None)

    # if i < 6:
    #     latencyP90CsvPath = csvPath + "/latencyP90_all.csv"
    #     latency = pd.read_csv(latencyP90CsvPath, header=None)
    #     latency_P90.append(latency.iloc[:, 0])
    # else:
    latency_P90.append(list(report.iloc[:, 3]))

    target.append(list(report.iloc[:, 0]))
    throughput.append(list(report.iloc[:, 1]))
    latency_avg.append(list(report.iloc[:, 2]))
    latency_max.append(list(report.iloc[:, -2]))

    # if i > 5:
    #     throughput[i - 1].reverse()
    #     latency_max[i - 1].reverse()
    #     latency_avg[i - 1].reverse()
    #     latency_P90[i - 1].reverse()

final_target = []
final_throughput = []
final_latency_avg = []
final_latency_P90 = []
final_latency_max = []

# getProcessAvg(target, final_target)
getProcessAvg(throughput, final_throughput)
getProcessAvg(latency_avg, final_latency_avg)
getProcessAvg(latency_P90, final_latency_P90)
getProcessAvg(latency_max, final_latency_max)

print(str(final_throughput))
final_latency_avg = [x / 1000 for x in final_latency_avg]
final_latency_P90 = [x / 1000 for x in final_latency_P90]

# x = np.arange(10, 200, 10)  # 点的横坐标
# plt.plot(x, final_throughput, 's-', color='r', label="throughput")  # s-:方形
# plt.plot(x, final_latency_avg, 'o-', color='g', label="latency_avg")  # s-:方形
# plt.plot(x, final_latency_P90, 'o-', color='b', label="latency_P90")  # s-:方形

# plt.plot(x, latency_avg, 'o-', color='g', label="latency_avg")  # o-:圆形
# plt.plot(x, latency_P90, 'o-', color='b', label="latency_P90")  # o-:圆形


x = np.arange(10, 200, 10)

# 吞吐量
line1, = ax1.plot(x, final_throughput, color=sns.xkcd_rgb["pale red"], linestyle='-',)
p1 = ax1.scatter(x, final_throughput, color=sns.xkcd_rgb["pale red"], marker='v', s=30, label='throughput')

# 时延
ax2 = ax1.twinx()
line2, = ax2.plot(x, final_latency_avg, color=sns.xkcd_rgb["denim blue"], linestyle='-',)
p2 = ax2.scatter(x, final_latency_avg, color=sns.xkcd_rgb["denim blue"], marker='o', s=30, label='latency_avg')
line3, = ax2.plot(x, final_latency_P90, color=sns.xkcd_rgb["denim blue"], linestyle='-',)
p3 = ax2.scatter(x, final_latency_P90, color=sns.xkcd_rgb["denim blue"], marker='s', s=30, label='latency_P90')

# 坐标轴设置
ax1.set_xticks(range(0, 200, 10))
ax1.set_ylim([0, 20])
ax2.set_ylim([0, 30])

ax1.set_xlabel("Target", fontsize=12)
ax1.set_ylabel("Throughput (RPS)", fontsize=12)
ax2.set_ylabel("Latency (s)", fontsize=12)

# 双Y轴标签颜色设置
ax1.yaxis.label.set_color(line1.get_color())
ax2.yaxis.label.set_color(line2.get_color())

# 双Y轴刻度颜色设置
ax1.tick_params(axis='y', colors=line1.get_color())
ax2.tick_params(axis='y', colors=line2.get_color())

plt.grid()
plt.legend(loc="lower right")  # 图例
plt.show()
