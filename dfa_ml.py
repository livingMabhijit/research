
from tensorflow import keras

import numpy as np
from enum import IntEnum

from sklearn import preprocessing
lb = preprocessing.LabelEncoder()
cls = [10110,10120,12110,13170,15110]
lb.fit(cls)

## data ingest
file = open("/home/abhijit/DFA_class/deployment/L35001002_20180101_000808.pqd.bin", "rb")
data = np.fromfile(file, '<f4')
print('Data shape : '+ str(data.shape))
arr_size = data.shape[0]
data1 = []
data1.append(data)


class Indx(IntEnum):
    ID = 0
    MONITOR = 1
    RECORD = 2
    FILE = 3
    CLASS = 4
    POSITION = 5
    PHASE = 6
    GROUND = 7
    FREQ = 8
    SECONDS = 9
    BLOB = 10
class SIndx(IntEnum):
    ID = 0
    NAME = 1
    PT_S_A = 2
    PT_S_B = 3
    PT_S_C = 4
    PT_P_A = 5
    PT_P_B = 6
    PT_P_C = 7
    CT_S_A = 8
    CT_S_B = 9
    CT_S_C = 10
                                                                                                                          1,1           Top