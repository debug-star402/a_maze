import sys
import os
import random
from mazegen import MazeGenerator, MazeSolver


def parse_config(filepath: str) -> dict[str, str]:
    """Reads the configuration file and returns a dictionary of settings."""
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


def render_terminal(generator: MazeGenerator, path_coords: list[tuple[int, int]], 
                    show_path: bool, wall_color: str, entry_coord: tuple[int, int], 
                    exit_coord: tuple[int, int]) -> None:
    """Renders the maze to the terminal using ASCII and ANSI color codes."""
    colors = {
        'white': '\033[97m',
        'red': '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    c_wall = colors.get(wall_color, colors['white'])
    c_reset = colors['reset']
    width, height = generator.width, generator.height
    print(c_wall + "+" + "---+" * width + c_reset)
    for y in range(height):
        room_wall = c_wall + "|" + c_reset
        for x in range(width):
            char = " "
            if (x, y) == entry_coord:
                char = "\033[93mS\033[0m"
            elif (x, y) == exit_coord:
                char = "\033[93mE\033[0m"
            elif show_path and (x, y) in path_coords:
                char = "\033[96m.\033[0m"
            elif generator.grid[y][x].is_42:
                char = "\033[95mX\033[0m"
            if generator.grid[y][x].walls['E']:
                room_wall += f" {char} {c_wall}|{c_reset}"
            else:
                room_wall += f" {char}  "
        print(room_wall)
        room_floor = c_wall + "+" + c_reset
        for x in range(width):
            if generator.grid[y][x].walls['S']:
                room_floor += c_wall + "---+" + c_reset
            else:
                room_floor += c_wall + "   +" + c_reset
        print(room_floor)


def interactive_menu(generator: MazeGenerator, solver: MazeSolver, 
                     entry_coord: tuple[int, int], exit_coord: tuple[int, int]) -> None:
    """Launches the interactive terminal loop required by the subject."""
    show_path: bool = False
    color_palette: list[str] = ['white', 'blue', 'green', 'red']
    color_idx: int = 0
    path_str = solver.solve(entry_coord[0], entry_coord[1], exit_coord[0], exit_coord[1])
    path_coords: list[tuple[int, int]] = []
    
    if path_str:
        cx, cy = entry_coord
        for move in path_str:
            if move == 'N': cy -= 1
            elif move == 'S': cy += 1
            elif move == 'E': cx += 1
            elif move == 'W': cx -= 1
            path_coords.append((cx, cy))

    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=== A-Maze-ing ===")
        render_terminal(generator, path_coords, show_path, color_palette[color_idx], entry_coord, exit_coord)
        print("\n1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")
        
        choice = input("Choice? (1-4): ").strip()
        if choice == '1':
            generator.generate()
            path_str = solver.solve(entry_coord[0], entry_coord[1], exit_coord[0], exit_coord[1])
            path_coords.clear()
            if path_str:
                cx, cy = entry_coord
                for move in path_str:
                    if move == 'N': cy -= 1
                    elif move == 'S': cy += 1
                    elif move == 'E': cx += 1
                    elif move == 'W': cx -= 1
                    path_coords.append((cx, cy))
        elif choice == '2':
            show_path = not show_path
        elif choice == '3':
            color_idx = (color_idx + 1) % len(color_palette)
        elif choice == '4':
            print("Exiting...")
            break


def main() -> None:
    """Main execution pipeline."""
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
    perfect: bool = config['PERFECT'].title() == 'True'
    seed: int | None = int(config['SEED']) if 'SEED' in config else None
    maze = MazeGenerator(width, height, perfect, seed)
    maze.generate()
    if entry_y == 0: maze.grid[entry_y][entry_x].walls['N'] = False
    elif entry_y == height - 1: maze.grid[entry_y][entry_x].walls['S'] = False
    elif entry_x == 0: maze.grid[entry_y][entry_x].walls['W'] = False
    elif entry_x == width - 1: maze.grid[entry_y][entry_x].walls['E'] = False
    if exit_y == 0: maze.grid[exit_y][exit_x].walls['N'] = False
    elif exit_y == height - 1: maze.grid[exit_y][exit_x].walls['S'] = False
    elif exit_x == 0: maze.grid[exit_y][exit_x].walls['W'] = False
    elif exit_x == width - 1: maze.grid[exit_y][exit_x].walls['E'] = False
    solver = MazeSolver(maze.grid, width, height)
    path_str = solver.solve(entry_x, entry_y, exit_x, exit_y)
    if path_str is None:
        print("Error: Maze is unsolvable!")
        sys.exit(1)
    hex_grid = maze.get_hex_grid()
    out_str = f"{hex_grid}\n\n{entry_x},{entry_y}\n{exit_x},{exit_y}\n{path_str}\n"
    with open(config['OUTPUT_FILE'], 'w') as file:
        file.write(out_str)
    print(f"Maze successfully written to {config['OUTPUT_FILE']}")
    input("Press Enter to launch the interactive terminal...")
    interactive_menu(maze, solver, (entry_x, entry_y), (exit_x, exit_y))


if __name__ == "__main__":
    main()
