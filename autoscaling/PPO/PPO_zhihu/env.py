import os

import gym
from bson.int64 import long
from gym import spaces
import numpy as np
import jpype
import time
import pandas as pd


class myEnv(gym.Env):

    def __init__(self):
        self.curTarget = 100
        self.curUtilization = 70
        # 动作空间，二维连续，[target, utilization]
        self.action_space = spaces.Box(low=np.array([30, 60]), high=np.array([199, 100]))
        # 环境空间，[target, utilization, cpu, mem]，还应包括此轮pod平均cpu及mem，平均执行时间(?)
        self.observation_space = spaces.Box(low=np.array([30, 60, 0, 0]), high=np.array([199, 100, 100, 100]))
        self.state = None
        self.reward_quan = 0.8
        self.runJVM()
        self.tiemstamp = long(int(round(time.time() * 1000)))
        self.resPath = "./res/"+str(self.tiemstamp)+"/"
        os.mkdir(self.resPath)

    def myStep(self, action, rod, episode):
        # assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
        # self.runJVM()

        # 获取待执行的当前动作
        self.curTarget = int(round(action[0]))
        self.curUtilization = int(round(action[1]))

        # 更新服务并调用Jmeter测试，获取性能结果
        QLearningClient = jpype.JClass("QLearning.QLearning")
        qLearningClient = QLearningClient()
        performanceInfo = qLearningClient.getTrainRes(episode, rod, self.curTarget, self.curUtilization, 1, 1)

        # AC = jpype.JClass("QLearning.AutoscaleController")
        # ac = AC()
        # performanceInfo = ac.executePlanWithChange(episode, rod, self.curTarget, self.curUtilization, 1)
        print(performanceInfo)
        # 计算 reward
        reward = self.calcuReward(performanceInfo)

        # 获取下一个环境
        MyPrometheusClient = jpype.JClass("Prometheus_Client.MyPrometheusClient")  # 获取Java类
        myPrometheusClient = MyPrometheusClient()  # 实例化
        timestamp = long(int(round(time.time() * 1000)))  # 获取long型时间戳
        resourceInfo = myPrometheusClient.getSystemInfo(timestamp)
        print("res[0]", resourceInfo[0])
        print("res[1]", resourceInfo[1])
        self.state = np.array([self.curTarget, self.curUtilization, resourceInfo[0], resourceInfo[1]], dtype="float32")

        line = pd.DataFrame([performanceInfo])
        line.to_csv(self.resPath+"perform_info.csv", mode='a', encoding='utf-8', header=False, index=False)

        return self.state, reward, True, {}


    def reset(self):

        MyPrometheusClient = jpype.JClass("Prometheus_Client.MyPrometheusClient")  # 获取Java类
        myPrometheusClient = MyPrometheusClient()  # 实例化
        timestamp = long(int(round(time.time() * 1000)))  # 获取long型时间戳
        resourceInfo = myPrometheusClient.getSystemInfo(timestamp)

        self.state = np.array([self.curTarget, self.curUtilization, resourceInfo[0], resourceInfo[1]], dtype="float32")

        return self.state

    # 计算 reward。使用平均吞吐量、响应时间，以及资源利用率
    def calcuReward(self, res):
        throughput = float(str(res[2]))
        latencyAvg = float(str(res[3]))
        latencyP90 = float(str(res[4]))
        reward = throughput / (self.reward_quan * latencyAvg + (1 - self.reward_quan) * latencyP90)

        return reward

    def runJVM(self):
        jvm_path = "C:\\Program Files\\Java\\jdk1.8.0_144\\jre\\bin\\server\\jvm.dll"
        java_class_path = "D:\\Seepen\\ACMIS\\MyGraduation\\project_work\\autoscaling\\PPO\\java_class\\cold-2-1.0" \
                          "-SNAPSHOT.jar "
        if not jpype.isJVMStarted():
            try:
                jpype.startJVM(jvm_path, "-ea", "-Djava.class.path=" + java_class_path, convertStrings=False)
            except Exception as e:
                print(str(e))


'''
    从Java接口获得的：
    · 获取env资源信息
    · 根据action更新
    · 执行Jmeter计划
'''
if __name__ == '__main__':
    myEnv = myEnv()
    # myEnv.runJVM()
    # jpype.shutdownJVM()
    pf = [199, 52, 61.25778559942488, 1079, 2225, 33, 3083, 0, 1670921780000, 1670921781674]
    # line = pd.DataFrame()
    # line = line.append(pd.DataFrame(pf, columns=None), ignore_index=True)
    #
    # line.to_csv(myEnv.resPath + "perform_info.csv", mode='a', encoding='utf-8', header=False, index=False)

    line = pd.DataFrame([pf])
    line.to_csv(myEnv.resPath + "perform_info.csv", mode='a', encoding='utf-8', header=False, index=False)
