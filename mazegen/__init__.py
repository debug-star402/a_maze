"""
mazegen — Maze Generator Package for the 42 Network A-Maze-ing project.

Public API
----------
MazeGenerator
    Build perfect or imperfect mazes with a randomised DFS algorithm.
    The "42" pattern is injected automatically for large-enough grids.

MazeSolver
    Find the shortest path between two cells using BFS.

Quick start
-----------
>>> from mazegen import MazeGenerator, MazeSolver
>>>
>>> # Create and generate a 21×15 perfect maze with a fixed seed
>>> gen = MazeGenerator(width=21, height=15, perfect=True, seed=42)
>>> gen.generate()
>>>
>>> # Access the raw grid (grid[y][x] returns a Cell object)
>>> cell = gen.grid[0][0]
>>> print(cell.walls)   # {'N': False, 'E': False, 'S': True, 'W': True}
>>>
>>> # Get the hexadecimal wall-encoding string (for writing to file)
>>> print(gen.get_hex_grid())
>>>
>>> # Solve from top-left to bottom-right
>>> solver = MazeSolver(gen.grid, gen.width, gen.height)
>>> path = solver.solve(0, 0, 20, 14)
>>> print(path)   # e.g. "SSEENESSWW..."
"""
from .generator import MazeGenerator
from .solver import MazeSolver

__all__ = ['MazeGenerator', 'MazeSolver']
