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
start_time = tool.start_time()

print(50* '*')
print('Starting to run ALL the steps AI...')
print(50* '*')

########################################################
#### Phase 1 

## Folder names:
gabaritos = 'gabaritos/'
names = 'names/'
pdfs = 'pdfs/'
csv = 'csv/'
allpdfs = 'allpdfs'
src = "data/"
toolkit = "toolkit.py"
source1 = "source/phase1/"

# Create folders
tool.create_folder(gabaritos)
os.chdir(gabaritos)
tool.create_folder(names)
os.chdir(names)
tool.create_folder(pdfs)
tool.create_folder(csv)
tool.create_folder(allpdfs)

# Change to root directory and copy files
os.chdir("../../")
dst = os.path.join(gabaritos, names)
shutil.copytree(src, dst, dirs_exist_ok=True)
shutil.copytree(source1, dst, dirs_exist_ok=True)

## toolkit 
dst = os.path.join(gabaritos, names, 'toolkit.py')
shutil.copy('toolkit.py', dst)

## model - gabarito
dst = os.path.join(gabaritos, names, 'main.pdf')
shutil.copy('model/main.pdf', dst)

# Run Phase 1:
os.chdir(gabaritos)
os.chdir(names)

os.system(f'python3 generate_gabarito_name.py')

# return to root directory of the master.py script
os.chdir("../../")

#############################################
### Phase 2
source2 = "source/phase2/"

os.chdir(gabaritos)

filled = "preenchidos/"
tool.create_folder(filled)
os.chdir(filled)
tool.create_folder(pdfs)
os.chdir("../../")

dst = os.path.join(gabaritos, filled)
shutil.copytree(source2, dst, dirs_exist_ok=True)

# Run Phase 2:
os.chdir(gabaritos)
os.chdir(filled)

os.system(f'python3 fill_answer_all.py')
############################################
### Phase 3
os.chdir("../../")

source3 = "source/phase3/"

os.chdir(gabaritos)
answers = 'respostas/'
tool.create_folder(answers)
os.chdir("../")

dst = os.path.join(gabaritos, answers)
shutil.copytree(source3, dst, dirs_exist_ok=True)

screenshots = 'screenshots/'
os.chdir(gabaritos)
os.chdir(answers)

tool.create_folder(screenshots)
os.chdir(screenshots)

math = 'math/'
cnt = 'cnt/'
tool.create_folder(math)
tool.create_folder(cnt)

os.chdir("../")
os.system(f'python3 get_answersALL.py')
############################################
### Phase 4
os.chdir("../../")

source4 = "source/phase4/"

os.chdir(gabaritos)
acertos = 'acertos/'
tool.create_folder(acertos)
os.chdir("../")

dst = os.path.join(gabaritos, acertos)
shutil.copytree(source4, dst, dirs_exist_ok=True)

os.chdir(gabaritos)
os.chdir(acertos)
tool.create_folder(screenshots)
os.chdir(screenshots)
corrected = 'corrected/'
tool.create_folder(corrected)
os.chdir('corrected/')

tool.create_folder(math)
tool.create_folder(cnt)
os.chdir("../../")

tool.create_folder(csv)

### >>> CNT
os.system(f'python3 detectCirclesToAnswerCNT_ALL.py')
os.system(f'python3 detectCirclesToAnswerMATH_ALL.py')

# time of execution in minutes
time_exec_min = round( (time.time() - start_time)/60, 4)

print(f'time of execution (preprocessing): {time_exec_min} minutes')
print('generate gabarito with names. Done!')

print(50* '*')
print('All steps AI done!')
print(50* '*')

tool.time_exec(start_time)