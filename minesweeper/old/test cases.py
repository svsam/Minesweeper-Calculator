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

# checks whether some square is inside or not the board
def cifInside(coords, height, width):
    if 0 <= coords[0] < height and 0 <= coords[1] < width:
        return True
    else:
        return False

def deduce_mines(board, newBoard, cSurroundingTiles):
    #get unknown (unrevealed and unflagged) tiles around a given square
    def get_unknowns_around(pos):
        return [pt for pt in cSurroundingTiles(pos, board)
                if board[pt[0]][pt[1]] is None and not isinstance(board[pt[0]][pt[1]], float)]

    #get surrounding tiles that are already identified as mines (flagged or marked as float 1.0)
    def get_mines_around(pos):
        return [pt for pt in cSurroundingTiles(pos, board)
                if board[pt[0]][pt[1]] == '1' or (isinstance(board[pt[0]][pt[1]], float) and board[pt[0]][pt[1]] == 1.0)]

    #get how many mines are still unaccounted for around a number-tile
    def get_value(pos):
        return board[pos[0]][pos[1]] - len(get_mines_around(pos))

    height, width = len(board), len(board[0])

    #step 1: Identify number tiles that touch unknown tiles (border squares)
    border_squares = [
        (y, x) for y in range(height) for x in range(width)
        if isinstance(board[y][x], int) and board[y][x] > 0 and
        any(board[ny][nx] is None for ny, nx in cSurroundingTiles((y, x), board))
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


def test_cSurroundingTiles():
    board = [[0 for _ in range(3)] for _ in range(3)]

    # Corner case: top-left (0, 0)
    assert sorted(cSurroundingTiles((0, 0), board)) == sorted([(0, 1), (1, 0), (1, 1)])

    # Edge case: top-middle (0, 1)
    assert sorted(cSurroundingTiles((0, 1), board)) == sorted([(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)])

    # Center case: middle (1, 1)
    assert sorted(cSurroundingTiles((1, 1), board)) == sorted([
        (0, 0), (0, 1), (0, 2),
        (1, 0),         (1, 2),
        (2, 0), (2, 1), (2, 2)
    ])

    print("All cSurroundingTiles tests passed.")

def run_deduce_mines_tests():
    def print_board(board):
        for row in board:
            print(row)
        print()

    def test_case(description, board, expected_changes=None):
        print(f"TEST: {description}")
        try:
            # Initialize newBoard with None
            newBoard = [[None for _ in row] for row in board]

            deduce_mines(board, newBoard, cSurroundingTiles)
            print_board(newBoard)

            if expected_changes:
                for (y, x), val in expected_changes.items():
                    assert newBoard[y][x] == val, f"Expected {val} at {(y, x)}, got {newBoard[y][x]}"

            print("Passed\n")

        except Exception as e:
            print(f"Failed with exception: {e}\n")

    # Corner deduction: top-left
    test_case(
        "Corner case: single mine deduced from corner",
        [
            [1, None],
            [None, None]
        ],
        expected_changes={
            (1, 1): 0.0  # Only this square is not shared with anything else
        }
    )

    # Edge overlap deduction
    test_case(
        "Edge overlap deduction with two adjacent numbers",
        [
            [1, 2, None],
            [None, None, None]
        ],
        expected_changes={
            (1, 0): 1.0,  # If diff == 1 and only this square is exclusive -> must be mine
            (1, 2): 0.0   # If it's not in the required difference → must be safe
        }
    )

    # Fully revealed board — should not crash or deduce
    test_case(
        "Fully revealed board",
        [
            [0, 1],
            [1, 0]
        ]
    )

    #Erroneous: non-rectangular board
    test_case(
        "Erroneous: Non-rectangular board",
        [
            [1, None],
            [None]
        ]
    )

    #Erroneous: invalid values
    test_case(
        "Erroneous: Invalid cell types",
        [
            [1, "banana"],
            [None, 2]
        ]
    )

def test_minesweeper_logic_calculator():
    test_cases = [
        # Valid Test Case 1
        {
            'board': [[None, 1, None], [None, 1, None], [None, 1, None]],
            'newBoard': [[None, None, None], [None, None, None], [None, None, None]],
            'expected_borderSquares': [(0, 1), (1, 1), (2, 1)],
            'expected_unbordered_sqrs': [(0, 0), (0, 2), (2, 0), (2, 2)]
        },
        # Erroneous Test Case 3
        {
            'board': [[None, "X", None], [None, 1, None], [None, None, 2]],
            'newBoard': [[None, None, None], [None, None, None], [None, None, None]],
            'expected_exception': ValueError  # Expecting an exception due to invalid cell type "X"
        },
        # Edge Test Case 5
        {
            'board': [[None]],
            'newBoard': [[None]],
            'expected_borderSquares': [],
            'expected_unbordered_sqrs': [(0, 0)]
        },
        # Add other test cases as needed
    ]
    
    for case in test_cases:
        try:
            borderSquares, unbordered_sqrs = minesweeper_logic(case['board'], case['newBoard'])  # assuming this is the function to test
            assert borderSquares == case['expected_borderSquares'], f"Failed for board: {case['board']}"
            assert unbordered_sqrs == case['expected_unbordered_sqrs'], f"Failed for board: {case['board']}"
        except Exception as e:
            if 'expected_exception' in case:
                assert isinstance(e, case['expected_exception']), f"Unexpected exception: {e}"
            else:
                raise e

test_minesweeper_logic_calculator()
run_deduce_mines_tests()
test_cSurroundingTiles()
