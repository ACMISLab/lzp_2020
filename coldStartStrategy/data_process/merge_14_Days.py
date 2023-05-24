# -*- coding: utf-8 -*-
'''
 将14天已处理好的函数调用序列文件，合并为一个整合的大文件
'''
import pandas as pd
import os

path = "../dataSet"
file_list = []
for f in range(8, 15):
    # if "newData_2019_" not in f:
    fname = "series_Data_2019_" + str(f) + ".csv"
    file_list.append(fname)

resData = pd.DataFrame({})
HashOwner = []
HashApp = []
HashFunction = []
Trigger = []
list_time = []
list_num = []
list_id = []

# 记录 <func_id, row_id>
hashMap = {}

row_id = 0  # 全局行号
days = 0  # 哪一天
for f_name in file_list:
    print(f_name)
    raw = pd.read_csv(path + "\\" + f_name, sep=';')

    for ind, row in raw.iterrows():
        # print(row)
        # 如果是新func，修正当前分钟，插入构造列中
        if hashMap.get(row['HashFunction'], -1) == -1:
            hashMap[row['HashFunction']] = row_id
            list_id.append(row_id)
            row_id += 1
            HashOwner.append(row['HashOwner'])
            HashApp.append(row['HashApp'])
            HashFunction.append(row['HashFunction'])
            Trigger.append(row['Trigger'])
            # print(row['invoc_time_series'])
            newInvocTime = [1440 * days + int(i) for i in row['invoc_time_series'][1:-1].split(', ')]  # 按天修正分钟
            list_time.append(newInvocTime)
            list_num.append(row['invoc_time_num'])

        else:  # 如果是之前已有func，只需更新其调用时间序列与并发序列即可
            old_row_id = hashMap[row['HashFunction']]
            newInvocTime = [1440 * days + int(i) for i in row['invoc_time_series'][1:-1].split(", ")]  # 按天修正分钟
            list_time[old_row_id] = list_time[old_row_id] + newInvocTime
            list_num[old_row_id] = list_num[old_row_id][0:-1] + ', ' + row['invoc_time_num'][1:]

    days += 1
    print(days)

resData['HashOwner'] = HashOwner
resData['HashApp'] = HashApp
resData['HashFunction'] = HashFunction
resData['Trigger'] = Trigger
resData['func_id'] = list_id
resData['invoc_time_series'] = list_time
resData['invoc_time_num'] = list_num

resData.to_csv('../dataSet/sevenDays/series_Data_2019_8-14_days.csv', sep=';')
