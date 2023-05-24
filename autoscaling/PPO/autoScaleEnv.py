
import gym
from bson.int64 import long
from gym import spaces
import numpy as np
import jpype
import time




class myEnv(gym.Env):

    def __init__(self):
        self.curTarget = 100
        self.curUtilization = 70
        # 动作空间，二维连续，[target, utilization]
        self.action_space = spaces.Box(low=np.array([10, 50]), high=np.array([200, 100]), dtype=np.uint8)
        # 环境空间，[target, utilization, cpu, mem]，还应包括此轮pod平均cpu及mem，平均执行时间(?)
        self.observation_space = spaces.Box(low=np.array([10, 50, 0, 0]), high=np.array([200, 100, 100, 100]), dtype=np.float)
        self.state = None
        self.reward_quan = 0.8

    def step(self, action, ):
        # assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
        self.runJVM()

        MyPrometheusClient = jpype.JClass("Prometheus_Client.MyPrometheusClient")   # 获取Java类
        myPrometheusClient = MyPrometheusClient()                   # 实例化
        timestamp = long(int(round(time.time() * 1000)))    # 获取long型时间戳
        resourceInfo = myPrometheusClient.getSystemInfo(timestamp)

        self.state = np.array([self.curTarget, self.curUtilization, resourceInfo[0], resourceInfo[1]], dtype="float32")

        MyJmeterClient = jpype.JClass("Jmeter_pkg.JmeterClient")
        myJmeterClient = MyJmeterClient()
        # performanceInfo = myJmeterClient.

        # reward = self.calcuReward(performanceInfo)


        # jpype.shutdownJVM()


        return self.state, 0, True, {}
        # return self.state, reward, done, {}


    def reset(self):
        self.runJVM()
        MyPrometheusClient = jpype.JClass("Prometheus_Client.MyPrometheusClient")  # 获取Java类
        myPrometheusClient = MyPrometheusClient()  # 实例化
        timestamp = long(int(round(time.time() * 1000)))  # 获取long型时间戳
        resourceInfo = myPrometheusClient.getSystemInfo(timestamp)

        self.state = np.array([self.curTarget, self.curUtilization, resourceInfo[0], resourceInfo[1]], dtype="float32")

        return self.state


    # 计算 reward。使用平均吞吐量、响应时间，以及资源利用率
    def calcuReward(self, res):
        throughput = float(res[2])
        latencyAvg = float(res[3])
        latencyP90 = float(res[4])
        reward = throughput / (self.reward_quan*latencyAvg + (1-self.reward_quan)*latencyP90)

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
    env = myEnv()
    print(env.action_space.sample())
    print(env.observation_space.sample())







