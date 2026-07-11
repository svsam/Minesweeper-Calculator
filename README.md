# Minesweeper AI Solver

Minesweeper AI Solver is a playable desktop Minesweeper game with a built-in probability assistant. You can play it like normal Minesweeper, or you can ask the solver to inspect the board, show mine probabilities, make certain moves, and step through decisions.

The project is written in Python with Pygame for the interface. The solving logic uses the visible numbers on the board to build constraints, work out safe cells and mine cells, and estimate risk when the board cannot be solved by certainty alone.

## What You Can Do

- Play a full Minesweeper game with left-click reveal and right-click flag controls.
- Ask the solver to display mine probabilities on hidden cells.
- Automatically reveal cells that are guaranteed safe.
- Automatically flag cells that are guaranteed mines.
- Step the AI forward one move at a time.
- Let the AI auto-solve until it wins, loses, or reaches an unavoidable guess.
- Detect unavoidable 50/50 situations and pause instead of pretending the move is logical.
- Change the music volume and board size in the Options screen.
- Reset the board at any time.

## Game States

### Fresh Board

When a new game starts, every tile is hidden and the solver panel shows the current mine count, flag count, and available controls.

![Fresh game board](image.png)

### Solved Board

When every safe tile has been revealed and every mine is accounted for, the game marks the board as won. The screenshot below shows the solver finishing a board with all 20 mines flagged.

![Solved winning board](wincondition.png)

### Lost Board

If the player or AI reveals a mine, the game ends and the mine layout is shown. This can happen when the solver has to take a real risk, or when a manual click hits a mine.

![AI losing board](AIlosingcondition.png)

## How The Program Works

The program has three main parts:

- `start.py` runs the Pygame window, menus, buttons, options screen, music, and main game loop.
- `visual.py` loads the tile images and draws the board.
- `functions.py` creates boards, reveals tiles, checks win/loss state, and calculates solver probabilities.

During a game, the board keeps track of three things:

- where the mines are internally
- what the player can currently see
- which hidden cells have been flagged

When you reveal a tile, the game checks whether it is a mine. If it is safe, the tile opens. If the tile is a `0`, nearby empty areas open automatically, like classic Minesweeper.

## How The Solver Thinks

The solver starts with simple Minesweeper logic. For each revealed number, it looks at the hidden cells around it and asks:

- Are all remaining hidden neighbours definitely mines?
- Are all required mines already flagged, making the rest safe?

If certainty is not enough, the solver builds a set of constraints from the visible numbers. Each numbered tile says something like, "these nearby hidden cells must contain exactly this many mines." The solver compares those rules across the board and counts the valid mine layouts that still fit.

From those valid layouts, it estimates the probability that each hidden cell contains a mine. A cell with `0%` is safe. A cell with `100%` is a mine. Anything in between is risk.

If the exact solver finds that every available move is equally risky at `50%`, and there is no logical way to do better, the game warns about an unavoidable 50/50 and pauses auto-solving.

## Controls

### Mouse

- Left-click: reveal a tile
- Right-click: place or remove a flag

### Keyboard

- `P`: show probabilities
- `L`: hide probabilities
- `C`: make all certain moves
- `S`: run one AI step
- `A`: start or pause auto-solve
- `R`: reset the board
- `Escape`: go back from the game or Options screen

### On-Screen Buttons

- `Probabilities`: calculate and display mine chances
- `Certain Moves`: reveal guaranteed safe cells and flag guaranteed mines
- `AI Step`: make one solver move
- `Auto Solve`: let the solver keep playing
- `Reset Board`: start over with a new board
- `Back`: return to the main menu

## Options

The Options screen lets you adjust:

- music volume
- square board size from `6 x 6` to `16 x 16`

The board scales automatically when the size changes. Mine count also scales with the selected board size.

## Running The Game

From the project folder, run:

```bash
python minesweeper/start.py
```

If your system uses `python3`, run:

```bash
python3 minesweeper/start.py
```

There is also a built Windows executable in the project root:

```text
game.exe
```

## Requirements

Install the required Python packages with:

```bash
pip install pygame-ce psutil sympy
```

`pygame-ce` is used as the Pygame-compatible package for the local environment.

## Project Layout

```text
Minesweeper-Calculator/
|-- README.md
|-- game.exe
|-- image.png
|-- wincondition.png
|-- AIlosingcondition.png
|-- minesweeper/
|   |-- start.py
|   |-- functions.py
|   |-- visual.py
|   |-- FirelinkShrine.mp3
|   `-- images/
`-- env/
```

## Why This Project Is Interesting

Minesweeper looks simple, but it is really a game about incomplete information. Sometimes the board gives you a clear logical answer. Sometimes it only gives you risk.

This project makes that difference visible. It shows when a move is guaranteed, when a move is only probably safe, and when the board has reached a true guess. That makes it useful as a game, a small AI project, and a readable example of probability-based problem solving in Python.

## Troubleshooting

If the game does not start, make sure the dependencies are installed in the environment you are using.

If images or music do not load, check that these paths still exist:

- `minesweeper/images`
- `minesweeper/FirelinkShrine.mp3`

If the Pygame window does not open, the program may be running in an environment that does not support desktop windows.
