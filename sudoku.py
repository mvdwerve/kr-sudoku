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

    def add_clauses(self, clauses):
        for clause in clauses:
            self.add_clause(clause)

    def rules(self):
        # http://sat.inesc.pt/~ines/publications/aimath06.pdf

        # 1. at least one number in each entry
        self.add_clauses([[self.var(x, y, z) for z in range(self.n_)] for x, y in product(range(self.n_), repeat=2)])

        # 2. every number appears at most once in each row/column
        self.add_clauses([["-" + self.var(x, y, z), "-" + self.var(i, y, z)] for y, z, x in product(range(self.n_), range(self.n_), range(self.n_ - 1)) for i in range(x + 1, self.n_)])
        self.add_clauses([["-" + self.var(x, y, z), "-" + self.var(x, i, z)] for y, z, x in product(range(self.n_), range(self.n_), range(self.n_ - 1)) for i in range(x + 1, self.n_)])

        # 3. each number appears at most once in each 3x3 subgrid
        self.add_clauses([["-" + self.var(3*i + x, 3*j + y, z), "-" + self.var(3*i + x, 3*j + k, z)] for z, i, j, x, y in product(range(self.n_), range(self.square_), range(self.square_), range(self.square_), range(self.square_)) for k in range(y + 1, self.square_)])
        self.add_clauses([["-" + self.var(3*i + x, 3*j + y, z), "-" + self.var(3*i + k, 3*j + l, z)] for z, i, j, x, y in product(range(self.n_), range(self.square_), range(self.square_), range(self.square_), range(self.square_)) for k in range(y + 1, self.square_)  for l in range(self.square_)])

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
        print(rules)

        # now we map it to the numeric vars
        cnf = [[self.index(ex) for ex in rule] for rule in rules]

        # solve using pycosat
        return pycosat.solve(cnf)

    def print(self, solved=True):
        print(self.solve())
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