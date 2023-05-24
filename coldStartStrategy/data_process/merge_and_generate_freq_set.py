# -*- coding: utf-8 -*-
'''
    根据生成的 s&w 关联集，合并出可作为策略输入的调用序列
'''
import pandas as pd
import os
from heapq import merge

## 合并各高频set到一个set
# path = "../dataSet/bak"
# file_list = []
#
# set_raw = pd.read_csv('../dataSet/freqSet_Data_2019_4_days_2.csv', sep=';')
# set_new = pd.DataFrame({})
# owner_new = []
# freq_new = []
# for idx, row in set_raw.iterrows():
#     str1 = row['FreqSet'][1:-1]
#     str1 = str1.replace('[], ', '')
#     str1 = str1.replace('[', '')
#     str1 = str1.replace(']', '')
#     if str1 == '':
#         continue
#     list1 = list(str1.split(", "))
#     for i in range(0,len(list1)):
#         if list1[i] == '':
#             list1.pop(i)
#         else:
#             list1[i] = int(list1[i])
#     # [int(i) for i in list1]
#
#     owner_new.append(row['HashOwner'])
#     tem = []
#     for i in list1:
#         tem.append(i)
#     freq_new.append(list(set(tem)))
#
# set_new['HashOwner'] = owner_new
# set_new['FreqSet'] = freq_new
#
# set_new.to_csv('../dataSet/freqSet_Data_2019_4_days_new_2.csv', sep=';')

raw = pd.read_csv('../dataSet/series_Data_2019_4_days.csv', sep=';')
set_new = pd.read_csv('../dataSet/freqSet_s&w_4_days_new_2.csv', sep=';')
setMap = {}     # 记录 <hashOwner, set集合>

for idx, row in set_new.iterrows():
    list1 = row['FreqSet'][1:-1].split(", ")
    list1 = [int(i) for i in list1]
    setMap[row['HashOwner']] = list1

HashOwner = []
HashFunction = []
Trigger = []
funcNums = []
hashMap = {}        # 记录 <set_id, row_id>, 如果没有set，就是func_id
resData = pd.DataFrame({})
HashApp = []
list_time = []
list_num = []
HashSet = []        # set的唯一标识，默认为0,1,2，……
set_id = 0          # 本文件中set号，也即行号
cur_start = 0        # 当前owner所有函数的起始下标
cur_owner = 'xx'

# 获取每个owner开始时的起始行
owner_start_id = {}
for ind, row in raw.iterrows():
    if cur_owner != row['HashOwner']:
        cur_start = ind
        cur_owner = row['HashOwner']
        if cur_owner not in owner_start_id:
            owner_start_id[cur_owner] = cur_start

print("stage 1")

# 合并依赖集，抽取相关行
for k, v in setMap.items():     # 对set中每个依赖集
    HashSet.append(set_id)
    set_id += 1
    temTime = []
    start = owner_start_id[k]
    for i in v:             # 对set中每一个调用
        # row = raw[start+i:start+i+1]
        # pos = start+i
        # if i > 30000:
        # print(k," ",i)
        list1 = raw.get_value(start+i, 'invoc_time_series')
        list1 = list1[1:-1].split(", ")
        list1 = [int(i) for i in list1]
        temTime = list(merge(temTime, list1))
        # temTime.sort()
        raw = raw.drop(start+i, axis=0)         # 抽取合并后就将这行从原表中删除
    # print(k)
    list_time.append(temTime)  # 整合后插入总表

    # print(temTime)

print("stage 2")

# 将剩余无关行插入
for idx, row in raw.iterrows():
    HashSet.append(set_id)
    set_id += 1
    list1 = row['invoc_time_series'][1:-1].split(", ")
    list1 = [int(i) for i in list1]
    list_time.append(list1)

print("stage 3")

# 遍历时序列表，生成并发num列表
for li in range(0, len(list_time)):
    l = list_time[li]
    # print(l)
    tem = []
    for i in range(0, len(l)):
        if i == 0 or l[i] != l[i - 1]:  # 如果到了下一时刻，就新增并发位 1
            tem.append(1)
        else:                       # 如果还是在该时刻内，就加1
            tem[len(tem) - 1] += 1
    list_num.append(tem)
    list_time[li] = list(set(l))
    list_time[li].sort()


print(len(HashSet))
print(len(list_time))
print(len(list_num))
# resData['HashOwner'] = HashOwner
resData['HashSet'] = HashSet
# resData['HashApp'] = HashApp
# resData['func_id'] = list_id
resData['invoc_time_series'] = list_time
resData['invoc_time_num'] = list_num

resData.to_csv('../dataSet/bak/setData_s&w_2019_4_days_2.csv', sep=';')
