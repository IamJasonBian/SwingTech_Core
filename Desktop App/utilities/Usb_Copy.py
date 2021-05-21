# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 13:09:31 2020

@author: Jason
"""

import shutil
import os
import pandas as pd
import re

def movedata():
    fromDirectory = r"C:\Users\Jason\Desktop\Test1"
    toDirectory = r"C:\Users\Jason\Desktop\Test_2"
    
    for i in os.listdir(fromDirectory):
        shutil.move(os.path.join(fromDirectory, i), toDirectory)
    
def pd_read(repo_input):
    pd.read_csv(repo_input)
    
def main():
    repo_input = "C:\\Users\\Jason\\Desktop\\Test_2"
    x = pd.read_csv(repo_input + '\\Data.csv')
    print(x.head())
    
if __name__ == '__main__':
    main()