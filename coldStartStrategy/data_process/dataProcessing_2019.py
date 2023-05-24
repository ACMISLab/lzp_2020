# -*- coding: utf-8 -*-

import pandas as pd
import os

path = "D:\\Seepen\\ACMIS\\毕设相关\\冷启动实验数据\\dataset2019\\invocations"
file_list = []
for f in os.listdir(path):
    # if "invocations_per_function" not in f:
    #     continue
    print(f)
    file_list.append(f)

# 先对每天
order = 1
for f_name in file_list:
    print(f_name)
    # raw = pd.read_csv('.\dataSet\invocations_per_function_md.anon.d01.csv')
    raw = pd.read_csv(path+"\\"+f_name)

    # print(raw)
    HashOwner = raw.loc[:, 'HashOwner']
    HashApp = raw.loc[:, 'HashApp']
    HashFunction = raw.loc[:, 'HashFunction']
    Trigger = raw.loc[:, 'Trigger']
    list_list_time = []
    list_list_num = []
    list_id = []
    newData = pd.DataFrame({})
    raw = raw.loc[:, '1':'1440']
    # 对每一行（每一个函数）
    for index, row in raw.iterrows():
        # if(index>20):
        #     break
        list_id.append(index)
        list_time = []
        list_num = []

        for i in range(0, 1440):
            if row[i] > 0:
                list_num.append(row[i])     # 并发量
                list_time.append(i+1)       # 调用时刻
        # print(index)
        # print(list_time)
        list_list_time.append(list_time)
        list_list_num.append(list_num)

    newData['HashOwner'] = HashOwner
    newData['HashApp'] = HashApp
    newData['HashFunction'] = HashFunction
    newData['Trigger'] = Trigger
    newData['func_id'] = list_id
    newData['invoc_time_series'] = list_list_time
    newData['invoc_time_num'] = list_list_num

    newData.to_csv('./dataSet/series_Data_2019_' + str(order) + '.csv', sep=';')
    order += 1
    print(order)
