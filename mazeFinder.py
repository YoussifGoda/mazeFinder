import pygame
import random
import sys
import time
import math
from collections import deque
import heapq

# Initialize Pygame
pygame.init()

# Enhanced Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1024, 768
MAZE_WIDTH = 700
GRID_SIZE = 21
CELL_SIZE = MAZE_WIDTH // GRID_SIZE
SIDEBAR_WIDTH = WINDOW_WIDTH - MAZE_WIDTH

# Enhanced Color Scheme
BACKGROUND = (18, 18, 18)
WALL_COLOR = (40, 44, 52)
PATH_COLOR = (255, 255, 255)
VISITED_COLOR = (103, 140, 177, 150)
SOLUTION_COLOR = (255, 204, 77)
START_COLOR = (72, 187, 120)
GOAL_COLOR = (235, 83, 83)
AGENT_COLOR = (52, 152, 219)

# Button colors
BUTTON_COLOR = (52, 73, 94)
BUTTON_HOVER_COLOR = (72, 93, 114)
BUTTON_TEXT_COLOR = (236, 240, 241)
NEW_MAZE_BUTTON_COLOR = (192, 57, 43)
NEW_MAZE_HOVER_COLOR = (231, 76, 60)

# Animation settings
TRANSITION_SPEED = 8
BUTTON_CLICK_DURATION = 100
FADE_DURATION = 500

class ModernButton:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.base_color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.click_animation = 0
        self.alpha = 255
        
    def draw(self, surface):
        target_color = self.hover_color if self.is_hovered else self.base_color
        current_color = list(self.color)
        for i in range(3):
            current_color[i] += (target_color[i] - current_color[i]) * 0.1
        self.color = tuple(map(int, current_color))

        elevation = max(0, 4 - self.click_animation)
        
        button_rect = self.rect.copy()
        button_rect.y -= self.click_animation
        pygame.draw.rect(surface, self.color, button_rect, border_radius=10)
        
        gradient = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(gradient, (255, 255, 255, 30), gradient.get_rect(), border_radius=10)
        gradient_rect = gradient.get_rect(topleft=button_rect.topleft)
        surface.blit(gradient, gradient_rect)
        
        font = pygame.font.Font(None, 36)
        shadow_surface = font.render(self.text, True, (0, 0, 0))
        text_surface = font.render(self.text, True, BUTTON_TEXT_COLOR)
        
        text_rect = text_surface.get_rect(center=button_rect.center)
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        
        shadow_surface.set_alpha(self.alpha // 2)
        text_surface.set_alpha(self.alpha)
        
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)
        
        if self.click_animation > 0:
            self.click_animation = max(0, self.click_animation - 0.5)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.click_animation = 4
            return True
        return False

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def create_particle(self, pos, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.particles.append({
            'pos': list(pos),
            'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
            'life': 1.0,
            'color': color
        })
        
    def update(self):
        for p in self.particles[:]:
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['life'] -= 0.02
            if p['life'] <= 0:
                self.particles.remove(p)
                
    def draw(self, surface):
        for p in self.particles:
            color = list(p['color'])
            color.append(int(255 * p['life']))
            pygame.draw.circle(surface, color, 
                             (int(p['pos'][0]), int(p['pos'][1])), 
                             int(3 * p['life']))

class SolutionTime:
    def __init__(self, method, time, path_length, nodes_visited):
        self.method = method
        self.time = time
        self.path_length = path_length
        self.nodes_visited = nodes_visited
        self.timestamp = pygame.time.get_ticks()

class MazeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Maze Pathfinding Visualizer")
        
        self.maze = self.generate_maze(GRID_SIZE)
        self.start_pos = (1, 1)
        self.goal_pos = (GRID_SIZE - 2, GRID_SIZE - 2)
        self.agent_pos = list(self.start_pos)
        
        self.particles = ParticleSystem()
        self.solution_time = None
        self.manual_mode = False
        self.user_start_time = None
        
        sidebar_x = MAZE_WIDTH + 20
        button_width = SIDEBAR_WIDTH - 40
        button_height = 50
        self.buttons = {
            'bfs': ModernButton(sidebar_x, 50, button_width, button_height, "BFS"),
            'dfs': ModernButton(sidebar_x, 120, button_width, button_height, "DFS"),
            'astar_manhattan': ModernButton(sidebar_x, 190, button_width, button_height, "A* Manhattan"),
            'astar_euclidean': ModernButton(sidebar_x, 260, button_width, button_height, "A* Euclidean"),
            'manual': ModernButton(sidebar_x, 330, button_width, button_height, "Manual Mode"),
            'new_maze': ModernButton(sidebar_x, WINDOW_HEIGHT - 70, button_width, button_height,
                                   "New Maze", NEW_MAZE_BUTTON_COLOR, NEW_MAZE_HOVER_COLOR)
        }

    def generate_maze(self, size):
        maze = [[1 for _ in range(size)] for _ in range(size)]
        
        def carve_passages(cx, cy):
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < size - 1 and 0 < ny < size - 1 and maze[ny][nx] == 1:
                    maze[cy + dy // 2][cx + dx // 2] = 0
                    maze[ny][nx] = 0
                    carve_passages(nx, ny)
        
        maze[1][1] = 0
        carve_passages(1, 1)
        maze[size - 2][size - 2] = 0
        return maze

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = seconds % 60
        if minutes > 0:
            return f"{minutes}m {seconds:.1f}s"
        return f"{seconds:.3f}s"

    def bfs_solve(self, start, goal):
        queue = deque([start])
        visited = set()
        parent_map = {}
        nodes_visited = 0

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            nodes_visited += 1

            self.draw_maze(visited=visited)
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
                if (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and 
                    (nx, ny) not in visited and self.maze[nx][ny] == 0):
                    queue.append((nx, ny))
                    parent_map[(nx, ny)] = current
        return [], nodes_visited

    def dfs_solve(self, start, goal):
        stack = [start]
        visited = set()
        parent_map = {}
        nodes_visited = 0

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            nodes_visited += 1

            self.draw_maze(visited=visited)
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
                if (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and 
                    (nx, ny) not in visited and self.maze[nx][ny] == 0):
                    stack.append((nx, ny))
                    parent_map[(nx, ny)] = current
        return [], nodes_visited

    def heuristic_manhattan(self, node, goal):
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    def heuristic_euclidean(self, node, goal):
        return math.sqrt((node[0] - goal[0])**2 + (node[1] - goal[1])**2)

    def astar_solve(self, start, goal, heuristic_func):
        p_queue = [(0, start)]
        visited = set()
        parent_map = {}
        g_score_map = {start: 0}
        nodes_visited = 0

        while p_queue:
            _, current = heapq.heappop(p_queue)
            if current in visited:
                continue
            visited.add(current)
            nodes_visited += 1

            self.draw_maze(visited=visited)
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
                if (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and 
                    (nx, ny) not in visited and self.maze[nx][ny] == 0):
                    g_score = g_score_map[current] + 1
                    if (nx, ny) not in g_score_map or g_score < g_score_map[(nx, ny)]:
                        g_score_map[(nx, ny)] = g_score
                        f_score = g_score + heuristic_func((nx, ny), goal)
                        heapq.heappush(p_queue, (f_score, (nx, ny)))
                        parent_map[(nx, ny)] = current
        return [], nodes_visited

    def move_agent_along_path(self, path):
        for next_pos in path:
            start_x, start_y = self.agent_pos
            end_x, end_y = next_pos
            
            for t in range(TRANSITION_SPEED + 1):
                progress = t / TRANSITION_SPEED
                current_x = start_x + (end_x - start_x) * progress
                current_y = start_y + (end_y - start_y) * progress
                self.agent_pos = [current_x, current_y]
                
                self.screen.fill(BACKGROUND)
                self.draw_maze(path=path)
                self.draw_sidebar()
                pygame.display.flip()
                pygame.time.delay(20)

            self.agent_pos = list(next_pos)
            # Create particles at agent position
            screen_x = self.agent_pos[1] * CELL_SIZE + CELL_SIZE // 2
            screen_y = self.agent_pos[0] * CELL_SIZE + CELL_SIZE // 2
            for _ in range(3):
                self.particles.create_particle((screen_x, screen_y), AGENT_COLOR)

    def try_move(self, dx, dy):
        if self.user_start_time is None and self.manual_mode:
            self.user_start_time = time.time()
        
        new_x = self.agent_pos[0] + dx
        new_y = self.agent_pos[1] + dy
        
        if (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and 
            self.maze[new_x][new_y] == 0):
            start_x, start_y = self.agent_pos
            for t in range(TRANSITION_SPEED + 1):
                progress = t / TRANSITION_SPEED
                current_x = start_x + dx * progress
                current_y = start_y + dy * progress
                self.agent_pos = [current_x, current_y]
                
                self.screen.fill(BACKGROUND)
                self.draw_maze()
                self.draw_sidebar()
                pygame.display.flip()
                pygame.time.delay(5)
            
            self.agent_pos = [new_x, new_y]
            
            if (new_x, new_y) == self.goal_pos and self.manual_mode:
                end_time = time.time()
                solve_time = end_time - self.user_start_time
                self.solution_time = SolutionTime("Manual", solve_time, 0, 0)
                pygame.time.delay(500)
                self.agent_pos = list(self.start_pos)
                self.user_start_time = None

    def handle_button_click(self, button_id):
        if button_id == 'bfs':
            path, nodes_visited = self.bfs_solve(self.start_pos, self.goal_pos)
            solve_time = time.time()
            self.solution_time = SolutionTime("BFS", solve_time, len(path), nodes_visited)
            self.move_agent_along_path(path)
            
        elif button_id == 'dfs':
            path, nodes_visited = self.dfs_solve(self.start_pos, self.goal_pos)
            solve_time = time.time()
            self.solution_time = SolutionTime("DFS", solve_time, len(path), nodes_visited)
            self.move_agent_along_path(path)
            
        elif button_id == 'astar_manhattan':
            path, nodes_visited = self.astar_solve(self.start_pos, self.goal_pos, self.heuristic_manhattan)
            solve_time = time.time()
            self.solution_time = SolutionTime("A* Manhattan", solve_time, len(path), nodes_visited)
            self.move_agent_along_path(path)
            
        elif button_id == 'astar_euclidean':
            path, nodes_visited = self.astar_solve(self.start_pos, self.goal_pos, self.heuristic_euclidean)
            solve_time = time.time()
            self.solution_time = SolutionTime("A* Euclidean", solve_time, len(path), nodes_visited)
            self.move_agent_along_path(path)
            
        elif button_id == 'manual':
            self.manual_mode = True
            self.agent_pos = list(self.start_pos)
            self.user_start_time = None
            self.solution_time = None
            
        elif button_id == 'new_maze':
            self.maze = self.generate_maze(GRID_SIZE)
            self.agent_pos = list(self.start_pos)
            self.solution_time = None
            self.user_start_time = None
            self.manual_mode = False

    def handle_keyboard_input(self, key):
        if key == pygame.K_UP:
            self.try_move(-1, 0)
        elif key == pygame.K_DOWN:
            self.try_move(1, 0)
        elif key == pygame.K_LEFT:
            self.try_move(0, -1)
        elif key == pygame.K_RIGHT:
            self.try_move(0, 1)

    def draw_cell(self, x, y, color, surface=None):
        if surface is None:
            surface = self.screen
            
        rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if color == WALL_COLOR:
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (30, 34, 42), rect, 1)
        else:
            pygame.draw.rect(surface, color, rect)
            if color != BACKGROUND:
                gradient = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(gradient, (255, 255, 255, 20), gradient.get_rect())
                surface.blit(gradient, rect)

    def draw_maze(self, visited=set(), path=[]):
        maze_surface = pygame.Surface((MAZE_WIDTH, MAZE_WIDTH))
        maze_surface.fill(BACKGROUND)
        
        for row_idx, row in enumerate(self.maze):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    self.draw_cell(row_idx, col_idx, WALL_COLOR, maze_surface)
                elif (row_idx, col_idx) in visited:
                    self.draw_cell(row_idx, col_idx, VISITED_COLOR, maze_surface)
                elif (row_idx, col_idx) in path:
                    self.draw_cell(row_idx, col_idx, SOLUTION_COLOR, maze_surface)
                else:
                    self.draw_cell(row_idx, col_idx, PATH_COLOR, maze_surface)

        self.draw_cell(self.start_pos[0], self.start_pos[1], START_COLOR, maze_surface)
        self.draw_cell(self.goal_pos[0], self.goal_pos[1], GOAL_COLOR, maze_surface)

        # Draw agent with glow effect
        agent_x = int(self.agent_pos[1] * CELL_SIZE)
        agent_y = int(self.agent_pos[0] * CELL_SIZE)
        
        glow_surface = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA)
        for radius in range(CELL_SIZE * 2, 0, -2):
            alpha = int(100 * (radius / (CELL_SIZE * 2)))
            pygame.draw.circle(glow_surface, (*AGENT_COLOR[:3], alpha), 
                             (CELL_SIZE * 1.5, CELL_SIZE * 1.5), radius)
        
        maze_surface.blit(glow_surface, (agent_x - CELL_SIZE, agent_y - CELL_SIZE))
        pygame.draw.rect(maze_surface, AGENT_COLOR, (agent_x, agent_y, CELL_SIZE, CELL_SIZE))

        # Grid overlay
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(maze_surface, (50, 50, 50), 
                           (i * CELL_SIZE, 0), 
                           (i * CELL_SIZE, MAZE_WIDTH))
            pygame.draw.line(maze_surface, (50, 50, 50), 
                           (0, i * CELL_SIZE), 
                           (MAZE_WIDTH, i * CELL_SIZE))

        self.screen.blit(maze_surface, (0, 0))

    def draw_sidebar(self):
        sidebar_surface = pygame.Surface((SIDEBAR_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            alpha = int(255 * (1 - y / WINDOW_HEIGHT))
            pygame.draw.line(sidebar_surface, (*BACKGROUND, alpha), 
                           (0, y), (SIDEBAR_WIDTH, y))
        self.screen.blit(sidebar_surface, (MAZE_WIDTH, 0))

        for button in self.buttons.values():
            button.draw(self.screen)

        if self.solution_time:
            self.draw_solution_stats()

    def draw_solution_stats(self):
        if not self.solution_time:
            return
            
        font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 24)
        
        stats_surface = pygame.Surface((SIDEBAR_WIDTH - 40, 100), pygame.SRCALPHA)
        pygame.draw.rect(stats_surface, (*BUTTON_COLOR, 200), 
                        stats_surface.get_rect(), border_radius=10)
        
        y_offset = 10
        stats = [
            f"{self.solution_time.method}",
            f"Time: {self.format_time(self.solution_time.time)}",
            f"Path Length: {self.solution_time.path_length}",
            f"Nodes Visited: {self.solution_time.nodes_visited}"
        ]
        
        for i, stat in enumerate(stats):
            color = BUTTON_TEXT_COLOR if i == 0 else (200, 200, 200)
            text = (font if i == 0 else small_font).render(stat, True, color)
            stats_surface.blit(text, (10, y_offset))
            y_offset += 25
            
        self.screen.blit(stats_surface, (MAZE_WIDTH + 20, 400))

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                for button_id, button in self.buttons.items():
                    if button.handle_event(event):
                        self.handle_button_click(button_id)
                
                if self.manual_mode and event.type == pygame.KEYDOWN:
                    self.handle_keyboard_input(event.key)
            
            self.particles.update()
            
            self.screen.fill(BACKGROUND)
            self.draw_maze()
            self.draw_sidebar()
            self.particles.draw(self.screen)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Create and run game
if __name__ == "__main__":
    game = MazeGame()
    game.run()