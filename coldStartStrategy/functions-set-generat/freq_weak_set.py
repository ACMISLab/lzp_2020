# -*- coding: utf-8 -*-
import pandas as pd

'''
 添加所有低频函数到所属高频set中，合并出最终的 s&w set
'''
raw = pd.read_csv('./dataSet/series_Data_2019_4_days.csv', sep=';')
path = "D:\\Seepen\\ACMIS\\毕设相关\\cold-2\\src\\dataSet\\func_result_4_days_cov=4.csv"
path_2 = "D:\\Seepen\\ACMIS\\毕设相关\\毕设工程工作\\coldStartStrategy\\dataSet\\freqSet_Data_2019_4_days_new_2.csv"
raw_2 = pd.read_csv(path_2, sep=';')
list1 = []
for s in raw_2['FreqSet']:
    tem = s[1:-1].split(", ")
    tem = [int(i) for i in tem]
    list1.append(tem)

set_map = dict(zip(raw_2['HashOwner'], list1))

func_invoc_cov = pd.read_csv(path).iloc[:, 3]
HashOwner = pd.read_csv(path).iloc[:, 4]
HashFunc = pd.read_csv(path).iloc[:, 5]

for idx in range(0, len(func_invoc_cov)):
    if str(func_invoc_cov[idx]) == "nan":
        func_invoc_cov[idx] = 0

# 筛选不可预测函数
low_cov_func = []
low_cov_owner = []
for idx in range(0, len(func_invoc_cov)):
    if func_invoc_cov[idx] < 5:
        low_cov_func.append(HashFunc[idx])
        low_cov_owner.append(HashOwner[idx])

print(len(set(low_cov_owner)))

# 获取每个owner开始时的起始行
owner_start_id = {}
cur_owner = "xx"
for ind, row in raw.iterrows():
    if cur_owner != row['HashOwner']:
        cur_start = ind
        cur_owner = row['HashOwner']
        if cur_owner not in owner_start_id:
            owner_start_id[cur_owner] = cur_start

print("stage 1")

# 将不可预测函数合并道所属owner关联集中
for ix, row in raw.iterrows():
    if row['HashFunction'] in low_cov_func:
        if row['HashOwner'] in set_map:
            # 拿到func在所在owner中的相对位置
            # print(ix, " ", owner_start_id[row['HashOwner']])
            pos = ix - owner_start_id[row['HashOwner']]
            set_map[row['HashOwner']].append(pos)
            # raw = raw.drop(ix)

# print(set_map)

output = pd.DataFrame({})
res_o = []
res_s = []
for k, v in set_map.items():
    res_o.append(k)
    res_s.append(list(set(v)))
output['HashOwner'] = res_o
output['FreqSet'] = res_s
output.to_csv('.\\dataSet\\freqSet_s&w_4_days_new_2.csv', sep=';')





