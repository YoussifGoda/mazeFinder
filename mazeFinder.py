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
pygame.display.set_caption("Random Maze Game")

def draw_maze():
    """Draw the maze and agent."""
    for row_idx, row in enumerate(maze):
        for col_idx, cell in enumerate(row):
            x, y = col_idx * CELL_SIZE, row_idx * CELL_SIZE
            if cell == 1:  # Wall
                pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE))
            elif cell == 0:  # Path
                pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))

    # Draw the start and goal points
    start_x, start_y = start_pos[1] * CELL_SIZE, start_pos[0] * CELL_SIZE
    goal_x, goal_y = goal_pos[1] * CELL_SIZE, goal_pos[0] * CELL_SIZE
    pygame.draw.rect(screen, GREEN, (start_x, start_y, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, (goal_x, goal_y, CELL_SIZE, CELL_SIZE))

    # Draw the agent
    agent_x, agent_y = agent_pos[1] * CELL_SIZE, agent_pos[0] * CELL_SIZE
    pygame.draw.rect(screen, BLUE, (agent_x, agent_y, CELL_SIZE, CELL_SIZE))

def move_agent(direction):
    """Move the agent in the specified direction if the move is valid."""
    global agent_pos
    moves = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1)
    }
    if direction in moves:
        new_pos = [agent_pos[0] + moves[direction][0], agent_pos[1] + moves[direction][1]]

        # Check bounds and if the position is a path
        if (0 <= new_pos[0] < GRID_SIZE and 0 <= new_pos[1] < GRID_SIZE and 
            maze[new_pos[0]][new_pos[1]] == 0):
            agent_pos = new_pos

# Main game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Check for key presses to move the agent
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        move_agent("up")
    if keys[pygame.K_DOWN]:
        move_agent("down")
    if keys[pygame.K_LEFT]:
        move_agent("left")
    if keys[pygame.K_RIGHT]:
        move_agent("right")

    # Check if agent reached the goal
    if agent_pos == list(goal_pos):
        print("You reached the goal!")
        pygame.quit()
        sys.exit()

    # Draw everything
    screen.fill(BLACK)
    draw_maze()
    pygame.display.flip()
    clock.tick(30)
