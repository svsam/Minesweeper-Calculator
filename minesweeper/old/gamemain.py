from functions import *
from visual import *
from time import sleep

#CONSTANTS
HEIGHT = 11
WIDTH = 10
NUM_MINES = 20
NUM_FLAGS = 0
BOARD = genBoard(HEIGHT, WIDTH, NUM_MINES)   # The board which determines if there is a mine or not in each square
BOARDVIEW = genKnownBoard(HEIGHT,WIDTH)      # The board that has what is shown to the player
BOARDPROBABILITY = None                      # The board which contains the probability of each square having a bomb
seen = []                                    # A list of the squares which have number 0 that have already been cleared

#SCREEN
tileSize = 80                                # Side length of each square in the board (probably in pixels)
clock = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode((WIDTH*tileSize, HEIGHT*tileSize))

#GAME LOOP
lost = False      # Whether the game has been lost or not
display = False   # Whether the probabilities are shown or not
running = True
while running:
    drawBoard(screen, BOARDVIEW,BOARD,BOARDPROBABILITY,tileSize,lost,display)
    clock.tick(MAX_FPS)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                display = True
                BOARDPROBABILITY = calcprobs(BOARDVIEW, NUM_MINES - NUM_FLAGS)
                print("=================================")
            elif event.key == pygame.K_l:
                display = False
            elif event.key == pygame.K_c:
                # Flags and clear the squares that are certainly mines or not
                for y,row in enumerate(BOARDPROBABILITY):
                    for x,cell in enumerate(row):
                        if cell == 0.0:
                            BOARDVIEW[y][x] = squareNum((y, x), BOARD)
                        elif cell == 1.0:
                            BOARDVIEW[y][x] = 'B'
                # Recounts the number of flags. This is to prevent some issues in which the number of flags was incorrect
                NUM_FLAGS = 0
                for row2 in BOARDVIEW:
                    for cell2 in row2:
                        if cell2 == 'B':
                            NUM_FLAGS += 1
                cleanboard(BOARDVIEW,BOARD,seen)
        if event.type == pygame.MOUSEBUTTONDOWN and not lost:
            location = pygame.mouse.get_pos()
            col = location[0] // tileSize
            row = location[1] // tileSize
            if event.button == 1:
                if BOARD[row][col] == 1:
                    if BOARDVIEW[row][col] != 'B':
                        print("It was a mine!")
                        lost = True
                else:
                    BOARDVIEW[row][col] = squareNum((row,col),BOARD)
                    cleanboard(BOARDVIEW,BOARD,seen)
            elif event.button == 3:
                if BOARDVIEW[row][col] == None:
                    BOARDVIEW[row][col] = 'B'
                    NUM_FLAGS += 1
                    print("Number of flags:", NUM_FLAGS)
                elif BOARDVIEW[row][col] == 'B':
                    BOARDVIEW[row][col] = None
                    NUM_FLAGS -= 1
                    print("Number of flags:", NUM_FLAGS)
