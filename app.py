import sys
import pandas as pd
import random
import os

input_file = sys.argv[1]
df = pd.read_csv(input_file)

df["Temperature"] = [random.randint(1, 100) for _ in range(len(df))]
output_file = "output.csv"
df.to_csv(output_file, index=False)

print(os.path.abspath(output_file))  # Optional if you're using stdout