import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('ggplot')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 平滑处理，类似tensorboard的smoothing函数。
def smooth(read_path, save_path, file_name, x='timestep', y='reward', weight=0.75):

    data = pd.read_csv(read_path + file_name)
    scalar = data[y].values
    last = scalar[0]
    smoothed = []
    for point in scalar:
        smoothed_val = last * weight + (1 - weight) * point
        smoothed.append(smoothed_val)
        last = smoothed_val

    save = pd.DataFrame({x: data[x].values, y: smoothed})
    save.to_csv(save_path + 'smooth_'+ file_name)

# 平滑预处理原始reward数据
smooth(read_path='./BipedalWalker-v3/', save_path='./BipedalWalker-v3/',
       file_name='PPO_BipedalWalker-v3_log_210.csv')
smooth(read_path='./BipedalWalker-v3/', save_path='./BipedalWalker-v3/',
       file_name='PPO_BipedalWalker-v3_log_310.csv')
smooth(read_path='./BipedalWalker-v3/', save_path='./BipedalWalker-v3/',
       file_name='PPO_BipedalWalker-v3_log_410.csv')

# 读取平滑后的数据
df1 = pd.read_csv('./BipedalWalker-v3/smooth_PPO_BipedalWalker-v3_log_210.csv')  #[1100: 1200]
df2 = pd.read_csv('./BipedalWalker-v3/smooth_PPO_BipedalWalker-v3_log_310.csv')  #[1100: 1200]
df3 = pd.read_csv('./BipedalWalker-v3/smooth_PPO_BipedalWalker-v3_log_410.csv')  #[1100: 1200]
# 拼接到一起
df = df1.append(df2.append(df3))
# 重新排列索引
df.index = range(len(df))
print(df)

# 设置图片大小
plt.figure(figsize=(15, 10))
# 画图
sns.lineplot(data=df, x="timestep", y="reward")