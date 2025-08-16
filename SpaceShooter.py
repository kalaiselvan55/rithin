import pygame, random, sys

# --- Config ---
W, H = 480, 640
PLAYER_SPEED = 6
BULLET_SPEED = -10
ENEMY_SPEED_MIN, ENEMY_SPEED_MAX = 2, 5
ENEMY_SPAWN_MS = 600  # spawn every 600 ms
MAX_ENEMIES = 12
# --------------

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Mini Space Shooter")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

def new_enemy():
    size = random.randint(20, 40)
    x = random.randint(0, W - size)
    y = -size
    speed = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
    return pygame.Rect(x, y, size, size), speed

def draw_text(text, x, y, color=(255,255,255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def game():
    # Player setup
    player = pygame.Rect(W // 2 - 20, H - 60, 40, 40)
    bullets = []  # list of rects
    enemies = []  # list of (rect, speed)
    score = 0
    alive = True

    # Spawn timer
    SPAWN = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN, ENEMY_SPAWN_MS)

    while True:
        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r and not alive:
                    return  # restart game loop
                if event.key == pygame.K_SPACE and alive:
                    # Create bullet centered on player
                    b = pygame.Rect(player.centerx - 3, player.top - 10, 6, 12)
                    bullets.append(b)
            if event.type == SPAWN and alive:
                if len(enemies) < MAX_ENEMIES:
                    enemies.append(new_enemy())

        # --- Input (continuous) ---
        keys = pygame.key.get_pressed()
        if alive:
            dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            player.x += dx * PLAYER_SPEED
            player.x = max(0, min(W - player.width, player.x))

        # --- Update bullets ---
        if alive:
            for b in bullets:
                b.y += BULLET_SPEED
            bullets = [b for b in bullets if b.bottom > 0]

        # --- Update enemies ---
        if alive:
            new_list = []
            for rect, speed in enemies:
                rect.y += speed
                # Hit player?
                if rect.colliderect(player):
                    alive = False
                # Reached bottom?
                if rect.top > H:
                    alive = False
                else:
                    new_list.append((rect, speed))
            enemies = new_list

        # --- Collisions (bullets vs enemies) ---
        if alive:
            kept_enemies = []
            for er, sp in enemies:
                hit = False
                for b in bullets[:]:
                    if er.colliderect(b):
                        bullets.remove(b)
                        hit = True
                        score += 1
                        break
                if not hit:
                    kept_enemies.append((er, sp))
            enemies = kept_enemies

        # --- Draw ---
        screen.fill((10, 10, 25))  # space background

        # Stars (tiny parallax)
        for _ in range(40):
            x = random.randint(0, W-1)
            y = random.randint(0, H-1)
            screen.fill((random.randint(150,255),)*3, ((x,y,1,1)))

        # Player
        color_player = (80, 220, 255) if alive else (120, 120, 120)
        pygame.draw.rect(screen, color_player, player, border_radius=6)
        # Nose triangle
        pygame.draw.polygon(screen, (200, 255, 255),
                            [(player.centerx, player.top-10),
                             (player.left, player.top+10),
                             (player.right, player.top+10)])

        # Bullets
        for b in bullets:
            pygame.draw.rect(screen, (255, 240, 120), b, border_radius=3)

        # Enemies
        for er, _ in enemies:
            pygame.draw.rect(screen, (255, 80, 80), er, border_radius=6)
            # little "eye"
            pygame.draw.circle(screen, (0,0,0), er.center, max(3, er.width//6))

        # UI
        draw_text(f"Score: {score}", 10, 10)
        draw_text("←/→ or A/D to move  |  SPACE to shoot  |  ESC to quit", 10, H-28, (200,200,200))

        if not alive:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            draw_text("GAME OVER", W//2 - 70, H//2 - 40)
            draw_text(f"Final Score: {score}", W//2 - 70, H//2 - 10)
            draw_text("Press R to Restart or ESC to Quit", W//2 - 150, H//2 + 20, (230,230,230))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    while True:
        game()
