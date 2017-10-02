from itertools import product, chain
from dimacs import DimacsMapper

class SudokuMapper(object):
    """Class makes a deterministic mapping for variables in sudokus."""

    def __init__(self, square):
        self.square = square
        self.n = square * square
        self.names_ = list(sorted([self.var(i, j, k) for i, j, k in product(range(square * square), repeat=3)]))

    def var(self, row, column, value):
        """
        Method to obtain a named variable from a given row, column and 
        value (all starting from zero). 
        """
        return "%d_%d__%d" % (row, column, value + 1)

    def name(self, idx):
        """
        Based on the index, return the name. 
        """
        return self.names_[idx]
        
    def index(self, name):
        """
        Method to convert a given variable name (e.g. 1_2__0) into 
        its index.  
        """
        return self.names_.index(name)

    def inverse(self, name):
        """
        Get a tuple with what the original index was in a tuple (row, column, value)
        """
        # split it into row_col and value
        rc, value = name.split('__')
        row, column = rc.split('_')
        return (row, column, value)

    def size(self):
        return len(self.names_)

class Encoder(object):
    def __init__(self, mapper):
        self.mapper = mapper
        self.cnf_ = [] 

    def add_clause(self, clause):
        # add the clause to the cnf
        self.cnf_.append(clause)

    def add_clauses(self, clauses):
        # add the clauses
        for clause in clauses:
            self.add_clause(clause)

    def encode(self):
        # first off we check if the cnf is non-empty, which would indicate we already did this or loaded something
        if len(self.cnf_) != 0:
            return self.cnf_

        # we are going to actually encode the rules
        self.encode_rules()

        # return the cnf
        return self.cnf_

    def encode_rules(self):
        raise NotImplementedError('encode_rules should be implemented by subclasses')

class NaiveEncoder(Encoder):
    def encode_rules(self):
        # http://sat.inesc.pt/~ines/publications/aimath06.pdf

        # Minimal encoding: 81 nine-ary encodings, 8748 binary
        # 1. at least one number in each entry
        self.add_clauses([[self.mapper.var(x, y, z) for z in range(self.mapper.n)] for x, y in product(range(self.mapper.n), repeat=2)])

        # 2. every number appears at most once in each row/column
        self.add_clauses([["-" + self.mapper.var(x, y, z), "-" + self.mapper.var(i, y, z)] for y, z, x in product(range(self.mapper.n), range(self.mapper.n), range(self.mapper.n - 1)) for i in range(x + 1, self.mapper.n)])
        self.add_clauses([["-" + self.mapper.var(x, y, z), "-" + self.mapper.var(x, i, z)] for x, z, y in product(range(self.mapper.n), range(self.mapper.n), range(self.mapper.n - 1)) for i in range(y + 1, self.mapper.n)])

        # 3. each number appears at most once in each 3x3 subgrid
        self.add_clauses([["-" + self.mapper.var(self.mapper.square*i + x, self.mapper.square*j + y, z), "-" + self.mapper.var(self.mapper.square*i + x, self.mapper.square*j + k, z)] for z, (i, j, x, y) in product(range(self.mapper.n), product(range(self.mapper.square), repeat=4)) for k in range(y + 1, self.mapper.square)])
        self.add_clauses([["-" + self.mapper.var(self.mapper.square*i + x, self.mapper.square*j + y, z), "-" + self.mapper.var(self.mapper.square*i + k, self.mapper.square*j + l, z)] for z, (i, j, l, x, y) in product(range(self.mapper.n), product(range(self.mapper.square), repeat=5)) for k in range(x + 1, self.mapper.square)])

class ExtendedNaiveEncoder(NaiveEncoder):
    def encode_rules(self):
        # http://sat.inesc.pt/~ines/publications/aimath06.pdf
        
        # first we make the naive encoding
        NaiveEncoder.encode_rules(self)

        # 1. at most one number in each entry
        self.add_clauses([["-" + self.mapper.var(x, y, z), "-" + self.mapper.var(x, y, i)] for x, y, z in product(range(self.mapper.n), range(self.mapper.n), range(self.mapper.n - 1)) for i in range(z + 1, self.mapper.n)])

        # 2. every number appears at least once in each row/column
        self.add_clauses([[self.mapper.var(x, y, z) for x in range(self.mapper.n)] for y, z in product(range(self.mapper.n), repeat=2)])
        self.add_clauses([[self.mapper.var(x, y, z) for y in range(self.mapper.n)] for x, z in product(range(self.mapper.n), repeat=2)])

        # 3. each number appears at least once in each 3x3 subgrid
        self.add_clauses([[self.mapper.var(self.mapper.square*i + x, self.mapper.square*j + y, z) for z in range(self.mapper.n)] for i, j, x, y in product(range(self.mapper.square), repeat=4)])

class EfficientEncoder(Encoder):
    def encode_rules(self):
        pass

if __name__=="__main__":
    # we need the argument parser
    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description='Encode the rules for an NxN sudoku.')
    parser.add_argument('--square', type=int, default=3, help='Square to use, e.g. 2 is for a 4x4 sudoku and 3 is for a 3^2 = 9x9 sudoku, etc.')
    parser.add_argument('--encoder', type=str, default='Naive', choices=['Naive', 'ExtendedNaive'])
    args = parser.parse_args()

    # get the square for the mapper and startup the dimacs
    mapper = SudokuMapper(args.square)
    dimacs = DimacsMapper(mapper)

    # we check the encoder
    if args.encoder == 'Naive':
        encoder = NaiveEncoder(mapper)
    elif args.encoder == 'ExtendedNaive':
        encoder = ExtendedNaiveEncoder(mapper)
    
    # now we actually encode the rules
    print(dimacs.encode(encoder.encode()))