import pandas as pd
import os
import ast

name_acertos = {}

gabarito_math = {1: 'D', 2: 'C', 3: 'B', 4: 'B', 5: 'A', 6: 'D', 7: 'C', 8: 'B', 9: 'B', 10: 'A'}
gabarito_cnt = {11: 'D', 12: 'C', 13: 'B', 14: 'B', 15: 'A', 16: 'D', 17: 'C', 18: 'B', 19: 'B', 20: 'A',
                 21: 'D', 22: 'C', 23: 'B', 24: 'B', 25: 'A', 26: 'D', 27: 'C', 28: 'B', 29: 'B', 30: 'A'}

df_math = pd.read_csv('csv/data_answer_math.csv', sep=',')
df_cnt = pd.read_csv('csv/data_answer_cnt.csv', sep=',')

## MATH
for name, turma, imath in zip(df_math['Nome'], df_math['Turma'], df_math['Respostas']):
    name = name.replace("_", " ")
    respostas_aluno = ast.literal_eval(imath)   # vira dict
    acertos = 0
    for k, correta in gabarito_math.items():
        if respostas_aluno.get(k) == correta:
            acertos += 1

    df = pd.DataFrame([{"Nome": name,
                        "Turma": turma,
                        "Acertos": acertos
                        }])

    path_file = "csv/data_answer_math_acertos.csv"

    # Se o arquivo existir, abre em modo append, sem escrever o cabeçalho de novo
    if os.path.exists(path_file):
        df.to_csv(path_file, mode="a", header=False, index=False)
    else:
        df.to_csv(path_file, index=False)

## CNT
for name, turma, icnt in zip(df_cnt['Nome'], df_cnt['Turma'], df_cnt['Respostas']):
    name = name.replace("_", " ")
    respostas_aluno = ast.literal_eval(icnt)   # vira dict
    acertos = 0
    
    for k, correta in gabarito_cnt.items():
        if respostas_aluno.get(k) == correta:
            acertos += 1

    df = pd.DataFrame([{"Nome": name,
                        "Turma": turma,
                        "Acertos": acertos
                        }])

    path_file = "csv/data_answer_cnt_acertos.csv"

    # Se o arquivo existir, abre em modo append, sem escrever o cabeçalho de novo
    if os.path.exists(path_file):
        df.to_csv(path_file, mode="a", header=False, index=False)
    else:
        df.to_csv(path_file, index=False)

#ic(df_math)
#ic(df_cnt)
