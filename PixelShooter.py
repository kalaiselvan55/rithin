import pygame, random, sys, math
from pygame.math import Vector2

# -------------------- Retro Low-Res Setup --------------------
LOW_W, LOW_H = 200, 150    # low-res canvas size (pixel-art scale)
SCALE = 4                  # window = LOW_* * SCALE
WIN_W, WIN_H = LOW_W * SCALE, LOW_H * SCALE

# -------------------- Game Config --------------------
PLAYER_SPEED = 70.0              # pixels/sec in low-res space
PLAYER_SIZE = 6
PLAYER_MAX_HP = 5
FIRE_COOLDOWN = 0.16             # seconds
BULLET_SPEED = 170.0
BULLET_LIFETIME = 1.4            # seconds
ENEMY_SPAWN_EVERY = 0.75         # seconds
ENEMY_SPEED_MIN = 28.0
ENEMY_SPEED_MAX = 50.0
ENEMY_SIZE = 7
INVULN_SEC = 0.6
WALL_COUNT = 16                  # random obstacles

# -------------------- Colors --------------------
BG = (10, 12, 16)
GRID = (20, 22, 28)
UI = (230, 230, 230)
PLAYER_C = (120, 220, 255)
PLAYER_HURT = (255, 170, 170)
BULLET_C = (255, 235, 120)
ENEMY_C = (120, 255, 120)
WALL_C = (70, 80, 95)
DANGER = (255, 100, 100)

def rect_collide(ax, ay, asz, bx, by, bsz):
    return not (ax+asz <= bx or bx+bsz <= ax or ay+asz <= by or by+bsz <= ay)

def clamp(val, lo, hi): return max(lo, min(hi, val))

def make_walls(rng):
    walls = []
    for _ in range(WALL_COUNT):
        w = rng.choice([10, 12, 16, 20])
        h = rng.choice([10, 12, 16])
        x = rng.randint(5, LOW_W - w - 5)
        y = rng.randint(10, LOW_H - h - 10)
        walls.append(pygame.Rect(x, y, w, h))
    return walls

def spawn_enemy(rng, walls):
    # spawn just off-screen border
    side = rng.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x, y = rng.randint(-10, LOW_W+10), -ENEMY_SIZE - 2
    elif side == "bottom":
        x, y = rng.randint(-10, LOW_W+10), LOW_H + 2
    elif side == "left":
        x, y = -ENEMY_SIZE - 2, rng.randint(-10, LOW_H+10)
    else:
        x, y = LOW_W + 2, rng.randint(-10, LOW_H+10)

    r = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
    # avoid walls at spawn (roughly)
    for w in walls:
        if r.colliderect(w):
            return None
    speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
    return {"rect": r, "speed": speed}

def line_rect_intersect(p0, p1, r):
    # simple check used to prevent bullets spawning inside walls; optional
    # Here we skip for simplicity (bullets small); return False to ignore
    return False

def main():
    pygame.init()
    window = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Pixel Shooter (Retro)")
    clock = pygame.time.Clock()

    # Low-res canvas (nearest-neighbor scaled to window)
    canvas = pygame.Surface((LOW_W, LOW_H))

    font = pygame.font.SysFont(None, 18)
    big = pygame.font.SysFont(None, 28)

    rng = random.Random()

    def new_game():
        player = pygame.Rect(LOW_W//2 - PLAYER_SIZE//2, LOW_H//2 - PLAYER_SIZE//2, PLAYER_SIZE, PLAYER_SIZE)
        hp = PLAYER_MAX_HP
        bullets = []  # dict: x,y,dx,dy,life
        enemies = []  # dict: rect, speed
        walls = make_walls(rng)

        # ensure spawn region around player is clear
        for w in walls[:]:
            if w.colliderect(player.inflate(40, 40)):
                walls.remove(w)

        last_shot_t = 0.0
        spawn_acc = 0.0
        alive = True
        invuln_until = -1.0
        score = 0
        t = 0.0
        return locals()  # pack state

    S = new_game()

    while True:
        dt = clock.tick(60) / 1000.0
        # Events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if not S["alive"] and e.key == pygame.K_r:
                    S = new_game()

        # --- Update ---
        if S["alive"]:
            S["t"] += dt
            keys = pygame.key.get_pressed()

            # Movement (WASD/Arrows)
            dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
            dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
            v = Vector2(dx, dy)
            if v.length_squared() > 0:
                v = v.normalize() * PLAYER_SPEED
            move = v * dt

            # Try move with simple collision vs walls (separate axis resolution)
            p = S["player"]
            # X
            p.x = int(p.x + move.x)
            for w in S["walls"]:
                if p.colliderect(w):
                    if move.x > 0: p.right = w.left
                    elif move.x < 0: p.left = w.right
            # Y
            p.y = int(p.y + move.y)
            for w in S["walls"]:
                if p.colliderect(w):
                    if move.y > 0: p.bottom = w.top
                    elif move.y < 0: p.top = w.bottom

            # Clamp to arena
            p.x = clamp(p.x, 0, LOW_W - p.width)
            p.y = clamp(p.y, 0, LOW_H - p.height)

            # Shooting
            mouse_pos = Vector2(pygame.mouse.get_pos()[0] / SCALE, pygame.mouse.get_pos()[1] / SCALE)
            want_fire = pygame.mouse.get_pressed()[0]
            # Also allow arrow-key shooting (4-dir)
            fire_dir = None
            shoot_dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            shoot_dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
            if shoot_dx or shoot_dy:
                fire_dir = Vector2(shoot_dx, shoot_dy)
            elif want_fire:
                dirv = mouse_pos - Vector2(p.center)
                if dirv.length_squared() > 0:
                    fire_dir = dirv

            if fire_dir is not None:
                if S["t"] - S["last_shot_t"] >= FIRE_COOLDOWN:
                    d = fire_dir.normalize()
                    bx = p.centerx + int(d.x * (PLAYER_SIZE//2 + 2)) - 1
                    by = p.centery + int(d.y * (PLAYER_SIZE//2 + 2)) - 1
                    bullet = {"x": float(bx), "y": float(by), "dx": d.x * BULLET_SPEED, "dy": d.y * BULLET_SPEED, "life": 0.0}
                    # avoid spawning bullet inside a wall
                    bad = False
                    br = pygame.Rect(int(bullet["x"]), int(bullet["y"]), 2, 2)
                    for w in S["walls"]:
                        if br.colliderect(w):
                            bad = True; break
                    if not bad:
                        S["bullets"].append(bullet)
                        S["last_shot_t"] = S["t"]

            # Update bullets
            kept_b = []
            for b in S["bullets"]:
                b["x"] += b["dx"] * dt
                b["y"] += b["dy"] * dt
                b["life"] += dt
                br = pygame.Rect(int(b["x"]), int(b["y"]), 2, 2)
                # out of bounds or lifetime over?
                if b["life"] > BULLET_LIFETIME or br.right < 0 or br.left > LOW_W or br.bottom < 0 or br.top > LOW_H:
                    continue
                # wall hit?
                hit_wall = False
                for w in S["walls"]:
                    if br.colliderect(w):
                        hit_wall = True; break
                if not hit_wall:
                    kept_b.append(b)
            S["bullets"] = kept_b

            # Spawn enemies
            S["spawn_acc"] += dt
            while S["spawn_acc"] >= ENEMY_SPAWN_EVERY:
                S["spawn_acc"] -= ENEMY_SPAWN_EVERY
                e = spawn_enemy(rng, S["walls"])
                if e: S["enemies"].append(e)

            # Update enemies
            kept_e = []
            pc = Vector2(S["player"].center)
            for e in S["enemies"]:
                er = e["rect"]
                # simple chase
                dirv = pc - Vector2(er.center)
                if dirv.length_squared() > 0:
                    dirv = dirv.normalize()
                step = dirv * e["speed"] * dt
                er.x = int(er.x + step.x)
                # collide walls X
                for w in S["walls"]:
                    if er.colliderect(w):
                        if step.x > 0: er.right = w.left
                        elif step.x < 0: er.left = w.right
                er.y = int(er.y + step.y)
                # collide walls Y
                for w in S["walls"]:
                    if er.colliderect(w):
                        if step.y > 0: er.bottom = w.top
                        elif step.y < 0: er.top = w.bottom
                # keep only those on/border
                if -ENEMY_SIZE <= er.x <= LOW_W and -ENEMY_SIZE <= er.y <= LOW_H:
                    kept_e.append(e)
            S["enemies"] = kept_e

            # Bullet -> Enemy
            kept_e = []
            for e in S["enemies"]:
                er = e["rect"]
                hit = False
                for b in S["bullets"][:]:
                    br = pygame.Rect(int(b["x"]), int(b["y"]), 2, 2)
                    if er.colliderect(br):
                        S["bullets"].remove(b)
                        S["score"] += 1
                        hit = True
                        break
                if not hit:
                    kept_e.append(e)
            S["enemies"] = kept_e

            # Enemy -> Player
            if S["t"] >= S["invuln_until"]:
                for e in S["enemies"]:
                    if S["player"].colliderect(e["rect"]):
                        S["hp"] -= 1
                        S["invuln_until"] = S["t"] + INVULN_SEC
                        if S["hp"] <= 0:
                            S["alive"] = False
                        break

        # --- Draw on low-res canvas ---
        c = canvas
        c.fill(BG)

        # Subtle grid (pixel-y vibe)
        for x in range(0, LOW_W, 10):
            pygame.draw.line(c, GRID, (x, 0), (x, LOW_H))
        for y in range(0, LOW_H, 10):
            pygame.draw.line(c, GRID, (0, y), (LOW_W, y))

        # Walls
        for w in S["walls"]:
            pygame.draw.rect(c, WALL_C, w)

        # Player
        pc = PLAYER_C if (not S["alive"] or S["t"] >= S["invuln_until"] or int(S["t"]*20)%2==0) else PLAYER_HURT
        pygame.draw.rect(c, pc if S["alive"] else (140,140,140), S["player"])

        # Gun muzzle indicator (toward mouse)
        mp = Vector2(pygame.mouse.get_pos()[0] / SCALE, pygame.mouse.get_pos()[1] / SCALE)
        aim = mp - Vector2(S["player"].center)
        if aim.length_squared() > 0:
            aim = aim.normalize()
            tip = Vector2(S["player"].center) + aim * (PLAYER_SIZE//2 + 3)
            pygame.draw.line(c, (210,240,255), S["player"].center, (int(tip.x), int(tip.y)), 1)

        # Bullets
        for b in S["bullets"]:
            pygame.draw.rect(c, BULLET_C, (int(b["x"]), int(b["y"]), 2, 2))

        # Enemies
        for e in S["enemies"]:
            pygame.draw.rect(c, ENEMY_C, e["rect"])

        # UI (drawn on canvas to keep pixelated)
        # Hearts
        for i in range(PLAYER_MAX_HP):
            col = (220,60,60) if i < S["hp"] else (70,40,40)
            pygame.draw.rect(c, col, (4 + i*8, 4, 6, 6))

        # Score
        score_surf = font.render(f"Score: {S['score']}", True, UI)
        c.blit(score_surf, (LOW_W - 70, 4))

        # Game over overlay
        if not S["alive"]:
            overlay = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            c.blit(overlay, (0, 0))
            txt1 = big.render("GAME OVER", True, UI)
            txt2 = font.render("Press R to Restart  •  ESC to Quit", True, (220,220,220))
            c.blit(txt1, (LOW_W//2 - txt1.get_width()//2, LOW_H//2 - 26))
            c.blit(txt2, (LOW_W//2 - txt2.get_width()//2, LOW_H//2 + 2))

        # --- Scale to window (nearest neighbor) ---
        pygame.transform.scale(canvas, (WIN_W, WIN_H), window)
        pygame.display.flip()

if __name__ == "__main__":
    main()
