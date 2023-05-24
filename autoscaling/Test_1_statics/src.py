# -*- coding: utf-8 -*-
import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

dictPath = "D:/Seepen/ACMIS/MyGraduation/cold-2/src/main/java/Jmeter_report"

plt.figure(figsize=(15, 8), )


def getProcessAvg(list_0, list_1):
    for i in range(0, 19):
        tem = []
        for j in range(0, 5):
            if latency_max[j][i] < 20000:
                tem.append(list_0[j][i])
        if len(tem) > 3:
            tem.sort()
            tem.pop()
            tem.pop(0)
        # print(str(tem))
        list_1.append(np.mean(tem))

res_list = []
for ccur in range(200, 501, 100):
    target = []
    throughput = []
    latency_avg = []
    latency_P90 = []
    latency_max = []
    for i in range(1, 6):
        csvPath = dictPath + "/ccur=" + str(ccur) + "/round_" + str(i)
        reportCsvPath = csvPath + "/report_all.csv"
        latencyP90CsvPath = csvPath + "/latencyP90_all.csv"
        report = pd.read_csv(reportCsvPath, header=None)
        # latency = pd.read_csv(latencyP90CsvPath, header=None)

        target.append(report.iloc[:, 0])
        throughput.append(report.iloc[:, 1])
        latency_avg.append(report.iloc[:, 2])
        latency_P90.append(report.iloc[:, 3])
        # latency_P90.append(latency.iloc[:, 0])
        latency_max.append(report.iloc[:, -2])
        # err_num = report.iloc[:, -1]

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
    res_list.append(final_throughput)

x = np.arange(10, 200, 10)  # 点的横坐标
plt.plot(x, res_list[0], 's-', color='r', label="throughput_200")  # s-:方形
plt.plot(x, res_list[1], 's-', color='g', label="throughput_300")  # s-:方形
plt.plot(x, res_list[2], 's-', color='b', label="throughput_400")  # s-:方形
plt.plot(x, res_list[3], 's-', color='y', label="throughput_500")  # s-:方形
# plt.plot(x, latency_avg, 'o-', color='g', label="latency_avg")  # o-:圆形
# plt.plot(x, latency_P90, 'o-', color='b', label="latency_P90")  # o-:圆形


xx = np.arange(10, 210, 10)  # 点的横坐标
plt.xticks(xx)

plt.xlabel("Target")  # 横坐标名字
plt.ylabel("Throughput(RPS)")  # 纵坐标名字
plt.legend(loc="best")  # 图例
plt.show()
