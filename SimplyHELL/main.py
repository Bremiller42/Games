import pygame, math, random, time, os, sys

MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
CURSOR_PATH = os.path.join(MAIN_DIR, "Images/cursor.png")
CROSSHAIR_PATH = os.path.join(MAIN_DIR, "Images/cross_hair.png")

DEBUG = True # Set to True to print debug statements

pygame.init()

FPS = 60

display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h
if DEBUG:
    print(SCREEN_WIDTH, SCREEN_HEIGHT)

LOGICAL_WIDTH = 800
LOGICAL_HEIGHT = 600

PLAYER_SIZE = 20
LEVEL = 1
PLAYER_SCORE = 0
PLAYER_SHIELD = 2
PLAYER_SPEED = 1
ORIGINAL_SPEED = PLAYER_SPEED
ENERGY_COST = 5
ENERGY_RECHARGE = 0.5

PLAYER_HEALTH = 100
MAX_HEALTH_BAR_WIDTH = (SCREEN_WIDTH - 100)
PLAYER_HEALTH_BAR = int((PLAYER_HEALTH / 100) * MAX_HEALTH_BAR_WIDTH)

PLAYER_ENERGY = 100
MAX_ENERGY_BAR_WIDTH = (SCREEN_WIDTH - 100)
PLAYER_ENERGY_BAR = min(int((PLAYER_ENERGY / 100) * MAX_ENERGY_BAR_WIDTH), MAX_ENERGY_BAR_WIDTH)

PLAYER_DAMAGE = 1

ENEMY_HEALTH = 1 * LEVEL
ENEMY_DAMAGE = 5 * LEVEL
ENEMY_ATTACK_SPEED = 1000
ENEMY_SPEED = 1 * (LEVEL / 2)
ENEMY_SIZE = 20
ENEMY_SHIELD = 1
ENEMIES_PER_LEVEL_AT_ONCE = 5 * (LEVEL / 2)
TOTAL_ENEMIES_PER_LEVEL = 10 * LEVEL
TOTAL_ENEMIES = 0
enemies = []

BULLET_SPEED = 5
BULLET_SIZE = 2
FIRE_RATE = 500
bullets = []

buttons = []

title_font_size = 100
menu_font_size = 30

title_font = pygame.font.Font(None, title_font_size)
menu_font = pygame.font.Font(None, menu_font_size)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 20)

running = True

class GameState:
    MAIN_MENU = 'main_menu'
    GAME = 'game'
    SETTINGS = 'settings' 
    UPGRADE_SHOP = 'upgrade_shop'
    PAUSE = 'pause_menu'

current_state = GameState.MAIN_MENU

def switch_state(new_state):
    global current_state
    current_state = new_state

# Load custom cursor Image
cursor_image = pygame.image.load(CURSOR_PATH)
cursor_image = pygame.transform.scale(cursor_image, (20, 25))
pygame.mouse.set_visible(False)  # Hides default cursor

def initialize_game():
    global LEVEL, PLAYER_SCORE, PLAYER_HEALTH, PLAYER_ENERGY, PLAYER_SHIELD, PLAYER_HEALTH_BAR, PLAYER_ENERGY_BAR, enemies, bullets, TOTAL_ENEMIES, player, last_shot_time
    LEVEL = 1
    PLAYER_SCORE = 0
    PLAYER_HEALTH = 100
    PLAYER_ENERGY = 100
    PLAYER_HEALTH_BAR = int((PLAYER_HEALTH / 100) * MAX_HEALTH_BAR_WIDTH)
    PLAYER_ENERGY_BAR = min(int((PLAYER_ENERGY / 100) * MAX_ENERGY_BAR_WIDTH), MAX_ENERGY_BAR_WIDTH)
    enemies = []
    bullets = []
    TOTAL_ENEMIES = 0
    last_shot_time = 0
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, PLAYER_SIZE, PLAYER_SPEED, PLAYER_SHIELD, PLAYER_HEALTH, PLAYER_ENERGY)

class Button:
    def __init__(self, text, x_percent, y_percent, width_percent, height_percent, font_size):
        self.text = text
        self.x_percent = x_percent
        self.y_percent = y_percent
        self.width_percent = width_percent
        self.height_percent = height_percent
        self.font_size = font_size
        self.font = pygame.font.Font(None, self.font_size)
        self.update_position_and_size()
    
    def update_position_and_size(self):
        button_width = int(SCREEN_WIDTH * self.width_percent)
        button_height = int(SCREEN_HEIGHT * self.height_percent)
        self.rect = pygame.Rect(
            int(SCREEN_WIDTH * self.x_percent) - button_width // 2,
            int(SCREEN_HEIGHT * self.y_percent),
            button_width,
            button_height
        )
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
        screen.blit(self.text_surface, self.text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def handle_screen_resize(width, height, fullscreen=False):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, buttons
    SCREEN_WIDTH, SCREEN_HEIGHT = width, height
    flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    
    # Update positions and sizes of buttons
    for button in buttons:
        button.update_position_and_size()

    # Redraw elements for the current state
    redraw_current_state_elements()

def redraw_settings_elements():
    global screen
    screen.fill((0, 0, 0))
    title_surface = title_font.render("Settings", True, (255, 255, 255))
    screen.blit(title_surface, (SCREEN_WIDTH / 2 - title_surface.get_width() / 2, SCREEN_HEIGHT / 24))
    resolution_surface = menu_font.render("Resolutions", True, (255, 255, 255))
    screen.blit(resolution_surface, (SCREEN_WIDTH / 10 - resolution_surface.get_width() / 2, SCREEN_HEIGHT * .175))
    for button in buttons:
        button.draw(screen)
    pygame.display.flip()

def redraw_current_state_elements():
    global current_state
    if current_state == GameState.SETTINGS:
        redraw_settings_elements()
    elif current_state == GameState.MAIN_MENU:
        # redraw_main_menu_elements()
        pass


def main_menu():
    global running, screen, SCREEN_WIDTH, SCREEN_HEIGHT
    screen.fill((0, 0, 0))

    # Define font sizes
    title_font_size = 100
    menu_font_size = 30

    title_font = pygame.font.Font(None, title_font_size)
    menu_font = pygame.font.Font(None, menu_font_size)

    title_surface = title_font.render("SimplyHELL", True, (255, 255, 255))
    play_button = Button("Play Game", 0.5, 0.33, 0.25, 0.083, 30)
    settings_button = Button("Settings", 0.5, 0.43, 0.25, 0.083, 30)
    upgrades_button = Button("Upgrade Shop", 0.5, 0.53, 0.25, 0.083, 30)
    quit_button = Button("Quit Game", 0.5, 0.63, 0.25, 0.083, 30)

    global buttons
    buttons = [play_button, settings_button, upgrades_button, quit_button]

    screen.blit(title_surface, (SCREEN_WIDTH / 2 - title_surface.get_width() / 2, SCREEN_HEIGHT / 8))    

    for button in buttons:
        button.draw(screen)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    screen.blit(cursor_image, (mouse_x, mouse_y))

    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            handle_screen_resize(SCREEN_WIDTH, SCREEN_HEIGHT)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                switch_state(GameState.GAME)
            elif event.key == pygame.K_s:
                switch_state(GameState.SETTINGS)
            elif event.key == pygame.K_u:
                switch_state(GameState.UPGRADE_SHOP)
            elif event.key == pygame.K_q:
                pygame.QUIT()
                exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if play_button.is_clicked(mouse_pos):
                initialize_game()
                switch_state(GameState.GAME)
            elif settings_button.is_clicked(mouse_pos):
                switch_state(GameState.SETTINGS)
            elif upgrades_button.is_clicked(mouse_pos):
                switch_state(GameState.UPGRADE_SHOP)
            elif quit_button.is_clicked(mouse_pos):
                pygame.quit()
                exit()

def settings():
    global running, SCREEN_WIDTH, SCREEN_HEIGHT, screen, CURSOR_PATH
    screen.fill((0, 0, 0))
    if DEBUG:
        print("Screen Loaded")
    title_font_size = 50
    menu_font_size = 30

    title_font = pygame.font.Font(None, title_font_size)
    menu_font = pygame.font.Font(None, menu_font_size)
    if DEBUG:
        print("Fonts Loaded")
    title_surface = title_font.render("Settings", True, (255, 255, 255))
    screen.blit(title_surface, (SCREEN_WIDTH / 2 - title_surface.get_width() / 2, SCREEN_HEIGHT / 24))
    if DEBUG:
        print("Settings surface Loaded")
    back_button = Button("Back", 0.15, .85, .15, .083, 30)

    # Resolutions
    resolution_surface = menu_font.render("Resolutions", True, (255, 255, 255))
    screen.blit(resolution_surface, (SCREEN_WIDTH / 10 - resolution_surface.get_width() / 2, SCREEN_HEIGHT * .175))

    R800600_button = Button("800 x 600", 0.30, 0.15, 0.15, 0.083, 30)
    R1024768_button = Button("1024 x 768", 0.47, 0.15, 0.15, 0.083, 30)
    R19201080_button = Button("1920 x 1080", 0.64, 0.15, 0.15, 0.083, 30)
    FULL_SCREEN_button = Button("Full Screen", 0.81, 0.15, 0.15, 0.083, 30)
    if DEBUG:
        print("Resolution Buttons Loaded")
    global buttons
    buttons = [back_button, R800600_button, R1024768_button, R19201080_button, FULL_SCREEN_button]

    for button in buttons:
        button.draw(screen)
    if DEBUG:
        print("Buttons Drawn")
    mouse_x, mouse_y = pygame.mouse.get_pos()
    screen.blit(cursor_image, (mouse_x, mouse_y))
    if DEBUG:
        print("Mouse and Cursor Loaded")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if back_button.is_clicked(mouse_pos):
                switch_state(GameState.MAIN_MENU)
            if R800600_button.is_clicked(mouse_pos):
                SCREEN_WIDTH = 800
                SCREEN_HEIGHT = 600
                handle_screen_resize(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen=False)
            elif R1024768_button.is_clicked(mouse_pos):
                SCREEN_WIDTH = 1024
                SCREEN_HEIGHT = 768
                handle_screen_resize(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen=False)
            elif R19201080_button.is_clicked(mouse_pos):
                SCREEN_WIDTH = 1920
                SCREEN_HEIGHT = 1080
                handle_screen_resize(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen=False)
            elif FULL_SCREEN_button.is_clicked(mouse_pos):
                display_info = pygame.display.Info()
                SCREEN_WIDTH = display_info.current_w
                SCREEN_HEIGHT = display_info.current_h
                if DEBUG:
                    print(f"Switched to full screen: width={SCREEN_WIDTH}, height={SCREEN_HEIGHT}")
                handle_screen_resize(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen=False)
    pygame.display.flip()

def pause_screen():
    global current_state, CURSOR_PATH, running

    title_font_size = 50
    menu_font_size = 30

    pygame.display.flip()
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = GameState.GAME
                    paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if quit_button.is_clicked(mouse_pos):
                    pygame.quit()
                    exit()
                elif main_menu_button.is_clicked(mouse_pos):
                    switch_state(GameState.MAIN_MENU)
                    paused = False

        # Redraw pause screen each loop iteration
        screen.fill((0, 0, 0))
        cursor_image = pygame.image.load(CURSOR_PATH)
        cursor_image = pygame.transform.scale(cursor_image, (20, 25))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(cursor_image, (mouse_x, mouse_y))

        pygame.mouse.set_visible(False)

        title_font = pygame.font.Font(None, title_font_size)
        menu_font = pygame.font.Font(None, menu_font_size)

        title_surface = title_font.render("Game Paused", True, (255, 255, 255))
        screen.blit(title_surface, (SCREEN_WIDTH / 2 - title_surface.get_width() / 2, SCREEN_HEIGHT / 24))

        main_menu_button = Button("Main Menu", 0.5, 0.65, 0.25, 0.083, 30)

        quit_button = Button("Quit Game", 0.5, 0.75, 0.25, 0.083, 30)

        global buttons
        buttons = [quit_button, main_menu_button]

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        
class Player:
    def __init__(self, x, y, size, speed, shield, health, energy):
        self.rect_1 = pygame.Rect(x - (size / 2), y - (size / 2), size, size)
        self.rect_2 = pygame.Rect(x - ((size - shield) / 2), y - ((size - shield) / 2), size - shield, size - shield)
        self.size = size
        self.speed = speed
        self.original_speed = speed
        self.shield = shield
        self.health = health
        self.energy = energy
        self.angle = 90
        self.health_bar = int((health / 100) * (SCREEN_WIDTH - 10))
        self.energy_bar = min(int((energy / 100) * MAX_ENERGY_BAR_WIDTH), MAX_ENERGY_BAR_WIDTH)
        self.damage = PLAYER_DAMAGE
        self.moving = False
        self.is_sprinting = False

    def move(self):
        keys = pygame.key.get_pressed()
        self.moving = False

        if keys[pygame.K_a] and self.rect_1.left > 0:
            self.moving = True
            self.rect_1.x -= self.speed
            self.rect_2.x -= self.speed

        if keys[pygame.K_d] and self.rect_1.right < SCREEN_WIDTH:
            self.moving = True
            self.rect_1.x += self.speed
            self.rect_2.x += self.speed

        if keys[pygame.K_w] and self.rect_1.top > 60:
            self.moving = True
            self.rect_1.y -= self.speed
            self.rect_2.y -= self.speed

        if keys[pygame.K_s] and self.rect_1.bottom < SCREEN_HEIGHT:
            self.moving = True
            self.rect_1.y += self.speed
            self.rect_2.y += self.speed
  
        if not self.is_sprinting:
            self.speed = self.original_speed

    def sprint(self):
        keys = pygame.key.get_pressed()

        # Start sprinting only if LSHIFT is pressed, player is moving, and energy is 100%
        if keys[pygame.K_LSHIFT] and self.moving and self.energy == 100:
            self.is_sprinting = True

        # If sprinting, decrease energy and increase speed
        if self.is_sprinting:
            self.energy -= ENERGY_COST
            if self.energy < 0:
                self.energy = 0
            self.speed = self.original_speed * 2
            
            # Stop sprinting if LSHIFT is released or energy runs out
            if not keys[pygame.K_LSHIFT] or self.energy <= 0:
                self.is_sprinting = False
                self.speed = self.original_speed
        
        # If not sprinting, recharge energy
        if not self.is_sprinting:
            self.energy += ENERGY_RECHARGE
            if self.energy > 100:
                self.energy = 100

        # Update energy bar
        self.energy_bar = min(int((self.energy / 100) * MAX_ENERGY_BAR_WIDTH), MAX_ENERGY_BAR_WIDTH)

    def draw(self):
        pygame.draw.rect(screen, (0, 200, 255), self.rect_1)
        pygame.draw.rect(screen, (0, 0, 0), self.rect_2)

    def shoot(self):
        global last_shot_time
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and current_time - last_shot_time >= FIRE_RATE:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            center_x = self.rect_1.centerx
            center_y = self.rect_1.centery
            dx = mouse_x - center_x
            dy = mouse_y - center_y
            angle = math.degrees(math.atan2(dy, dx))
            if DEBUG:
                print(f"Shooting bullet: center_x={center_x}, center_y={center_y}, mouse_x={mouse_x}, mouse_y={mouse_y}, angle={angle}")

            bullets.append(Bullet(center_x, center_y, angle))
            last_shot_time = current_time

    def check_collisions(self):
        global PLAYER_HEALTH, PLAYER_HEALTH_BAR
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy.x - enemy.size / 2 - 2, enemy.y - enemy.size / 2 - 2, enemy.size + 4, enemy.size + 4)
            player_rect = self.rect_1.inflate(4, 4)

            if player_rect.colliderect(enemy_rect):
                if enemy.attack():
                    self.health -= enemy.damage
                if enemy.attack_count >= 3:
                    enemies.remove(enemy)
                if self.health <= 0:
                    self.health = 0
                    switch_state(GameState.MAIN_MENU)
                
        self.health_bar = min(int((self.health / 100) * MAX_HEALTH_BAR_WIDTH), MAX_HEALTH_BAR_WIDTH)
        return True

    def scale(self, factor):
        self.rect_1.x *= factor
        self.rect_1.y *= factor
        self.rect_1.width *= factor
        self.rect_1.height *= factor
        self.rect_2.x *= factor
        self.rect_2.y *= factor
        self.rect_2.width *= factor
        self.rect_2.height *= factor
        self.speed *= factor
        self.original_speed *= factor

class Enemy:
    def __init__(self, x, y, attack_count=0):
        self.x = x
        self.y = y
        self.speed = ENEMY_SPEED
        self.health = ENEMY_HEALTH
        self.shield = ENEMY_SHIELD
        self.size = ENEMY_SIZE
        self.damage = ENEMY_DAMAGE
        self.attack_speed = ENEMY_ATTACK_SPEED
        self.attack_count = attack_count
        self.last_attack_time = pygame.time.get_ticks()

    def move(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        stop_distance = (self.size / 2) + (PLAYER_SIZE / 2)
        if dist > stop_distance:
            dx = dx / dist
            dy = dy / dist
            self.x += dx * self.speed
            self.y += dy * self.speed

    def draw(self):
        half_size = self.size / 2
        points = [
            (self.x, self.y - half_size),
            (self.x - half_size, self.y + half_size),
            (self.x + half_size, self.y + half_size)
        ]
        pygame.draw.polygon(screen, (255, 0, 0), points, ENEMY_SHIELD)

    def attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= ENEMY_ATTACK_SPEED:
            self.attack_count += 1
            self.last_attack_time = current_time
            return True
        return False
    
    def scale(self, factor):
        self.x  *= factor
        self.y *= factor
        self.speed  *= factor
        self.size  *= factor
        self.damage  *= factor

class Bullet:   
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.size = BULLET_SIZE
        self.damage = PLAYER_DAMAGE

    def move(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        if DEBUG:
            print(f"Bullet moved to: x={self.x}, y={self.y}, angle={self.angle}")

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size)

    def scale(self, factor):
        self.x  *= factor
        self.y *= factor
        self.speed  *= factor
        self.size  *= factor
        self.damage  *= factor

def level_up():
    global TOTAL_ENEMIES, LEVEL
    TOTAL_ENEMIES = 0
    LEVEL += 1

clock_timer = 0
last_shot_time = 0

player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, PLAYER_SIZE, PLAYER_SPEED, PLAYER_SHIELD, PLAYER_HEALTH, PLAYER_ENERGY)

def game_screen():
    global running, TOTAL_ENEMIES, LEVEL, last_shot_time, PLAYER_SCORE, current_state
    clock.tick(FPS)
    screen.fill((0, 0, 0))

    crosshair_image = pygame.image.load(CROSSHAIR_PATH)
    crosshair_image = pygame.transform.scale(crosshair_image, (30, 30))

    pygame.mouse.set_visible(False)  # Hides default cursor

    mouse_x, mouse_y = pygame.mouse.get_pos()
    screen.blit(crosshair_image, (mouse_x - crosshair_image.get_width() // 2, mouse_y - crosshair_image.get_height() // 2))

    player.draw()
    player.move()
    player.sprint()
    player.shoot()
    if not player.check_collisions():
        running = False

    health_text_surface = font.render("Health: ", True, (255, 255, 255))
    energy_text_surface = font.render("Energy: ", True, (255, 255, 255))
    score_text_surface = font.render(f"Score: {PLAYER_SCORE}", True, (255, 255, 255))
    level_text_surface = font.render(f" Level {LEVEL}", True, (255, 255, 255))

    health_text_rect = health_text_surface.get_rect()
    energy_text_rect = energy_text_surface.get_rect()
    score_text_rect = score_text_surface.get_rect()
    level_text_rect = level_text_surface.get_rect()

    health_text_rect.topleft = (10, 28)
    energy_text_rect.topleft = (10, 48)
    score_text_rect.topleft = (10, 10)
    level_text_rect.topleft = (SCREEN_WIDTH / 2 - 30, 10)

    screen.blit(health_text_surface, health_text_rect)
    screen.blit(energy_text_surface, energy_text_rect)
    screen.blit(score_text_surface, score_text_rect)
    screen.blit(level_text_surface, level_text_rect)

    pygame.draw.rect(screen, (255, 0, 0), (65, 30, player.health_bar, 10))
    pygame.draw.rect(screen, (0, 0, 255), (65, 50, player.energy_bar, 10))

    if TOTAL_ENEMIES < TOTAL_ENEMIES_PER_LEVEL:
        if len(enemies) < ENEMIES_PER_LEVEL_AT_ONCE:
            enemy_x = random.randint(0, SCREEN_WIDTH)
            enemy_y = random.randint(0, SCREEN_HEIGHT)
            enemies.append(Enemy(enemy_x, enemy_y))
            TOTAL_ENEMIES += 1

    for enemy in enemies:
        enemy.move(player.rect_1.centerx, player.rect_1.centery)
        enemy.draw()

    for bullet in bullets[:]:
        bullet.move()
        bullet.draw()
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy.x - enemy.size / 2, enemy.y - enemy.size / 2, enemy.size, enemy.size)
            if enemy_rect.collidepoint(bullet.x, bullet.y):
                bullets.remove(bullet)
                enemy.health -= bullet.damage
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    PLAYER_SCORE += 1
        if bullet.x < 0 or bullet.x > SCREEN_WIDTH or bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
            bullets.remove(bullet)

    if TOTAL_ENEMIES >= TOTAL_ENEMIES_PER_LEVEL and not enemies:
        level_up()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                current_state = GameState.PAUSE 
    pygame.display.flip()

while running:
    if current_state == GameState.MAIN_MENU:
        main_menu()
    elif current_state == GameState.GAME:
        game_screen()
    elif current_state == GameState.SETTINGS:
        settings()
    elif current_state == GameState.UPGRADE_SHOP:
        pass
    elif current_state == GameState.PAUSE:
        pause_screen()
    
pygame.quit()
