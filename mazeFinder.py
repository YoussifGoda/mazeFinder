import pygame
import random
import sys
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600  # Increased width for sidebar
MAZE_WIDTH = 600  # Original maze size
GRID_SIZE = 21  # Maze grid dimensions (must be odd for proper walls)
CELL_SIZE = MAZE_WIDTH // GRID_SIZE
SIDEBAR_WIDTH = WINDOW_WIDTH - MAZE_WIDTH

# Colors
BLACK = (0, 0, 0)  # Walls
WHITE = (255, 255, 255)  # Paths
GREEN = (0, 255, 0)  # Start point
RED = (255, 0, 0)  # Goal point
BLUE = (0, 0, 255)  # Agent
YELLOW = (255, 255, 0)  # Solution path
LIGHT_BLUE = (173, 216, 230)  # Visited cells
BUTTON_COLOR = (200, 200, 200)
SIDEBAR_COLOR = (150, 150, 150)
BUTTON_HOVER_COLOR = (180, 180, 180)

def generate_maze(size):
    """Generate a solvable random maze using recursive backtracking."""
    maze = [[1 for _ in range(size)] for _ in range(size)]

    def carve_passages(cx, cy):
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < size and 0 < ny < size and maze[ny][nx] == 1:
                maze[cy + dy // 2][cx + dx // 2] = 0
                maze[ny][nx] = 0
                carve_passages(nx, ny)

    maze[1][1] = 0
    carve_passages(1, 1)
    maze[size - 2][size - 2] = 0
    return maze

# Generate the maze
maze = generate_maze(GRID_SIZE)

# Find the start and goal positions
start_pos = (1, 1)
goal_pos = (GRID_SIZE - 2, GRID_SIZE - 2)
agent_pos = list(start_pos)

# Setup Pygame window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Maze Solver")

font = pygame.font.Font(None, 36)

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False

    def draw(self):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Create buttons
sidebar_x = MAZE_WIDTH + 20
button_width = SIDEBAR_WIDTH - 40
button_height = 50
buttons = {
    'bfs': Button(sidebar_x, 50, button_width, button_height, "Solve by BFS"),
    'dfs': Button(sidebar_x, 120, button_width, button_height, "Solve by DFS"),
    'manual': Button(sidebar_x, 190, button_width, button_height, "Try Yourself"),
    'new_maze': Button(sidebar_x, WINDOW_HEIGHT - 70, button_width, button_height, "New Maze")
}

def draw_maze(visited=set(), path=[]):
    """Draw the maze, agent, and additional visualization."""
    for row_idx, row in enumerate(maze):
        for col_idx, cell in enumerate(row):
            x, y = col_idx * CELL_SIZE, row_idx * CELL_SIZE
            if cell == 1:
                pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE))
            elif (row_idx, col_idx) in visited:
                pygame.draw.rect(screen, LIGHT_BLUE, (x, y, CELL_SIZE, CELL_SIZE))
            elif (row_idx, col_idx) in path:
                pygame.draw.rect(screen, YELLOW, (x, y, CELL_SIZE, CELL_SIZE))
            else:
                pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))

    # Draw start and goal
    start_x, start_y = start_pos[1] * CELL_SIZE, start_pos[0] * CELL_SIZE
    goal_x, goal_y = goal_pos[1] * CELL_SIZE, goal_pos[0] * CELL_SIZE
    pygame.draw.rect(screen, GREEN, (start_x, start_y, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, (goal_x, goal_y, CELL_SIZE, CELL_SIZE))

    # Draw agent
    agent_x, agent_y = agent_pos[1] * CELL_SIZE, agent_pos[0] * CELL_SIZE
    pygame.draw.rect(screen, BLUE, (agent_x, agent_y, CELL_SIZE, CELL_SIZE))

def draw_sidebar():
    """Draw the sidebar with buttons."""
    pygame.draw.rect(screen, SIDEBAR_COLOR, (MAZE_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
    for button in buttons.values():
        button.draw()

def bfs_solve(maze, start, goal):
    """Solve the maze using BFS with visualization."""
    queue = deque([start])
    visited = set()
    parent_map = {}

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        draw_maze(visited=visited)
        pygame.display.flip()
        pygame.time.delay(50)

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent_map.get(current)
            return path[::-1]

        x, y = current
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited and maze[nx][ny] == 0:
                queue.append((nx, ny))
                parent_map[(nx, ny)] = current
    return []

def dfs_solve(maze, start, goal):
    """Solve the maze using DFS with visualization."""
    stack = [start]
    visited = set()
    parent_map = {}

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        draw_maze(visited=visited)
        pygame.display.flip()
        pygame.time.delay(50)

        if current == goal:
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
        screen.fill(BLACK)
        draw_maze(path=path)
        draw_sidebar()
        pygame.display.flip()
        pygame.time.delay(100)

def try_move(dx, dy):
    """Try to move the agent in the given direction."""
    global agent_pos
    new_x, new_y = agent_pos[0] + dx, agent_pos[1] + dy
    if (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and 
        maze[new_x][new_y] == 0):
        agent_pos = [new_x, new_y]

# Game state
manual_mode = False

# Main game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Handle button events
        for button_id, button in buttons.items():
            if button.handle_event(event):
                if button_id == 'bfs':
                    solution_path = bfs_solve(maze, start_pos, goal_pos)
                    move_agent_along_path(solution_path)
                elif button_id == 'dfs':
                    solution_path = dfs_solve(maze, start_pos, goal_pos)
                    move_agent_along_path(solution_path)
                elif button_id == 'manual':
                    manual_mode = True
                    agent_pos = list(start_pos)
                elif button_id == 'new_maze':
                    maze = generate_maze(GRID_SIZE)
                    agent_pos = list(start_pos)
        
        # Handle keyboard events in manual mode
        if manual_mode and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                try_move(-1, 0)
            elif event.key == pygame.K_DOWN:
                try_move(1, 0)
            elif event.key == pygame.K_LEFT:
                try_move(0, -1)
            elif event.key == pygame.K_RIGHT:
                try_move(0, 1)

    # Draw everything
    screen.fill(BLACK)
    draw_maze()
    draw_sidebar()
    pygame.display.flip()
    clock.tick(30)