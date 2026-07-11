from pathlib import Path
from textwrap import wrap

import math
import pygame
import psutil  # For CPU usage monitoring
from functions import *
from visual import *

pygame.init()

#window variables
WIDTHw, HEIGHTw = 1800, 960

#display creation
pygame.display.set_icon(Icon)
screen = pygame.display.set_mode((WIDTHw, HEIGHTw))
pygame.display.set_caption('Minesweeper')
clock = pygame.time.Clock()

#CONSTANTS
MIN_BOARD_SIZE = 6
MAX_BOARD_SIZE = 16
BOARD_SIZE = 10
MINE_DENSITY = 0.20
MAX_BOARD_PIXELS = 770
HEIGHT = WIDTH = BOARD_SIZE
NUM_MINES = 20
tileSize = min(90, MAX_BOARD_PIXELS // BOARD_SIZE)
BOARD_X = 50
BOARD_Y = 100
CONTROL_X = 850
CONTROL_WIDTH = 300
AI_DELAY_MS = 250

boardScreen = pygame.Surface((WIDTH * tileSize, HEIGHT * tileSize))
boardRect = pygame.Rect(BOARD_X, BOARD_Y, WIDTH * tileSize, HEIGHT * tileSize)

#colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (111, 111, 111)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_GREY = (225, 225, 225)
LIGHT_GREEN = (170, 225, 170)
DARK_GREY = (150, 150, 150)
ORANGE = (230, 135, 25)

#music Initialization
pygame.mixer.init()
pygame.mixer.music.load(str(Path(__file__).resolve().with_name('FirelinkShrine.mp3')))
pygame.mixer.music.play(-1)  # Loop indefinitely
music_volume = 1.0
pygame.mixer.music.set_volume(music_volume)
music_on = True


def configure_board(size):
    global BOARD_SIZE, HEIGHT, WIDTH, NUM_MINES, tileSize, boardScreen, boardRect
    BOARD_SIZE = max(MIN_BOARD_SIZE, min(MAX_BOARD_SIZE, int(round(size))))
    HEIGHT = WIDTH = BOARD_SIZE
    NUM_MINES = max(1, min(BOARD_SIZE * BOARD_SIZE - 1, round(BOARD_SIZE * BOARD_SIZE * MINE_DENSITY)))
    tileSize = min(90, MAX_BOARD_PIXELS // BOARD_SIZE)
    board_pixels = BOARD_SIZE * tileSize
    boardScreen = pygame.Surface((board_pixels, board_pixels))
    boardRect = pygame.Rect(
        BOARD_X + (MAX_BOARD_PIXELS - board_pixels) // 2,
        BOARD_Y + (MAX_BOARD_PIXELS - board_pixels) // 2,
        board_pixels,
        board_pixels,
    )


def set_music_volume(volume):
    global music_volume
    music_volume = max(0.0, min(1.0, float(volume)))
    pygame.mixer.music.set_volume(music_volume)

#buttons
class Button():
    def __init__(self, x, y, text, width=110, height=60, font_size=24):
        self.font = pygame.font.SysFont('Georgia', font_size, bold=True)
        self.text = None
        self.button = pygame.Rect(x, y, width, height)
        self.set_text(text)

    def set_text(self, text):
        if text == self.text:
            return
        self.text = text
        self.surf = self.font.render(text, True, BLACK)
        self.text_x = self.button.x + (self.button.width - self.surf.get_width()) // 2
        self.text_y = self.button.y + (self.button.height - self.surf.get_height()) // 2

    def get_button(self):
        return self.button

    def draw(self, active=False, enabled=True):
        a, b = pygame.mouse.get_pos()
        if not enabled:
            pygame.draw.rect(screen, DARK_GREY, self.button)
        elif self.button.collidepoint(a, b):  # If mouse is hovering over the button
            pygame.draw.rect(screen, GREY, self.button)
        elif active:
            pygame.draw.rect(screen, LIGHT_GREEN, self.button)
        else:
            pygame.draw.rect(screen, WHITE, self.button)
        pygame.draw.rect(screen, BLACK, self.button, 3)
        screen.blit(self.surf, (self.text_x, self.text_y))  # Centered text


class Slider:
    def __init__(self, x, y, width, minimum, maximum, value, step=None):
        self.track = pygame.Rect(x, y, width, 10)
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.value = value
        self.dragging = False

    def set_from_x(self, x):
        ratio = max(0.0, min(1.0, (x - self.track.left) / self.track.width))
        value = self.minimum + ratio * (self.maximum - self.minimum)
        if self.step:
            value = self.minimum + round((value - self.minimum) / self.step) * self.step
        value = max(self.minimum, min(self.maximum, value))
        changed = value != self.value
        self.value = value
        return changed

    def handle_event(self, event):
        interaction_area = self.track.inflate(30, 44)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if interaction_area.collidepoint(event.pos):
                self.dragging = True
                return self.set_from_x(event.pos[0])
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            return self.set_from_x(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            changed = self.dragging and self.set_from_x(event.pos[0])
            self.dragging = False
            return changed
        return False

    def draw(self, label, value_text):
        label_font = pygame.font.SysFont('Georgia', 28, bold=True)
        value_font = pygame.font.SysFont('Arial', 24, bold=True)
        label_surface = label_font.render(label, True, BLACK)
        value_surface = value_font.render(value_text, True, BLACK)
        screen.blit(label_surface, (self.track.left, self.track.top - 58))
        screen.blit(value_surface, (self.track.right - value_surface.get_width(), self.track.top - 50))

        pygame.draw.rect(screen, DARK_GREY, self.track, border_radius=5)
        ratio = (self.value - self.minimum) / (self.maximum - self.minimum)
        filled = pygame.Rect(self.track.left, self.track.top, round(self.track.width * ratio), self.track.height)
        if filled.width > 0:
            pygame.draw.rect(screen, LIGHT_GREEN, filled, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.track, 2, border_radius=5)
        knob_x = round(self.track.left + self.track.width * ratio)
        pygame.draw.circle(screen, WHITE, (knob_x, self.track.centery), 15)
        pygame.draw.circle(screen, BLACK, (knob_x, self.track.centery), 15, 3)

def toggle_music():
    """Toggles the music on and off."""
    global music_on
    if music_on:
        pygame.mixer.music.pause()
        music_on = False
    else:
        pygame.mixer.music.unpause()
        music_on = True

def draw_fps_and_cpu(x=10):
    """Displays the FPS and CPU usage on the screen."""
    font = pygame.font.SysFont('Arial', 18, bold=True)
    
    # FPS
    fps = f"FPS: {int(clock.get_fps())}"
    fps_surf = font.render(fps, True, BLACK)
    screen.blit(fps_surf, (x, 10))  # Top-left corner
    
    # CPU usage
    cpu_usage = f"CPU: {psutil.cpu_percent()}%"
    cpu_surf = font.render(cpu_usage, True, BLACK)
    screen.blit(cpu_surf, (x, 40))  # Below the FPS


class GameSession:
    def __init__(self):
        self.reset()

    @property
    def flag_count(self):
        return countFlags(self.view)

    @property
    def finished(self):
        return self.lost or self.won

    def reset(self):
        self.board = genBoard(HEIGHT, WIDTH, NUM_MINES)
        self.view = genKnownBoard(HEIGHT, WIDTH)
        self.seen = []
        self.probabilities = None
        self.probabilities_are_estimate = False
        self.fifty_fifty_cells = []
        self.show_probabilities = False
        self.lost = False
        self.won = False
        self.ai_running = False
        self.status = "New board ready"

    def clear_probabilities(self):
        self.probabilities = None
        self.probabilities_are_estimate = False
        self.fifty_fifty_cells = []
        self.show_probabilities = False

    def has_revealed_cell(self):
        return any(type(cell) is int for row in self.view for cell in row)

    def check_win(self):
        if not self.lost and hasWon(self.board, self.view):
            self.won = True
            self.ai_running = False
            self.clear_probabilities()
            for y, row in enumerate(self.board):
                for x, cell in enumerate(row):
                    if cell == 1 and self.view[y][x] is None:
                        self.view[y][x] = 'B'
            self.status = "Board solved"
            return True
        return False

    def reveal(self, coords, source="Player", pause_ai=True):
        if self.finished:
            return False
        if pause_ai:
            self.ai_running = False

        result = revealCell(
            self.view,
            self.board,
            self.seen,
            coords,
            safeFirstMove=not self.has_revealed_cell(),
        )
        if result == 'ignored':
            return False

        self.clear_probabilities()
        if result == 'mine':
            self.lost = True
            self.ai_running = False
            self.status = f"{source} hit a mine"
            return True

        if not self.check_win():
            self.status = f"{source} revealed a tile"
            if pause_ai:
                self.calculate_probabilities(show=False, announce=False)
        return True

    def toggle_flag(self, coords):
        if self.finished:
            return False

        y, x = coords
        self.ai_running = False
        if self.view[y][x] == 'B':
            self.view[y][x] = None
            self.clear_probabilities()
            self.status = "Flag removed"
            if self.has_revealed_cell():
                self.calculate_probabilities(show=False, announce=False)
            return True
        if self.view[y][x] is None:
            if self.flag_count >= NUM_MINES:
                self.status = "All available flags are already in use"
                return False
            self.view[y][x] = 'B'
            self.clear_probabilities()
            self.status = "Flag placed"
            if self.has_revealed_cell():
                self.calculate_probabilities(show=False, announce=False)
            return True
        return False

    def calculate_probabilities(self, show=True, announce=True):
        if self.finished:
            return False

        error = validateBoardState(self.view, NUM_MINES)
        if error:
            self.ai_running = False
            self.clear_probabilities()
            self.status = error
            return False

        hidden = [
            (y, x)
            for y, row in enumerate(self.view)
            for x, cell in enumerate(row)
            if cell is None
        ]
        if not hidden:
            self.check_win()
            return False

        try:
            probabilities = calcprobs(self.view, NUM_MINES - self.flag_count)
        except Exception as error:
            self.ai_running = False
            self.clear_probabilities()
            self.status = "The solver could not analyze this position"
            print(f"Solver error: {error}")
            return False

        if any(probabilities[y][x] is None for y, x in hidden):
            self.ai_running = False
            self.clear_probabilities()
            self.status = "No valid mine placement matches the current flags"
            return False

        probability_values = [float(probabilities[y][x]) for y, x in hidden]
        remaining_mines = NUM_MINES - self.flag_count
        if (
            any(not math.isfinite(value) or not -1e-9 <= value <= 1 + 1e-9 for value in probability_values)
            or abs(sum(probability_values) - remaining_mines) > 1e-6
        ):
            self.ai_running = False
            self.clear_probabilities()
            self.status = "No valid mine placement matches the current flags"
            return False

        self.probabilities = probabilities
        self.probabilities_are_estimate = getattr(calcprobs, 'used_estimate', False)
        self.fifty_fifty_cells = forcedFiftyFiftyCells(
            self.view,
            probabilities,
            estimated=self.probabilities_are_estimate,
        )
        self.show_probabilities = show
        if self.fifty_fifty_cells:
            self.ai_running = False
            self.show_probabilities = True
            self.status = "Forced 50/50: no safer move exists; choose a highlighted tile"
            return True
        if announce:
            if self.probabilities_are_estimate:
                self.status = "Complex position: showing a bounded probability estimate"
            else:
                self.status = "Mine probabilities calculated"
        return True

    def fallback_guess(self):
        hidden = [
            (y, x)
            for y, row in enumerate(self.view)
            for x, cell in enumerate(row)
            if cell is None
        ]
        if not hidden:
            return None

        center_y = (HEIGHT - 1) / 2
        center_x = (WIDTH - 1) / 2
        coords = min(
            hidden,
            key=lambda point: (
                (point[0] - center_y) ** 2 + (point[1] - center_x) ** 2,
                point[0],
                point[1],
            ),
        )
        risk = max(0.0, min(1.0, (NUM_MINES - self.flag_count) / len(hidden)))
        return coords, risk

    def solver_step(self, allow_guess=True):
        if self.finished:
            self.ai_running = False
            return False
        if not self.calculate_probabilities(show=not allow_guess, announce=False):
            return False
        if self.fifty_fifty_cells:
            return False

        used_estimate = self.probabilities_are_estimate
        safe, mines, guess = solverActions(self.view, self.probabilities)
        if safe or mines:
            flagged = 0
            revealed = 0
            for y, x in mines:
                if self.view[y][x] is None:
                    self.view[y][x] = 'B'
                    flagged += 1

            for coords in safe:
                if self.finished:
                    break
                if self.reveal(coords, source="AI", pause_ai=False):
                    revealed += 1

            self.clear_probabilities()
            if not self.check_win():
                self.status = f"AI revealed {revealed} safe and flagged {flagged} mine(s)"
            return flagged > 0 or revealed > 0

        if not allow_guess:
            self.show_probabilities = True
            self.status = "No certain move; probabilities are shown"
            return False

        if guess is None:
            guess = self.fallback_guess()
        if guess is None:
            self.ai_running = False
            self.check_win()
            return False

        coords, risk = guess
        changed = self.reveal(coords, source="AI", pause_ai=False)
        if changed and not self.finished:
            estimate_label = "estimated " if used_estimate else ""
            self.status = f"AI chose the safest tile ({estimate_label}{risk:.1%} mine risk)"
        return changed


def draw_game_info(session):
    heading_font = pygame.font.SysFont('Georgia', 30, bold=True)
    info_font = pygame.font.SysFont('Arial', 24, bold=True)
    status_font = pygame.font.SysFont('Arial', 22)
    x = CONTROL_X + CONTROL_WIDTH + 60
    y = 125

    heading = heading_font.render("Solver status", True, BLACK)
    screen.blit(heading, (x, y))
    y += 60

    if session.won:
        game_state = "Won"
    elif session.lost:
        game_state = "Lost"
    elif session.fifty_fifty_cells:
        game_state = "Forced 50/50"
    elif session.ai_running:
        game_state = "AI running"
    else:
        game_state = "Playing"

    details = [
        f"State: {game_state}",
        f"Mines: {NUM_MINES}",
        f"Flags: {session.flag_count}",
        f"Mines left: {NUM_MINES - session.flag_count}",
    ]
    for detail in details:
        label = info_font.render(detail, True, BLACK)
        screen.blit(label, (x, y))
        y += 38

    y += 20
    if session.fifty_fifty_cells:
        warning = info_font.render("UNAVOIDABLE 50/50 RISK", True, ORANGE)
        screen.blit(warning, (x, y))
        y += 42
    for line in wrap(session.status, width=42):
        color = ORANGE if session.fifty_fifty_cells else BLACK
        label = status_font.render(line, True, color)
        screen.blit(label, (x, y))
        y += 30

    y += 35
    shortcuts = ["P: probabilities", "C: certain moves", "S: AI step", "A: auto solve", "R: reset"]
    for shortcut in shortcuts:
        label = status_font.render(shortcut, True, BLACK)
        screen.blit(label, (x, y))
        y += 30

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
    session = GameSession()
    probability_button = Button(CONTROL_X, 130, "Probabilities (P)", CONTROL_WIDTH, 55, 20)
    certain_button = Button(CONTROL_X, 200, "Certain Moves (C)", CONTROL_WIDTH, 55, 20)
    step_button = Button(CONTROL_X, 270, "AI Step (S)", CONTROL_WIDTH, 55, 20)
    auto_button = Button(CONTROL_X, 340, "Auto Solve (A)", CONTROL_WIDTH, 55, 20)
    reset_button = Button(CONTROL_X, 410, "Reset Board (R)", CONTROL_WIDTH, 55, 20)
    back_button = Button(CONTROL_X, 480, "Back", CONTROL_WIDTH, 55, 20)
    title_font = pygame.font.SysFont('Papyrus', 48, bold=True)
    title = title_font.render("Minesweeper AI Solver", True, BLACK)
    next_ai_step = pygame.time.get_ticks()

    def toggle_probability_overlay():
        session.ai_running = False
        if session.fifty_fifty_cells:
            session.show_probabilities = True
            session.status = "Forced 50/50: no safer move exists; choose a highlighted tile"
        elif session.show_probabilities:
            session.show_probabilities = False
            session.status = "Probability overlay hidden"
        else:
            session.calculate_probabilities(show=True)

    def toggle_auto_solver():
        nonlocal next_ai_step
        if session.finished:
            session.status = "Reset the board before starting the AI"
            return
        if session.fifty_fifty_cells:
            session.status = "Forced 50/50: choose a highlighted tile before continuing"
            return
        session.ai_running = not session.ai_running
        session.clear_probabilities()
        if session.ai_running:
            session.status = "AI solver started"
            next_ai_step = pygame.time.get_ticks()
        else:
            session.status = "AI solver paused"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_p and not session.finished:
                    session.ai_running = False
                    session.calculate_probabilities(show=True)
                elif event.key == pygame.K_l:
                    if session.fifty_fifty_cells:
                        session.show_probabilities = True
                        session.status = "Forced 50/50: choose a highlighted tile before continuing"
                    else:
                        session.show_probabilities = False
                        session.status = "Probability overlay hidden"
                elif event.key == pygame.K_c and not session.finished:
                    session.ai_running = False
                    session.solver_step(allow_guess=False)
                elif event.key == pygame.K_s and not session.finished:
                    session.ai_running = False
                    session.solver_step(allow_guess=True)
                elif event.key == pygame.K_a and not session.finished:
                    toggle_auto_solver()
                elif event.key == pygame.K_r:
                    session.reset()
                    next_ai_step = pygame.time.get_ticks()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_button.get_button().collidepoint(event.pos):
                        return
                    elif reset_button.get_button().collidepoint(event.pos):
                        session.reset()
                        next_ai_step = pygame.time.get_ticks()
                    elif probability_button.get_button().collidepoint(event.pos) and not session.finished:
                        toggle_probability_overlay()
                    elif certain_button.get_button().collidepoint(event.pos) and not session.finished:
                        session.ai_running = False
                        session.solver_step(allow_guess=False)
                    elif step_button.get_button().collidepoint(event.pos) and not session.finished:
                        session.ai_running = False
                        session.solver_step(allow_guess=True)
                    elif auto_button.get_button().collidepoint(event.pos) and not session.finished:
                        toggle_auto_solver()
                    elif boardRect.collidepoint(event.pos):
                        col = (event.pos[0] - boardRect.x) // tileSize
                        row = (event.pos[1] - boardRect.y) // tileSize
                        session.reveal((row, col))
                elif event.button == 3 and boardRect.collidepoint(event.pos):
                    col = (event.pos[0] - boardRect.x) // tileSize
                    row = (event.pos[1] - boardRect.y) // tileSize
                    session.toggle_flag((row, col))

        now = pygame.time.get_ticks()
        if session.ai_running and now >= next_ai_step:
            session.solver_step(allow_guess=True)
            next_ai_step = pygame.time.get_ticks() + AI_DELAY_MS

        probability_button.set_text(
            "Hide Probabilities (L)" if session.show_probabilities else "Probabilities (P)"
        )
        auto_button.set_text("Pause AI (A)" if session.ai_running else "Auto Solve (A)")

        screen.fill(WHITE)
        pygame.draw.rect(
            screen,
            LIGHT_GREY,
            pygame.Rect(CONTROL_X - 25, BOARD_Y, WIDTHw - CONTROL_X - 25, MAX_BOARD_PIXELS),
        )
        drawBoard(
            boardScreen,
            session.view,
            session.board,
            session.probabilities,
            tileSize,
            session.lost,
            session.show_probabilities,
        )
        screen.blit(boardScreen, boardRect.topleft)
        pygame.draw.rect(screen, BLACK, boardRect, 3)
        for y, x in session.fifty_fifty_cells:
            warning_rect = pygame.Rect(
                boardRect.x + x * tileSize,
                boardRect.y + y * tileSize,
                tileSize,
                tileSize,
            )
            pygame.draw.rect(screen, ORANGE, warning_rect, max(4, tileSize // 12))
        screen.blit(title, (boardRect.centerx - title.get_width() // 2, 25))

        controls_enabled = not session.finished
        probability_button.draw(active=session.show_probabilities, enabled=controls_enabled)
        certain_button.draw(enabled=controls_enabled)
        step_button.draw(enabled=controls_enabled)
        auto_button.draw(active=session.ai_running, enabled=controls_enabled)
        reset_button.draw()
        back_button.draw()
        draw_game_info(session)
        draw_fps_and_cpu()

        pygame.display.flip()
        clock.tick(60)

def options():
    volume_slider = Slider(550, 350, 700, 0.0, 1.0, music_volume, step=0.01)
    size_slider = Slider(550, 540, 700, MIN_BOARD_SIZE, MAX_BOARD_SIZE, BOARD_SIZE, step=1)
    back_button = Button((WIDTHw - 220) // 2, 690, "Back", width=220)
    heading_font = pygame.font.SysFont('Georgia', 42, bold=True)
    description_font = pygame.font.SysFont('Arial', 22)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and back_button.get_button().collidepoint(event.pos)
            ):
                return

            if volume_slider.handle_event(event):
                set_music_volume(volume_slider.value)
            if size_slider.handle_event(event):
                configure_board(size_slider.value)

        screen.fill(WHITE)
        pygame.draw.rect(screen, LIGHT_GREY, pygame.Rect(350, 150, 1100, 650))

        heading = heading_font.render("Options", True, BLACK)
        screen.blit(heading, ((WIDTHw - heading.get_width()) // 2, 185))

        description = description_font.render(
            "Settings apply immediately and are used for the next game.",
            True,
            BLACK,
        )
        screen.blit(description, ((WIDTHw - description.get_width()) // 2, 255))

        volume_slider.draw("Music volume", f"{round(music_volume * 100)}%")
        size_slider.draw(
            "Square board size",
            f"{BOARD_SIZE} x {BOARD_SIZE}  ({NUM_MINES} mines)",
        )

        back_button.draw()
        draw_fps_and_cpu()

        pygame.display.flip()
        clock.tick(60)

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
music_button = Button(WIDTHw - 150, HEIGHTw - 80, "Music", width=130)

#main loop
if __name__ == '__main__':
    start()
