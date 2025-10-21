#cmd
# pip install pygame


import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 300, 600
BLOCK = 30
COLUMNS, ROWS = WIDTH // BLOCK, HEIGHT // BLOCK
SCREEN = pygame.display.set_mode((WIDTH + 150, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 20)

# 테트리스 블록 모양 (4x4 회전 상태들)
SHAPES = {
    'I': [
        ["....",
         "####",
         "....",
         "...."],
        ["..#.",
         "..#.",
         "..#.",
         "..#."]
    ],
    'O': [
        ["....",
         ".##.",
         ".##.",
         "...."]
    ],
    'T': [
        ["....",
         ".###",
         "..#.",
         "...."],
        ["..#.",
         ".##.",
         "..#.",
         "...."],
        ["..#.",
         ".###",
         "....",
         "...."],
        ["..#.",
         "..##",
         "..#.",
         "...."]
    ],
    'S': [
        ["....",
         ".##.",
         "##..",
         "...."],
        ["..#.",
         ".##.",
         "...#",
         "...."]
    ],
    'Z': [
        ["....",
         "##..",
         ".##.",
         "...."],
        ["...#",
         ".##.",
         "..#.",
         "...."]
    ],
    'J': [
        ["....",
         ".#..",
         ".###",
         "...."],
        ["..##",
         "..#.",
         "..#.",
         "...."],
        ["....",
         ".###",
         "...#",
         "...."],
        ["..#.",
         "..#.",
         ".##.",
         "...."]
    ],
    'L': [
        ["....",
         "...#",
         ".###",
         "...."],
        ["..#.",
         "..#.",
         "..##",
         "...."],
        ["....",
         ".###",
         ".#..",
         "...."],
        [".##.",
         "..#.",
         "..#.",
         "...."]
    ]
}

COLORS = {
    'I': (0, 240, 240),
    'O': (240, 240, 0),
    'T': (160, 0, 240),
    'S': (0, 240, 0),
    'Z': (240, 0, 0),
    'J': (0, 0, 240),
    'L': (240, 160, 0)
}

def rotate_shape(shape, rot):
    s = SHAPES[shape][rot % len(SHAPES[shape])]
    coords = []
    for y, row in enumerate(s):
        for x, ch in enumerate(row):
            if ch == '#':
                coords.append((x, y))
    return coords

class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.rotation = 0
        self.blocks = rotate_shape(shape, self.rotation)
        self.x = COLUMNS // 2 - 2
        self.y = 0

    def rotate(self, grid):
        old_rot = self.rotation
        self.rotation = (self.rotation + 1) % len(SHAPES[self.shape])
        new_blocks = rotate_shape(self.shape, self.rotation)
        if not valid_position(new_blocks, self.x, self.y, grid):
            # wall kicks: try left/right
            for dx in (-1, 1, -2, 2):
                if valid_position(new_blocks, self.x + dx, self.y, grid):
                    self.x += dx
                    self.blocks = new_blocks
                    return
            self.rotation = old_rot
        else:
            self.blocks = new_blocks

    def get_cells(self):
        return [(self.x + bx, self.y + by) for bx, by in self.blocks]

def create_grid():
    return [[None for _ in range(COLUMNS)] for _ in range(ROWS)]

def valid_position(blocks, x, y, grid):
    for bx, by in blocks:
        gx, gy = x + bx, y + by
        if gx < 0 or gx >= COLUMNS or gy >= ROWS:
            return False
        if gy >= 0 and grid[gy][gx] is not None:
            return False
    return True

def lock_piece(piece, grid):
    for gx, gy in piece.get_cells():
        if gy < 0:
            return False  # 게임오버
        grid[gy][gx] = piece.shape
    return True

def clear_lines(grid):
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    cleared = ROWS - len(new_grid)
    for _ in range(cleared):
        new_grid.insert(0, [None for _ in range(COLUMNS)])
    return new_grid, cleared

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            cell = grid[y][x]
            rect = pygame.Rect(x*BLOCK, y*BLOCK, BLOCK, BLOCK)
            pygame.draw.rect(surface, (30,30,30), rect, 1)
            if cell:
                pygame.draw.rect(surface, COLORS[cell], rect.inflate(-2, -2))

def draw_piece(surface, piece, offset_x=0):
    for x, y in piece.get_cells():
        if y >= 0:
            rect = pygame.Rect(x*BLOCK + offset_x, y*BLOCK, BLOCK, BLOCK)
            pygame.draw.rect(surface, COLORS[piece.shape], rect.inflate(-2, -2))

def draw_next(surface, next_piece):
    sx = WIDTH + 20
    sy = 20
    label = FONT.render("NEXT", True, (255,255,255))
    surface.blit(label, (sx, sy))
    for bx, by in rotate_shape(next_piece.shape, 0):
        rect = pygame.Rect(sx + (bx)*BLOCK, sy + 30 + (by)*BLOCK, BLOCK, BLOCK)
        pygame.draw.rect(surface, COLORS[next_piece.shape], rect.inflate(-2, -2))

def draw_info(surface, score, level):
    sx = WIDTH + 20
    sy = 200
    surface.blit(FONT.render(f"SCORE: {score}", True, (255,255,255)), (sx, sy))
    surface.blit(FONT.render(f"LEVEL: {level}", True, (255,255,255)), (sx, sy+30))

def new_piece():
    return Piece(random.choice(list(SHAPES.keys())))

def main():
    grid = create_grid()
    current = new_piece()
    nxt = new_piece()
    fall_time = 0
    fall_speed = 250  # ms per cell (decreases with level) -- 전체 속도 2배
    score = 0
    level = 1
    lines_cleared_total = 0
    running = True
    drop_fast = False
    last_move_down = pygame.time.get_ticks()

    while running:
        dt = CLOCK.tick(60)
        fall_time += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    if valid_position(current.blocks, current.x-1, current.y, grid):
                        current.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if valid_position(current.blocks, current.x+1, current.y, grid):
                        current.x += 1
                elif event.key == pygame.K_UP:
                    current.rotate(grid)
                elif event.key == pygame.K_DOWN:
                    drop_fast = True
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    while valid_position(current.blocks, current.x, current.y+1, grid):
                        current.y += 1
                    if not lock_piece(current, grid):
                        running = False
                    grid, cleared = clear_lines(grid)
                    if cleared:
                        lines_cleared_total += cleared
                        score += [0,100,300,500,800][cleared]
                        level = 1 + lines_cleared_total//10
                        # 단계 증가시 속도도 2배로 조정
                        fall_speed = max(50, 250 - (level-1)*15)
                    current = nxt
                    nxt = new_piece()
                elif event.key == pygame.K_r:
                    # restart
                    grid = create_grid()
                    current = new_piece()
                    nxt = new_piece()
                    score = 0
                    level = 1
                    lines_cleared_total = 0
                    fall_speed = 250
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    drop_fast = False

        # 자동 낙하
        interval = 25 if drop_fast else fall_speed
        if fall_time >= interval:
            fall_time = 0
            if valid_position(current.blocks, current.x, current.y+1, grid):
                current.y += 1
            else:
                ok = lock_piece(current, grid)
                if not ok:
                    # 게임 오버
                    running = False
                    continue
                grid, cleared = clear_lines(grid)
                if cleared:
                    lines_cleared_total += cleared
                    score += [0,100,300,500,800][cleared]
                    level = 1 + lines_cleared_total//10
                    fall_speed = max(50, 250 - (level-1)*15)
                current = nxt
                nxt = new_piece()

        SCREEN.fill((0,0,0))
        # 플레이 영역 배경
        pygame.draw.rect(SCREEN, (40,40,40), (0,0, WIDTH, HEIGHT))
        draw_grid(SCREEN, grid)
        draw_piece(SCREEN, current)
        draw_next(SCREEN, nxt)
        draw_info(SCREEN, score, level)
        pygame.display.flip()

    # 게임오버 화면
    SCREEN.fill((0,0,0))
    text = FONT.render("GAME OVER - R to restart or ESC to exit", True, (255,255,255))
    SCREEN.blit(text, (10, HEIGHT//2 - 10))
    pygame.display.flip()
    # 대기
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                waiting = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    waiting = False
                elif e.key == pygame.K_r:
                    main()
                    return
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()