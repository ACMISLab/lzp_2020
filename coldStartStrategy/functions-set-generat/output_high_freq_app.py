# -*- coding: utf-8 -*-

import pandas as pd

raw = pd.read_csv('./dataSet/series_Data_2019_4_days.csv', sep=';')
highFreqAppList_raw = pd.read_csv('./dataSet/high_freq_app_list.csv')
highFreqAppList = list(highFreqAppList_raw['high_freq_app'])
newRaw = pd.DataFrame()

cnt = 0
for idx, row in raw.iterrows():
    if row['HashApp'] in highFreqAppList:
        print(cnt)
        cnt += 1
        newRaw.append(row)
        print(newRaw)

newRaw.to_csv('./dataSet/high_freq_app_series_data.csv', sep=';')
