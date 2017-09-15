import operator
from itertools import product
from functools import reduce
import sympy
from sympy.logic.boolalg import simplify_logic, to_cnf, Not
from sys import argv

class Sudoku:
    def __init__(self, square):
        self.square_ = int(square)
        self.n_ = self.square_ * self.square_
        self.rules_ = None

        # generate _all_ the variables, in an n*n*n matrix, because each variable has n options in n*n places
        # the indices are row, column, variables, or rather self.vars_[row][column][var]
        self.names_ = ['%d_%d_%d' % (j, i, k + 1) for i, j, k in product(range(self.n_), repeat=3)]
        self.syms_ = dict(zip(self.names_, sympy.symbols(self.names_)))

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
        total = one & two_row & two_col & block_rule

        # finally, all the rules should be true, and in cnf
        return to_cnf(total)

    def var(self, row, column, value):
        return self.syms_['%d_%d_%d' % (row, column, value + 1)]

    def index(self, var):
        return self.names_.index(var.name) + 1

    def dimacs(self):
        # get the rules once
        rules = self.rules().args

        # the header that is required
        header = "p cnf %d %d\n" % (len(self.names_), len(rules)) 
        
        # do a nice list comprehension
        l = "\n".join([" ".join(["%s%d" % ("-" if isinstance(a, Not) else "", sudoku.index(a.args[0] if isinstance(a, Not) else a)) for a in rule.args]) for rule in rules])

        # simply append
        return header + l

if __name__=="__main__":
    # create a normal standard sudoku
    sudoku = Sudoku(int(argv[1]))

    # and output the rules
    print(sudoku.dimacs())