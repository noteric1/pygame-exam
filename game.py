import pygame
import sys
import random
import math
import os
import array

# INITIALIZATION -
pygame.init()
try:
    # Standard frequency for OGG playback
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except:
    print("Audio Warning: Could not initialize mixer")

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "NEON DRIFTER: FINAL STABLE (V15)"

# Colors (Neon Palette)
BLACK = (5, 5, 10)
NEON_CYAN = (0, 255, 255)
NEON_ORANGE = (255, 165, 0)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_YELLOW = (255, 255, 0)
NEON_BLUE = (30, 144, 255)
NEON_PURPLE = (180, 0, 255)
NEON_RED = (255, 0, 60)
RED = (200, 0, 0)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
DARK_GREY = (40, 40, 40)
BUTTON_COLOR = (20, 20, 40)
BUTTON_HOVER = (40, 40, 80)
SEMI_TRANSPARENT_BLACK = (0, 0, 0, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# GLOBAL CONFIGURATION -
CONFIG = { 'volume': 0.5, 'trails': True }

# SYNTH SOUND ENGINE & MUSIC -
def generate_beep(frequency=440, duration=0.1):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    amplitude = 32767 * 0.5 
    for i in range(n_samples):
        t = float(i) / sample_rate
        val = 1 if int(t * frequency * 2) % 2 else -1
        buf[i] = int(val * amplitude)
    return pygame.mixer.Sound(buffer=buf)

snd_shoot = generate_beep(440, 0.05)
snd_enemy_shoot = generate_beep(220, 0.05)
snd_expl = generate_beep(100, 0.1)
snd_powerup = generate_beep(880, 0.1)
snd_dash = generate_beep(600, 0.1)
snd_emp = generate_beep(150, 0.3)

def update_volumes():
    vol = CONFIG['volume']
    snd_shoot.set_volume(0.2 * vol)
    snd_enemy_shoot.set_volume(0.2 * vol)
    snd_expl.set_volume(0.4 * vol)
    snd_powerup.set_volume(0.3 * vol)
    snd_dash.set_volume(0.3 * vol)
    snd_emp.set_volume(0.5 * vol)
    # Set background music volume
    pygame.mixer.music.set_volume(0.5 * vol)

def load_and_play_music(filename="music.ogg"):
    if os.path.exists(filename):
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play(-1) # Loop indefinitely
        except Exception as e:
            print(f"Music Error: {e}")
    else:
        print(f"Warning: {filename} not found.")

update_volumes() 

# GLOBAL VARIABLES -
shake_duration = 0
shake_magnitude = 0
shake_offset = [0, 0]
current_multiplier = 1
boss_active = False

def trigger_shake(duration, magnitude):
    global shake_duration, shake_magnitude
    shake_duration = duration
    shake_magnitude = magnitude

# HELPER FUNCTIONS -
def get_high_score():
    if not os.path.exists("highscore.txt"):
        return 0
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(new_score):
    current = get_high_score()
    if new_score > current:
        with open("highscore.txt", "w") as f:
            f.write(str(new_score))
        return new_score
    return current

def draw_text(surface, text, size, color, x, y, align="center"):
    try: font = pygame.font.Font(None, size)
    except: font = pygame.font.SysFont("arial", size, bold=True)
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    if align == "center": rect.center = (x, y)
    elif align == "left": rect.topleft = (x, y)
    elif align == "right": rect.topright = (x, y)
    surface.blit(text_surface, rect)

class Button:
    def __init__(self, x, y, w, h, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER, text_color=WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color; self.hover_color = hover_color; self.text_color = text_color
        self.is_hovered = False
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, NEON_CYAN if self.is_hovered else DARK_GREY, self.rect, 2, border_radius=10)
        draw_text(surface, self.text, 28, self.text_color, self.rect.centerx, self.rect.centery)
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered

def draw_powerup_icon(surface, type, center_x, center_y):
    if type == "fuel":
        pygame.draw.rect(surface, NEON_GREEN, (center_x-6, center_y-6, 12, 12))
        pygame.draw.rect(surface, WHITE, (center_x-6, center_y-6, 12, 12), 1)
    elif type == "shield":
        pygame.draw.circle(surface, NEON_BLUE, (center_x, center_y), 8)
        pygame.draw.circle(surface, WHITE, (center_x, center_y), 8, 1)
    elif type == "health":
        pygame.draw.rect(surface, NEON_RED, (center_x-2, center_y-8, 4, 16))
        pygame.draw.rect(surface, NEON_RED, (center_x-8, center_y-2, 16, 4))
    elif type == "frenzy":
        pygame.draw.circle(surface, NEON_PURPLE, (center_x, center_y), 8)
        pygame.draw.line(surface, WHITE, (center_x-6, center_y-6), (center_x+6, center_y+6), 2)
        pygame.draw.line(surface, WHITE, (center_x+6, center_y-6), (center_x-6, center_y+6), 2)
    elif type == "multiplier":
        pygame.draw.line(surface, GOLD, (center_x-6, center_y-6), (center_x+6, center_y+6), 3)
        pygame.draw.line(surface, GOLD, (center_x+6, center_y-6), (center_x-6, center_y+6), 3)

# CLASSES -

class Drifter(pygame.sprite.Sprite):
    def __init__(self, player_id=1):
        super().__init__()
        self.player_id = player_id
        self.color = NEON_CYAN if player_id == 1 else NEON_ORANGE
        self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
        self.base_image = self.image.copy()
        pygame.draw.polygon(self.base_image, self.color, [(15, 0), (30, 40), (15, 30), (0, 40)])
        self.original_image = self.base_image.copy()
        start_x = WIDTH//3 if player_id == 1 else (WIDTH//3) * 2
        self.rect = self.image.get_rect(center=(start_x, HEIGHT//2))
        self.pos = pygame.math.Vector2(start_x, HEIGHT//2)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.friction = 0.98
        self.fuel = 100
        self.health = 100
        self.dash_cooldown = 0
        self.shoot_cooldown = 0
        self.shield_active = False; self.shield_timer = 0
        self.frenzy_active = False; self.frenzy_timer = 0
        self.multiplier_active = False; self.multiplier_timer = 0
        self.invincible = True; self.invincible_timer = 180
        self.emp_active = False; self.emp_radius = 0

    def activate_shield(self): self.shield_active = True; self.shield_timer = 300
    def activate_frenzy(self): self.frenzy_active = True; self.frenzy_timer = 300
    def activate_multiplier(self): global current_multiplier; self.multiplier_active = True; current_multiplier = 2; self.multiplier_timer = 600

    def get_input(self):
        keys = pygame.key.get_pressed()
        thrust = False; dash = False; shoot = False; emp = False
        if self.player_id == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x -= shake_offset[0]; mouse_y -= shake_offset[1]
            rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
            self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90
            if keys[pygame.K_w]: thrust = True
            if keys[pygame.K_SPACE]: dash = True
            if pygame.mouse.get_pressed()[0]: shoot = True
            if keys[pygame.K_e]: emp = True
        elif self.player_id == 2:
            if keys[pygame.K_LEFT]: self.angle += 5
            if keys[pygame.K_RIGHT]: self.angle -= 5
            if keys[pygame.K_UP]: thrust = True
            if keys[pygame.K_RSHIFT]: dash = True
            if keys[pygame.K_RETURN] or keys[pygame.K_RCTRL]: shoot = True
            if keys[pygame.K_KP0]: emp = True
        return thrust, dash, shoot, emp

    def shoot(self):
        if self.shoot_cooldown == 0:
            snd_shoot.play()
            if self.frenzy_active:
                for i in range(0, 360, 45):
                    rad = math.radians(i)
                    direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                    bullets.add(Bullet(self.rect.centerx, self.rect.centery, direction, NEON_PURPLE, is_player=True))
                self.shoot_cooldown = 10 
            else:
                direction = pygame.math.Vector2(0, -1).rotate(-self.angle)
                bullet_pos = self.pos + direction * 20
                bullets.add(Bullet(bullet_pos.x, bullet_pos.y, direction, NEON_YELLOW, is_player=True))
                self.shoot_cooldown = 15 

    def update(self):
        thrust, dash, do_shoot, do_emp = self.get_input()
        if self.frenzy_active: self.angle += 15 
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0: 
                self.invincible = False
                self.original_image = self.base_image.copy()
            else:
                if (pygame.time.get_ticks() // 100) % 2 == 0:
                    self.original_image.fill((0,0,0,0))
                    pygame.draw.polygon(self.original_image, WHITE, [(15, 0), (30, 40), (15, 30), (0, 40)])
                else:
                    self.original_image = self.base_image.copy()
        
        self.image = pygame.transform.rotate(self.original_image, int(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.acc = pygame.math.Vector2(0, 0)
        
        if self.dash_cooldown > 0: self.dash_cooldown -= 1
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        
        if self.shield_active:
            self.shield_timer -= 1; 
            if self.shield_timer <= 0: self.shield_active = False
        if self.frenzy_active:
            self.frenzy_timer -= 1; 
            if self.frenzy_timer <= 0: self.frenzy_active = False
        if self.multiplier_active:
            global current_multiplier; self.multiplier_timer -= 1
            if self.multiplier_timer <= 0: self.multiplier_active = False; current_multiplier = 1

        if self.fuel > 0:
            if thrust:
                direction = pygame.math.Vector2(0, -1).rotate(-self.angle)
                self.acc = direction * 0.5
                self.fuel -= 0.1
                if CONFIG['trails'] and random.randint(0,2) == 0: 
                    trail = Particle(self.rect.centerx, self.rect.centery, self.color, speed=0)
                    trail.image = self.image.copy()
                    trail.image.set_alpha(100)
                    trail.lifetime = 10
                    particles.add(trail)

            if dash and self.dash_cooldown == 0 and self.fuel > 10:
                snd_dash.play()
                direction = pygame.math.Vector2(0, -1).rotate(-self.angle)
                self.vel += direction * 15
                self.fuel -= 10
                self.dash_cooldown = 60
                trigger_shake(5, 3)
                if CONFIG['trails']:
                    for _ in range(10): particles.add(Particle(self.rect.centerx, self.rect.centery, self.color, speed=3))
            
            if do_emp and self.fuel >= 50 and not self.emp_active:
                self.fuel -= 50
                self.emp_active = True
                self.emp_radius = 10
                snd_emp.play()
                trigger_shake(20, 10)

        if do_shoot: self.shoot()
        self.vel += self.acc; self.vel *= self.friction
        if self.vel.length() > 10: self.vel.scale_to_length(10)
        self.pos += self.vel
        if self.pos.x > WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = WIDTH
        if self.pos.y > HEIGHT: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = HEIGHT
        self.rect.center = self.pos

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, color, is_player=False):
        super().__init__()
        self.image = pygame.Surface((6, 6)); self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.vel = direction * (12 if is_player else 7)
        self.lifetime = 50 if is_player else 80
        self.is_player = is_player
    def update(self):
        self.pos += self.vel; self.rect.center = self.pos
        self.lifetime -= 1
        if self.lifetime <= 0: self.kill()

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color):
        super().__init__()
        try: font = pygame.font.Font(None, 24)
        except: font = pygame.font.SysFont("arial", 20, bold=True)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = -1.5
        self.lifetime = 40
    def update(self):
        self.rect.y += self.vel_y
        self.lifetime -= 1
        if self.lifetime < 10: self.image.set_alpha(self.lifetime * 25)
        if self.lifetime <= 0: self.kill()

class Hunter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = random.randint(15, 25)
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, NEON_RED, (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, WHITE, (self.radius, self.radius), self.radius, 2)
        self.rect = self.image.get_rect()
        self.pos = self.get_spawn(); self.rect.center = self.pos
        self.speed = random.uniform(2, 3.5); self.type = "chaser"
    def get_spawn(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top': return pygame.math.Vector2(random.randint(0, WIDTH), -50)
        elif side == 'bottom': return pygame.math.Vector2(random.randint(0, WIDTH), HEIGHT + 50)
        elif side == 'left': return pygame.math.Vector2(-50, random.randint(0, HEIGHT))
        return pygame.math.Vector2(WIDTH + 50, random.randint(0, HEIGHT))
    def update(self, players):
        closest_dist = float('inf'); target_pos = None
        for p in players:
            d = p.pos.distance_to(self.pos)
            if d < closest_dist: closest_dist = d; target_pos = p.pos
        if target_pos:
            d_vec = (target_pos - self.pos)
            if d_vec.length() > 0: d_vec = d_vec.normalize()
            self.pos += d_vec * self.speed; self.rect.center = self.pos

class Sniper(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, NEON_YELLOW, [(0, 0), (30, 0), (15, 30)])
        self.rect = self.image.get_rect()
        self.pos = Hunter().get_spawn(); self.rect.center = self.pos
        self.speed = 1.5; self.shoot_timer = random.randint(60, 180); self.type = "sniper"
    def update(self, players):
        closest_dist = float('inf'); target_pos = None
        for p in players:
            d = p.pos.distance_to(self.pos)
            if d < closest_dist: closest_dist = d; target_pos = p.pos
        if target_pos:
            d_vec = target_pos - self.pos; dist = d_vec.length()
            if dist > 250:
                if dist > 0: self.pos += d_vec.normalize() * self.speed
            elif dist < 150:
                if dist > 0: self.pos -= d_vec.normalize() * self.speed
            self.rect.center = self.pos
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                if dist > 0:
                    enemy_bullets.add(Bullet(self.rect.centerx, self.rect.centery, d_vec.normalize(), NEON_RED, False))
                    snd_enemy_shoot.play()
                    self.shoot_timer = 120

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 60
        self.angle = 0
        self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
        self.draw_boss()
        self.rect = self.image.get_rect(center=(WIDTH//2, -100))
        self.pos = pygame.math.Vector2(WIDTH//2, -100)
        self.health = 500
        self.max_health = 500
        self.shoot_timer = 0
        self.state = "enter" 
        self.type = "boss"

    def draw_boss(self):
        self.image.fill((0,0,0,0))
        points = []
        for i in range(6):
            rad = math.radians(i * 60 + self.angle)
            x = 60 + 50 * math.cos(rad)
            y = 60 + 50 * math.sin(rad)
            points.append((x, y))
        pygame.draw.polygon(self.image, NEON_PURPLE, points, 5)
        pygame.draw.circle(self.image, RED, (60, 60), 20)

    def update(self, players):
        self.angle += 2
        self.draw_boss()
        
        if self.state == "enter":
            self.pos.y += 2
            if self.pos.y >= 150: self.state = "fight"
        elif self.state == "fight":
            self.pos.x += math.sin(pygame.time.get_ticks() * 0.002) * 2
            self.shoot_timer += 1
            if self.shoot_timer >= 5: 
                for i in range(0, 360, 90): 
                    rad = math.radians(i + self.angle) 
                    direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                    enemy_bullets.add(Bullet(self.rect.centerx, self.rect.centery, direction, NEON_PURPLE, False))
                self.shoot_timer = 0
        self.rect.center = self.pos

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed=1):
        super().__init__()
        size = random.randint(2, 5)
        self.image = pygame.Surface((size, size)); self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * speed
        self.lifetime = random.randint(15, 30)
    def update(self):
        self.rect.center += self.vel; self.lifetime -= 1
        if self.lifetime <= 0: self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
        draw_powerup_icon(self.image, self.type, 10, 10)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH); self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 2); self.speed = random.uniform(0.2, 0.8)
    def move(self):
        self.y += self.speed
        if self.y > HEIGHT: self.y = 0; self.x = random.randint(0, WIDTH)
    def draw(self, surface):
        sx = self.x + shake_offset[0] * 0.5; sy = self.y + shake_offset[1] * 0.5
        pygame.draw.circle(surface, DARK_GREY, (int(sx), int(sy)), self.size)

# GROUPS -
players = pygame.sprite.Group()
bullets = pygame.sprite.Group(); enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group(); powerups = pygame.sprite.Group()
particles = pygame.sprite.Group()
stars = [Star() for _ in range(50)]
boss_group = pygame.sprite.Group()
ui_group = pygame.sprite.Group() 

# SCENES (MENUS) -

def settings_menu():
    btn_back = Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, "BACK", NEON_RED, RED)
    btn_vol_down = Button(WIDTH//2 - 120, 200, 50, 50, "-", NEON_BLUE, BUTTON_HOVER)
    btn_vol_up = Button(WIDTH//2 + 70, 200, 50, 50, "+", NEON_BLUE, BUTTON_HOVER)
    btn_trails = Button(WIDTH//2 - 100, 350, 200, 50, "TOGGLE", NEON_PURPLE, BUTTON_HOVER)

    while True:
        screen.fill(BLACK)
        for s in stars: s.move(); s.draw(screen)
        
        draw_text(screen, "SETTINGS", 50, NEON_CYAN, WIDTH//2, 50)
        draw_text(screen, f"VOLUME: {int(CONFIG['volume']*100)}%", 30, WHITE, WIDTH//2, 160)
        btn_vol_down.draw(screen); btn_vol_up.draw(screen)
        
        draw_text(screen, "NEON TRAILS", 30, WHITE, WIDTH//2, 310)
        status_text = "ON" if CONFIG['trails'] else "OFF"
        status_color = NEON_GREEN if CONFIG['trails'] else RED
        draw_text(screen, status_text, 30, status_color, WIDTH//2, 430)
        btn_trails.draw(screen)

        btn_back.draw(screen)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if btn_back.is_clicked(event): return
            if btn_vol_down.is_clicked(event): CONFIG['volume'] = max(0.0, CONFIG['volume'] - 0.1); update_volumes()
            if btn_vol_up.is_clicked(event): CONFIG['volume'] = min(1.0, CONFIG['volume'] + 0.1); update_volumes()
            if btn_trails.is_clicked(event): CONFIG['trails'] = not CONFIG['trails']

def instruction_menu():
    btn_back = Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, "BACK", NEON_RED, RED)
    while True:
        screen.fill(BLACK)
        for s in stars: s.move(); s.draw(screen)
        draw_text(screen, "HOW TO PLAY", 50, NEON_CYAN, WIDTH//2, 50)
        
        draw_text(screen, "PLAYER 1 (Cyan):", 26, NEON_CYAN, WIDTH//4, 110)
        draw_text(screen, "WASD + Mouse", 20, WHITE, WIDTH//4, 140)
        draw_text(screen, "SPACE: Dash", 20, WHITE, WIDTH//4, 165)
        draw_text(screen, "E: EMP (50 Fuel)", 20, NEON_YELLOW, WIDTH//4, 190)

        draw_text(screen, "PLAYER 2 (Orange):", 26, NEON_ORANGE, 3*WIDTH//4, 110)
        draw_text(screen, "Arrows (Turn/Thrust)", 20, WHITE, 3*WIDTH//4, 140)
        draw_text(screen, "R-CTRL: Shoot", 20, WHITE, 3*WIDTH//4, 165)
        draw_text(screen, "R-SHIFT: Dash", 20, WHITE, 3*WIDTH//4, 190)
        draw_text(screen, "NUM 0: EMP", 20, NEON_YELLOW, 3*WIDTH//4, 215)

        y = 260
        draw_text(screen, "POWER-UPS:", 30, GOLD, WIDTH//2, y)
        draw_powerup_icon(screen, "fuel", WIDTH//3, y + 35); draw_text(screen, "FUEL", 20, NEON_GREEN, WIDTH//3 + 20, y + 35, "left")
        draw_powerup_icon(screen, "shield", WIDTH//3, y + 65); draw_text(screen, "SHIELD (Ram)", 20, NEON_BLUE, WIDTH//3 + 20, y + 65, "left")
        draw_powerup_icon(screen, "health", WIDTH//3, y + 95); draw_text(screen, "REPAIR", 20, NEON_RED, WIDTH//3 + 20, y + 95, "left")
        draw_powerup_icon(screen, "frenzy", WIDTH//3, y + 125); draw_text(screen, "FRENZY", 20, NEON_PURPLE, WIDTH//3 + 20, y + 125, "left")
        draw_powerup_icon(screen, "multiplier", WIDTH//3, y + 155); draw_text(screen, "X2 SCORE", 20, GOLD, WIDTH//3 + 20, y + 155, "left")
        
        draw_text(screen, "BOSS EVERY 2000 PTS!", 30, NEON_RED, WIDTH//2, 480)

        btn_back.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if btn_back.is_clicked(event): return

def main_menu():
    high_score = get_high_score()
    btn_1p = Button(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50, "1 PLAYER", NEON_CYAN, (20, 100, 100))
    btn_2p = Button(WIDTH//2 - 100, HEIGHT//2 + 10, 200, 50, "2 PLAYERS", NEON_ORANGE, (150, 100, 0))
    btn_settings = Button(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50, "SETTINGS", NEON_PINK, BUTTON_HOVER)
    btn_help = Button(WIDTH//2 - 100, HEIGHT//2 + 150, 200, 50, "INSTRUCTIONS", NEON_BLUE, (50, 50, 200))
    btn_quit = Button(WIDTH//2 - 100, HEIGHT//2 + 220, 200, 50, "QUIT", NEON_RED, RED)

    while True:
        screen.fill(BLACK)
        for star in stars: star.move(); star.draw(screen)
        draw_text(screen, "NEON DRIFTER", 70, NEON_PURPLE, WIDTH//2, HEIGHT//3 - 40)
        draw_text(screen, "FINAL STABLE V15", 40, NEON_GREEN, WIDTH//2, HEIGHT//3 + 20)
        draw_text(screen, f"BEST SCORE: {high_score}", 30, GOLD, WIDTH//2, HEIGHT//3 + 70)
        
        btn_1p.draw(screen); btn_2p.draw(screen); 
        btn_settings.draw(screen); btn_help.draw(screen); btn_quit.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if btn_1p.is_clicked(event): return 1
            if btn_2p.is_clicked(event): return 2
            if btn_settings.is_clicked(event): settings_menu()
            if btn_help.is_clicked(event): instruction_menu()
            if btn_quit.is_clicked(event): pygame.quit(); sys.exit()

def game_over_screen(score):
    save_high_score(score)
    btn_restart = Button(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50, "PLAY AGAIN", NEON_GREEN, (50, 200, 50))
    btn_menu = Button(WIDTH//2 - 100, HEIGHT//2 + 130, 200, 50, "MAIN MENU", NEON_BLUE, (50, 50, 200))
    while True:
        screen.fill(BLACK)
        draw_text(screen, "MISSION FAILED", 60, NEON_RED, WIDTH//2, HEIGHT//3)
        draw_text(screen, f"TEAM SCORE: {score}", 40, WHITE, WIDTH//2, HEIGHT//2)
        btn_restart.draw(screen); btn_menu.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if btn_restart.is_clicked(event): return "restart"
            if btn_menu.is_clicked(event): return "menu"

def draw_hud(player, x_offset):
    draw_text(screen, f"P{player.player_id}", 20, player.color, x_offset + 50, 20)
    pygame.draw.rect(screen, RED, (x_offset, 35, 100, 10))
    pygame.draw.rect(screen, NEON_GREEN, (x_offset, 35, 100 * (player.health/100), 10))
    pygame.draw.rect(screen, (100, 100, 0), (x_offset, 50, 100, 10))
    pygame.draw.rect(screen, NEON_YELLOW, (x_offset, 50, 100 * (player.fuel/100), 10))
    status_y = 70
    if player.invincible: draw_text(screen, "READY!", 14, WHITE, x_offset + 50, status_y)
    elif player.frenzy_active: draw_text(screen, "FRENZY", 14, NEON_PURPLE, x_offset + 50, status_y)
    elif player.shield_active: draw_text(screen, "SHIELD", 14, NEON_BLUE, x_offset + 50, status_y)

def run_game(mode):
    global shake_duration, shake_magnitude, shake_offset, current_multiplier, boss_active
    
    players.empty(); p1 = Drifter(1); players.add(p1)
    if mode == 2: p2 = Drifter(2); players.add(p2)
    
    current_multiplier = 1; boss_active = False
    enemies.empty(); powerups.empty(); bullets.empty(); enemy_bullets.empty(); particles.empty(); boss_group.empty(); ui_group.empty()
    score = 0; spawn_timer = 0; paused = False; next_boss_score = 2000
    
    btn_pause_hud = Button(WIDTH - 50, 10, 40, 40, "||", DARK_GREY, WHITE)
    btn_resume = Button(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 50, "RESUME", NEON_GREEN, (50, 200, 50))
    btn_menu = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "MAIN MENU", NEON_RED, RED)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_ESCAPE): paused = not paused
            if paused:
                if btn_resume.is_clicked(event): paused = False
                if btn_menu.is_clicked(event): return -1 # Signal return to menu
            else:
                if btn_pause_hud.is_clicked(event): paused = True

        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(SEMI_TRANSPARENT_BLACK)
            screen.blit(overlay, (0, 0))
            draw_text(screen, "PAUSED", 80, WHITE, WIDTH//2, HEIGHT//3)
            btn_resume.draw(screen); btn_menu.draw(screen)
            pygame.display.flip(); clock.tick(FPS); continue

        shake_offset = [0, 0]
        if shake_duration > 0:
            shake_offset[0] = random.randint(-shake_magnitude, shake_magnitude)
            shake_offset[1] = random.randint(-shake_magnitude, shake_magnitude)
            shake_duration -= 1

        players.update()
        bullets.update(); enemy_bullets.update(); particles.update(); powerups.update(); boss_group.update(players); ui_group.update()
        for e in enemies: e.update(players)
        for s in stars: s.move()

        if score >= next_boss_score and not boss_active:
            boss_active = True
            boss_group.add(Boss())
            enemies.empty()
            trigger_shake(30, 5)
        
        if boss_active and len(boss_group) == 0:
            boss_active = False
            next_boss_score += 3000

        if not boss_active:
            spawn_timer += 1
            if spawn_timer >= max(40, 60 - (score // 500)):
                if random.random() < 0.3: enemies.add(Sniper())
                else: enemies.add(Hunter())
                spawn_timer = 0
            
            if random.randint(1, 150) < 2 + (1 if mode == 2 else 0) and len(powerups) < 3:
                r = random.random(); type = "fuel"
                if r < 0.4: type = "fuel"
                elif r < 0.55: type = "shield"
                elif r < 0.70: type = "health"
                elif r < 0.85: type = "frenzy"
                else: type = "multiplier"
                powerups.add(PowerUp(type))

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            pts = 100 * current_multiplier
            score += pts
            ui_group.add(FloatingText(hit.rect.centerx, hit.rect.centery, f"+{pts}", WHITE))
            snd_expl.play()
            trigger_shake(5, 5)
            color = NEON_YELLOW if hit.type == "sniper" else NEON_RED
            for _ in range(8): particles.add(Particle(hit.rect.centerx, hit.rect.centery, color, speed=2))

        if boss_active:
            for boss in boss_group:
                hit_bullets = pygame.sprite.spritecollide(boss, bullets, True)
                for b in hit_bullets:
                    boss.health -= 5 * current_multiplier
                    particles.add(Particle(b.rect.centerx, b.rect.centery, NEON_PURPLE))
                    if boss.health <= 0:
                        boss.kill()
                        pts = 5000 * current_multiplier
                        score += pts
                        ui_group.add(FloatingText(WIDTH//2, HEIGHT//2, f"BOSS DESTROYED +{pts}", GOLD))
                        trigger_shake(60, 10)
                        for _ in range(50): particles.add(Particle(boss.rect.centerx, boss.rect.centery, NEON_PURPLE, speed=5))

        for p in players:
            # EMP Drawing and Collision
            if p.emp_active:
                p.emp_radius += 15
                pygame.draw.circle(screen, NEON_CYAN, p.rect.center, p.emp_radius, 5)
                # Kill enemies in circle
                for e in enemies:
                    if p.pos.distance_to(e.pos) < p.emp_radius:
                        e.kill(); score += 50; particles.add(Particle(e.rect.centerx, e.rect.centery, NEON_BLUE, speed=4))
                # Kill bullets
                for b in enemy_bullets:
                    if p.pos.distance_to(b.pos) < p.emp_radius: b.kill()
                
                if p.emp_radius > 600: p.emp_active = False

            col = pygame.sprite.spritecollideany(p, powerups)
            if col:
                snd_powerup.play()
                if col.type == "fuel": 
                    pts = 50*current_multiplier
                    score += pts; p.fuel = min(100, p.fuel+25); particles.add(Particle(p.rect.centerx, p.rect.centery, NEON_GREEN))
                    ui_group.add(FloatingText(p.rect.centerx, p.rect.centery, f"+{pts}", NEON_GREEN))
                elif col.type == "shield": p.activate_shield(); ui_group.add(FloatingText(p.rect.centerx, p.rect.top, "SHIELD", NEON_BLUE))
                elif col.type == "health": p.health = min(100, p.health + 30); ui_group.add(FloatingText(p.rect.centerx, p.rect.top, "HP UP", NEON_RED))
                elif col.type == "frenzy": p.activate_frenzy(); ui_group.add(FloatingText(p.rect.centerx, p.rect.top, "FRENZY", NEON_PURPLE))
                elif col.type == "multiplier": p.activate_multiplier(); ui_group.add(FloatingText(p.rect.centerx, p.rect.top, "X2 SCORE", GOLD))
                col.kill()

        for p in players:
            if p.invincible: continue
            body_hits = pygame.sprite.spritecollide(p, enemies, False) 
            bullet_hits = pygame.sprite.spritecollide(p, enemy_bullets, True)
            
            if body_hits or bullet_hits:
                if p.shield_active:
                    for e in body_hits: e.kill(); score += 100 * current_multiplier; trigger_shake(8, 8)
                else:
                    if body_hits:
                        for e in body_hits: e.kill()
                    p.health -= 25; trigger_shake(10, 10)
                    for _ in range(15): particles.add(Particle(p.rect.centerx, p.rect.centery, WHITE, speed=3))
            
            if p.health <= 0 or p.fuel <= 0: p.kill()
        
        if len(players) == 0: return score

        screen.fill(BLACK)
        for s in stars: s.draw(screen)
        gx, gy = shake_offset
        for x in range(0, WIDTH, 40): pygame.draw.line(screen, (15, 15, 20), (x + gx, 0 + gy), (x + gx, HEIGHT + gy))
        for y in range(0, HEIGHT, 40): pygame.draw.line(screen, (15, 15, 20), (0 + gx, y + gy), (WIDTH + gx, y + gy))
        
        for group in [particles, powerups, bullets, enemy_bullets, enemies, players, boss_group]:
            for sprite in group: screen.blit(sprite.image, sprite.rect.move(shake_offset))
        
        for p in players:
            if p.shield_active: pygame.draw.circle(screen, NEON_BLUE, (p.rect.centerx + gx, p.rect.centery + gy), 35, 2)
            if p.emp_active: pygame.draw.circle(screen, NEON_CYAN, (p.rect.centerx + gx, p.rect.centery + gy), p.emp_radius, 5)

        for ui in ui_group: screen.blit(ui.image, ui.rect.move(shake_offset))

        alive_players = list(players)
        p1_still_alive = False; p2_still_alive = False
        for p in alive_players:
            if p.player_id == 1: draw_hud(p, 20); p1_still_alive = True
            if p.player_id == 2: draw_hud(p, WIDTH - 120); p2_still_alive = True
        
        if mode == 2 and not p1_still_alive: draw_text(screen, "P1 DEAD", 20, RED, 60, 20)
        if mode == 2 and not p2_still_alive: draw_text(screen, "P2 DEAD", 20, RED, WIDTH - 60, 20)

        if boss_active:
            for boss in boss_group:
                pygame.draw.rect(screen, RED, (WIDTH//2 - 150, 50, 300, 20))
                pygame.draw.rect(screen, NEON_PURPLE, (WIDTH//2 - 150, 50, 300 * (boss.health/boss.max_health), 20))
                draw_text(screen, "NEON COLOSSUS", 20, WHITE, WIDTH//2, 40)

        draw_text(screen, f"{score}", 30, WHITE, WIDTH // 2, 20)
        btn_pause_hud.draw(screen)
        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__":
    load_and_play_music("music.ogg") # Start music on launch
    current_mode = 1
    while True:
        current_mode = main_menu() 
        final_score = run_game(current_mode) 
        if final_score == -1: continue # If -1, go to menu without game over
        choice = game_over_screen(final_score) 
        if choice == "menu": continue 
        elif choice == "restart": pass

##
    