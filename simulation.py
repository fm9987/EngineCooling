import random
import numpy as np

def final(df):
    """ Use this function to actually start the simulation,
    once it is started you can just use this to store the results from
    it inside of df to then send back to main python script"""
    df = df.copy()  # to avoid modifying original df if you want

    # This is used to obtain new columns in the output excel file
    df["Area"] = np.pi * df["r"] ** 2
    df["Temperature"] = [random.randint(1, 100) for _ in range(len(df))]
    return df
