"""
Cell module for the A-Maze-ing project (42 Network).

Defines the Cell class, which represents a single room (node) in the maze grid.
"""


class Cell:
    """Represent a single cell (room) within the maze grid.

    Each cell tracks its grid position, whether it has been visited during
    maze generation, which of its four walls are still closed, and whether it
    belongs to the decorative "42" pattern.

    Attributes:
        x: Column index of this cell (0-based).
        y: Row index of this cell (0-based).
        visited: True once the maze-generation algorithm has processed this cell.
        walls: Mapping from cardinal direction to a boolean indicating whether
               the wall in that direction is closed (True) or open (False).
               Keys are 'N' (north), 'E' (east), 'S' (south), 'W' (west).
        is_42: True if this cell is part of the decorative "42" pattern and
               must remain fully walled throughout generation.
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialise a cell at (x, y) with all walls closed and unvisited.

        Args:
            x: Column index of the cell within the maze grid.
            y: Row index of the cell within the maze grid.
        """
        self.x: int = x
        self.y: int = y
        self.visited: bool = False
        self.walls: dict[str, bool] = {
            'N': True,
            'E': True,
            'S': True,
            'W': True,
        }
        self.is_42: bool = False

    def get_hex(self) -> str:
        """Return the hexadecimal wall encoding for this cell.

        The encoding is a single uppercase hex digit whose bits represent
        closed walls: bit 0 (LSB) = North, bit 1 = East, bit 2 = South,
        bit 3 = West.  A set bit (1) means the wall is closed; a clear
        bit (0) means the wall is open.

        Returns:
            A single uppercase hexadecimal character ('0'–'F').

        Example:
            A cell with only its north and east walls closed returns '3'
            (binary 0011).  A fully enclosed cell returns 'F' (binary 1111).
        """
        val: int = 0
        if self.walls['N']:
            val += 1
        if self.walls['E']:
            val += 2
        if self.walls['S']:
            val += 4
        if self.walls['W']:
            val += 8
        return hex(val)[2:].upper()
