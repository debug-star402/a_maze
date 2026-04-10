"""
Maze generator module for the A-Maze-ing project (42 Network).

Provides the MazeGenerator class, which builds perfect or imperfect mazes
using a randomised depth-first search (recursive backtracker) algorithm and
embeds the "42" pattern as a set of fully-closed cells.
"""
import random
from mazegen.cell import Cell


class MazeGenerator:
    """Generate a grid-based maze using a randomised depth-first search.

    The generator supports both *perfect* mazes (a unique path between every
    pair of cells) and *imperfect* mazes (extra passages that create loops).
    A "42" pattern of fully-walled cells is injected into the centre of any
    maze that is large enough to accommodate it (at least 15 × 9 cells).

    Attributes:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
        perfect: Whether to produce a perfect (loop-free) maze.
        grid: 2-D list of Cell objects, indexed as grid[y][x].

    Example:
        >>> from mazegen import MazeGenerator, MazeSolver
        >>> gen = MazeGenerator(21, 15, perfect=True, seed=42)
        >>> gen.generate()
        >>> print(gen.get_hex_grid())   # hexadecimal wall encoding
        >>> solver = MazeSolver(gen.grid, gen.width, gen.height)
        >>> path = solver.solve(0, 0, 20, 14)
        >>> print(path)  # e.g. "SSEENE..."
    """

    def __init__(self, width: int, height: int, perfect: bool,
                 seed: int | None = None) -> None:
        """Initialise the generator with maze dimensions and options.

        Args:
            width: Number of columns (must be ≥ 2).
            height: Number of rows (must be ≥ 2).
            perfect: If True the maze will have exactly one path between any
                two reachable cells.  If False, extra walls are randomly
                removed to introduce loops.
            seed: Optional integer seed for the random-number generator.
                  Supplying the same seed always produces the same maze.
        """
        self.width: int = width
        self.height: int = height
        self.perfect: bool = perfect
        self.grid: list[list[Cell]] = []
        if seed is not None:
            random.seed(seed)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self) -> None:
        """Build a new maze in-place.

        Resets the grid, injects the "42" pattern, carves the maze with a
        randomised DFS, and—if the maze is imperfect—punches extra passages
        while guaranteeing that no 3 × 3 open area is created.
        """
        self._create_grid()
        self._inject_42()
        self._carve_maze()
        if not self.perfect:
            self._make_imperfect()

    def get_hex_grid(self) -> str:
        """Return the maze as a string of hexadecimal wall-encoding characters.

        Each cell is represented by a single uppercase hex digit whose bits
        encode closed walls: bit 0 = North, bit 1 = East, bit 2 = South,
        bit 3 = West.  Rows are separated by newline characters.

        Returns:
            A multi-line string with one row of hex digits per maze row.
        """
        maze_lines: list[str] = []
        for y in range(self.height):
            row_str: str = ""
            for x in range(self.width):
                row_str += self.grid[y][x].get_hex()
            maze_lines.append(row_str)
        return "\n".join(maze_lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _create_grid(self) -> None:
        """Initialise a fresh grid of unvisited, fully-walled cells."""
        self.grid = []
        for y in range(self.height):
            row: list[Cell] = []
            for x in range(self.width):
                row.append(Cell(x, y))
            self.grid.append(row)

    def _inject_42(self) -> None:
        """Mark the cells that form the "42" pattern as visited and closed.

        The pattern is centred in the maze.  If the maze is smaller than
        15 × 9 cells a warning is printed and the pattern is skipped.
        """
        if self.width < 15 or self.height < 9:
            print("Warning: Maze too small to generate the '42' pattern.")
            return
        start_x: int = (self.width - 9) // 2
        start_y: int = (self.height - 5) // 2
        coords_42: list[tuple[int, int]] = [
            (0, 0), (3, 0), (0, 1), (3, 1),
            (0, 2), (1, 2), (2, 2), (3, 2),
            (3, 3), (3, 4),
            (5, 0), (6, 0), (7, 0), (8, 0),
            (8, 1), (5, 2), (6, 2), (7, 2), (8, 2),
            (5, 3), (5, 4), (6, 4), (7, 4), (8, 4)
        ]
        for dx, dy in coords_42:
            x: int = start_x + dx
            y: int = start_y + dy
            self.grid[y][x].visited = True
            self.grid[y][x].is_42 = True

    def _carve_maze(self) -> None:
        """Carve passages using a randomised iterative depth-first search.

        Starts from the top-left non-42 cell and visits every non-42 cell
        exactly once, removing walls between adjacent unvisited neighbours.
        """
        start_x, start_y = 0, 0
        while self.grid[start_y][start_x].is_42:
            start_x += 1
        self.grid[start_y][start_x].visited = True
        stack: list[tuple[int, int]] = [(start_x, start_y)]
        walls_map: dict[tuple[int, int], tuple[str, str]] = {
            (0, -1): ('N', 'S'),
            (1, 0):  ('E', 'W'),
            (0, 1):  ('S', 'N'),
            (-1, 0): ('W', 'E'),
        }
        while stack:
            cx, cy = stack[-1]
            unvisited: list[tuple[int, int, int, int]] = []
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx: int = cx + dx
                ny: int = cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not self.grid[ny][nx].visited:
                        unvisited.append((nx, ny, dx, dy))
            if unvisited:
                nx, ny, dx, dy = random.choice(unvisited)
                cur_wall, nxt_wall = walls_map[(dx, dy)]
                self.grid[cy][cx].walls[cur_wall] = False
                self.grid[ny][nx].walls[nxt_wall] = False
                self.grid[ny][nx].visited = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def _make_imperfect(self) -> None:
        """Randomly remove walls to introduce loops into the maze.

        Each candidate wall is removed with an 8 % probability.  Before
        committing a removal the method checks that no 3 × 3 fully-open
        area would be created; if one would, the wall is restored.
        The "42" pattern cells and their neighbours are never modified.
        """
        remove_chance: float = 0.08
        opposite: dict[str, str] = {'S': 'N', 'N': 'S', 'E': 'W', 'W': 'E'}

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].is_42:
                    continue

                # Try removing the south wall
                if y < self.height - 1 and not self.grid[y + 1][x].is_42:
                    if random.random() < remove_chance:
                        self.grid[y][x].walls['S'] = False
                        self.grid[y + 1][x].walls['N'] = False
                        if self._has_3x3_open_near(x, y):
                            self.grid[y][x].walls['S'] = True
                            self.grid[y + 1][x].walls[opposite['S']] = True

                # Try removing the east wall
                if x < self.width - 1 and not self.grid[y][x + 1].is_42:
                    if random.random() < remove_chance:
                        self.grid[y][x].walls['E'] = False
                        self.grid[y][x + 1].walls['W'] = False
                        if self._has_3x3_open_near(x, y):
                            self.grid[y][x].walls['E'] = True
                            self.grid[y][x + 1].walls[opposite['E']] = True

    def _has_3x3_open_near(self, x: int, y: int) -> bool:
        """Check whether any 3 × 3 block near (x, y) is fully open internally.

        Args:
            x: Column of the recently modified cell.
            y: Row of the recently modified cell.

        Returns:
            True if at least one neighbouring 3 × 3 block has all internal
            walls removed, False otherwise.
        """
        for ty in range(y - 2, y + 2):
            for tx in range(x - 2, x + 2):
                if self._is_3x3_open_block(tx, ty):
                    return True
        return False

    def _is_3x3_open_block(self, top_x: int, top_y: int) -> bool:
        """Return True if the 3 × 3 block at (top_x, top_y) is fully open.

        A block is considered fully open when every internal south wall
        (between rows) and every internal east wall (between columns) within
        the block is absent.

        Args:
            top_x: Column index of the block's top-left corner.
            top_y: Row index of the block's top-left corner.

        Returns:
            True if all internal walls in the block are open, False otherwise.
        """
        for cy in range(top_y, top_y + 3):
            for cx in range(top_x, top_x + 3):
                if not (0 <= cx < self.width and 0 <= cy < self.height):
                    return False
                if cy < top_y + 2 and self.grid[cy][cx].walls['S']:
                    return False
                if cx < top_x + 2 and self.grid[cy][cx].walls['E']:
                    return False
        return True
