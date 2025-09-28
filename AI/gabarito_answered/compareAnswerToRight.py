import pandas as pd
import numpy as np
import os
from icecream import ic

df_math = pd.read_csv('csv/data_answer_math.csv', sep=',')
df_cnt = pd.read_csv('csv/data_answer_cnt.csv', sep=',')

ic(df_math)
ic(df_cnt)
