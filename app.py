import sys
import pandas as pd
import random
import os
import numpy as np
import simulation as sim

# READ THE CSV FILE IN HERE
input_file = sys.argv[1]
# input_file="example.csv"
input_dir = os.path.dirname(os.path.abspath(input_file))

#Obtain the dataframe to start with
df = pd.read_csv(input_file)

results=sim.final(df)

#THIS JUST STORES IN THE SAME DIRECTORY (BE CAREFUL ON HOW TO CHANGE THIS)
output_file = os.path.join(input_dir, "output.csv")
results.to_csv(output_file, index=False)

print(os.path.abspath(output_file)) # Optional if you're using stdou

