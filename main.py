import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
PLAYER_LIVES = 3
HIGH_SCORE = 5000  # Default
NEW_LIFE_THRESHOLD = 5000

# Load assets
player_image = pygame.image.load('player_ship.png')
player_image = pygame.transform.scale(player_image, (28, 28))  # Reduce scale further to make the player ship smaller

enemy_image_2 = pygame.image.load('enemy_ship_2.png')
enemy_image_2 = pygame.transform.scale(enemy_image_2, (50, 50))
enemy_image_2 = pygame.transform.rotate(enemy_image_2, 180)  

enemy_image_3 = pygame.image.load('enemy_ship_3.png')
enemy_image_3 = pygame.transform.scale(enemy_image_3, (50, 50))
enemy_image_3 = pygame.transform.rotate(enemy_image_3, 180)  

enemy_image = pygame.image.load('enemy_ship.png')
enemy_image = pygame.transform.scale(enemy_image, (50, 50))
enemy_image = pygame.transform.rotate(enemy_image, 180) 

bullet_image = pygame.image.load('bullet.png')
bullet_image = pygame.transform.scale(bullet_image, (10, 20))

enemy_bullet_image = pygame.image.load('enemy_bullet.png')
enemy_bullet_image = pygame.transform.scale(enemy_bullet_image, (10, 20))

shoot_sound = pygame.mixer.Sound('shoot.wav')
enemy_shoot_sound = pygame.mixer.Sound('enemy_shoot.wav')
hit_sound = pygame.mixer.Sound('hit.wav')
explosion_sound = pygame.mixer.Sound('explosion.wav')
# Load start sound
start_sound = pygame.mixer.Sound('start_sound.wav')
# Load game over sound
game_over_sound = pygame.mixer.Sound('game_over.wav')

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga's Revenge")

# Fonts
font = pygame.font.Font(None, 36)

# Initialize joystick
joystick = None
if pygame.joystick.get_count() > 0:
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print("Joystick initialized:", joystick.get_name())
    except pygame.error as e:
        print(f"Joystick initialization error: {e}")
        joystick = None
else:
    print("No joystick found.")

# Star class for background
class Star:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (self.x, self.y), 1)

# Create stars for the background
stars_far = [Star(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), 1) for _ in range(100)]
stars_near = [Star(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), 2) for _ in range(50)]

# Function to show start screen
def show_start_screen():
    start_sound.play()
    screen.fill((0, 0, 0))  # Black background

    # Draw stars (parallax effect on start screen)
    for star in stars_far:
        star.update()
        star.draw(screen)
    for star in stars_near:
        star.update()
        star.draw(screen)

    # Draw title and prompt to start
    title_font = pygame.font.Font(None, 74)
    title_text = title_font.render("Galaga's Revenge", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4 - 100))

    # Arrange game assets to create a fight scene
    # Draw player ship shooting towards enemies
    screen.blit(player_image, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 100))
    screen.blit(bullet_image, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 80))
    
    # Draw multiple enemy ships in a more dynamic formation
    screen.blit(enemy_image, (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 4 + 30))
    screen.blit(enemy_image_2, (SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 4 + 80))
    screen.blit(enemy_image_3, (SCREEN_WIDTH // 2 + 190, SCREEN_HEIGHT // 4 + 130))

    # Draw enemy bullets directed at player ship
    screen.blit(enemy_bullet_image, (SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 + 50))
    screen.blit(enemy_bullet_image, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2 + 70))

    # Draw start button prompt
    button_font = pygame.font.Font(None, 50)
    if joystick and joystick.get_init():
        button_text = button_font.render("Press X to Start", True, WHITE)
    else:
        button_text = button_font.render("Click to Start", True, WHITE)
    screen.blit(button_text, (SCREEN_WIDTH // 2 - button_text.get_width() // 2, SCREEN_HEIGHT // 2 + 200))

    pygame.display.flip()

    waiting = True
    while waiting:
        try:
            events = pygame.event.get()
        except SystemError as e:
            print(f"Error during event polling: {e}")
            events = []
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    waiting = False
                    start_sound.fadeout(2000)
            if joystick and joystick.get_init() and event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # Ensure joystick is initialized and button 0 is pressed
                    start_sound.fadeout(2000)
                    waiting = False


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        self.lives = PLAYER_LIVES

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

        # Joystick movement
        if joystick and joystick.get_init():
            axis_x = joystick.get_axis(0)
            if abs(axis_x) > 0.1:  # Dead zone
                self.rect.x += int(axis_x * self.speed * 2)
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type=1):
        super().__init__()
        if enemy_type == 1:
            self.image = enemy_image
        elif enemy_type == 2:
            self.image = enemy_image_2
        elif enemy_type == 3:
            self.image = enemy_image_3
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2
        self.shoot_chance = 1  # Base shooting chance, will increase with each wave

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.y = -self.rect.height
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        if random.randint(0, 100) < self.shoot_chance and len(enemy_bullets) < len(enemies):  # Randomly shoot bullets
            self.shoot()

    def shoot(self):
        enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)
        enemy_shoot_sound.play()

# Enemy Bullet class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_bullet_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Function to show game over screen and wait for player to restart
def show_game_over():
    # Stop all sounds
    shoot_sound.stop()
    enemy_shoot_sound.stop()
    start_sound.stop()
    explosion_sound.stop()
    hit_sound.stop()
    game_over_sound.play()
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    button_font = pygame.font.Font(None, 50)
    if joystick and joystick.get_init():
        button_text = button_font.render("Press X to Restart", True, WHITE)
    else:
        button_text = button_font.render("Press R to Restart", True, WHITE)
    screen.blit(button_text, (SCREEN_WIDTH // 2 - button_text.get_width() // 2, SCREEN_HEIGHT // 2 + text.get_height()))

    # Show score
    high_score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + text.get_height() + 60))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    game_over_sound.fadeout(100)
            if joystick and joystick.get_init() and event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    waiting = False
                    game_over_sound.fadeout(100)

# Function to reset the game
def reset_game():
    global all_sprites, bullets, enemies, enemy_bullets, player, score, wave, HIGH_SCORE
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    for i in range(5):
        enemy = Enemy(random.randint(0, SCREEN_WIDTH - 50), random.randint(-100, -40))
        all_sprites.add(enemy)
        enemies.add(enemy)

    if score >= HIGH_SCORE:
        HIGH_SCORE += NEW_LIFE_THRESHOLD
        player.lives += 1
    score = 0
    wave = 1

# Initialize sprite groups before creating player and other entities
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# Initialize player and add to all_sprites
player = Player()
all_sprites.add(player)

# Create initial enemies
for i in range(5):
    enemy = Enemy(random.randint(0, SCREEN_WIDTH - 50), random.randint(-100, -40))
    all_sprites.add(enemy)
    enemies.add(enemy)

# Initialize score and wave variables
score = 0
wave = 1

# Show start screen
show_start_screen()

# Main game loop
running = True
while running:
    screen.fill((0, 0, 0))  # Black background

    # Draw stars (parallax effect)
    for star in stars_far:
        star.update()
        star.draw(screen)
    for star in stars_near:
        star.update()
        star.draw(screen)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
        elif joystick and joystick.get_init() and event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # Assuming button 0 is the shoot button
                player.shoot()

    # Update
    all_sprites.update()

    # Check for collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        explosion_sound.play()
        score += 100
        if score >= HIGH_SCORE:
            player.lives += 1
            HIGH_SCORE += NEW_LIFE_THRESHOLD
        if len(enemies) == 0:
            # Advance to the next wave
            wave += 1
            positions = []
            for i in range(5 + wave):  # Increase number of enemies each wave
                if wave >= 10:
                    enemy_type = random.choices([1, 2, 3], weights=[3, 3, 4])[0]  # Introduce enemy_ship_3 starting from wave 10
                elif wave >= 5:
                    enemy_type = random.choices([1, 2], weights=[4, 6])[0]  # Introduce enemy_ship_2 starting from wave 5
                else:
                    enemy_type = 1

                # Ensure enemies do not overlap
                while True:
                    x = random.randint(0, SCREEN_WIDTH - 50)
                    y = random.randint(-100, -40)
                    overlap = False
                    for pos in positions:
                        if abs(x - pos[0]) < 50 and abs(y - pos[1]) < 50:
                            overlap = True
                            break
                    if not overlap:
                        positions.append((x, y))
                        break

                enemy = Enemy(x, y, enemy_type)
                enemy.shoot_chance = min(1 + wave, 15)  # Gradually increase shoot chance with each wave, starting slowly
                all_sprites.add(enemy)
                enemies.add(enemy)

    player_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    for hit in player_hits:
        hit_sound.play()
        player.lives -= 1
        if player.lives <= 0:
            game_over_sound.play()
            show_game_over()
            reset_game()

    # Draw
    all_sprites.draw(screen)

    # Draw player lives in the top right corner
    lives_label = font.render("Lives:", True, WHITE)
    lives_label_width = lives_label.get_width() + (player.lives * 35) + 20
    screen.blit(lives_label, (SCREEN_WIDTH - lives_label_width, 10))
    for i in range(player.lives):
        screen.blit(pygame.transform.scale(player_image, (28, 28)), (SCREEN_WIDTH - lives_label_width + lives_label.get_width() + 10 + i * 35, 10))

    # Draw score and wave
    score_text = font.render(f"Score: {score}", True, WHITE)
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(wave_text, (10, 50))

    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
