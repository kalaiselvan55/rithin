import sys, random, math, pygame
from pygame.math import Vector2

# ---------------- Config ----------------
W, H = 960, 600
PLAYER_SPEED = 260.0          # pixels/sec
PLAYER_RADIUS = 18
PLAYER_MAX_HP = 100
INVULN_MS = 600               # brief invulnerability after getting hit
BULLET_SPEED = 800.0
BULLET_LIFETIME = 1.5         # seconds
FIRE_COOLDOWN = 0.16          # seconds between shots
ZOMBIE_MIN_SPEED = 90.0
ZOMBIE_MAX_SPEED = 140.0
ZOMBIE_RADIUS = 16
SPAWN_EVERY_MS = 900          # initial spawn interval
SPAWN_ACCEL_MS = -6           # spawn a bit faster each spawn, to a floor
SPAWN_FLOOR_MS = 400
KNOCKBACK = 180.0             # knock player on hit
# ----------------------------------------

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Zombie Shooter")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 54)

BG = (18, 22, 26)
UI = (230, 230, 230)
PLAYER_C = (120, 220, 255)
PLAYER_HURT = (255, 170, 170)
ZOMBIE_C = (120, 255, 120)
BULLET_C = (255, 235, 120)
HP_BAR_BG = (60, 60, 70)
HP_BAR = (120, 230, 120)
DANGER = (255, 120, 120)

def draw_text(text, pos, color=UI, center=False, big=False):
    f = big_font if big else font
    img = f.render(text, True, color)
    rect = img.get_rect()
    rect.center = pos if center else rect.move(pos).topleft
    screen.blit(img, rect)

def spawn_pos_outside():
    side = random.choice(["top","bottom","left","right"])
    margin = 40
    if side == "top":
        return Vector2(random.randint(-margin, W+margin), -margin)
    if side == "bottom":
        return Vector2(random.randint(-margin, W+margin), H+margin)
    if side == "left":
        return Vector2(-margin, random.randint(-margin, H+margin))
    return Vector2(W+margin, random.randint(-margin, H+margin))

def clamp(val, lo, hi): return max(lo, min(hi, val))

def game():
    # --- State ---
    player_pos = Vector2(W/2, H/2)
    player_vel = Vector2(0, 0)
    player_hp = PLAYER_MAX_HP
    last_hit_ms = -9999
    alive = True
    score = 0
    time_alive = 0.0

    bullets = []  # dicts: pos(Vector2), vel(Vector2), t(float)
    zombies = []  # dicts: pos(Vector2), speed(float)

    can_shoot_at = 0.0
    spawn_timer_ms = SPAWN_EVERY_MS
    last_spawn_ms = 0

    # Main loop
    while True:
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000.0
        now_ms = pygame.time.get_ticks()

        # ----- Events -----
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if not alive and e.key == pygame.K_r:
                    return  # restart game()
            if alive and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if time_alive >= can_shoot_at:
                    # fire a bullet toward mouse
                    mouse = Vector2(pygame.mouse.get_pos())
                    dirv = (mouse - player_pos)
                    if dirv.length_squared() > 0:
                        dirv = dirv.normalize()
                        bullets.append({"pos": player_pos.copy(),
                                        "vel": dirv * BULLET_SPEED,
                                        "t": 0.0})
                        can_shoot_at = time_alive + FIRE_COOLDOWN

        keys = pygame.key.get_pressed()

        # ----- Update -----
        if alive:
            time_alive += dt

            # Movement (WASD)
            move = Vector2(
                (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
                (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
            )
            if move.length_squared() > 0:
                move = move.normalize()
            player_vel = move * PLAYER_SPEED
            player_pos += player_vel * dt
            player_pos.x = clamp(player_pos.x, PLAYER_RADIUS, W - PLAYER_RADIUS)
            player_pos.y = clamp(player_pos.y, PLAYER_RADIUS, H - PLAYER_RADIUS)

            # Shooting (hold-to-shoot with mouse)
            if pygame.mouse.get_pressed()[0]:
                if time_alive >= can_shoot_at:
                    mouse = Vector2(pygame.mouse.get_pos())
                    dirv = (mouse - player_pos)
                    if dirv.length_squared() > 0:
                        dirv = dirv.normalize()
                        bullets.append({"pos": player_pos.copy(),
                                        "vel": dirv * BULLET_SPEED,
                                        "t": 0.0})
                        can_shoot_at = time_alive + FIRE_COOLDOWN

            # Update bullets
            kept_bullets = []
            for b in bullets:
                b["pos"] += b["vel"] * dt
                b["t"] += dt
                # keep on screen briefly
                if 0-40 <= b["pos"].x <= W+40 and 0-40 <= b["pos"].y <= H+40 and b["t"] <= BULLET_LIFETIME:
                    kept_bullets.append(b)
            bullets = kept_bullets

            # Spawn zombies
            if now_ms - last_spawn_ms >= spawn_timer_ms:
                last_spawn_ms = now_ms
                for _ in range(random.randint(1, 2)):
                    zpos = spawn_pos_outside()
                    zspeed = random.uniform(ZOMBIE_MIN_SPEED, ZOMBIE_MAX_SPEED)
                    zombies.append({"pos": zpos, "speed": zspeed})
                # ramp difficulty
                spawn_timer_ms = max(SPAWN_FLOOR_MS, spawn_timer_ms + SPAWN_ACCEL_MS)

            # Update zombies
            kept_zombies = []
            for z in zombies:
                dirv = (player_pos - z["pos"])
                if dirv.length_squared() > 0:
                    dirv = dirv.normalize()
                z["pos"] += dirv * z["speed"] * dt
                kept_zombies.append(z)
            zombies = kept_zombies

            # Bullet→Zombie collisions
            kept_zombies = []
            for z in zombies:
                hit = False
                for b in bullets[:]:
                    if (b["pos"] - z["pos"]).length_squared() <= (ZOMBIE_RADIUS + 5) ** 2:
                        bullets.remove(b)
                        score += 1
                        hit = True
                        break
                if not hit:
                    kept_zombies.append(z)
            zombies = kept_zombies

            # Zombie→Player collisions
            if now_ms - last_hit_ms > INVULN_MS:
                for z in zombies:
                    if (z["pos"] - player_pos).length_squared() <= (ZOMBIE_RADIUS + PLAYER_RADIUS) ** 2:
                        last_hit_ms = now_ms
                        player_hp -= random.randint(6, 12)
                        # knockback
                        away = (player_pos - z["pos"])
                        if away.length_squared() > 0:
                            away = away.normalize()
                            player_pos += away * (KNOCKBACK * dt)
                        if player_hp <= 0:
                            alive = False
                            break

        # ----- Draw -----
        screen.fill(BG)

        # Draw subtle grid for vibe
        for x in range(0, W, 40):
            pygame.draw.line(screen, (28, 32, 36), (x, 0), (x, H))
        for y in range(0, H, 40):
            pygame.draw.line(screen, (28, 32, 36), (0, y), (W, y))

        # Draw player (aim toward mouse)
        mouse = Vector2(pygame.mouse.get_pos())
        color = PLAYER_C if (now_ms - last_hit_ms) > 120 or not alive else PLAYER_HURT
        pygame.draw.circle(screen, color, player_pos, PLAYER_RADIUS)

        # Gun line
        aim_dir = (mouse - player_pos)
        if aim_dir.length_squared() > 0:
            aim_dir = aim_dir.normalize()
            tip = player_pos + aim_dir * (PLAYER_RADIUS + 10)
            pygame.draw.line(screen, (210, 240, 255), player_pos, tip, 3)

        # Draw bullets
        for b in bullets:
            pygame.draw.circle(screen, BULLET_C, b["pos"], 4)

        # Draw zombies
        for z in zombies:
            pygame.draw.circle(screen, ZOMBIE_C, z["pos"], ZOMBIE_RADIUS)
            # simple "eyes" pointing to player
            to_p = (player_pos - z["pos"])
            if to_p.length_squared() > 0:
                to_p = to_p.normalize()
                eye1 = z["pos"] + Vector2(-6, -4)
                eye2 = z["pos"] + Vector2(6, -4)
                pygame.draw.circle(screen, (0, 0, 0), (eye1 + to_p * 3), 3)
                pygame.draw.circle(screen, (0, 0, 0), (eye2 + to_p * 3), 3)

        # UI
        draw_text(f"Score: {score}", (12, 10))
        draw_text(f"Time: {int(time_alive)}s", (140, 10))
        # HP bar
        pygame.draw.rect(screen, HP_BAR_BG, (W-220, 12, 200, 16), border_radius=6)
        hpw = int(200 * clamp(player_hp / PLAYER_MAX_HP, 0, 1))
        hp_color = HP_BAR if player_hp > 30 else DANGER
        pygame.draw.rect(screen, hp_color, (W-220, 12, hpw, 16), border_radius=6)
        draw_text(f"HP: {player_hp}", (W-220, 34))

        draw_text("WASD/Arrows to move  •  Mouse to aim  •  LMB to shoot  •  R to restart  •  ESC to quit",
                  (W//2, H-18), center=True, color=(200,200,200))

        if not alive:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            draw_text("Z O M B I E   S H O O T E R", (W//2, H//2 - 90), center=True, big=True)
            draw_text(f"Score: {score}    Time: {int(time_alive)}s", (W//2, H//2 - 40), center=True)
            draw_text("Press R to play again", (W//2, H//2 + 8), center=True, color=(230,230,230))

        pygame.display.flip()

if __name__ == "__main__":
    while True:
        game()
