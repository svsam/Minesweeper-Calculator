import sympy
from random import sample
import itertools
import math
import copy

#generates a board and populates it with mines
def genBoard(height, width, numberOfMines):
    if not 0 <= numberOfMines <= height * width:
        raise ValueError('numberOfMines must fit within the board')

    board = [[0] * width for _ in range(height)]
    for position in sample(range(height * width), numberOfMines):
        ypos, xpos = divmod(position, width)
        board[ypos][xpos] = 1
    return board

#generates the initial state of what the player can see of the board
def genKnownBoard(h, w):
    board = []
    for i in range(h):
        board.append([None] * w)
    return (board)

# checks whether some square is inside or not the board
def cifInside(coords, height, width):
    if 0 <= coords[0] < height and 0 <= coords[1] < width:
        return True
    else:
        return False

# returns all the surrounding squares of a given tile
def cSurroundingTiles(coords, board):
    y, x = coords[0], coords[1]
    possibilities = [(y + 1, x),
                    (y + 1, x + 1),
                    (y, x + 1), 
                    (y - 1, x), 
                    (y - 1, x - 1), 
                    (y, x - 1), 
                    (y + 1, x - 1),
                    (y - 1, x + 1)]
    surroundingSquares = []

    for square in possibilities:
        if cifInside(square, len(board), len(board[0])):
            surroundingSquares.append(square)
    return surroundingSquares

# returns the number of mines around a given square
def squareNum(coords, board):
    y, x = coords[0], coords[1]
    possibilities = [(y + 1, x), (y + 1, x + 1), (y, x + 1), (y - 1, x), (y - 1, x - 1), (y, x - 1), (y + 1, x - 1),
                     (y - 1, x + 1)]
    bombcount = 0
    for sqr in possibilities:
        if cifInside(sqr, len(board), len(board[0])):
            bombcount += board[sqr[0]][sqr[1]]
    return (bombcount)

#In minesweeper, when the player clicks a square with number 0, all surrouding squares are cleared automatically
#this function does that.
def cleanboard(knownBoard,gameBoard,seen):
    # count is the number of squares of number 0 whose surroundings haven't been cleared yet
    count = None
    while count != 0:
        count = 0
        zerosqrs = []
        for y, r in enumerate(knownBoard):
            for x, c in enumerate(r):
                if c == 0 and (y, x) not in seen:
                    for sqr in cSurroundingTiles((y, x), gameBoard):
                        if gameBoard[sqr[0]][sqr[1]] == 0 and knownBoard[sqr[0]][sqr[1]] != 'B':
                            sqrNum = squareNum(sqr, gameBoard)
                            if sqrNum == 0:
                                count += 1
                                zerosqrs.append((sqr[0], sqr[1]))
                            else:
                                knownBoard[sqr[0]][sqr[1]] = sqrNum
                    seen.append((y, x))
        for sqr in zerosqrs:
            knownBoard[sqr[0]][sqr[1]] = 0


def countFlags(knownBoard):
    return sum(cell == 'B' for row in knownBoard for cell in row)


def validateBoardState(knownBoard, numberOfMines):
    flags = countFlags(knownBoard)
    unknowns = sum(cell is None for row in knownBoard for cell in row)

    if flags > numberOfMines:
        return "Too many flags have been placed"
    if flags + unknowns < numberOfMines:
        return "There are not enough hidden squares for the remaining mines"

    for y, row in enumerate(knownBoard):
        for x, cell in enumerate(row):
            if type(cell) is not int:
                continue

            surrounding = cSurroundingTiles((y, x), knownBoard)
            surrounding_flags = sum(knownBoard[ny][nx] == 'B' for ny, nx in surrounding)
            surrounding_unknowns = sum(knownBoard[ny][nx] is None for ny, nx in surrounding)
            if surrounding_flags > cell or surrounding_flags + surrounding_unknowns < cell:
                return "The current flags conflict with a revealed number"

    return None


def relocateMine(gameBoard, knownBoard, coords):
    y, x = coords
    if gameBoard[y][x] != 1:
        return False

    for new_y, row in enumerate(gameBoard):
        for new_x, cell in enumerate(row):
            if cell == 0 and knownBoard[new_y][new_x] is None and (new_y, new_x) != coords:
                gameBoard[y][x] = 0
                gameBoard[new_y][new_x] = 1
                return True

    return False


def revealCell(knownBoard, gameBoard, seen, coords, safeFirstMove=False):
    if not cifInside(coords, len(gameBoard), len(gameBoard[0])):
        return 'ignored'

    y, x = coords
    if knownBoard[y][x] is not None:
        return 'ignored'

    if safeFirstMove:
        relocateMine(gameBoard, knownBoard, coords)

    if gameBoard[y][x] == 1:
        return 'mine'

    knownBoard[y][x] = squareNum(coords, gameBoard)
    cleanboard(knownBoard, gameBoard, seen)
    return 'revealed'


def hasWon(gameBoard, knownBoard):
    return all(
        gameBoard[y][x] == 1 or type(knownBoard[y][x]) is int
        for y in range(len(gameBoard))
        for x in range(len(gameBoard[0]))
    )


def solverActions(knownBoard, probabilityBoard, tolerance=1e-12):
    safe = []
    mines = []
    candidates = []
    center_y = (len(knownBoard) - 1) / 2
    center_x = (len(knownBoard[0]) - 1) / 2

    for y, row in enumerate(knownBoard):
        for x, cell in enumerate(row):
            if cell is not None or probabilityBoard[y][x] is None:
                continue

            probability = float(probabilityBoard[y][x])
            if not math.isfinite(probability):
                continue
            if probability <= tolerance:
                safe.append((y, x))
            elif probability >= 1 - tolerance:
                mines.append((y, x))
            else:
                distance = (y - center_y) ** 2 + (x - center_x) ** 2
                candidates.append((probability, distance, y, x))

    if safe or mines:
        return safe, mines, None
    if candidates:
        probability, _, y, x = min(candidates)
        return [], [], ((y, x), probability)
    return [], [], None


def forcedFiftyFiftyCells(knownBoard, probabilityBoard, estimated=False, tolerance=1e-9):
    if estimated or probabilityBoard is None:
        return []
    if not any(type(cell) is int for row in knownBoard for cell in row):
        return []

    candidates = []
    for y, row in enumerate(knownBoard):
        for x, cell in enumerate(row):
            probability = probabilityBoard[y][x]
            if cell is None and probability is not None:
                candidates.append(((y, x), float(probability)))

    if len(candidates) < 2:
        return []
    if any(probability <= tolerance or probability >= 1 - tolerance for _, probability in candidates):
        return []

    safest_probability = min(probability for _, probability in candidates)
    if abs(safest_probability - 0.5) > tolerance:
        return []

    fifty_fifty = [
        coords for coords, probability in candidates
        if abs(probability - 0.5) <= tolerance
    ]
    return fifty_fifty

#generates all combinations of a list l of symbols with length n
def foo(l,n):
    yield from itertools.product(*([l] * n))

#breaks down a parametric solution of a linear system into groups of parameters that affect each other
def gen_groups(solution,parameters):
    groups = []
    for i in range(len(parameters)):
        groups.append([])
    for i,par in enumerate(parameters):
        groups[i].append(par)
        for eq in solution:
            if eq.coeff(par) != 0:
                for par2 in parameters:
                    if eq.coeff(par2) != 0 and par2!=par and par2 not in groups[i]:
                        groups[i].append(par2)
    for par in parameters:
        hasit = []
        for i,group in enumerate(groups):
            if par in group and group not in hasit:
                hasit.append(group)
        if len(hasit) > 1:
            newgroup = []
            for group in hasit:
                groups.remove(group)
                for par2 in group:
                    if par2 not in newgroup:
                        newgroup.append(par2)
            groups.append(newgroup)
    return(groups)


# The function that returns a board with the probability of each border square having a mine
def calcprobs(board,rem_mines):
    calcprobs.used_estimate = False
    newBoard = []
    for _ in range(len(board)):
            newBoard.append([None] * len(board[0]))
    prev = None
    # rule 1 : "if the number of unknown surrounding squares is equal to the number of the square, then all of them have mines")
    while prev != newBoard:
        prev = copy.deepcopy(newBoard)
        for y, row in enumerate(board):
            for x, cell in enumerate(row):
                if type(cell) is int:
                    surroundingSquare = cSurroundingTiles((y, x), board)
                    known_mines = [
                        square for square in surroundingSquare
                        if board[square[0]][square[1]] == 'B'
                        or newBoard[square[0]][square[1]] == 1.0
                    ]
                    unknown_squares = [
                        square for square in surroundingSquare
                        if board[square[0]][square[1]] is None
                        and newBoard[square[0]][square[1]] is None
                    ]
                    remaining_mines = cell - len(known_mines)

                    if remaining_mines == len(unknown_squares):
                        for square in unknown_squares:
                            newBoard[square[0]][square[1]] = 1.0
                    elif remaining_mines == 0:
                        for square in unknown_squares:
                            newBoard[square[0]][square[1]] = 0.0


    #uses groups and set ideas to determine which squares must have mines or not. 
    #hhttps://www.youtube.com/watch?v=8j7bkNXNx4M
    #gets all border squares which still are not known to be mines or not
    #get unknown (unrevealed and unflagged) tiles around a given square
    def get_unknowns_around(pos):
        return [pt for pt in cSurroundingTiles(pos, board)
                if board[pt[0]][pt[1]] is None and not isinstance(newBoard[pt[0]][pt[1]], float)]

    #get surrounding tiles that are already identified as mines (flagged or marked as float 1.0)
    def get_mines_around(pos):
        return [pt for pt in cSurroundingTiles(pos, board)
                if board[pt[0]][pt[1]] == 'B' or newBoard[pt[0]][pt[1]] == 1.0]

    #get how many mines are still unaccounted for around a number-tile
    def get_value(pos):
        return board[pos[0]][pos[1]] - len(get_mines_around(pos))

    height, width = len(board), len(board[0])

    #step 1: Identify number tiles that touch unknown tiles (border squares)
    border_squares = [
        (y, x) for y in range(height) for x in range(width)
        if isinstance(board[y][x], int) and board[y][x] > 0 and
        any(board[ny][nx] is None and not isinstance(newBoard[ny][nx], float)
            for ny, nx in cSurroundingTiles((y, x), board))
    ]

    #step 2: For each border square, compare it with neighboring border squares
    for sqr in border_squares:
        sqr_val = get_value(sqr)               #how many mines remain around this square
        sur_unknown = get_unknowns_around(sqr) #unknown neighbors around this square

        for adj_sqr in cSurroundingTiles(sqr, board):
            if adj_sqr not in border_squares:
                continue  #only compare to other border squares

            adj_val = get_value(adj_sqr)               #remaining mines around adjacent square
            adj_unknown = get_unknowns_around(adj_sqr) #unknowns around adjacent square

            # Calculate the "extra" unknowns that only belong to one of the two sets
            only_adj = [pt for pt in adj_unknown if pt not in sur_unknown]
            only_sqr = [pt for pt in sur_unknown if pt not in adj_unknown]

            # Logic deduction:
            # If the difference in required mines equals the number of unique unknowns,
            # then those unique unknowns **must** be mines, and the others are safe.
            if adj_val - sqr_val == len(only_adj):
                for pt in only_adj:
                    newBoard[pt[0]][pt[1]] = 1.0  #definitely a mine
                for pt in only_sqr:
                    newBoard[pt[0]][pt[1]] = 0.0  #definitely safe

    #gets all border squares which still are not known to be mines or not
    borderSquares = []
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if type(cell) == int:
                if cell > 0:
                    borderSquares += [x for x in cSurroundingTiles((y, x), board) if
                                    board[x[0]][x[1]] == None and type(newBoard[x[0]][x[1]])!=float]

    newborders_sqrs = []
    for x in borderSquares:
        if x not in newborders_sqrs:
            newborders_sqrs.append(x)
    borderSquares = newborders_sqrs

    #gets the equation for each number square
    equation_matrix = []
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if type(cell) == int:
                if cell > 0:
                    equation = [0] * (len(borderSquares) + 1)
                    for sqr in [x for x in cSurroundingTiles((y, x), board) if board[x[0]][x[1]] == None and type(newBoard[x[0]][x[1]])!=float]:
                        equation[borderSquares.index(sqr)] = 1
                    equation[-1] = cell - len([x for x in cSurroundingTiles((y,x),board) if board[x[0]][x[1]] == 'B' or newBoard[x[0]][x[1]] == 1.0])
                    equation_matrix.append(equation)

    # The squares that are not a border square and are not a cleared square
    unbordered_sqrs = []
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell == None and ((y,x) not in borderSquares) and type(newBoard[y][x])!=float:
                unbordered_sqrs.append((y,x))

    # Proceeds with solving the linear system if there are unknown squares probabilities at all
    if len(borderSquares) > 0:
        # Names each border square with a1, a2, ...
        variables = sympy.symbols(f'a0:{len(borderSquares)}')

        # Solves the system
        solution_set = sympy.linsolve(sympy.Matrix(equation_matrix), variables)
        if solution_set is sympy.EmptySet:
            return newBoard
        solution = next(iter(solution_set))

        # Determines what are the parameters of the solution
        parameters = [variable for variable in variables if variable in solution.free_symbols]

        # Exact enumeration grows exponentially. Keep exact constant deductions, then
        # use the global remaining-mine rate for unresolved cells on complex boards.
        if len(parameters) > 18:
            calcprobs.used_estimate = True
            for i, expression in enumerate(solution):
                if expression == sympy.core.numbers.Zero:
                    newBoard[borderSquares[i][0]][borderSquares[i][1]] = 0.0
                elif expression == sympy.core.numbers.One:
                    newBoard[borderSquares[i][0]][borderSquares[i][1]] = 1.0

            found_mines = sum(cell == 1.0 for row in newBoard for cell in row)
            unresolved = [
                (y, x)
                for y, row in enumerate(board)
                for x, cell in enumerate(row)
                if cell is None and not isinstance(newBoard[y][x], float)
            ]
            remaining = rem_mines - found_mines
            if unresolved and 0 <= remaining <= len(unresolved):
                estimate = remaining / len(unresolved)
                for y, x in unresolved:
                    newBoard[y][x] = estimate
            return newBoard

        # Separates the solution in groups that are independent between each other
        groups = gen_groups(solution,parameters)

        # Gets the equations that belong to each group. An additional group is created to put the expressions which ONLY have constants
        eq_groups = []
        for i in range(len(groups)+1):
            eq_groups.append([])
        eq_groups_num = []  # This is the number of the group that each expression in the solution belongs
        for eq in solution:
            num = len(groups)
            for j,group in enumerate(groups):
                if any(eq.coeff(par) != 0 for par in group):
                    num = j
                    break
            eq_groups[num].append(eq)
            eq_groups_num.append(num)

        # Sorts the border_sqrs and solution lists such that the first part correponds to the first group, the 2nd to the 2nd and so on
        borderSquares = [x for _, x in sorted(zip(eq_groups_num, borderSquares), key=lambda pair: pair[0])]
        solution = [x for _, x in sorted(zip(eq_groups_num, solution), key=lambda pair: pair[0])]

        groups = groups + [[]] # Adds an additional group that contains the parameters for the expressions that only have constants, which is an empty group
        alleq_groups = []  # Contains every possible solution for each group
        for i,eqgroup in enumerate(eq_groups):
            f = sympy.lambdify(groups[i], eqgroup)
            local_possible_solutions = []
            for possibility in foo([0, 1], len(groups[i])):
                localsolution = f(*possibility)
                valid = True
                for x in localsolution:
                    # Each square either has or doesn't have a mine
                    if x != 1 and x != 0:
                        valid = False
                        break
                if valid:
                    local_possible_solutions.append(localsolution)
            alleq_groups.append(local_possible_solutions)

        # It doesn't continue if there are too many parameters, because it could take a lot of time
        # The number of maximum parameters can be changing depending on the speed of the computer
        if len(parameters) < 35:
            # The number of mines that already have been found by the previous two methods
            alreadyFoundMines = 0
            for y,row in enumerate(newBoard):
                for x,cell in enumerate(row):
                    if cell == 1.0 and board[y][x]!='B':
                        alreadyFoundMines += 1

            numberOfPossibilities = {}                  # A dictionary to reuse some big values already calculated with comb()
            problist = [0]*len(borderSquares)             # The probabilities of each respective border square having a mine
            unbordered_prob = 0                         # The probability of each unbordered square having a mine
            total = 0                                   # Total number of possible states of mines
            unbordered_mine_weight = 0                  # weighted mine count across unbordered squares

            # Generates every possible combination of all the possible solutions for each group
            for c in itertools.product(*[list(range(len(x))) for x in alleq_groups]):
                result = []
                for x in [alleq_groups[i][j] for i, j in enumerate(c)]:
                    result = result + x   # Because the border squares were sorted based on the group number, the group possible solutions can just be summed to the list

                val = int(sum(result))
                remaining_unbordered = rem_mines - val - alreadyFoundMines
                if 0 <= remaining_unbordered <= len(unbordered_sqrs):
                    if val not in numberOfPossibilities:
                        numberOfPossibilities[val] = math.comb(len(unbordered_sqrs), remaining_unbordered)
                    total += numberOfPossibilities[val]
                    unbordered_mine_weight += remaining_unbordered * numberOfPossibilities[val]
                    for i, x in enumerate(result):
                        problist[i] += x * numberOfPossibilities[val]

            if total > 0:
                problist = [x/total for x in problist]
                if len(unbordered_sqrs) > 0:
                    unbordered_prob = unbordered_mine_weight / (total * len(unbordered_sqrs))
                # Substitutes each found probability to the probability board
                for i,sqr in enumerate(borderSquares):
                    newBoard[sqr[0]][sqr[1]] = problist[i]
                for sqr in unbordered_sqrs:
                    newBoard[sqr[0]][sqr[1]] = unbordered_prob
            else:
                return newBoard
        else:
            # In case there were too many parameters, at least some squares are definitely mines because the
            # solution of the linear system gave that they are constants 1 or 0
            for i in range(len(borderSquares)):
                if solution[i] == sympy.core.numbers.Zero:
                    newBoard[borderSquares[i][0]][borderSquares[i][1]] = 0.0
                elif solution[i] == sympy.core.numbers.One:
                    newBoard[borderSquares[i][0]][borderSquares[i][1]] = 1.0
    else:
        alreadyFoundMines = sum(cell == 1.0 for row in newBoard for cell in row)
        remaining_mines = rem_mines - alreadyFoundMines
        if unbordered_sqrs and 0 <= remaining_mines <= len(unbordered_sqrs):
            probability = remaining_mines / len(unbordered_sqrs)
            for y, x in unbordered_sqrs:
                newBoard[y][x] = probability
    return(newBoard)
