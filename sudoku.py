from encoder import SudokuMapper, NaiveEncoder, ExtendedNaiveEncoder, EfficientEncoder, GivensEncoder
from dimacs import DimacsMapper

import pandas as pd

# these are a 16x16 and 25x25 sudoku so that we have givens
fourbyfour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10, 11, 12, 13, 14, 15, 1, 0, 0, 2, 3, 4, 0, 0, 11, 0, 6, 0, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 7, 0, 0, 3, 0, 0, 9, 9, 6, 10, 0, 11, 0, 0, 9, 0, 0, 1, 0, 12, 0, 10, 0, 0, 13, 0, 3, 0, 0, 14, 2, 0, 0, 13, 0, 0, 0, 9, 0, 0, 11, 0, 12, 0, 0, 0, 8, 0, 0, 9, 0, 11, 2, 0, 1, 14, 0, 0, 0, 10, 7, 6, 0, 0, 0, 15, 0, 0, 0, 14, 0, 0, 5, 12, 0, 0, 0, 9, 0, 5, 14, 0, 0, 4, 0, 8, 0, 0, 10, 0, 15, 0, 0, 5, 9, 11, 0, 0, 1, 0, 0, 0, 0, 0, 8, 0, 0, 2, 0, 0, 0, 0, 0, 12, 0, 0, 11, 5, 8, 0, 0, 3, 0, 12, 0, 0, 14, 0, 3, 0, 0, 13, 8, 0, 15, 0, 0, 0, 5, 8, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 12, 9, 14, 0, 0, 0, 11, 4, 0, 6, 15, 0, 12, 0, 0, 7, 0, 0, 0, 5, 0, 3, 0, 0, 11, 0, 0, 0, 6, 0, 0, 4, 10, 0, 0, 15, 0, 7, 0, 0, 15, 0, 5, 0, 13, 0, 0, 1, 0, 0, 2, 0, 10, 1, 14, 9, 0, 0, 12, 0, 0, 2, 0, 0, 0, 13, 0, 0, 0, 13, 0, 0, 0, 10, 0, 2, 0, 0, 12, 3, 5, 0, 0, 11]
fivebyfive = [1, 2, 0, 0, 0, 6, 0, 0, 0, 0, 0, 12, 0, 0, 15, 0, 0, 18, 19, 0, 0, 22, 0, 0, 25, 0, 0, 8, 0, 10, 0, 12, 13, 0, 0, 0, 17, 0, 0, 20, 21, 22, 0, 0, 0, 0, 0, 3, 4, 0, 11, 12, 0, 0, 0, 0, 17, 18, 0, 0, 21, 0, 23, 0, 0, 1, 2, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 19, 0, 0, 0, 0, 24, 25, 0, 0, 0, 4, 0, 0, 0, 0, 0, 10, 11, 0, 0, 0, 15, 0, 0, 23, 0, 25, 1, 0, 0, 4, 0, 6, 0, 8, 0, 0, 0, 0, 13, 14, 0, 16, 12, 0, 0, 0, 2, 0, 0, 5, 0, 0, 8, 9, 0, 0, 12, 13, 0, 0, 0, 0, 0, 19, 0, 21, 0, 0, 0, 25, 1, 22, 0, 0, 10, 0, 0, 0, 0, 15, 0, 0, 0, 19, 20, 0, 0, 0, 0, 25, 16, 0, 18, 4, 0, 0, 0, 13, 0, 0, 0, 17, 0, 0, 0, 21, 0, 0, 0, 0, 1, 2, 0, 4, 0, 0, 7, 0, 9, 0, 0, 0, 0, 19, 0, 21, 0, 0, 24, 25, 0, 2, 0, 0, 5, 0, 7, 0, 0, 10, 0, 0, 0, 0, 0, 16, 0, 0, 24, 0, 11, 12, 13, 0, 0, 0, 0, 18, 9, 0, 0, 0, 23, 0, 0, 0, 2, 0, 0, 20, 0, 23, 0, 0, 1, 0, 0, 0, 5, 0, 7, 0, 14, 0, 0, 12, 0, 0, 15, 0, 17, 18, 0, 20, 0, 0, 8, 0, 0, 0, 12, 13, 0, 10, 0, 0, 18, 0, 15, 0, 0, 23, 0, 0, 0, 0, 0, 4, 25, 0, 0, 0, 14, 0, 0, 17, 0, 19, 0, 0, 22, 0, 0, 0, 0, 2, 0, 0, 0, 6, 7, 8, 0, 0, 0, 12, 0, 0, 20, 0, 0, 0, 0, 0, 1, 0, 3, 0, 0, 6, 0, 8, 9, 0, 0, 0, 0, 14, 0, 0, 17, 0, 0, 10, 6, 0, 8, 4, 0, 0, 0, 0, 9, 20, 0, 0, 0, 14, 0, 21, 0, 0, 0, 0, 1, 0, 4, 0, 6, 0, 0, 9, 0, 0, 0, 13, 14, 15, 0, 0, 0, 0, 20, 21, 0, 0, 0, 0, 1, 0, 3, 0, 0, 0, 0, 13, 24, 0, 0, 0, 0, 0, 0, 21, 0, 23, 9, 0, 0, 0, 0, 14, 0, 0, 0, 8, 0, 15, 0, 22, 0, 0, 20, 0, 2, 0, 0, 25, 0, 7, 0, 0, 5, 0, 0, 8, 0, 10, 0, 17, 0, 9, 20, 0, 0, 0, 0, 25, 0, 17, 0, 19, 0, 0, 22, 0, 0, 0, 0, 2, 13, 4, 0, 0, 0, 0, 0, 0, 21, 2, 0, 0, 0, 1, 0, 8, 0, 0, 0, 0, 13, 0, 0, 11, 17, 0, 0, 20, 16, 0, 0, 0, 1, 0, 0, 9, 0, 0, 17, 0, 14, 15, 0, 0, 0, 19, 0, 16, 0, 23, 0, 0, 0, 0, 0, 4, 0, 11, 0, 13, 0, 0, 0, 12, 18, 0, 0, 0, 0, 23, 24, 0, 1, 0, 3, 0, 5, 0, 2, 0, 0, 0, 0, 17, 0, 0, 0, 21, 0, 0, 0, 0, 0, 2, 3, 0, 5, 0, 0, 0, 0, 0, 11, 12, 0, 0, 20, 0, 0, 0, 24, 25, 0, 0, 3, 0, 5, 0, 7, 0, 0, 0, 0, 12, 0, 14, 0, 16, 0, 18, 0, 25, 0, 0, 3, 0, 5, 0, 0, 0, 9, 0, 16, 0, 0, 0, 0, 0, 17, 0, 19, 20, 0, 0, 23, 0]

# normal 9x9 sudoku is 
def getnormal(rand=False):
    # normal sudoku is really easy
    sudokus = pd.read_csv('sudoku.csv')

    # only do the first one for now
    return [int(x) if x != '.' else 0 for x in sudokus.iloc[0][0]] if not rand else None

# get a sudoku
def getsudoku(square):
    # the square may not exist
    if not square in [3, 4, 5]:
        raise NotImplementedError('currently we cannot test that')
    
    # return the right sudoku for the job
    if square == 3:
        return getnormal()
    if square == 4:
        return fourbyfour
    if square == 5:
        return fivebyfive

if __name__=="__main__":
    # we need the argument parser
    import argparse

    # make the encoders
    encoders = {
        'naive': NaiveEncoder,
        'extended': ExtendedNaiveEncoder,
        'efficient': EfficientEncoder
    }

    # parse arguments
    parser = argparse.ArgumentParser(description='Encode the rules for an NxN sudoku.')
    parser.add_argument('--square', type=int, default=3, help='Square to use, e.g. 2 is for a 4x4 sudoku and 3 is for a 3^2 = 9x9 sudoku, etc.')
    parser.add_argument('--encoder', type=str, default='naive', choices=list(encoders.keys()))
    args = parser.parse_args()

    # get the square for the mapper and startup the dimacs
    mapper = SudokuMapper(args.square)
    dimacs = DimacsMapper(mapper)

    # get the encoder
    encoder = encoders[args.encoder](mapper)
    
    # get a sudoku
    sudoku = getsudoku(args.square)

    # now we actually encode the rules
    print(dimacs.encode(encoder.encode() + GivensEncoder(mapper, sudoku).encode()))