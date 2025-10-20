import random
from pygame import Rect
import pgzrun

TITLE = "Platformer Adventure"
WIDTH, HEIGHT = 800, 600

GRAVITY = 0.8
JUMP_FORCE = -15
MENU, PLAYING, GAME_OVER = 0, 1, 2
music_volume = 0.5
music_enabled = True
sounds_enabled = True

HERO_IDLE = ['hero/hero_idle1', 'hero/hero_idle2', 'hero/hero_idle3', 'hero/hero_idle4']
HERO_WALK = ['hero/walk1', 'hero/walk2', 'hero/walk3', 'hero/walk4']
ENEMY_TYPES = [['enemies/enemy1_1', 'enemies/enemy1_2'], ['enemies/enemy2_1', 'enemies/enemy2_2']]
COYOTE_FRAMES = 6
JUMP_BUFFER_FRAMES = 6

class Hero:
    def __init__(self):
        self.reset()
        self.speed = 5
        self.animation_speed = 0.12

    def reset(self):
        self.x, self.y = 100, 200
        self.vel_x = self.vel_y = 0
        self.on_ground = False
        self.width, self.height = 50, 70
        self.coyote_timer = self.jump_buffer = 0
        self.idle_counter = self.walk_counter = 0.0
        self.facing_right = True
        self.is_jumping = False

    def update(self, platforms):
        self.vel_y += GRAVITY
        new_x = self.x + self.vel_x
        hero_rect = Rect(new_x, self.y, self.width, self.height)
        for p in platforms:
            if hero_rect.colliderect(p):
                new_x = p.left - self.width if self.vel_x > 0 else p.right
                break
        self.x = new_x

        new_y = self.y + self.vel_y
        hero_rect = Rect(self.x, new_y, self.width, self.height)
        self.on_ground = False
        for p in platforms:
            if hero_rect.colliderect(p):
                if self.vel_y > 0 and hero_rect.bottom > p.top and hero_rect.top < p.top:
                    new_y = p.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.vel_y < 0 and hero_rect.top < p.bottom:
                    new_y = p.bottom
                    self.vel_y = 0
                break
        self.y = new_y

        self.x = max(0, min(self.x, WIDTH - self.width))
        if self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True
            self.is_jumping = False

        if self.on_ground:
            self.coyote_timer = COYOTE_FRAMES
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        self.idle_counter += self.animation_speed if self.vel_x == 0 else 0
        self.walk_counter += self.animation_speed if self.vel_x != 0 else 0
        self.facing_right = self.vel_x > 0 if self.vel_x != 0 else self.facing_right

    def try_jump(self):
        if (self.on_ground or self.coyote_timer > 0) and not self.is_jumping:
            self.vel_y = JUMP_FORCE
            self.is_jumping = True
            self.on_ground = False
            self.coyote_timer = self.jump_buffer = 0
            self.play_sound('jump')
            return True
        return False

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        frames = HERO_IDLE if self.vel_x == 0 else HERO_WALK
        counter = self.idle_counter if self.vel_x == 0 else self.walk_counter
        frame = int(counter) % len(frames)
        try:
            actor = Actor(frames[frame])
            actor.pos = (self.x + self.width // 2, self.y + self.height)
            actor.flip_x = not self.facing_right
            actor.draw()
        except:
            screen.draw.filled_rect(self.get_rect(), (0, 100, 200))

    def play_sound(self, sound_name):
        if sounds_enabled:
            getattr(sounds, sound_name).play()

class Enemy:
    def __init__(self, x, y, patrol_distance=100):
        self.x = self.start_x = x
        self.y = y
        self.patrol_distance = patrol_distance
        self.speed = 2
        self.direction = 1
        self.width = self.height = 50
        self.animation_counter = 0.0
        self.animation_speed = 0.12
        self.type = random.randint(0, len(ENEMY_TYPES) - 1)

    def update(self):
        self.x += self.speed * self.direction
        if self.x > self.start_x + self.patrol_distance:
            self.direction = -1
        elif self.x < self.start_x - self.patrol_distance:
            self.direction = 1
        self.animation_counter += self.animation_speed

    def get_rect(self):
        shrink = 0.7
        w, h = self.width * shrink, self.height * shrink
        return Rect(self.x + (self.width - w)/2, self.y + (self.height - h)/2, w, h)

    def draw(self):
        frames = ENEMY_TYPES[self.type]
        frame = int(self.animation_counter) % len(frames)
        try:
            actor = Actor(frames[frame])
            actor.pos = (self.x + self.width // 2, self.y + self.height)
            actor.flip_x = self.direction < 0
            actor.draw()
        except:
            screen.draw.filled_circle((self.x + self.width//2, self.y + self.height//2), self.width//2, (200, 50, 50))

class Button:
    def __init__(self, x, y, w, h, text, color=(100,100,200), hover=(120,120,220)):
        self.rect = Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover
        self.is_hovered = False

    def draw(self):
        c = self.hover_color if self.is_hovered else self.color
        screen.draw.filled_rect(self.rect, c)
        screen.draw.text(self.text, center=self.rect.center, color=(255,255,255), fontsize=24)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

game_state = MENU
hero = Hero()
enemies = []
platforms = []
keys_pressed = set()

def create_level():
    global platforms
    platforms = [Rect(0,500,300,20), Rect(450,500,350,20), Rect(350,400,200,20), Rect(100,350,150,20)]

def spawn_enemies():
    global enemies
    enemies = []
    for p, d in [(platforms[2],40), (platforms[3],30)]:
        x = p.centerx - 25
        y = p.top - 50
        enemies.append(Enemy(x, y, d))

def reset_game():
    keys_pressed.clear()
    create_level()
    hero.reset()
    spawn_enemies()

start_button = Button(WIDTH//2-100, HEIGHT//2-50, 200, 50, "Start Game")
music_button = Button(WIDTH//2-100, HEIGHT//2+20, 200, 50, "Music ON")
exit_button = Button(WIDTH//2-100, HEIGHT//2+90, 200, 50, "Exit")

def init_music():
    if music_enabled:
        music.play('theme')
        music.set_volume(music_volume)

def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        music.play('theme')
        music.set_volume(music_volume)
        music_button.text = "Music ON"
    else:
        music.stop()
        music_button.text = "Music OFF"

def draw():
    screen.clear()
    screen.fill((50,120,180))
    if game_state == MENU:
        screen.draw.text("PLATFORMER ADVENTURE", center=(WIDTH//2, HEIGHT//4), color=(255,255,255), fontsize=48)
        start_button.draw()
        music_button.draw()
        exit_button.draw()
    elif game_state == PLAYING:
        for p in platforms:
            screen.draw.filled_rect(p, (100,70,40))
        hero.draw()
        for e in enemies:
            e.draw()
    elif game_state == GAME_OVER:
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//3), color=(255,50,50), fontsize=64)
        screen.draw.text("Click to return to menu", center=(WIDTH//2, HEIGHT//2), color=(255,255,255), fontsize=32)

def update():
    global game_state
    if game_state == PLAYING:
        hero.vel_x = 0
        if 'left' in keys_pressed:
            hero.vel_x = -hero.speed
        if 'right' in keys_pressed:
            hero.vel_x = hero.speed
        hero.update(platforms)
        if hero.jump_buffer > 0:
            hero.try_jump()
        for e in enemies:
            e.update()
            if hero.get_rect().colliderect(e.get_rect()):
                hero.play_sound('hit')
                game_state = GAME_OVER

def on_mouse_move(pos):
    if game_state == MENU:
        start_button.check_hover(pos)
        music_button.check_hover(pos)
        exit_button.check_hover(pos)

def on_mouse_down(pos):
    global game_state
    if game_state == MENU:
        if start_button.is_clicked(pos, True):
            reset_game()
            game_state = PLAYING
        elif music_button.is_clicked(pos, True):
            toggle_music()
        elif exit_button.is_clicked(pos, True):
            import sys; sys.exit()
    elif game_state == GAME_OVER:
        game_state = MENU

def on_key_down(key):
    if game_state == PLAYING:
        if key == keys.LEFT:
            keys_pressed.add('left')
        elif key == keys.RIGHT:
            keys_pressed.add('right')
        elif key == keys.UP:
            hero.jump_buffer = JUMP_BUFFER_FRAMES

def on_key_up(key):
    if game_state == PLAYING:
        if key == keys.LEFT:
            keys_pressed.discard('left')
        elif key == keys.RIGHT:
            keys_pressed.discard('right')

init_music()
reset_game()
pgzrun.go()
