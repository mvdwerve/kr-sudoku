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
        self.names_ = ['%d_%d_%d' % (i, j, k + 1) for i, j, k in product(range(self.n_), repeat=3)]
        #self.syms_ = dict(zip(self.names_, sympy.symbols(self.names_)))

        # the context and the found highest
        self.ctx_ = bx.Context()
        self.highest_ = 0

        # nothing given yet
        self.given_ = None

        # add the givens
        for i, c in enumerate(given):
            # if nothing is given, we skip
            if c == '.':
                continue

            # calculate the row and colum
            col = i % 9 
            row = int((i - col) / 9) 
            
            # get the variable and add it as a unit clause
            var = self.var(row, col, int(c) - 1)
            self.given_ = var if self.given_ == None else self.given_ & var


    def rules(self):
        if self.rules_ != None:
            return self.rules_

        # we are going to generate the rules

        # 1. every square may only have a _single_ variable set
        # variable ^ all other variables in the depth
        one = reduce(operator.and_, [reduce(operator.xor, [self.var(i, j, k) for k in range(self.n_)]) for i, j in product(range(self.n_), repeat=2)])

        # 2. every row and column _must_ have all numbers set differently
        # variables in row ^ all other of the same variable in row
        # variables in column ^ all other of the same variable in column
        two_row = reduce(operator.and_, [reduce(operator.xor, [self.var(k, j, i) for k in range(self.n_)]) for i, j in product(range(self.n_), repeat=2)])
        two_col = reduce(operator.and_, [reduce(operator.xor, [self.var(j, k, i) for k in range(self.n_)]) for i, j in product(range(self.n_), repeat=2)])
        
        # 3. all elements in a block must be set precisely once
        # for every variable in block ^ other variables in the block
        block_rule = reduce(operator.and_, [reduce(operator.xor, [self.var(br + i, bc + j, k) for i, j in product(range(self.square_), repeat=2)]) for br, bc, k in product(range(self.square_), range(self.square_), range(self.n_))])

        # all rules should be true
        total = one & two_row & two_col & block_rule & self.given_

        # finally, all the rules should be true, and in cnf
        return total.simplify().tseytin(self.ctx_).simplify()

    def var(self, row, column, value):
        return self.ctx_.get_var('%d_%d_%d' % (row, column, value + 1))

    def extract(self, var):
        name = str(var)
        return name[1:] if name[0] == '~' else name 

    def index(self, var):
        name = self.extract(var)
        if 'a' in name:
            found = int(name[2:])
            self.highest_ = max(self.highest_, found)
            return len(self.names_) + found
        return self.names_.index(name) + 1

    def dimac_sentence(self, expr):
        if isinstance(expr, bx.Variable):
            return str(self.index(expr))
        elif isinstance(expr, bx.Complement):
            return "-" + str(self.index(expr))
        else:
            return " ".join([self.dimac_sentence(ex) for ex in expr.args])

    def cnf_sentence(self, expr):
        if isinstance(expr, bx.Variable):
            return [self.index(expr)]
        elif isinstance(expr, bx.Complement):
            return [-self.index(expr)]
        else:
            return [self.cnf_sentence(ex)[0] for ex in expr.args]  

    def dimacs(self):
        # get the rules once
        rules = self.rules().args

        # do a nice list comprehension
        l = "\n".join([" ".join([str(c) for c in self.cnf_sentence(rule)]) + " 0" for rule in rules])

        # the header that is required
        header = "p cnf %d %d\n" % (len(self.names_) + self.highest_, len(rules)) 

        # simply append
        return header + l

    def solve(self):
        # get the rules
        rules = self.rules().args

        # now we map it to the numeric vars
        cnf = [self.cnf_sentence(rule) for rule in rules]

        print(cnf)

        # solve using pycosat
        return pycosat.solve(cnf)

    def print(self, solved=True):
        # first, get all the givens  
        filled = [self.index(el.args[0]) for el in self.rules().args if len(el.args) == 1] if not solved else [el for el in self.solve() if el > 0]
        
        # and we get the indices that
        print(len(filled))

        # now we convert these numbers to 

if __name__=="__main__":
    # load the 100 sudokus
    sudokus = pd.read_csv('sudoku.csv')

    # create a normal standard sudoku
    sudoku = Sudoku(int(argv[1]), sudokus.iloc[0][0])

    # and output the rules
    #sudoku.print(solved=False)
    #sudoku.print(solved=True)
    print(sudoku.dimacs())