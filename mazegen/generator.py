import random
from mazegen.cell import Cell


class MazeGenerator:
    def __init__(self, width: int, height: int, perfect: bool, seed: int | None = None) -> None:
        self.width: int = width
        self.height: int = height
        self.perfect: bool = perfect
        self.grid: list[list[Cell]] = []
        if seed is not None:
            random.seed(seed)

    def generate(self) -> None:
        self._create_grid()
        self._inject_42()
        self._carve_maze()
        if not self.perfect:
            self._make_imperfect()

    def _create_grid(self) -> None:
        self.grid = []
        for y in range(self.height):
            row: list[Cell] = []
            for x in range(self.width):
                row.append(Cell(x, y))
            self.grid.append(row)

    def _inject_42(self) -> None:
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
        start_x, start_y = 0, 0
        while self.grid[start_y][start_x].is_42:
            start_x += 1
        self.grid[start_y][start_x].visited = True
        stack: list[tuple[int, int]] = [(start_x, start_y)]
        walls_map: dict[tuple[int, int], tuple[str, str]] = {
            (0, -1): ('N', 'S'),
            (1, 0): ('E', 'W'),
            (0, 1): ('S', 'N'),
            (-1, 0): ('W', 'E')
        }
        while len(stack) > 0:
            cx, cy = stack[-1]
            unvisited_neighbors: list[tuple[int, int, int, int]] = []
            directions: list[tuple[int, int]] = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            for dx, dy in directions:
                nx: int = cx + dx
                ny: int = cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not self.grid[ny][nx].visited:
                        unvisited_neighbors.append((nx, ny, dx, dy))
            if len(unvisited_neighbors) > 0:
                nx, ny, dx, dy = random.choice(unvisited_neighbors)
                current_wall, next_wall = walls_map[(dx, dy)]
                self.grid[cy][cx].walls[current_wall] = False
                self.grid[ny][nx].walls[next_wall] = False
                self.grid[ny][nx].visited = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def _make_imperfect(self) -> None:
        remove_chance: float = 0.08
        for y in range(self.height):
            for x in range(self.width):
                # Protect the 42 pattern from being smashed
                if self.grid[y][x].is_42:
                    continue
                if y < self.height - 1 and not self.grid[y+1][x].is_42:
                    if random.random() < remove_chance:
                        self.grid[y][x].walls['S'] = False
                        self.grid[y+1][x].walls['N'] = False
                if x < self.width - 1 and not self.grid[y][x+1].is_42:
                    if random.random() < remove_chance:
                        self.grid[y][x].walls['E'] = False
                        self.grid[y][x+1].walls['W'] = False

    def get_hex_grid(self) -> str:
        maze_lines: list[str] = []
        for y in range(self.height):
            row_str: str = ""
            for x in range(self.width):
                row_str += self.grid[y][x].get_hex()
            maze_lines.append(row_str)
        return "\n".join(maze_lines)
