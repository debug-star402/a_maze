import sys
import os
import random
from mazegen import MazeGenerator, MazeSolver

WALL_CHAR = '█'


def parse_config(filepath: str) -> dict[str, str]:
    """Read the configuration file and return a dictionary of settings.

    Args:
        filepath: Path to the configuration file.

    Returns:
        A dictionary mapping configuration keys (uppercased) to their string values.
    """
    config: dict[str, str] = {}
    if not os.path.exists(filepath):
        print(f"Error: Configuration file '{filepath}' not found.")
        sys.exit(1)
    try:
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip().upper()] = value.strip()
    except IOError:
        print("Error: Could not read the configuration file.")
        sys.exit(1)
    required: list[str] = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'PERFECT', 'OUTPUT_FILE']
    for req in required:
        if req not in config:
            print(f"Error: Missing required configuration key: {req}")
            sys.exit(1)
    return config


def open_border_wall(generator: MazeGenerator, x: int, y: int) -> None:
    """Open the appropriate border wall for an entry or exit cell.

    Args:
        generator: The MazeGenerator instance containing the grid.
        x: The x-coordinate of the cell.
        y: The y-coordinate of the cell.
    """
    width, height = generator.width, generator.height
    if y == 0:
        generator.grid[y][x].walls['N'] = False
    elif y == height - 1:
        generator.grid[y][x].walls['S'] = False
    elif x == 0:
        generator.grid[y][x].walls['W'] = False
    elif x == width - 1:
        generator.grid[y][x].walls['E'] = False


def render_terminal(generator: MazeGenerator, path_coords: list[tuple[int, int]],
                    show_path: bool, wall_color: str, entry_coord: tuple[int, int],
                    exit_coord: tuple[int, int]) -> None:
    """Render the maze using Unicode block characters and ANSI colours.

    Each cell is 3 characters wide and 1 character tall. Walls are solid
    block characters coloured with ANSI escape codes.

    Args:
        generator: The MazeGenerator instance containing the grid to render.
        path_coords: List of (x, y) coordinates forming the solution path.
        show_path: Whether to display the solution path.
        wall_color: Colour name for maze walls ('white', 'red', 'green', 'blue').
        entry_coord: (x, y) tuple of the entry cell.
        exit_coord: (x, y) tuple of the exit cell.
    """
    ansi: dict[str, str] = {
        'white':   '\033[97m',
        'red':     '\033[91m',
        'green':   '\033[92m',
        'blue':    '\033[94m',
        'yellow':  '\033[93m',
        'cyan':    '\033[96m',
        'magenta': '\033[95m',
        'reset':   '\033[0m',
    }

    c_wall  = ansi.get(wall_color, ansi['white'])
    c_reset = ansi['reset']
    W = generator.width
    H = generator.height
    path_set = set(path_coords)

    def wall_block(count: int = 1) -> str:
        return c_wall + WALL_CHAR * count + c_reset

    def h_segment(cx: int, cy_cell: int, from_south: bool) -> str:
        if from_south:
            closed = generator.grid[cy_cell][cx].walls['S']
        else:
            closed = generator.grid[cy_cell][cx].walls['N']
        return wall_block(3) if closed else '   '

    def cell_content(cx: int, cy: int) -> str:
        if (cx, cy) == entry_coord:
            return ansi['yellow'] + ' S ' + c_reset
        if (cx, cy) == exit_coord:
            return ansi['red'] + ' E ' + c_reset
        if show_path and (cx, cy) in path_set:
            return ansi['cyan'] + ' \u00b7 ' + c_reset
        if generator.grid[cy][cx].is_42:
            return ansi['magenta'] + WALL_CHAR * 3 + c_reset
        return '   '

    for row in range(2 * H + 1):
        line = ''
        if row % 2 == 0:
            cy = row // 2
            line += wall_block()
            for cx in range(W):
                if cy < H:
                    line += h_segment(cx, cy, from_south=False)
                else:
                    line += h_segment(cx, cy - 1, from_south=True)
                line += wall_block()
        else:
            cy = row // 2
            line += wall_block() if generator.grid[cy][0].walls['W'] else ' '
            for cx in range(W):
                line += cell_content(cx, cy)
                line += wall_block() if generator.grid[cy][cx].walls['E'] else ' '
        print(line)


def interactive_menu(generator: MazeGenerator, solver: MazeSolver,
                     entry_coord: tuple[int, int], exit_coord: tuple[int, int]) -> None:
    """Launch the interactive terminal loop.

    Args:
        generator: The MazeGenerator instance.
        solver: The MazeSolver instance.
        entry_coord: (x, y) tuple of the maze entry cell.
        exit_coord: (x, y) tuple of the maze exit cell.
    """
    show_path: bool = False
    color_palette: list[str] = ['white', 'blue', 'green', 'red']
    color_idx: int = 0

    def compute_path() -> list[tuple[int, int]]:
        path_str = solver.solve(
            entry_coord[0], entry_coord[1],
            exit_coord[0], exit_coord[1]
        )
        coords: list[tuple[int, int]] = []
        if path_str:
            cx, cy = entry_coord
            for move in path_str:
                if move == 'N':
                    cy -= 1
                elif move == 'S':
                    cy += 1
                elif move == 'E':
                    cx += 1
                elif move == 'W':
                    cx -= 1
                coords.append((cx, cy))
        return coords

    path_coords: list[tuple[int, int]] = compute_path()

    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=== A-Maze-ing ===")
        render_terminal(
            generator, path_coords, show_path,
            color_palette[color_idx], entry_coord, exit_coord
        )
        print("\n1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")

        choice = input("Choice? (1-4): ").strip()
        if choice == '1':
            generator.generate()
            open_border_wall(generator, entry_coord[0], entry_coord[1])
            open_border_wall(generator, exit_coord[0], exit_coord[1])
            solver.grid = generator.grid
            path_coords = compute_path()
        elif choice == '2':
            show_path = not show_path
        elif choice == '3':
            color_idx = (color_idx + 1) % len(color_palette)
        elif choice == '4':
            print("Exiting...")
            break


def main() -> None:
    """Run the A-Maze-ing application."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config.txt>")
        sys.exit(1)
    config = parse_config(sys.argv[1])
    try:
        width: int = int(config['WIDTH'])
        height: int = int(config['HEIGHT'])
        entry_x, entry_y = map(int, config['ENTRY'].split(','))
        exit_x, exit_y = map(int, config['EXIT'].split(','))
    except ValueError:
        print("Error: Invalid numeric values in configuration.")
        sys.exit(1)

    if width < 2 or height < 2:
        print("Error: Maze dimensions must be at least 2x2.")
        sys.exit(1)
    if not (0 <= entry_x < width and 0 <= entry_y < height):
        print("Error: ENTRY coordinates are outside maze bounds.")
        sys.exit(1)
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        print("Error: EXIT coordinates are outside maze bounds.")
        sys.exit(1)
    if (entry_x, entry_y) == (exit_x, exit_y):
        print("Error: ENTRY and EXIT must be different cells.")
        sys.exit(1)

    perfect: bool = config['PERFECT'].strip().lower() == 'true'
    seed: int | None = None
    if 'SEED' in config:
        try:
            seed = int(config['SEED'])
        except ValueError:
            print("Error: SEED must be an integer.")
            sys.exit(1)

    maze = MazeGenerator(width, height, perfect, seed)
    maze.generate()
    open_border_wall(maze, entry_x, entry_y)
    open_border_wall(maze, exit_x, exit_y)

    solver = MazeSolver(maze.grid, width, height)
    path_str = solver.solve(entry_x, entry_y, exit_x, exit_y)
    if path_str is None:
        print("Error: Maze is unsolvable!")
        sys.exit(1)

    hex_grid = maze.get_hex_grid()
    out_str = f"{hex_grid}\n\n{entry_x},{entry_y}\n{exit_x},{exit_y}\n{path_str}\n"
    try:
        with open(config['OUTPUT_FILE'], 'w') as file:
            file.write(out_str)
    except IOError:
        print(f"Error: Could not write to output file '{config['OUTPUT_FILE']}'.")
        sys.exit(1)

    print(f"Maze successfully written to {config['OUTPUT_FILE']}")
    input("Press Enter to launch the interactive terminal...")
    interactive_menu(maze, solver, (entry_x, entry_y), (exit_x, exit_y))


if __name__ == "__main__":
    main()
