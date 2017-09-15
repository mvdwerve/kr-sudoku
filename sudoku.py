import operator
from itertools import product
from functools import reduce
import sympy
from sympy.logic.boolalg import simplify_logic

class Sudoku:
    def __init__(self, square):
        self.square_ = int(square)
        self.n_ = self.square_ * self.square_
        self.rules_ = None

        # generate _all_ the variables, in an n*n*n matrix, because each variable has n options in n*n places
        # the indices are row, column, variables, or rather self.vars_[row][column][var]
        names = ['%d_%d_%d' % (j, i, k + 1) for i, j, k in product(range(self.n_), range(self.n_), range(self.n_))]
        self.syms_ = dict(zip(names, sympy.symbols(names)))

    def rules(self):
        if self.rules_ != None:
            return self.rules_

        # we are going to generate the rules

        # 1. every square may only have a _single_ variable set
        # variable ^ all other variables in the depth
        one = reduce(operator.and_, [reduce(operator.xor, [self.var(i, j, k) for k in range(self.n_)]) for i, j in product(range(self.n_), range(self.n_))])

        # 2. every row and column _must_ have all numbers set differently
        # variables in row ^ all other of the same variable in row
        # variables in column ^ all other of the same variable in column
        two_row = reduce(operator.and_, [reduce(operator.xor, [self.var(k, j, i) for k in range(self.n_)]) for i, j in product(range(self.n_), range(self.n_))])
        two_col = reduce(operator.and_, [reduce(operator.xor, [self.var(j, k, i) for k in range(self.n_)]) for i, j in product(range(self.n_), range(self.n_))])
        
        # 3. all elements in a block must be set precisely once
        # for every variable in block ^ other variables in the block
        three = one

        # finally, all the rules should be true, and in cnf
        return one & two_row & two_col & three
        return simplify_logic(one & two_row & two_col & three, form='cnf')

    def var(self, row, column, value):
        return self.syms_['%d_%d_%d' % (row, column, value + 1)]

if __name__=="__main__":
    # create a normal standard sudoku
    sudoku = Sudoku(3)

    # and output the rules
    print(sudoku.rules())