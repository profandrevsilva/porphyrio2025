#!/bin/zsh
# Run all the scripts

echo "Please, run all the python scripts."

for i in {1..100}; do    
    python fill_answer_gabarito.py
    python get_answers.py
    #python readpng_math.py
    #python readpng_cnt.py
    python readpngtoarray.py
    detectCirclesToAnswer.py

    sleep 2
done

echo "All scritps were executed. Check the results!"
