"""
Maze solver module for the A-Maze-ing project (42 Network).

Provides the MazeSolver class, which finds the shortest path between two
cells in a maze grid using breadth-first search (BFS).
"""
from collections import deque
from mazegen.cell import Cell


class MazeSolver:
    """Find the shortest path through a maze grid using breadth-first search.

    The solver operates on the same Cell grid produced by MazeGenerator.
    It respects the wall flags on each cell, only traversing passages where
    the relevant wall has been removed.

    Attributes:
        grid: 2-D list of Cell objects, indexed as grid[y][x].
        width: Number of columns in the maze.
        height: Number of rows in the maze.

    Example:
        >>> from mazegen import MazeGenerator, MazeSolver
        >>> gen = MazeGenerator(21, 15, perfect=True, seed=42)
        >>> gen.generate()
        >>> solver = MazeSolver(gen.grid, gen.width, gen.height)
        >>> path = solver.solve(0, 0, 20, 14)
        >>> print(path)  # e.g. "SSEENESE..."
    """

    def __init__(self, grid: list[list[Cell]], width: int, height: int) -> None:
        """Initialise the solver with a maze grid.

        Args:
            grid: 2-D list of Cell objects representing the maze.
            width: Number of columns in the maze.
            height: Number of rows in the maze.
        """
        self.grid: list[list[Cell]] = grid
        self.width: int = width
        self.height: int = height

    def solve(self, start_x: int, start_y: int,
              exit_x: int, exit_y: int) -> str | None:
        """Find the shortest path from a start cell to an exit cell.

        Uses BFS to guarantee the shortest path in an unweighted grid.
        Movement between two adjacent cells is only allowed when the
        separating wall is open on both sides.

        Args:
            start_x: Column index of the start cell.
            start_y: Row index of the start cell.
            exit_x: Column index of the target cell.
            exit_y: Row index of the target cell.

        Returns:
            A string of direction characters ('N', 'E', 'S', 'W') describing
            the shortest path, or None if no path exists.
        """
        queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
        came_from: dict[tuple[int, int], tuple[tuple[int, int], str] | None] = {
            (start_x, start_y): None
        }
        directions: list[tuple[int, int, str]] = [
            (0, -1, 'N'),
            (1, 0,  'E'),
            (0, 1,  'S'),
            (-1, 0, 'W'),
        ]
        while queue:
            cx, cy = queue.popleft()
            if cx == exit_x and cy == exit_y:
                return self._build_path(came_from, exit_x, exit_y)
            for dx, dy, direction in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not self.grid[cy][cx].walls[direction]:
                        if (nx, ny) not in came_from:
                            queue.append((nx, ny))
                            came_from[(nx, ny)] = ((cx, cy), direction)
        return None

    def _build_path(self,
                    came_from: dict[tuple[int, int],
                                    tuple[tuple[int, int], str] | None],
                    end_x: int, end_y: int) -> str:
        """Reconstruct the path string by back-tracking through came_from.

        Args:
            came_from: Dictionary mapping each visited cell to the cell it
                       was reached from and the direction taken.
            end_x: Column index of the destination cell.
            end_y: Row index of the destination cell.

        Returns:
            A string of direction characters representing the path from
            the start cell to (end_x, end_y).
        """
        path: str = ""
        current_step: tuple[int, int] = (end_x, end_y)
        while True:
            val = came_from[current_step]
            if val is None:
                break
            prev_step, direction = val
            path += direction
            current_step = prev_step
        return path[::-1]
