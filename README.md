# Minesweeper Calculator

Minesweeper Calculator is a desktop Python project that combines a playable **Minesweeper game** with a **probability-based solving assistant**. Instead of only letting you click tiles and place flags, the project can also analyze the current board, estimate which hidden cells are safest or most dangerous, and help you make smarter moves.

It is built with **Pygame** for the user interface and uses **SymPy** plus combinatorics-based logic in the solver to reason about mine placement probabilities. The result is a project that is part game, part puzzle-analysis tool, and part learning resource for people interested in logic, probability, or algorithmic problem solving.

---

## What this project does

At its core, this project gives you a graphical Minesweeper experience with a few extra features:

- **Generates a Minesweeper board** with a configurable width, height, and number of mines.
- **Lets you play interactively** using left-clicks to reveal tiles and right-clicks to place or remove flags.
- **Automatically clears empty regions** when a `0` tile is revealed, similar to classic Minesweeper behavior.
- **Calculates mine probabilities** for unrevealed tiles when requested.
- **Highlights certainty** by identifying tiles that are definitely safe or definitely mines.
- **Displays simple performance stats** such as FPS and CPU usage while the game runs.
- **Includes menu screens and music controls** for a more complete desktop-app feel.

This makes the project useful both as a game and as a basic solver/assistant for understanding how Minesweeper positions can be analyzed mathematically.

---

## How it helps people

This project can help different kinds of users in different ways:

### For players
- Helps you make better decisions when a Minesweeper board becomes uncertain.
- Shows probability estimates so you can choose the safest move instead of guessing blindly.
- Makes classic Minesweeper more approachable for beginners.

### For students and learners
- Demonstrates how logic constraints can be turned into equations.
- Shows a practical use of **linear algebra**, **symbolic math**, and **combinatorics**.
- Provides a concrete example of how probability can be used in game-solving.

### For developers
- Offers a small but interesting Python codebase combining gameplay, rendering, and solver logic.
- Shows how to structure a simple Pygame application with helper modules.
- Can be extended into a stronger AI/solver, a teaching tool, or a polished desktop game.

### For educators or hobbyists
- Can be used to explain the difference between **certainty** and **probability** in decision making.
- Gives a visual way to demonstrate how local rules and global constraints interact.

---

## Main features

### 1. Playable Minesweeper interface
The game starts in a menu screen and lets you launch a board-based Minesweeper session. The interface includes:

- Start button
- Options screen
- Back button
- Music toggle
- FPS / CPU display

### 2. Probability calculator / solver assistant
A major feature of the project is the mine-probability engine. When the board reaches an uncertain state, the solver can:

- Look at revealed numbered tiles
- Determine surrounding unknown cells
- Apply direct deduction rules
- Build a system of constraints
- Use symbolic solving to find valid mine combinations
- Estimate the probability that each hidden tile contains a mine

This means the project is more than a clone of Minesweeper—it actively helps analyze the puzzle.

### 3. Automatic clearing of empty areas
When a `0` tile is uncovered, the project reveals nearby empty sections automatically so the player does not have to click every empty square one by one.

### 4. Audio and visual assets
The game includes image assets for:

- hidden tiles
- flags
- mines
- number tiles
- window icon

It also includes background music for the game session.

---

## How the solver works at a high level

The "calculator" part of the project is implemented in the logic module and follows a layered approach:

1. **Basic deduction**  
   If a number tile has exactly as many unknown neighbors as remaining mines, those neighbors must be mines. Likewise, if all needed mines are already accounted for, the rest must be safe.

2. **Border analysis**  
   The solver focuses on unknown cells near revealed numbered tiles, because those are the cells constrained by visible information.

3. **Equation building**  
   Each numbered tile creates a relationship between nearby unknown cells and the number of mines still required around it.

4. **Symbolic solving**  
   The project uses SymPy to solve the resulting system.

5. **Combinatorial counting**  
   When multiple valid mine layouts remain, the project counts possibilities and converts them into per-tile mine probabilities.

This makes the project especially interesting if you want to explore how a game can be solved using formal reasoning rather than only heuristics.

---

## Project structure

```text
Minesweeper-Calculator/
├── README.md
├── minesweeper/
│   ├── start.py          # Main game loop, menus, controls, and runtime setup
│   ├── functions.py      # Board generation, reveal logic, and probability solver
│   ├── visual.py         # Rendering logic and image loading
│   ├── images/           # Sprites/icons for tiles, flags, mines, and numbers
│   ├── FirelinkShrine.mp3
│   └── old/              # Older experimental files / legacy code
```

---

## Requirements

You will need Python 3 installed, plus these Python packages:

- `pygame`
- `psutil`
- `sympy`

Install them with:

```bash
pip install pygame psutil sympy
```

If you are on Linux, you may also need the usual SDL/Pygame-related system libraries depending on your environment.

---

## How to run the project

From the repository root, run:

```bash
python minesweeper/start.py
```

If your system uses `python3`, run:

```bash
python3 minesweeper/start.py
```

---

## Controls

### Mouse
- **Left-click**: reveal a tile
- **Right-click**: place or remove a flag

### Keyboard
- **P**: calculate and display mine probabilities
- **L**: hide probability overlay
- **C**: automatically act on certainty
  - reveals tiles with probability `0.0`
  - flags tiles with probability `1.0`

### Menu actions
- **Start**: begin the game
- **Options**: open the options screen
- **Music**: pause or resume the background music
- **Back**: return from sub-screens
- **Quit / close window**: exit the application

---

## Current default board settings

The current configuration in the game sets:

- **Height:** 11
- **Width:** 10
- **Mines:** 20

These values are defined in `minesweeper/start.py` and can be edited if you want to experiment with different difficulty levels.

---

## Example ways to use it

Here are a few practical uses for the project:

### Use it as a normal game
If you just want to play Minesweeper with some extra polish, launch the app and play normally.

### Use it as a decision-support tool
When you reach a difficult board state:

1. press `P`
2. inspect the probability values
3. choose the lowest-risk tile
4. optionally press `C` to apply guaranteed moves automatically

### Use it as a learning project
Read through the code to study:

- board generation
- recursive-style clearing behavior
- Pygame rendering
- constraint-based puzzle solving
- symbolic equation solving with SymPy

---

## Why the project matters

Minesweeper is a deceptively simple game. Under the surface, it involves:

- local logic rules
- incomplete information
- uncertainty
- risk management
- mathematical reasoning

This project helps turn those ideas into something visible and interactive. It can help people understand that solving a puzzle is not always about finding one exact answer immediately—sometimes it is about narrowing possibilities, measuring risk, and making the best decision with the information available.

That makes this project valuable not just as entertainment, but also as a small educational tool.

---

## Known limitations / things to improve

Like many personal or experimental projects, this codebase has room to grow. Potential improvements include:

- fixing path handling to work more smoothly across operating systems
- adding a `requirements.txt` or `pyproject.toml`
- allowing difficulty selection in the UI
- resetting or regenerating the board without restarting
- improving the menu flow and back-button behavior
- adding win detection and end-game messaging
- improving comments, docstrings, and code organization
- packaging the game for easier installation
- adding automated tests

If you want to contribute, these would all be strong next steps.

---

## Troubleshooting

### The game does not start
Make sure all required packages are installed:

```bash
pip install pygame psutil sympy
```

### Images or music do not load
Check that you are running the project from the repository root so the relative asset paths resolve correctly.

### Pygame window issues
Some environments (especially remote servers, headless systems, or restricted containers) may not support opening desktop windows directly.

---

## Future ideas

Possible directions for expanding the project:

- add difficulty presets such as beginner / intermediate / expert
- add a hint button
- color-code probabilities visually
- add a true "solver mode" that plays automatically
- save statistics from completed runs
- add a tutorial mode explaining why a move is safe
- turn the code into a cleaner educational demo for logic and probability

---

## Summary

**Minesweeper Calculator** is a Python-based Minesweeper game with an integrated solver assistant. It helps people:

- play Minesweeper
- understand risk on uncertain boards
- learn logic and probability concepts
- explore how symbolic math can support puzzle solving

If you enjoy games, programming, or mathematical problem solving, this project is a great starting point for experimentation and improvement.
