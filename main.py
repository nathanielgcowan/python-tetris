import pygame
import random
import time
import sys

# Game constants
WINDOW_WIDTH, WINDOW_HEIGHT = 300, 600
BLOCK_SIZE = 30
COLUMNS = WINDOW_WIDTH // BLOCK_SIZE
ROWS = WINDOW_HEIGHT // BLOCK_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0),    # Z
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
]

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

class Tetromino:
    def __init__(self, x, y, shape, color):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color

    def rotate(self):
        self.shape = rotate(self.shape)

    def get_coords(self):
        coords = []
        for i, row in enumerate(self.shape):
            for j, val in enumerate(row):
                if val:
                    coords.append((self.x + j, self.y + i))
        return coords

def create_grid(locked):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked:
                grid[y][x] = locked[(x, y)]
    return grid

def valid_space(shape, grid, offset):
    for i, row in enumerate(shape):
        for j, val in enumerate(row):
            if val:
                x = offset[0] + j
                y = offset[1] + i
                if x < 0 or x >= COLUMNS or y >= ROWS:
                    return False
                if y >= 0 and grid[y][x] != BLACK:
                    return False
    return True

def clear_rows(grid, locked):
    cleared = 0
    for y in range(ROWS-1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            for x in range(COLUMNS):
                try:
                    del locked[(x, y)]
                except:
                    continue
            for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
                x, y2 = key
                if y2 < y:
                    locked[(x, y2+1)] = locked.pop((x, y2))
    return cleared

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(surface, grid[y][x], (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    for x in range(COLUMNS):
        pygame.draw.line(surface, GRAY, (x*BLOCK_SIZE, 0), (x*BLOCK_SIZE, WINDOW_HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y*BLOCK_SIZE), (WINDOW_WIDTH, y*BLOCK_SIZE))

def draw_text(surface, text, size, color, pos):
    font = pygame.font.SysFont('Arial', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, pos)

def get_new_tetromino():
    idx = random.randint(0, len(SHAPES)-1)
    shape = SHAPES[idx]
    color = COLORS[idx]
    x = COLUMNS // 2 - len(shape[0]) // 2
    y = 0
    return Tetromino(x, y, shape, color)

def main():
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    locked = {}
    grid = create_grid(locked)
    change_piece = False
    run = True
    current_piece = get_new_tetromino()
    next_piece = get_new_tetromino()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    while run:
        grid = create_grid(locked)
        fall_time += clock.get_rawtime() / 1000
        clock.tick(FPS)

        if fall_time > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    old_shape = current_piece.shape
                    current_piece.rotate()
                    if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                        current_piece.shape = old_shape

        for x, y in current_piece.get_coords():
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for x, y in current_piece.get_coords():
                if y < 0:
                    run = False
                else:
                    locked[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_new_tetromino()
            cleared = clear_rows(grid, locked)
            score += cleared * 100
            change_piece = False

        win.fill(BLACK)
        draw_grid(win, grid)
        draw_text(win, f'Score: {score}', 24, WHITE, (10, 10))
        pygame.display.update()

    pygame.quit()

def main_menu():
    main()

if __name__ == '__main__':
    main_menu()
