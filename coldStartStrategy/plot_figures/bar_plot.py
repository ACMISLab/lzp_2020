from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns

name_list = ["Function", "Application", "Set_strong\nTop-10", "Set_strong\nTop-15"]
x = list(range(len(name_list)))
num_list = [12, 87, 32, 34]
colors = [sns.xkcd_rgb["denim blue"], sns.xkcd_rgb["orange"], sns.xkcd_rgb["grass green"], sns.xkcd_rgb["pale red"], ]
plt.bar(x, num_list, color=colors, tick_label=name_list)

plt.text(1, 102, '10-min Fixed')
plt.axhline(100, c='0.55', ls='--', linewidth='2')

plt.tick_params(labelsize=12)
#设置坐标轴名称
plt.ylabel('Normalized Memory Waste Time(%)', fontsize=16)

#设置坐标轴刻度
# my_x_ticks = np.arange(0, 101, 20)
my_y_ticks = np.arange(0, 121, 20)
# plt.xticks(my_x_ticks)
plt.yticks(my_y_ticks)

plt.show()