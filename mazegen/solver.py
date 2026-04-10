from collections import deque
from mazegen.cell import Cell


class MazeSolver:
    def __init__(self, grid: list[list[Cell]], width: int, height: int) -> None:
        self.grid: list[list[Cell]] = grid
        self.width: int = width
        self.height: int = height

    def solve(self, start_x: int, start_y: int, exit_x: int, exit_y: int) -> str | None:
        queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
        came_from: dict[tuple[int, int], tuple[tuple[int, int], str] | None] = {}
        came_from[(start_x, start_y)] = None
        directions: list[tuple[int, int, str]] = [
            (0, -1, 'N'),
            (1, 0, 'E'),
            (0, 1, 'S'),
            (-1, 0, 'W')
        ]
        while len(queue) > 0:
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
                    came_from: dict[tuple[int, int], tuple[tuple[int, int], str] | None], 
                    end_x: int, end_y: int) -> str:
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
