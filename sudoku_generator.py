import itertools
import sys
import random
import copy
import z3 


def rows():
    return range(0,9)


def cols():
    return range(0,9)


def solve(initial_values):
    s = z3.Solver()
    cells = [[None for _ in cols()] for _ in rows()]

    # Constrain the solver with initially known values
    for r in rows():
        for c in cols():
            v = z3.Int('c_%d_%d' % (r, c))
            cells[r][c] = v
            if (r,c) in initial_values:
                s.add(v == initial_values[(r, c)])

    # Add normal sudoku contraints - unit, row & column 
    add_constraints(s, cells)
    sudoku = {}

    # If the sudoku is solvable
    if s.check() == z3.sat:
        m = s.model()
        for r in rows():
            for c in cols():
                v = m.evaluate(cells[r][c])
                sudoku[(r, c)] = v
    return sudoku


# Helper function to add constraints, with only classic constraints a bit superfluous
def add_constraints(solver, cells):
    classic_constraints(solver, cells)


def classic_constraints(solver, cells):
    for r in rows():
        for c in cols():
            v = cells[r][c]
            solver.add(z3.And(v >= 1, v <= 9))

    for r in rows():
        solver.add(z3.Distinct(cells[r]))
    
    for c in cols():
        solver.add(z3.Distinct([cells[r][c] for r in rows()]))
    
    offsets = list(itertools.product(range(0,3), range(0,3)))
    for r in range(0, 9, 3):
        for c in range(0, 9, 3):
            group_cells = []
            for dy, dx in offsets:
                group_cells.append(cells[r+dy][c+dx])
            solver.add(z3.Distinct(group_cells))


def uniquely_solvable(initial_values):
    solvable = False
    unique = True

    s = z3.Solver()
    cells = [ [ None for _ in cols() ] for _ in rows() ]
    for r in rows():
        for c in cols():
            v = z3.Int('c_%d_%d' % (r, c))
            cells[r][c] = v
            if (r, c) in initial_values:
                s.add(v == initial_values[(r, c)])

    add_constraints(s, cells)

    cells2 = [ [ None for _ in cols() ] for _ in rows() ]
    cond_list = []

    # Sudoku is solvable
    if s.check() == z3.sat:
        solvable = True
        m = s.model()
        for r in rows():
            for c in cols():
                v2 = z3.Int('c_%d_%d' % (r, c))
                cells2[r][c] = v2
                if (r, c) in initial_values:
                    s.add(v2 == initial_values[(r, c)])
                else:
                    cond_list.append((v2 != m.evaluate(cells[r][c])))
        s.add(z3.Or(cond_list))
    
    # Sudoku has another solution
    if s.check() == z3.sat:
        unique = False
    
    return solvable and unique 


def make_starting_board():
    # Fill in first row in random order and let solve fill in the rest
    initial_numbers =['1', '2', '3', '4', '5', '6', '7', '8', '9']
    random.shuffle(initial_numbers)
    sudoku = solve({
        (0, 0): initial_numbers[0],
        (0, 1): initial_numbers[1],
        (0, 2): initial_numbers[2],
        (0, 3): initial_numbers[3],
        (0, 4): initial_numbers[4],
        (0, 5): initial_numbers[5],
        (0, 6): initial_numbers[6],
        (0, 7): initial_numbers[7],
        (0, 8): initial_numbers[8],
    })
    return sudoku 


def fill_sudoku(sudoku, starting_board):
    coordinate = (random.randint(0, 8), random.randint(0,8))

    while sudoku.get(coordinate) != None:
        coordinate = (random.randint(0, 8), random.randint(0,8))
    
    sudoku[coordinate] = starting_board.get(coordinate)

    return sudoku


def make_sudoku(sudoku = {}, starting_board = {}, clues = 81, tries = 0):
    # Try taking out random cells and check if sudoku is still uniquely solvable
    # If not, fill the clue back in
    if clues < 24:
        return sudoku
    else:
        # if stuck, fill in a cell from the original filled sudoku board
        if tries > 20:
            sudoku = fill_sudoku(sudoku, starting_board)
            tries = 0
            clues = clues + 1
        random_index = (random.randint(0,8), random.randint(0,8))
        last_replaced = (random_index, sudoku.get(random_index))

        while(last_replaced[1] == None):
            random_index = (random.randint(0, 8), random.randint(0, 8))
            last_replaced = (random_index, sudoku.get(random_index))
        
        del sudoku[random_index]

        if uniquely_solvable(sudoku):
            return make_sudoku(sudoku, starting_board, clues - 1, 0)
        else:
            sudoku[random_index] = last_replaced[1]
            return make_sudoku(sudoku, starting_board, clues, tries + 1)


def pretty_print(sudoku):
    for r in rows():
        for c in cols():
            print(sudoku.get((r, c), '.'), end=' ')
            if (c+1) % 3 == 0:
                print(' ', end='')
        print()
        if (r+1) % 3 == 0:
            print()
    print()


def print_in_line(sudoku):
    for r in rows():
        for c in cols():
            print(sudoku.get((r, c), '.'), end='')
    print('\n')


if __name__ == '__main__':

    sys.setrecursionlimit(1500)

    full_board = make_starting_board()
    starting_board = copy.copy(full_board)
    clue_board = make_sudoku(sudoku=full_board, starting_board=starting_board)

    print('uniquely solvable: ', uniquely_solvable(clue_board))
    pretty_print(clue_board)
    print_in_line(clue_board)
   