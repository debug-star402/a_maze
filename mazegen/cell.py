"""
Cell module for representing a single room in the maze.
"""
class Cell:
    """
    Represents a single cell within the maze grid.
    """

    def __init__(self, x: int, y: int) -> None:
        """
        Initializes a cell with its (x, y) coordinates.
        All walls are closed by default.
        """
        self.x: int = x
        self.y: int = y
        self.visited: bool = False
        self.walls: dict[str, bool] = {
            'N': True,
            'E': True,
            'S': True,
            'W': True
        }
        self.is_42: bool = False


    def get_hex(self) -> str:
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
