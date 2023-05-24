# -*- coding: utf-8 -*-

from pmdarima import auto_arima
import sys
import numpy as np

if __name__ == '__main__':
    # nums = [250,503,795,1098,1341,1773]
    nums = ""
    for i in range(1, len(sys.argv)):
        nums = sys.argv[i]
    # print(nums)
    nums = nums[1:-1]
    nums = nums.replace(' ', '')
    nums = nums.split(",")
    nums = list(map(int, nums))
    nums = np.array(nums)
    nums = nums.reshape(-1, 1)

    # split_point = int(len(nums) * 0.85)
    # # 确定训练集/测试集
    # data_train, data_test = nums[0:split_point], nums[split_point:len(nums)]
    # 使用训练集的数据来拟合模型
    '''
     网址: http://alkaline-ml.com/pmdarima/modules/generated/pmdarima.arima.auto_arima.html?highlight=auto_arima
     auto_arima部分参数解析(季节性参数未写):
         1.start_p:p的起始值，自回归(“AR”)模型的阶数(或滞后时间的数量),必须是正整数
         2.start_q:q的初始值，移动平均(MA)模型的阶数。必须是正整数。
         3.max_p:p的最大值，必须是大于或等于start_p的正整数。
         4.max_q:q的最大值，必须是一个大于start_q的正整数
         5.seasonal:是否适合季节性ARIMA。默认是正确的。注意，如果season为真，而m == 1，则season将设置为False。
         6.stationary :时间序列是否平稳，d是否为零。
         6.information_criterion：信息准则用于选择最佳的ARIMA模型。(‘aic’，‘bic’，‘hqic’，‘oob’)之一
         7.alpha：检验水平的检验显著性，默认0.05
         8.test:如果stationary为假且d为None，用来检测平稳性的单位根检验的类型。默认为‘kpss’;可设置为adf
         9.n_jobs ：网格搜索中并行拟合的模型数(逐步=False)。默认值是1，但是-1可以用来表示“尽可能多”。
         10.suppress_warnings：statsmodel中可能会抛出许多警告。如果suppress_warnings为真，那么来自ARIMA的所有警告都将被压制
         11.error_action:如果由于某种原因无法匹配ARIMA，则可以控制错误处理行为。(warn,raise,ignore,trace)
         12.max_d:d的最大值，即非季节差异的最大数量。必须是大于或等于d的正整数。
         13.trace:是否打印适合的状态。如果值为False，则不会打印任何调试信息。值为真会打印一些
     '''
    fitted_model = \
        auto_arima(nums,
                   start_p=0,  # p最小值
                   start_q=0,  # q最小值
                   test='kpss',  # ADF检验确认差分阶数d, 或直接用 kpss
                   max_p=5,  # p最大值
                   max_q=5,  # q最大值
                   m=1,  # 季节性周期长度，当m=1时则不考虑季节性
                   max_d=3, max_order=None,  # 通过函数来计算d
                   seasonal=False, trace=False,
                   error_action='ignore', suppress_warnings=True,
                   stepwise=True, information_criterion='bic', njob=-1  # stepwise为False则不进行完全组合遍历
                   )

    output = fitted_model.predict(1)
    print(output)

    # print(fitted_model.summary())

