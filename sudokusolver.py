
from solver import parse, Solver
from sys import argv

if __name__=="__main__":
    # open the rules
    solver = parse(open(argv[1], 'r').read())

    #string = arguments.file.read()
    #solver = parse(string)