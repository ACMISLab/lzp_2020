# -*- coding: utf-8 -*-
'''
实验数据处理流程：
 1. 原数据
 2. 按天合并序列后数据 --- dataProcessing_2019.py
 3. 合并 n 天的数据  --- merge_14_Days.py
    4.1 输入策略获取函数 CV --- Java-Cold-2
    4.2 挖掘频繁模式 --- freq_pattern_mining.py
 5. 根据 CV 选出不可预测函数，将强弱关联集合并为 s&w_set --- freq_weak_set.py
 6. 根据 set 及预测集序列，将函数合并为关联集粒度 --- merge_and_generate_freq_set.py
 7. 合并预测集所有函数为应用粒度 --- merge_14_apps.py
 8. 以三种粒度，输入策略获取实验结果

'''

mean = 0.002
scope = 5000
