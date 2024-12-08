import pygame
import random
import sys
import time
import math
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
MAZE_WIDTH = 600
GRID_SIZE = 21
CELL_SIZE = MAZE_WIDTH // GRID_SIZE
SIDEBAR_WIDTH = WINDOW_WIDTH - MAZE_WIDTH

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (173, 216, 230)
BUTTON_COLOR = (200, 200, 200)
SIDEBAR_COLOR = (150, 150, 150)
BUTTON_HOVER_COLOR = (180, 180, 180)
NEW_MAZE_BUTTON_COLOR = (220, 60, 60)
NEW_MAZE_HOVER_COLOR = (200, 40, 40)

# Animation settings
TRANSITION_SPEED = 5
BUTTON_CLICK_DURATION = 100

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.base_color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.click_animation = 0
        
    def draw(self, surface):
        # Calculate button elevation based on click animation
        elevation = max(0, 4 - self.click_animation)
        
        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += elevation
        pygame.draw.rect(surface, (100, 100, 100), shadow_rect)
        
        # Draw main button
        button_rect = self.rect.copy()
        button_rect.y -= self.click_animation
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, button_rect, border_radius=5)
        
        # Draw text
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        
        # Update click animation
        if self.click_animation > 0:
            self.click_animation = max(0, self.click_animation - 0.5)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.click_animation = 4
            return True
        return False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.click_animation = 4
            return True
        return False
        
class SolutionTime:
    def __init__(self, method, time, path_length, nodes_visited):
        self.method = method
        self.time = time
        self.path_length = path_length
        self.nodes_visited = nodes_visited
        self.timestamp = pygame.time.get_ticks()

def generate_maze(size):
    # Generate a solvable random maze using recursive backtracking.
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
small_font = pygame.font.Font(None, 24)

# Create buttons
sidebar_x = MAZE_WIDTH + 20
button_width = SIDEBAR_WIDTH - 40
button_height = 50
buttons = {
    'bfs': Button(sidebar_x, 50, button_width, button_height, "BFS"),
    'dfs': Button(sidebar_x, 120, button_width, button_height, "DFS"),
    'astar_manhattan': Button(sidebar_x, 190, button_width, button_height, "A* Manhattan"),
    'astar_euclidean': Button(sidebar_x, 260, button_width, button_height, "A* Euclidean"),
    'manual': Button(sidebar_x, 330, button_width, button_height, "Try Yourself"),
    'new_maze': Button(sidebar_x, WINDOW_HEIGHT - 70, button_width, button_height, 
                      "New Maze", NEW_MAZE_BUTTON_COLOR, NEW_MAZE_HOVER_COLOR)
}

def draw_maze(visited=set(), path=[]):
    # Draw the maze and agent.
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
    # Draw the sidebar with buttons.
    pygame.draw.rect(screen, SIDEBAR_COLOR, (MAZE_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
    for button in buttons.values():
        button.draw(screen)  # Pass the screen surface to the draw method

def dfs_solve(maze, start, goal):
    # Solve the maze using DFS with visualization.
    stack = [start]
    visited = set()
    parent_map = {}
    nodes_visited = 0  # Count nodes visited

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        nodes_visited += 1  # Increment nodes visited

        draw_maze(visited=visited)
        pygame.display.flip()
        pygame.time.delay(50)

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent_map.get(current)
            return path[::-1], nodes_visited  # Return path and nodes visited

        x, y = current
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited and maze[nx][ny] == 0:
                stack.append((nx, ny))
                parent_map[(nx, ny)] = current
    return [], nodes_visited  # Return empty path if unsolvable

def bfs_solve(maze, start, goal):
    # Solve the maze using BFS with visualization.
    queue = deque([start])
    visited = set()
    parent_map = {}
    nodes_visited = 0  # Count nodes visited

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        nodes_visited += 1  # Increment nodes visited

        draw_maze(visited=visited)
        pygame.display.flip()
        pygame.time.delay(50)

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent_map.get(current)
            return path[::-1], nodes_visited  # Return path and nodes visited

        x, y = current
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited and maze[nx][ny] == 0:
                queue.append((nx, ny))
                parent_map[(nx, ny)] = current
    return [], nodes_visited

import heapq

def astar_manhattan_solve(maze, start, goal):
    p_queue = [(0, start)]
    visited = set()
    parent_map = {}
    g_score_map = {}
    nodes_visited = 0

    while p_queue:
        current = heapq.heappop(p_queue)[1]
        if current in visited:
            continue
        visited.add(current)
        nodes_visited += 1

        draw_maze(visited)
        pygame.display.flip()
        pygame.time.delay(50)

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent_map.get(current)
            return path[::-1], nodes_visited

        x, y = current
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited and maze[nx][ny] == 0:
                g_score = g_score_map.get((x, y), 0) + 1
                f_score = g_score + heuristic_manhattan((nx, ny), goal)
                heapq.heappush(p_queue, (f_score, (nx, ny)))
                parent_map[(nx, ny)] = (x, y)
                g_score_map[(nx, ny)] = g_score

    return [], nodes_visited

def astar_euclidean_solve(maze, start, goal):
    p_queue = [(0, start)]
    visited = set()
    parent_map = {}
    g_score_map = {}
    nodes_visited = 0

    while p_queue:
        current = heapq.heappop(p_queue)[1]
        if current in visited:
            continue
        visited.add(current)
        nodes_visited += 1

        draw_maze(visited)
        pygame.display.flip()
        pygame.time.delay(50)

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent_map.get(current)
            return path[::-1], nodes_visited

        x, y = current
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited and maze[nx][ny] == 0:
                g_score = g_score_map.get((x, y), 0) + 1
                f_score = g_score + heuristic_euclidean((nx, ny), goal)
                heapq.heappush(p_queue, (f_score, (nx, ny)))
                parent_map[(nx, ny)] = (x, y)
                g_score_map[(nx, ny)] = g_score

    return [], nodes_visited

def heuristic_manhattan(node,goal): # This is just used for AStar (Manhattan distance)
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

def heuristic_euclidean(node,goal): # This is just used for AStar (Euclidean distance)
    dx = node[0] - goal[0]
    dy = node[1] - goal[1]
    return math.sqrt(dx**2 + dy**2)

def show_message(message, duration=2000):
    # Show a message in the center of the maze area.
    text_surface = font.render(message, True, BLACK)
    text_rect = text_surface.get_rect(center=(MAZE_WIDTH // 2, WINDOW_HEIGHT // 2))
    background_rect = text_rect.inflate(20, 20)
    
    # Store the current time
    start_time = pygame.time.get_ticks()
    
    while pygame.time.get_ticks() - start_time < duration:
        # Draw the current state
        screen.fill(BLACK)
        draw_maze()
        draw_sidebar()
        
        # Draw message with background
        pygame.draw.rect(screen, WHITE, background_rect)
        screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        pygame.time.delay(10)

def format_time(seconds):
    # Return string that represents time (takes secnds as input)
    minutes = int(seconds // 60)
    seconds = seconds % 60
    if minutes > 0:
        return f"{minutes}m {seconds:.1f}s"
    return f"{seconds:.3f}s"

def draw_solution_time():
    # Draw the recorded solution time and stats on the sidebar.
    start_y = 400

    time_text = f"{solution_time.method}: {format_time(solution_time.time)}"
    path_text = f"Path Length: {solution_time.path_length}"
    nodes_text = f"Nodes Visited: {solution_time.nodes_visited}"

    time_surface = small_font.render(time_text, True, BLACK)
    path_surface = small_font.render(path_text, True, BLACK)
    nodes_surface = small_font.render(nodes_text, True, BLACK)

    screen.blit(time_surface, (sidebar_x, start_y))
    screen.blit(path_surface, (sidebar_x, start_y + 20))
    screen.blit(nodes_surface, (sidebar_x, start_y + 40))

def solve_with_timer(solver_func, maze, start, goal):
    # Run the solver and measure time, nodes visited, and path length.
    start_time = time.time()
    path, nodes_visited = solver_func(maze, start, goal)
    end_time = time.time()
    path_length = len(path)
    return path, end_time - start_time, path_length, nodes_visited

def draw_solve_time(solve_time, x, y):
    #Draw the solving time on the sidebar.
    time_text = f"Time: {solve_time:.3f}s"
    time_surface = small_font.render(time_text, True, BLACK)
    screen.blit(time_surface, (x, y))

# Modified movement functions for smoother animation
def move_agent_along_path(path):
    # Move the agent smoothly along the solution path.
    global agent_pos
    current_pos = list(agent_pos)
    
    for next_pos in path:
        # Animate movement between current and next position
        start_x, start_y = current_pos
        end_x, end_y = next_pos
        
        for t in range(TRANSITION_SPEED + 1):
            progress = t / TRANSITION_SPEED
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            agent_pos = [current_x, current_y]
            
            screen.fill(BLACK)
            draw_maze(path=path)
            draw_sidebar()
            pygame.display.flip()
            pygame.time.delay(20)
        
        current_pos = list(next_pos)
    
    agent_pos = list(path[-1])

def try_move(dx, dy):
    # Try to move the agent with smooth animation.
    global agent_pos, user_start_time
    new_x, new_y = agent_pos[0] + dx, agent_pos[1] + dy
    
    # Start timing on first move
    if user_start_time is None and manual_mode:
        user_start_time = time.time()
    
    if (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and 
        maze[new_x][new_y] == 0):
        # Animate movement
        start_x, start_y = agent_pos
        for t in range(TRANSITION_SPEED + 1): # This makes the agent smoother by altering their speed through the maze in increments instead of by full bloks
            progress = t / TRANSITION_SPEED
            current_x = start_x + dx * progress
            current_y = start_y + dy * progress
            agent_pos = [current_x, current_y]
            
            screen.fill(BLACK)
            draw_maze()
            draw_sidebar()
            pygame.display.flip()
            pygame.time.delay(5)
        
        agent_pos = [new_x, new_y]
        
        # Check if goal is reached
        if (new_x, new_y) == goal_pos and manual_mode:
            end_time = time.time()
            solve_time = end_time - user_start_time
            #solution_times.append(SolutionTime("Manual", solve_time))
            #show_message(f"Goal Reached! Time: {format_time(solve_time)}")
            pygame.time.delay(500)
            agent_pos = list(start_pos)
            user_start_time = None








# Main game loop
clock = pygame.time.Clock()
manual_mode = False
last_solve_time = None
solve_method = None
solution_time = None
user_start_time = None  # Track when user starts solving


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Handle button events
        for button_id, button in buttons.items():
            if button.handle_event(event):
                if button_id == 'bfs':
                     path, solve_time, path_length, nodes_visited = solve_with_timer(bfs_solve, maze, start_pos, goal_pos)
                     solution_time = (SolutionTime("BFS", solve_time, path_length, nodes_visited))
                     move_agent_along_path(path)
                elif button_id == 'dfs':
                    path, solve_time, path_length, nodes_visited = solve_with_timer(dfs_solve, maze, start_pos, goal_pos)
                    solution_time = (SolutionTime("DFS", solve_time, path_length, nodes_visited))
                    move_agent_along_path(path)
                elif button_id == 'astar_manhattan':
                    path, solve_time, path_length, nodes_visited = solve_with_timer(astar_manhattan_solve, maze, start_pos, goal_pos)
                    solution_time = (SolutionTime("ASTAR MANHATTAN", solve_time, path_length, nodes_visited))
                    move_agent_along_path(path)
                elif button_id == 'astar_euclidean':
                    path, solve_time, path_length, nodes_visited = solve_with_timer(astar_euclidean_solve, maze, start_pos, goal_pos)
                    solution_time = (SolutionTime("ASTAR EUCLIDEAN", solve_time, path_length, nodes_visited))
                    move_agent_along_path(path)
                elif button_id == 'manual':
                    manual_mode = True
                    agent_pos = list(start_pos)
                    user_start_time = None  # Reset user time
                elif button_id == 'new_maze':
                    maze = generate_maze(GRID_SIZE)
                    agent_pos = list(start_pos)
                    solution_times = []  # Clear solution times for new maze
                    user_start_time = None
                    manual_mode = False
        
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
    if solution_time is not None:
        draw_solution_time()  # Draw all solution times
    
    pygame.display.flip()
    clock.tick(60)