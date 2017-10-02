import operator
from functools import reduce
from sys import argv
import pandas as pd
from encoder import SudokuMapper, NaiveEncoder, ExtendedNaiveEncoder
from dimacs import DimacsMapper

class Sudoku:
    def __init__(self, square, given, extended = False):
        # create the mapper
        self.mapper = SudokuMapper(square)

    def print(self, solved=True):
        if not solved:
            # first, get all the givens  
            filled = [self.index(el[0]) for el in self.rules() if len(el) == 1] 
            
        else: 
            # get the solution
            sol = self.solve()

            # not satisfiable
            if sol == "UNSAT":
                raise ValueError('UNSAT')
            
            # get the filled
            filled = [el for el in self.solve() if el > 0]

        # sort the variables for easy printing
        vars = [self.varname(idx) for idx in sorted(filled)]

        # the last
        last = (0, 0)

        if len(filled) != self.mapper.n * self.mapper.n:
            raise ValueError("Not solved: " + str(filled))

        # and we get the actual variables
        for var in vars:
            # split it into row_col and value
            rc, val = var.split('__')
            r, c = rc.split('_')

            # print a newline every row
            print("|%.2d" % int(val), end="")

            if int(c) == self.n_ - 1:
                print("")

            # store the last set value
            last = (int(r), int(c))

        # now we convert these numbers to 


if __name__=="__main__":
    # load the 100 sudokus
    sudokus = pd.read_csv('sudoku.csv')

    # the dimension
    dim = int(argv[1])
    ext = argv[2]

    if dim == 3 and False:
        # create a normal standard sudoku
        sudoku = Sudoku(dim, sudokus.iloc[0][0], ext)
    else:
        # for 4d, lets assume no givens
        sudoku = Sudoku(dim, [], ext)

    """
    try:
        sudoku.print(solved=False)
    except:
        pass

    try:
        sudoku.print(solved=True)
    except:
        pass
    # and output the rules
    """

    print(sudoku.dimacs(), end="")