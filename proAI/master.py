#################################################
# Author: Andre Silva: @andvsilva
# github: https://github.com/andvsilva
# Description: This code runs all steps of the AI
# ter 30 set 2025
#################################################

import os
import toolkit as tool
import shutil
import time

# Get start time 
start_time = time.time()

print(50* '*')
print('Starting to run ALL steps AI...')
print(50* '*')

## Folder names:
gabaritos = 'gabaritos/'
names = 'names/'
pdfs = 'pdfs/'
csv = 'csv/'
allpdfs = 'allpdfs'
src = "data/"
toolkit = "toolkit.py"
source1 = "source/phase1/"

########################################################
# Create folders
tool.create_folder(gabaritos)
os.chdir(gabaritos)
tool.create_folder(names)
os.chdir(names)
tool.create_folder(pdfs)
tool.create_folder(csv)
tool.create_folder(allpdfs)

# Change to root directory
os.chdir("../../")
dst = os.path.join(gabaritos, names)
shutil.copytree(src, dst, dirs_exist_ok=True)  # copia pasta 
shutil.copytree(source1, dst, dirs_exist_ok=True)

## toolkit 
dst = os.path.join(gabaritos, names, 'toolkit.py')
shutil.copy('toolkit.py', dst)

## model - gabarito
dst = os.path.join(gabaritos, names, 'main.pdf')
shutil.copy('model/main.pdf', dst)

############################################################
# Run Phase 1:
os.chdir(gabaritos)
os.chdir(names)

os.system(f'python3 generate_gabarito_name.py')

# return to root directory of the master.py script
#os.chdir("..")
#print(os.getcwd())
#############################################


# time of execution in minutes
time_exec_min = round( (time.time() - start_time)/60, 4)

print(f'time of execution (preprocessing): {time_exec_min} minutes')
print('generate gabarito with names. Done!')

print(50* '*')
print('All steps AI done!')
print(50* '*')