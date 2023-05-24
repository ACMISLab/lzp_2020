# -*- coding: utf-8 -*-
'''
 将14个已处理好的函数调用序列文件，分别地，合并为以app为粒度的调用记录
'''
import pandas as pd
import os
from heapq import merge

path = "../dataSet/bak"
file_list = []
for f in range(1, 15):
    # if "newData_2019_" not in f:
    fname = "newData_2019_" + str(f) + ".csv"
    file_list.append(fname)


HashOwner = []

HashFunction = []
Trigger = []

list_id = []


days = 0  # 哪一天
for f_name in file_list:
    print(f_name)
    # 记录 <func_id, row_id>
    hashMap = {}
    resData = pd.DataFrame({})
    HashApp = []
    list_time = []
    list_num = []
    raw = pd.read_csv(path + "\\" + f_name, sep=';')
    row_id = 0  # 本文件行号

    for ind, row in raw.iterrows():
        # 如果是新app
        if hashMap.get(row['HashApp'], -1) == -1:
            hashMap[row['HashApp']] = row_id
            row_id += 1
            HashApp.append(row['HashApp'])
            list1 = row['invoc_time_series'][1:-1].split(", ")
            list1 = [int(i) for i in list1]
            list_time.append(list1)
            # list2 = row['invoc_time_num'][1:-1].split(", ")
            # list2 = [int(i) for i in list2]
            # list_num.append(list2)
        else:
            r_id = hashMap[row['HashApp']]
            list1 = row['invoc_time_series'][1:-1].split(", ")
            list1 = [int(i) for i in list1]
            list2 = list_time[r_id]
            list_time[r_id] = list(merge(list1, list2))
    print(len(list_time))

    for li in range(0, len(list_time)):
        l = list_time[li]
        tem = []
        for i in range(0, len(l)):
            if i == 0 or l[i] != l[i - 1]:
                tem.append(1)
            else:
                tem[len(tem) - 1] += 1
        list_num.append(tem)
        list_time[li] = list(set(l))
        list_time[li].sort()
        # print("time ", list_time[li])
        # print("num ", list_num[li])

    print(len(HashApp))
    days += 1
    resData['HashApp'] = HashApp
    # resData['func_id'] = list_id
    resData['invoc_time_series'] = list_time
    resData['invoc_time_num'] = list_num

    resData.to_csv('./dataSet/bak/appData_2019_' + str(days) + '.csv', sep=';')
