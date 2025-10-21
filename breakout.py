"""
간단한 블럭깨기(브레이크아웃) 게임 — single file
사용법:
  1) pygame 설치: pip install pygame
  2) 실행: python c:\work\breakout.py
왼/오른쪽 화살표 또는 마우스로 패들 조작. 공을 모두 제거하면 승리, 공이 바닥에 떨어지면 목숨 소모.
"""

import pygame
import sys
import random

# ---- 설정 ----
WIDTH, HEIGHT = 800, 600
FPS = 60

BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_WIDTH = (WIDTH - 100) // BRICK_COLS
BRICK_HEIGHT = 24
BRICK_PADDING = 4
TOP_OFFSET = 60

PADDLE_W = 120  # 패들 폭을 줄임 (기존 360 -> 120)
PADDLE_H = 16
PADDLE_Y = HEIGHT - 50
PADDLE_SPEED = 8

BALL_RADIUS = 9
BALL_SPEED = 5

LIVES = 3

# 아이템/총알 설정
ITEM_CHANCE = 0.30  # 브릭 파괴 시 아이템 생성 확률
ITEM_FALL_SPEED = 3
BULLET_SPEED = 9
BULLET_COOLDOWN_FRAMES = 10
BULLET_AMMO_GAIN = 5  # 아이템을 먹으면 얻는 총알 수

# ---- 색상 ----
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (140, 140, 140)
RED = (220, 60, 60)
GREEN = (80, 200, 120)
BLUE = (70, 140, 230)
YELLOW = (240, 200, 80)
COLORS = [
    (255, 90, 90),    # 선명한 빨강
    (255, 160, 60),   # 주황
    (255, 220, 80),   # 노랑
    (120, 220, 140),  # 연녹색
    (90, 200, 255),   # 하늘색
    (150, 120, 255),  # 보라
    (255, 120, 200),  # 핑크
    (255, 255, 150),  # 연노랑
]

# ---- 게임 객체 ----
class Paddle:
    def __init__(self):
        self.rect = pygame.Rect((WIDTH - PADDLE_W) // 2, PADDLE_Y, PADDLE_W, PADDLE_H)
        self.speed = PADDLE_SPEED
        self.bullet_ammo = 0
        self.shoot_cooldown = 0

    def move_left(self):
        self.rect.x -= self.speed
        if self.rect.left < 0:
            self.rect.left = 0

    def move_right(self):
        self.rect.x += self.speed
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def move_to(self, x):
        self.rect.centerx = x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def can_shoot(self):
        return self.bullet_ammo > 0 and self.shoot_cooldown == 0

    def shoot(self):
        if not self.can_shoot():
            return None
        # 발사 위치: 패들 위쪽 중앙
        bx = self.rect.centerx
        by = self.rect.top - 6
        self.bullet_ammo -= 1
        self.shoot_cooldown = BULLET_COOLDOWN_FRAMES
        return Bullet(bx, by)

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, surf):
        pygame.draw.rect(surf, GRAY, self.rect, border_radius=6)

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = PADDLE_Y - BALL_RADIUS - 2
        angle = random.uniform(-0.9, -0.5)  # 위쪽으로
        self.vx = BALL_SPEED * random.choice([-1, 1]) * abs(random.uniform(0.6, 1.0))
        self.vy = BALL_SPEED * angle

    def update(self):
        self.x += self.vx
        self.y += self.vy

        # 좌우 벽 충돌
        if self.x - BALL_RADIUS <= 0:
            self.x = BALL_RADIUS
            self.vx = -self.vx
        if self.x + BALL_RADIUS >= WIDTH:
            self.x = WIDTH - BALL_RADIUS
            self.vx = -self.vx
        # 천장 충돌
        if self.y - BALL_RADIUS <= 0:
            self.y = BALL_RADIUS
            self.vy = -self.vy

    def rect(self):
        return pygame.Rect(int(self.x - BALL_RADIUS), int(self.y - BALL_RADIUS), BALL_RADIUS*2, BALL_RADIUS*2)

    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), BALL_RADIUS)

class Brick:
    def __init__(self, x, y, w, h, color, hits=1):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hits = hits

    def hit(self):
        self.hits -= 1
        return self.hits <= 0

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=4)
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=4)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = -BULLET_SPEED
        self.radius = 4

    def update(self):
        self.y += self.vy

    def rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius*2, self.radius*2)

    def draw(self, surf):
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.radius)

class Item:
    def __init__(self, x, y, kind="shoot"):
        self.x = x
        self.y = y
        self.vy = ITEM_FALL_SPEED
        self.kind = kind
        self.radius = 10
        # 색상: 종류별
        self.color = (255, 200, 60) if kind == "shoot" else (200, 200, 200)

    def update(self):
        self.y += self.vy

    def rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius*2, self.radius*2)

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        # 간단한 기호
        font = pygame.font.SysFont("arial", 14, bold=True)
        txt = font.render("B", True, BLACK) if self.kind == "shoot" else font.render("?", True, BLACK)
        tr = txt.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(txt, tr)

# ---- 유틸 ----
def create_bricks():
    bricks = []
    x_start = 50
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = x_start + col * BRICK_WIDTH
            y = TOP_OFFSET + row * (BRICK_HEIGHT + BRICK_PADDING)
            color = COLORS[row % len(COLORS)]
            bricks.append(Brick(x, y, BRICK_WIDTH - BRICK_PADDING, BRICK_HEIGHT, color))
    return bricks

def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("arial", size)
    r = font.render(text, True, color)
    rect = r.get_rect(center=(x, y))
    surf.blit(r, rect)

# ---- 메인 루프 ----
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("블럭깨기")
    clock = pygame.time.Clock()

    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks()
    bullets = []
    items = []

    score = 0
    lives = LIVES
    running = True
    paused = False

    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_r:
                    # 리셋
                    bricks = create_bricks()
                    ball.reset()
                    bullets.clear()
                    items.clear()
                    score = 0
                    lives = LIVES
                    paddle = Paddle()
                    paused = False
                if event.key == pygame.K_z:
                    # Z로 발사
                    b = paddle.shoot()
                    if b:
                        bullets.append(b)
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                paddle.move_to(mx)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move_left()
        if keys[pygame.K_RIGHT]:
            paddle.move_right()

        paddle.update()

        if not paused:
            ball.update()

            # 공과 패들 충돌
            if ball.rect().colliderect(paddle.rect):
                # 충돌 위치에 따라 반사 각도 조절
                overlap_x = (ball.x - paddle.rect.centerx) / (paddle.rect.width / 2)
                ball.vx = BALL_SPEED * overlap_x * 1.5
                ball.vy = -abs(ball.vy)
                ball.y = paddle.rect.top - BALL_RADIUS - 1

            # 공과 블럭 충돌
            hit_brick = None
            for brick in bricks:
                if ball.rect().colliderect(brick.rect):
                    hit_brick = brick
                    break
            if hit_brick:
                # 충돌방향 판정: 간단히 수평/수직 반전
                brect = hit_brick.rect
                ball_rect = ball.rect()
                # 중심 차이
                dx = (ball.x) - brect.centerx
                dy = (ball.y) - brect.centery
                if abs(dx) > abs(dy):
                    ball.vx = -ball.vx
                else:
                    ball.vy = -ball.vy
                # 브릭 파괴 처리 및 아이템 드롭
                if hit_brick.hit():
                    # 위치 중심에서 아이템 생성
                    if random.random() < ITEM_CHANCE:
                        items.append(Item(hit_brick.rect.centerx, hit_brick.rect.centery, kind="shoot"))
                    bricks.remove(hit_brick)
                    score += 10

            # 바닥 통과: 목숨 감소
            if ball.y - BALL_RADIUS > HEIGHT:
                lives -= 1
                if lives <= 0:
                    paused = True
                ball.reset()

            # 총알 업데이트 및 브릭 충돌 검사
            for b in bullets[:]:
                b.update()
                if b.y + b.radius < 0:
                    bullets.remove(b)
                    continue
                # 충돌 검사
                hit = None
                for brick in bricks:
                    if b.rect().colliderect(brick.rect):
                        hit = brick
                        break
                if hit:
                    # 브릭 즉시 파괴
                    if random.random() < ITEM_CHANCE:
                        items.append(Item(hit.rect.centerx, hit.rect.centery, kind="shoot"))
                    try:
                        bricks.remove(hit)
                    except ValueError:
                        pass
                    score += 10
                    if b in bullets:
                        bullets.remove(b)

            # 아이템 업데이트 및 패들과 충돌
            for it in items[:]:
                it.update()
                if it.y - it.radius > HEIGHT:
                    items.remove(it)
                    continue
                if it.rect().colliderect(paddle.rect):
                    # 획득 효과: 총알 부여
                    if it.kind == "shoot":
                        paddle.bullet_ammo += BULLET_AMMO_GAIN
                    items.remove(it)

            # 승리 판정
            if not bricks:
                paused = True

        # 그리기
        screen.fill((30, 30, 45))
        for brick in bricks:
            brick.draw(screen)
        for it in items:
            it.draw(screen)
        paddle.draw(screen)
        ball.draw(screen)
        for b in bullets:
            b.draw(screen)

        # UI
        draw_text(screen, f"점수: {score}", 20, 70, 20)
        draw_text(screen, f"목숨: {lives}", 20, WIDTH - 120, 20)
        draw_text(screen, f"총알: {paddle.bullet_ammo}", 20, WIDTH - 40, 20)
        if paused:
            if not bricks and lives > 0:
                draw_text(screen, "승리! R로 다시하기", 36, WIDTH // 2, HEIGHT // 2, YELLOW)
            elif lives <= 0:
                draw_text(screen, "게임오버! R로 다시하기", 36, WIDTH // 2, HEIGHT // 2, RED)
            else:
                draw_text(screen, "일시정지 - 스페이스로 재개 (Z: 총알 발사)", 22, WIDTH // 2, HEIGHT // 2, WHITE)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()