import pygame
import psutil  # For CPU usage monitoring
from functions import *
from visual import *

pygame.init()

#window variables
WIDTHw, HEIGHTw = 1800, 960

#display creation
screen = pygame.display.set_mode((WIDTHw, HEIGHTw))
pygame.display.set_caption('Minesweeper')
clock = pygame.time.Clock()

#CONSTANTS
HEIGHT = 11
WIDTH = 10
NUM_MINES = 20

boardScreen = pygame.Surface((WIDTHw//2, HEIGHTw//2))
BOARD = genBoard(WIDTH, HEIGHT, NUM_MINES)   # The board which determines if there is a mine or not in each square
BOARDVIEW = genKnownBoard(HEIGHT,WIDTH)      # The board that has what is shown to the player
BOARDPROBABILITY = None                      # The board which contains the probability of each square having a bomb
seen = []                                    # A list of the squares which have number 0 that have already been cleared
tileSize = 20

#colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (111, 111, 111)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

#music Initialization
pygame.mixer.init()
pygame.mixer.music.load("minesweeper\FirelinkShrine.mp3")
pygame.mixer.music.play(-1)  # Loop indefinitely
music_on = True

#buttons
class Button():
    def __init__(self, x, y, text, width=110, height=60, font_size=24):
        font = pygame.font.SysFont('Georgia', font_size, bold=True)
        self.surf = font.render(text, True, BLACK)
        self.button = pygame.Rect(x, y, width, height)
        self.text_x = self.button.x + (self.button.width - self.surf.get_width()) // 2
        self.text_y = self.button.y + (self.button.height - self.surf.get_height()) // 2

    def get_button(self):
        return self.button

    def draw(self):
        a, b = pygame.mouse.get_pos()
        if self.button.collidepoint(a, b):  # If mouse is hovering over the button
            pygame.draw.rect(screen, GREY, self.button)
        else:
            pygame.draw.rect(screen, WHITE, self.button)
        pygame.draw.rect(screen, BLACK, self.button, 3)
        screen.blit(self.surf, (self.text_x, self.text_y))  # Centered text

def toggle_music():
    """Toggles the music on and off."""
    global music_on
    if music_on:
        pygame.mixer.music.pause()
        music_on = False
    else:
        pygame.mixer.music.unpause()
        music_on = True

def draw_fps_and_cpu():
    """Displays the FPS and CPU usage on the screen."""
    font = pygame.font.SysFont('Arial', 18, bold=True)
    
    # FPS
    fps = f"FPS: {int(clock.get_fps())}"
    fps_surf = font.render(fps, True, BLACK)
    screen.blit(fps_surf, (10, 10))  # Top-left corner
    
    # CPU usage
    cpu_usage = f"CPU: {psutil.cpu_percent()}%"
    cpu_surf = font.render(cpu_usage, True, BLACK)
    screen.blit(cpu_surf, (10, 40))  # Below the FPS

def start():
    global music_on
    while True:
        for event in pygame.event.get():  # Event handling
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if quit_button.get_button().collidepoint(event.pos):
                    pygame.quit()
                    exit()
                elif start_button.get_button().collidepoint(event.pos):
                    game()
                elif option_button.get_button().collidepoint(event.pos):
                    options()
                elif music_button.get_button().collidepoint(event.pos):
                    toggle_music()

        screen.fill(WHITE)  # Background colour

        draw_title()
        quit_button.draw()
        start_button.draw()
        option_button.draw()
        music_button.draw()
        draw_fps_and_cpu()  # Draw FPS and CPU usage

        pygame.display.flip()
        clock.tick(60)  # Keeps is at a maximum of 60 FPS

def game():
    back_button = Button(WIDTHw - 120, 20, "Back", width=100)  #back button in the top-right corner
    num_flag = 0
    lost = False      #whether the game has been lost or not
    display = False   #whether the probabilities are shown or not
    boardProbability = None
    while True:
        drawBoard(boardScreen, BOARDVIEW, BOARD, boardProbability, tileSize, lost, display)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


            if event.type == pygame.MOUSEBUTTONDOWN:
                            if back_button.get_button().collidepoint(event.pos):
                                running = False  # start screen

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    display = True
                    boardProbability = calcprobs(BOARDVIEW, (NUM_MINES - num_flag))
                    print("=================================")


                elif event.key == pygame.K_l:
                    display = False
                elif event.key == pygame.K_c:
                    # Flags and clear the squares that are certainly mines or not
                    for y,row in enumerate(boardProbability):
                        for x,cell in enumerate(row):
                            if cell == 0.0:
                                BOARDVIEW[y][x] = squareNum((y, x), BOARD)
                            elif cell == 1.0:
                                BOARDVIEW[y][x] = 'B'
                    # Recounts the number of flags. This is to prevent some issues in which the number of flags was incorrect
                    num_flag = 0
                    for row2 in BOARDVIEW:
                        for cell2 in row2:
                            if cell2 == 'B':
                                num_flag += 1
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
                        num_flag += 1
                        print("Number of flags:", num_flag)
                    elif BOARDVIEW[row][col] == 'B':
                        BOARDVIEW[row][col] = None
                        num_flag -= 1
                        print("Number of flags:", num_flag)

            screen.fill(RED)  # Background colour

            back_button.draw()
            draw_fps_and_cpu()  # Draw FPS and CPU usage

            pygame.display.flip()
            clock.tick(60)  # Keeps is at a maximum of 60 FPS

def options():
    back_button = Button(WIDTHw - 120, 20, "Back", width=100)  # Back button in the top-right corner
    while True:
        for event in pygame.event.get():  # Event handling
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.get_button().collidepoint(event.pos):
                    return  # Go back to the start screen

        screen.fill(GREY)  # Background colour

        draw_title()
        back_button.draw()
        draw_fps_and_cpu()  # Draw FPS and CPU usage

        pygame.display.flip()
        clock.tick(60)  # Keeps is at a maximum of 60 FPS

def draw_title():
    """Draws the title 'Minesweeper' at the top-center of the screen in Papyrus font."""
    papyrus_font = pygame.font.SysFont('Papyrus', 48, bold=True)
    text_surf = papyrus_font.render("Minesweeper", True, BLACK)
    text_x = (WIDTHw - text_surf.get_width()) // 2
    text_y = 20
    screen.blit(text_surf, (text_x, text_y))

# Create buttons
start_button = Button((WIDTHw - 200) // 2, 200, "Start", width=200)
option_button = Button((WIDTHw - 200) // 2, 300, "Options", width=200)
quit_button = Button((WIDTHw - 200) // 2, 400, "Quit", width=200)
music_button = Button(WIDTHw - 150, HEIGHT - 80, "Music", width=130)

#main loop
while True:
    for event in pygame.event.get():  # Event handling
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    running = start()

    pygame.display.flip()
    clock.tick(60)  # Keeps at a maximum of 60 FPS

    pygame.quit()
