import operator
from itertools import product
from functools import reduce
from sys import argv
import pandas as pd

class Sudoku:
    def __init__(self, square, given, extended = False):
        self.square_ = int(square)
        self.n_ = self.square_ * self.square_
        self.rules_ = None
        self.ext_rules_ = extended

        # generate _all_ the variables, in an n*n*n matrix, because each variable has n options in n*n places
        # the indices are row, column, variables, or rather self.vars_[row][column][var]
        self.names_ = ['%d_%d__%d' % (i, j, k + 1) for i, j, k in product(range(self.n_), repeat=3)]

        # the context and the found highest
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

        self.generatedrules_ = False

    def add_clause(self, clause):
        # todo: don't add double clauses
        self.total_.append(clause)

    def add_clauses(self, clauses):
        for clause in clauses:
            self.add_clause(clause)

    def rules(self):
        if self.generatedrules_:
            return self.total_

        # http://sat.inesc.pt/~ines/publications/aimath06.pdf

        # Minimal encoding: 81 nine-ary encodings, 8748 binary
        # 1. at least one number in each entry
        self.add_clauses([[self.var(x, y, z) for z in range(self.n_)] for x, y in product(range(self.n_), repeat=2)])

        # 2. every number appears at most once in each row/column
        self.add_clauses([["-" + self.var(x, y, z), "-" + self.var(i, y, z)] for y, z, x in product(range(self.n_), range(self.n_), range(self.n_ - 1)) for i in range(x + 1, self.n_)])
        self.add_clauses([["-" + self.var(x, y, z), "-" + self.var(x, i, z)] for x, z, y in product(range(self.n_), range(self.n_), range(self.n_ - 1)) for i in range(y + 1, self.n_)])

        # 3. each number appears at most once in each 3x3 subgrid
        self.add_clauses([["-" + self.var(self.square_*i + x, self.square_*j + y, z), "-" + self.var(self.square_*i + x, self.square_*j + k, z)] for z, i, j, x, y in product(range(self.n_), range(self.square_), range(self.square_), range(self.square_), range(self.square_)) for k in range(y + 1, self.square_)])
        self.add_clauses([["-" + self.var(self.square_*i + x, self.square_*j + y, z), "-" + self.var(self.square_*i + k, self.square_*j + l, z)] for z, i, j, x, y in product(range(self.n_), range(self.square_), range(self.square_), range(self.square_), range(self.square_)) for k in range(x + 1, self.square_)  for l in range(self.square_)])

        # Extended encoding:
        if self.ext_rules_:
            # 1. at most one number in each entry
            self.add_clauses([["-" + self.var(x, y, z), "-" + self.var(x, y, i)] for x, y, z in product(range(self.n_), range(self.n_), range(self.n_ - 1)) for i in range(z + 1, self.n_)])

            # 2. every number appears at least once in each row/column
            self.add_clauses([[self.var(x, y, z) for x in range(self.n_)] for y, z in product(range(self.n_), repeat=2)])
            self.add_clauses([[self.var(x, y, z) for y in range(self.n_)] for x, z in product(range(self.n_), repeat=2)])

            # 3. each number appears at least once in each 3x3 subgrid
            self.add_clauses([[self.var(self.square_*i + x, self.square_*j + y, z) for z in range(self.n_)] for i, j, x, y in product(range(self.square_), repeat=4)])

        # we now generated the rules
        self.generatedrules_ = True

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

    def varname(self, index):
        return self.names_[abs(index) - 1]

    def dimac_sentence(self, expr):
        return " ".join([str(self.index(ex)) for ex in expr])

    def dimacs(self):
        # get the rules once
        rules = self.rules()

        # do a nice list comprehension
        l = "\n".join([" ".join([str(el) for el in rule]) + " 0" for rule in self.cnf()])

        # the header that is required
        header = "p cnf %d %d\n" % (len(self.names_), len(rules)) 

        # simply append
        return header + l

    def cnf(self):
        return [[self.index(ex) for ex in rule] for rule in self.rules()]

    def solve(self):
        # solve using pycosat
        return pycosat.solve(self.cnf())

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

        if len(filled) != self.n_ * self.n_:
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

    if dim == 3:
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