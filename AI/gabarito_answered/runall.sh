#!/bin/zsh
# Run all the scripts

echo "Please, run all the python scripts."

python fill_answer_gabarito.py
python get_answers.py
python readpng.py
python readpngcnt.py
python readpngtoarray.py

echo "All scritps were executed. Check the results!"