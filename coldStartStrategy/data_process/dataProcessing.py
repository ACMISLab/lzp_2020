# -*- coding: utf-8 -*-

import pandas as pd

raw = pd.read_csv('../dataSet/AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt')
app = raw.pop('app')
raw['start_timestamp'] = raw['end_timestamp']-raw['duration']

map = dict.fromkeys(raw['func'])
i=0
for k, v in map.items():
    map[k] = i
    i+=1
list_temp = raw['func'].values.tolist()
list_num = []
for i in list_temp:
    list_num.append(map[i])

raw['func_num'] = list_num
raw.pop('func')
print(raw)
raw.to_csv('./dataSet/AzureFunction2021.csv ')