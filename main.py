import pgzrun
import math
import random
from pygame import Rect

# 🎨 ALTERE AQUI as configurações básicas do jogo
TITLE = "Platformer Adventure"
WIDTH = 800
HEIGHT = 600
GRAVITY = 0.8
JUMP_FORCE = -15

# Estados do jogo
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Configurações de áudio
music_volume = 0.5
sound_volume = 0.7
music_enabled = True
sounds_enabled = True

# 🎨 ALTERE AQUI os arquivos de sprites do herói
hero_idle_images = ['hero/idle1', 'hero/idle2']
hero_walk_images = ['hero/walk1', 'hero/walk2', 'hero/walk3', 'hero/walk4']

# 🎨 ALTERE AQUI os arquivos de sprites dos inimigos
enemy_images = [
    ['enemies/enemy1_1', 'enemies/enemy1_2'],
    ['enemies/enemy2_1', 'enemies/enemy2_2']
]

class Hero:
    def __init__(self):
        self.reset()
        # ⚙️ ALTERE AQUI a velocidade de movimento do herói
        self.speed = 5
        self.animation_speed = 0.2
        self.idle_counter = 0
        self.walk_counter = 0
        self.facing_right = True
        
    def reset(self):
        # ⚙️ ALTERE AQUI a posição inicial do herói
        self.x = 100
        self.y = 300
        self.vel_x = 0
        self.vel_y = 0
        self.is_jumping = False
        self.on_ground = False
        self.width = 50
        self.height = 70
        
    def update(self, platforms):
        # Aplicar gravidade
        self.vel_y += GRAVITY
        
        # Movimento horizontal
        self.x += self.vel_x
        
        # Verificar colisões horizontais
        hero_rect = self.get_rect()
        for platform in platforms:
            if hero_rect.colliderect(platform):
                if self.vel_x > 0:  # Movendo para direita
                    self.x = platform.left - self.width
                elif self.vel_x < 0:  # Movendo para esquerda
                    self.x = platform.right
                break
        
        # Movimento vertical
        self.y += self.vel_y
        self.on_ground = False
        
        # Verificar colisões verticais
        hero_rect = self.get_rect()
        for platform in platforms:
            if hero_rect.colliderect(platform):
                if self.vel_y > 0:  # Caindo
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.vel_y < 0:  # Pulando
                    self.y = platform.bottom
                    self.vel_y = 0
                break
        
        # Limitar movimento vertical
        if self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True
            self.is_jumping = False
            
        # Limitar movimento horizontal
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
            
        # Atualizar animações
        if self.vel_x == 0:
            self.idle_counter += self.animation_speed
        else:
            self.walk_counter += self.animation_speed
            
        if self.vel_x > 0:
            self.facing_right = True
        elif self.vel_x < 0:
            self.facing_right = False
    
    def jump(self):
        if self.on_ground and not self.is_jumping:
            self.vel_y = JUMP_FORCE
            self.is_jumping = True
            self.on_ground = False
            if sounds_enabled:
                try:
                    sounds.jump.play()
                except:
                    print("🔇 Arquivo jump.wav não encontrado")

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)
    
    def draw(self):
        # Selecionar animação baseada no estado
        if self.vel_x == 0:  # Idle
            frame = int(self.idle_counter) % len(hero_idle_images)
            image_name = hero_idle_images[frame]
        else:  # Walking
            frame = int(self.walk_counter) % len(hero_walk_images)
            image_name = hero_walk_images[frame]
        
        # 🔧 CORREÇÃO: Carregar a imagem primeiro
        try:
            image = Actor(image_name)
            image.pos = (self.x + self.width//2, self.y + self.height//2)
            
            # Desenhar com direção correta
            if not self.facing_right:
                image.flip_x = True
            image.draw()
        except:
            # Fallback: desenhar retângulo se imagem não carregar
            screen.draw.filled_rect(self.get_rect(), (0, 100, 200))
            # Olhos para mostrar direção
            eye_x = self.x + 35 if self.facing_right else self.x + 15
            screen.draw.filled_circle((eye_x, self.y + 20), 5, (255, 255, 255))

class Enemy:
    def __init__(self, x, y, patrol_distance=100):
        self.x = x
        self.y = y
        self.start_x = x
        self.patrol_distance = patrol_distance
        # ⚙️ ALTERE AQUI a velocidade dos inimigos
        self.speed = 2
        self.direction = 1
        self.width = 50
        self.height = 50
        self.animation_counter = 0
        self.animation_speed = 0.1
        self.type = random.randint(0, len(enemy_images) - 1)
        
    def update(self):
        # Movimento de patrulha
        self.x += self.speed * self.direction
        
        # Verificar limites de patrulha
        if self.x > self.start_x + self.patrol_distance:
            self.direction = -1
        elif self.x < self.start_x - self.patrol_distance:
            self.direction = 1
            
        # Atualizar animação
        self.animation_counter += self.animation_speed
    
    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)
    
    def draw(self):
        frame = int(self.animation_counter) % len(enemy_images[self.type])
        image_name = enemy_images[self.type][frame]
        
        try:
            image = Actor(image_name)
            image.pos = (self.x + self.width//2, self.y + self.height//2)
            
            # Inverter sprite baseado na direção
            if self.direction < 0:
                image.flip_x = True
            image.draw()
        except:
            # Fallback: desenhar círculo se imagem não carregar
            center = (self.x + self.width//2, self.y + self.height//2)
            screen.draw.filled_circle(center, self.width//2, (200, 50, 50))

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 200), hover_color=(120, 120, 220)):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        screen.draw.filled_rect(self.rect, color)
        screen.draw.text(self.text, center=self.rect.center, color=(255, 255, 255), fontsize=24)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Inicialização do jogo
game_state = MENU
hero = Hero()
enemies = []
platforms = []

# 🎨 ALTERE AQUI as plataformas do nível
def create_level():
    global platforms
    platforms = [
        Rect(0, 400, 300, 20),
        Rect(400, 400, 400, 20),
        Rect(200, 300, 200, 20),
        Rect(500, 250, 150, 20),
        Rect(100, 200, 150, 20)
    ]

def spawn_enemies():
    global enemies
    enemies = [
        # ⚙️ ALTERE AQUI a posição e área de patrulha dos inimigos
        Enemy(150, 330, 80),
        Enemy(450, 330, 100),
        Enemy(300, 180, 60)
    ]

def reset_game():
    hero.reset()
    spawn_enemies()
    create_level()

# Botões do menu
start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Start Game")
music_button = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Music ON")
exit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 90, 200, 50, "Exit")

# 🔈 ALTERE AQUI o volume da música
def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        try:
            music.play('theme')
            music.set_volume(music_volume)
            music_button.text = "Music ON"
        except:
            print("🔇 Arquivo theme.ogg não encontrado")
            music_enabled = False
            music_button.text = "Music OFF"
    else:
        music.stop()
        music_button.text = "Music OFF"

def update():
    global game_state
    
    if game_state == PLAYING:
        hero.update(platforms)
        
        for enemy in enemies:
            enemy.update()
            
            # Verificar colisão com inimigos
            if hero.get_rect().colliderect(enemy.get_rect()):
                if sounds_enabled:
                    try:
                        sounds.hit.play()
                    except:
                        print("🔇 Arquivo hit.wav não encontrado")
                game_state = GAME_OVER

def draw():
    screen.clear()
    screen.fill((50, 120, 180))  # Cor de fundo azul
    
    if game_state == MENU:
        screen.draw.text("PLATFORMER ADVENTURE", center=(WIDTH//2, HEIGHT//4), 
                        color=(255, 255, 255), fontsize=48)
        start_button.draw()
        music_button.draw()
        exit_button.draw()
        
    elif game_state == PLAYING:
        # Desenhar plataformas
        for platform in platforms:
            screen.draw.filled_rect(platform, (100, 70, 40))
        
        # Desenhar personagens
        hero.draw()
        for enemy in enemies:
            enemy.draw()
            
    elif game_state == GAME_OVER:
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//3), 
                        color=(255, 50, 50), fontsize=64)
        screen.draw.text("Click to return to menu", center=(WIDTH//2, HEIGHT//2), 
                        color=(255, 255, 255), fontsize=32)

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
            exit()
    
    elif game_state == GAME_OVER:
        game_state = MENU

def on_key_down(key):
    if game_state == PLAYING:
        if key in (keys.LEFT, keys.A):
            hero.vel_x = -hero.speed
        elif key in (keys.RIGHT, keys.D):
            hero.vel_x = hero.speed
        elif key == keys.SPACE:
            hero.jump()

def on_key_up(key):
    if game_state == PLAYING:
        if key in (keys.LEFT, keys.A, keys.RIGHT, keys.D):
            hero.vel_x = 0

# Iniciar música apenas se habilitada
if music_enabled:
    toggle_music()

# Iniciar o jogo
pgzrun.go()