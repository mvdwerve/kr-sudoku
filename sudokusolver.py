
from solver import parse, Solver
from sys import argv
import numpy as np
import pandas as pd

if __name__=="__main__":
    # open the rules
    solver = parse(open('sudoku_rules_9x9.cnf', 'r').read())
    sudokus = pd.read_csv('sudoku.csv')
    print(sudokus.iloc[1][0])

    for i, c in enumerate(sudokus.iloc[0][0]):
        col = i % 9 
        row = int((i - col) / 9) 
        if col == 0:
            print("")
        print(c, end="")
        unit = 

    #string = arguments.file.read()
    #solver = parse(string)