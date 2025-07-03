import random
import pandas as pd
import csv
import os

# Write to CSV
numbers = [random.randint(1, 100) for _ in range(100)]
output_file = "output.csv"

with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Temperature"])
    for num in numbers:
        writer.writerow([num])

# ✅ Output ONLY the file path, nothing else
print(os.path.abspath(output_file))
