# -*- coding: utf-8 -*-
import pandas as pd
# from mlxtend.preprocessing import TransactionEncoder  # 传入模型的数据需要满足特定的格式，可以用这种方法来转换为bool值，也可以用函数转换为0、1
# from mlxtend.frequent_patterns import fpgrowth
# from mlxtend.frequent_patterns import association_rules
# 调包演示
import pyfpgrowth

from fpgrowth_py import fpgrowth
'''
    根据合并好的时序数据，利用 FP-Growth 生成强关联集
'''

def get_freq_items(trans, maxLen):
    # 两个参数, minSupRatio 支持度, minConf置信度
    # freqItemSet, rules = fpgrowth(trans, minSupRatio=0.1, minConf=0.1)
    factory = int(maxLen/20)        # 因子
    freq = len(trans) / 10
    # print(factory)
    # if factory > 2:
    #     freq = len(trans) / 3

    for i in range(0, len(trans)):
        tran = trans.pop(0)
        tem = []
        # print(tran)
        for j in range(0, len(tran)):
            tem.append(tran[j])
            if len(tem) % 20 == 0:      # 满20个一组
                trans.append(tem)
                tem.clear()
            elif j == len(tran)-1 and len(tem)>0:
                trans.append(tem)

        # trans[i] = trans[i][0:min(len(trans[i]), max(12, int(maxLen/factory)))]
        # 对每个候选项进行裁剪，

    patterns = pyfpgrowth.find_frequent_patterns(trans, freq)  # 频数删选  频数大于freq的
    patterns = dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True))  # 按频数降序
    if len(patterns) == 0:
        return []
    curV = list(patterns.values())[0]       # 最高频数
    curK = []                               # 最高频数对应的项集
    res = []                # 最终前15个高频项集

    for k, v in patterns.items():
        if len(res) > 15:
            break
        if v == curV:           # 对相同频数的所有项进行合并，得到不重复的一个大项
            [curK.append(i) for i in k]
        else:
            curV = v
            res.append(sorted(list(set(curK))))
            curK.clear()

    return res


raw = pd.read_csv("./dataSet/sevenDays/series_Data_2019_1-7_days.csv", sep=";")
outData = pd.DataFrame({})
HashOwner = []
FreqSet = []
time_series = []

tem = []                            # 每个用户所有函数的调用序列
maxTranLength = 0       # 记录一个trans中最长的tran的长度
curUser = raw['HashOwner'][0]

for idx, row in raw.iterrows():

    if row['HashOwner'] == curUser:
        ll = row['invoc_time_series'][1:-1].split(', ')
        ll = [int(i) for i in ll]
        tem.append(ll)

    else:                                   # 上一个用户所有函数记录完了，要完成频繁模式挖掘 & 下个用户记录的更新
        # print("tem len ", len(tem))
        trans = []                           # fp-growth 输入，是对每个时间窗口内统计调用不为0的函数id，放在一个tran中，最终组成trans输入
        for i in range(0, 1440*4, 10):      # 对每个时间片
            tran = []                       # 当前时间片内，函数名list初始化
            for j in range(0, len(tem)):     # 对每个函数时间序列
                for it in tem[j]:           # 对时间序列里每个调用检查是否落在当前时间片内
                    if i <= int(it) < i+10:
                        tran.append(j)
                        break
                    elif int(it) >= i+10:
                        break
            # trans.append(tran[0:min(10, len(tran))])
            trans.append(tran)
            maxTranLength = max(maxTranLength, len(tran))

        res = get_freq_items(trans, maxTranLength)
        HashOwner.append(curUser)
        FreqSet.append(res)
        print(curUser)
        print(res)

        # 更新下一个用户信息

        curUser = row['HashOwner']
        tem.clear()
        ll = row['invoc_time_series'][1:-1].split(', ')
        ll = [int(i) for i in ll]
        tem.append(ll)


outData['HashOwner'] = HashOwner
outData['Freq Set'] = FreqSet

outData.to_csv('./dataSet/sevenDays/freqSet_Data_2019_1-7_days.csv', sep=';')


'''
    transactions = [[1, 2, 5],
                    [2, 4],
                    [2, 3],
                    [1, 2, 4],
                    [1, 3],
                    [2, 3],
                    [1, 3],
                    [1, 2, 3, 5],
                    [1, 2, 3]]
    
    patterns = pyfpgrowth.find_frequent_patterns(transactions, 2)  # 频数删选  频数大于2
    rules = pyfpgrowth.generate_association_rules(patterns, 0.6)  # 置信度(条件概率)删选
    
    print(patterns)
    print('===============')
    print(rules)
'''