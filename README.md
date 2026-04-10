# A-Maze-ing

*This project has been created as part of the 42 curriculum by diaae.*

---

## Description

**A-Maze-ing** is a Python maze generator and interactive visualiser built for the 42 Network curriculum.

The program reads a configuration file, generates a rectangular maze (perfect or imperfect), and writes the result to a text file using a hexadecimal wall-encoding format.  After generation the user enters an interactive terminal session where they can re-generate the maze, reveal the shortest solution path, and cycle through wall colour themes.

Key features:
- **Perfect mazes** (exactly one path between any two cells) via a randomised depth-first search (recursive backtracker).
- **Imperfect mazes** with random extra passages — guaranteed never to create a 3 × 3 open area.
- Embedded **"42" pattern** of fully-walled cells centred in every maze that is at least 15 × 9 cells.
- **BFS solver** that finds and displays the shortest path from entry to exit.
- **Reproducible generation** via an optional integer seed.
- Reusable `mazegen` package installable with `pip`.

---

## Instructions

### Requirements

- Python 3.10 or later
- Dependencies listed in `requirements.txt`

### Installation

```bash
# Install runtime and development dependencies
make install
```

### Running

```bash
# Run with the default configuration file
make run

# Or directly
python3 a_maze_ing.py config.txt
```

### Debug mode

```bash
make debug
```

### Linting

```bash
make lint          # flake8 + mypy (standard flags)
make lint-strict   # flake8 + mypy --strict
```

### Cleanup

```bash
make clean
```

---

## Configuration file format

The configuration file contains one `KEY=VALUE` pair per line.  Lines beginning with `#` are treated as comments and ignored.

| Key           | Required | Description                                      | Example              |
|---------------|----------|--------------------------------------------------|----------------------|
| `WIDTH`       | ✓        | Number of columns (cells) in the maze            | `WIDTH=21`           |
| `HEIGHT`      | ✓        | Number of rows (cells) in the maze               | `HEIGHT=15`          |
| `ENTRY`       | ✓        | Entry cell coordinates as `x,y`                  | `ENTRY=0,0`          |
| `EXIT`        | ✓        | Exit cell coordinates as `x,y`                   | `EXIT=20,14`         |
| `PERFECT`     | ✓        | `True` for a perfect maze, `False` for loops     | `PERFECT=True`       |
| `OUTPUT_FILE` | ✓        | Filename for the hexadecimal output              | `OUTPUT_FILE=maze.txt` |
| `SEED`        | ✗        | Integer seed for reproducible generation         | `SEED=42`            |

Entry and exit coordinates must lie on the border of the maze (they define where the outer wall is opened).

### Example `config.txt`

```
# A-Maze-ing configuration
WIDTH=21
HEIGHT=15
ENTRY=0,0
EXIT=20,14
PERFECT=False
OUTPUT_FILE=maze.txt
SEED=42
```

---

## Output file format

```
<hex row 0>
<hex row 1>
...
<hex row HEIGHT-1>

<entry_x>,<entry_y>
<exit_x>,<exit_y>
<shortest path as N/E/S/W characters>
```

Each cell is encoded as a single uppercase hexadecimal character.  The bits of the value indicate which walls are **closed**: bit 0 (LSB) = North, bit 1 = East, bit 2 = South, bit 3 = West.

---

## Maze generation algorithm

The generator uses a **randomised depth-first search** (also known as the *recursive backtracker*), implemented iteratively with an explicit stack.

### Why this algorithm?

| Property | Value |
|---|---|
| Maze quality | Long, winding corridors — visually appealing |
| Complexity | O(width × height) time and space |
| Perfect-maze guarantee | Yes (it produces a spanning tree) |
| Ease of implementation | High — simple stack-based loop |
| Reproducibility | Trivially achieved by seeding Python's `random` |

The recursive backtracker was chosen because it is straightforward to implement correctly, produces aesthetically interesting mazes with long passages, and naturally integrates a seed for reproducibility.  Extending it to an imperfect maze is equally simple: after carving the spanning tree, a configurable percentage of remaining walls are removed at random (subject to the 3 × 3 open-area constraint).

---

## Reusable code — `mazegen` package

The maze generation and solving logic lives entirely inside the `mazegen/` directory and is packaged as a standalone pip-installable library.

### What is reusable

| Class | Module | Purpose |
|---|---|---|
| `MazeGenerator` | `mazegen.generator` | Build and expose the maze grid |
| `MazeSolver` | `mazegen.solver` | BFS shortest-path solver |
| `Cell` | `mazegen.cell` | Single grid cell (walls, position, is_42 flag) |

### Installing the package

A pre-built wheel is included at the repository root:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

To rebuild from source:

```bash
pip install build
python -m build          # produces dist/mazegen-1.0.0-py3-none-any.whl
```

### Usage example

```python
from mazegen import MazeGenerator, MazeSolver

# 1. Instantiate and generate
gen = MazeGenerator(width=21, height=15, perfect=True, seed=42)
gen.generate()

# 2. Access the grid
cell = gen.grid[0][0]           # Cell at column 0, row 0
print(cell.walls)               # {'N': False, 'E': False, 'S': True, 'W': True}
print(cell.is_42)               # True if part of the "42" decoration

# 3. Get the hex encoding (for writing to file)
print(gen.get_hex_grid())

# 4. Solve the maze
solver = MazeSolver(gen.grid, gen.width, gen.height)
path = solver.solve(start_x=0, start_y=0, exit_x=20, exit_y=14)
print(path)   # e.g. "SSNEESE..."  (None if unsolvable)
```

### Custom parameters

| Parameter | Type | Description |
|---|---|---|
| `width` | `int` | Number of columns (≥ 2) |
| `height` | `int` | Number of rows (≥ 2) |
| `perfect` | `bool` | `True` = spanning-tree maze; `False` = adds loops |
| `seed` | `int \| None` | Fixed seed for reproducibility; `None` = random |

---

## Interactive terminal controls

Once the maze is written to the output file the program enters an interactive loop:

| Key | Action |
|---|---|
| `1` | Re-generate a new maze and display it |
| `2` | Toggle the shortest solution path on/off |
| `3` | Cycle wall colour (white → blue → green → red) |
| `4` | Quit |

---

## Team and project management

### Roles

| Member | Responsibilities |
|---|---|
| diaae | Architecture, maze generator, solver, terminal renderer, packaging, documentation |

### Planning

**Initial plan (week 1):**  Core Cell/Grid model → DFS generator → BFS solver → hex output → terminal renderer → pip packaging → README.

**How it evolved:**  The imperfect-maze constraint (no 3 × 3 open areas) and the interactive re-generation bug (stale solver grid reference, missing entry/exit wall re-opening) were discovered during testing and required dedicated fixes.  Overall the plan was followed closely; packaging and documentation took slightly longer than expected.

### What worked well

- The iterative DFS with an explicit stack was simple to debug and extend.
- Separating generation logic into a pip package kept `a_maze_ing.py` thin and focused.
- The hexadecimal wall-encoding made output verification straightforward.

### What could be improved

- The imperfect-maze wall-removal pass runs in a fixed raster order; a random traversal order would give more uniform loop distribution.
- A graphical MLX display would provide a much richer interactive experience.
- Unit tests for the 3 × 3 open-area guard and for edge-case maze sizes would improve confidence.

### Tools used

- **Python 3.12** — implementation language
- **flake8 + mypy** — linting and static type checking
- **pytest** — manual local test runs (not submitted)
- **build** — Python package build tool
- **Claude (Anthropic)** — used to review code against the subject requirements, identify bugs (stale solver grid reference, missing wall re-opening after regeneration, absent 3 × 3 open-area check), and assist with generating comprehensive docstrings and this README template.  All generated content was reviewed, understood, and adapted before inclusion.

---

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker — think-maths.co.uk](https://www.think-maths.co.uk/sites/default/files/2020-04/Maze%20worksheet.pdf)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python `random` module documentation](https://docs.python.org/3/library/random.html)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)

### AI usage

**Claude (Anthropic)** was used during this project for:
- Cross-checking the implementation against the subject PDF to identify missing or incorrect behaviours.
- Suggesting fixes for the stale `solver.grid` reference and the missing border-wall re-opening logic in the interactive menu.
- Drafting comprehensive PEP 257-compliant docstrings across all modules.
- Drafting sections of this README.

In every case the generated suggestions were read, tested, and understood before being integrated.  No code was copied blindly.
