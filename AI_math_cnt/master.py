import os

print(30* '*')
print('Starting to run ALL steps AI...')
print(30* '*')

#############################################
### Etapa 1:
path1 = 'gabaritosnames/'
os.chdir(path1)
os.system(f'python3 generate_gabarito_name.py')

# return to root directory of the master.py script
os.chdir("..")
print(os.getcwd())
#############################################

print(30* '*')
print('All steps AI done!')
print(30* '*')