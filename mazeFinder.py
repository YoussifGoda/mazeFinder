import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 600
GRID_SIZE = 21  # Maze grid dimensions (must be odd for proper walls)
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE

# Colors
BLACK = (0, 0, 0)  # Walls
WHITE = (255, 255, 255)  # Paths
GREEN = (0, 255, 0)  # Start point
RED = (255, 0, 0)  # Goal point
BLUE = (0, 0, 255)  # Agent
YELLOW = (255, 255, 0)  # Solution path
LIGHT_BLUE = (173, 216, 230)  # Visited cells
BUTTON_COLOR = (200, 200, 200)

def generate_maze(size):
    """Generate a solvable random maze using recursive backtracking."""
    maze = [[1 for _ in range(size)] for _ in range(size)]  # Start with all walls

    def carve_passages(cx, cy):
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < size and 0 < ny < size and maze[ny][nx] == 1:
                maze[cy + dy // 2][cx + dx // 2] = 0  # Carve path
                maze[ny][nx] = 0
                carve_passages(nx, ny)

    maze[1][1] = 0  # Starting point
    carve_passages(1, 1)
    maze[size - 2][size - 2] = 0  # Goal point
    return maze

# Generate the maze
maze = generate_maze(GRID_SIZE)

# Find the start and goal positions
start_pos = (1, 1)
goal_pos = (GRID_SIZE - 2, GRID_SIZE - 2)
agent_pos = list(start_pos)

# Setup Pygame window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Maze Solver with DFS")

font = pygame.font.Font(None, 36)

def draw_button(text, x, y, width, height, color):
    """Draw a button with text."""
    pygame.draw.rect(screen, color, (x, y, width, height))
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (x + 10, y + 10))

def draw_maze(visited=set(), path=[]):
    """Draw the maze, agent, and additional visualization."""
    for row_idx, row in enumerate(maze):
        for col_idx, cell in enumerate(row):
            x, y = col_idx * CELL_SIZE, row_idx * CELL_SIZE
            if cell == 1:  # Wall
                pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE))
            elif (row_idx, col_idx) in visited:  # Visited cells
                pygame.draw.rect(screen, LIGHT_BLUE, (x, y, CELL_SIZE, CELL_SIZE))
            elif (row_idx, col_idx) in path:  # Solution path
                pygame.draw.rect(screen, YELLOW, (x, y, CELL_SIZE, CELL_SIZE))
            else:  # Path
                pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))

    # Draw the start and goal points
    start_x, start_y = start_pos[1] * CELL_SIZE, start_pos[0] * CELL_SIZE
    goal_x, goal_y = goal_pos[1] * CELL_SIZE, goal_pos[0] * CELL_SIZE
    pygame.draw.rect(screen, GREEN, (start_x, start_y, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, (goal_x, goal_y, CELL_SIZE, CELL_SIZE))

    # Draw the agent
    agent_x, agent_y = agent_pos[1] * CELL_SIZE, agent_pos[0] * CELL_SIZE
    pygame.draw.rect(screen, BLUE, (agent_x, agent_y, CELL_SIZE, CELL_SIZE))

def dfs_visualized(maze, start, goal):
    """Solve the maze using DFS with visualization."""
    stack = [start]
    visited = set()
    parent_map = {}

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        # Draw and update the screen to visualize exploration
        draw_maze(visited=visited)
        pygame.display.flip()
        pygame.time.delay(50)  # Slow down for visualization

        if current == goal:
            # Reconstruct path
            path = []
            while current:
                path.append(current)
                current = parent_map.get(current)
            return path[::-1]

        x, y = current
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited and maze[nx][ny] == 0:
                stack.append((nx, ny))
                parent_map[(nx, ny)] = current
    return []

def move_agent_along_path(path):
    """Move the agent step-by-step along the solution path."""
    global agent_pos
    for step in path:
        agent_pos[0], agent_pos[1] = step
        draw_maze(path=path)
        pygame.display.flip()
        pygame.time.delay(100)

# Main game loop
clock = pygame.time.Clock()
button_rect = pygame.Rect(450, 550, 120, 40)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                solution_path = dfs_visualized(maze, start_pos, goal_pos)
                move_agent_along_path(solution_path)

    # Draw everything
    screen.fill(BLACK)
    draw_maze()
    draw_button("Solve", 450, 550, 120, 40, BUTTON_COLOR)
    pygame.display.flip()
    clock.tick(30)
