# -*- coding: utf-8 -*-

import sys
import numpy as np
if __name__ == '__main__':
    for i in range(1, len(sys.argv)):
        num = sys.argv[i]
    print(num)
    num = num[1:-1]
    num = num.replace(' ','')
    num = num.split(",")
    num = list(map(int, num))
    num = np.array(num)
    num = num.reshape(-1, 1)
