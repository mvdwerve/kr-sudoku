import operator
from itertools import product
from functools import reduce
import sympy
from sys import argv
import boolexpr as bx
import pandas as pd
import pycosat 

class Sudoku:
    def __init__(self, square, given):
        self.square_ = int(square)
        self.n_ = self.square_ * self.square_
        self.rules_ = None

        # generate _all_ the variables, in an n*n*n matrix, because each variable has n options in n*n places
        # the indices are row, column, variables, or rather self.vars_[row][column][var]
        self.names_ = ['%d_%d__%d' % (i, j, k + 1) for i, j, k in product(range(self.n_), repeat=3)]
        #self.syms_ = dict(zip(self.names_, sympy.symbols(self.names_)))

        # the context and the found highest
        self.ctx_ = bx.Context()
        self.highest_ = 0

        # nothing given yet
        self.total_ = []

        # add the givens
        for i, c in enumerate(given):
            # if nothing is given, we skip
            if c == '.':
                continue

            # calculate the row and colum
            col = i % 9 
            row = int((i - col) / 9) 
            
            # get the variable and add it as a unit clause
            self.add_clause([self.var(row, col, int(c) - 1)])

    def add_clause(self, clause):
        # todo: don't add double clauses
        self.total_.append(clause)

    def rules(self):
        # 1. every square _must_ have a single one set
        for row, column in product(range(self.n_), repeat=2):
            self.add_clause([self.var(row, column, v) for v in range(self.n_)])

        # 2. every number must be set in a row at least once
        for v in range(self.n_):
            for i in range(self.n_):
                self.add_clause([self.var(i, j, v) for j in range(self.n_)])
                self.add_clause([self.var(j, i, v) for j in range(self.n_)])

        # blocks should have every number _at least_ once
        for v in range(self.n_):
            for br, bc in product(range(self.square_), repeat=2):
                self.add_clause([self.var(br + i, bc + j, v) for i, j in product(range(self.square_), repeat=2)])

        # each cell may have _at most_ a single entry
        for r, c in product(range(self.n_), repeat=2):
            for v in range(self.n_ - 1):
                self.add_clause(["-" + self.var(r, c, v), "-" + self.var(r, c, v + 1)])

        # finally, all the rules should be true, and in cnf
        return self.total_

    def var(self, row, column, value):
        return '%d_%d__%d' % (row, column, value + 1)

    def extract(self, var):
        name = str(var)
        return name[1:] if name[0] == '-' else name 

    def index(self, var):
        mult = -1 if var[0] == '-' else 1
        return mult * (self.names_.index(self.extract(var)) + 1)

    def dimac_sentence(self, expr):
        return " ".join([str(self.index(ex)) for ex in expr])

    def dimacs(self):
        # get the rules once
        rules = self.rules()

        # do a nice list comprehension
        l = "\n".join([self.dimac_sentence(rule) + " 0" for rule in rules])

        # the header that is required
        header = "p cnf %d %d\n" % (len(self.names_) + self.highest_, len(rules)) 

        # simply append
        return header + l

    def solve(self):
        # get the rules
        rules = self.rules()

        # now we map it to the numeric vars
        cnf = [[self.index(ex) for ex in rule] for rule in rules]

        # solve using pycosat
        return pycosat.solve(cnf)

    def print(self, solved=True):
        # first, get all the givens  
        filled = [self.index(el[0]) for el in self.rules() if len(el) == 1] if not solved else [el for el in self.solve() if el > 0]
        
        # and we get the indices that
        print(len(filled))

        # now we convert these numbers to 


if __name__=="__main__":
    # load the 100 sudokus
    sudokus = pd.read_csv('sudoku.csv')

    # create a normal standard sudoku
    sudoku = Sudoku(int(argv[1]), sudokus.iloc[0][0])

    sudoku.print(solved=False)
    sudoku.print(solved=True)

    # and output the rules
    #print(sudoku.dimacs(), end="")