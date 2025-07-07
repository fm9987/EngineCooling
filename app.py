import sys
import pandas as pd
import random
import os
import numpy as np
from Regen import final as regen
# import Film as film
import json

# READ THE CSV FILE IN HERE
# input_file = sys.argv[1]
input_file="example.csv"
input_dir = os.path.dirname(os.path.abspath(input_file))

#Obtain the dataframe to start with
Types = os.path.join(os.path.dirname(__file__), 'IC.json')
with open(Types, 'r') as f:
    Types = json.load(f)
df = pd.read_csv(input_file)

regen_enabled = Types.get('regen', False)
film_enabled = Types.get('film', False)

if regen_enabled & film_enabled:
    print("They are both ON")
    results=regen(df)
elif regen_enabled:
    # print("Regenerative cooling is ON")
    results=regen(df)
elif film_enabled:
    # print("Film cooling is ON")
    # Results=film.final(df)
    results=regen(df)
else:
    # results=pd.read_csv("output.csv")
    results=regen(df)
    # print("They are both off dummy")

# #THIS JUST STORES IN THE SAME DIRECTORY (BE CAREFUL ON HOW TO CHANGE THIS)
output_file = os.path.join(input_dir, "output.csv")
results.to_csv(output_file, index=False)

print(os.path.abspath(output_file)) # Optional if you're using stdou