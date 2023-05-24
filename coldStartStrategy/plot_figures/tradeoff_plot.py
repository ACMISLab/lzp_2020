import matplotlib.pyplot as plt
import numpy as np


ax = plt.subplot()
ax.scatter(81, 12, c='blue', marker='v', label='function')
ax.scatter(39, 87, c='red', marker='>', label='application')
ax.scatter(26, 32, c='green', marker='<', label='Set_strong=10')
ax.scatter(20, 34, c='orange', marker='^', label='Set_strong=15')
# plt.scatter(x, y, color=colors)

plt.text(40, 102, '10-min Fixed')
plt.axhline(100, c='0.55', ls='--', linewidth='2')

plt.tick_params(labelsize=12)
#设置坐标轴名称
plt.xlabel('P75 Cold Start Rate(%)', fontsize=16)
plt.ylabel('Normalized Memory Waste Time(%)', fontsize=16)

#设置坐标轴刻度
my_x_ticks = np.arange(0, 101, 20)
my_y_ticks = np.arange(0, 121, 20)
plt.xticks(my_x_ticks)
plt.yticks(my_y_ticks)

plt.legend(loc='center right')

plt.show()