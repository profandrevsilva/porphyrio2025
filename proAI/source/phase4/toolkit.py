import os
import time

def start_time():
    start_time = time.time()
    return start_time

def time_exec(start_time):
    # time of execution in minutes
    time_exec_min = round( (time.time() - start_time)/60, 4)

    print(f'time of execution (preprocessing): {time_exec_min} minutes')
    print('Done!')

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully!")
    else:
        print(f"Folder '{folder_name}' already exists.")