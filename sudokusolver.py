
from solver import parse, Solver
from sys import argv
import numpy as np
import pandas as pd

if __name__=="__main__":
    # open the rules
    solver = parse(open('sudoku_rules_9x9.cnf', 'r').read())
    sudokus = pd.read_csv('sudoku.csv')
    print(sudokus[1, :])

    #string = arguments.file.read()
    #solver = parse(string)