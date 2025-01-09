import pygame
import random
import os
import sys
from pygame import mixer

# Khởi tạo pygame
pygame.init()
mixer.init()

# Thiết lập màn hình
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Advanced Mario')

# Màu sắc
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)

# Font
font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self, name, platforms_group):
        super().__init__()
        self.name = name
        self.width = 30
        self.height = 60
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 120
        
        # Reference to platforms group
        self.platforms = platforms_group
        
        # Physics
        self.change_x = 0
        self.change_y = 0
        self.jumping = False
        self.score = 0
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_timer = 0
        
    def update(self):
        # Gravity
        self.change_y += 0.8
        
        # Di chuyển theo trục y
        self.rect.y += self.change_y
        
        # Kiểm tra va chạm với platform
        platform_hit_list = pygame.sprite.spritecollide(self, self.platforms, False)
        for platform in platform_hit_list:
            if self.change_y > 0:
                self.rect.bottom = platform.rect.top
                self.change_y = 0
                self.jumping = False
            elif self.change_y < 0:
                self.rect.top = platform.rect.bottom
                self.change_y = 0
                
        # Di chuyển theo trục x
        self.rect.x += self.change_x
        
        # Giới hạn màn hình
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Xử lý thời gian bất tử
        if self.invulnerable:
            self.invulnerable_timer += 1
            if self.invulnerable_timer > 60:
                self.invulnerable = False
                self.invulnerable_timer = 0
                
        # Kiểm tra rơi xuống vực
        if self.rect.top > SCREEN_HEIGHT:
            self.die()

    def jump(self):
        if not self.jumping:
            self.change_y = -15
            self.jumping = True
    
    def go_left(self):
        self.change_x = -5
        
    def go_right(self):
        self.change_x = 5
        
    def stop(self):
        self.change_x = 0
        
    def die(self):
        if not self.invulnerable:
            self.lives -= 1
            self.rect.x = 50
            self.rect.y = SCREEN_HEIGHT - 120
            self.invulnerable = True
            if self.lives <= 0:
                return True
        return False

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([15, 15])
        self.image.fill((255, 215, 0))  # Gold color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_x = 2
        self.distance = 0
        self.max_distance = 100

    def update(self):
        self.rect.x += self.change_x
        self.distance += abs(self.change_x)
        if self.distance >= self.max_distance:
            self.change_x *= -1
            self.distance = 0

class Game:
    def __init__(self):
        self.game_over = False
        self.score = 0
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Lấy tên người chơi
        self.player_name = self.get_player_name()
        
        # Tạo player với tham chiếu đến platforms group
        self.player = Player(self.player_name, self.platforms)
        self.all_sprites.add(self.player)
        
        # Tạo nền
        ground = Platform(SCREEN_WIDTH, 60, 0, SCREEN_HEIGHT - 60)
        self.platforms.add(ground)
        self.all_sprites.add(ground)
        
        # Tạo các platform
        platform_positions = [
            (100, 20, 300, 400),
            (100, 20, 500, 300),
            (100, 20, 200, 200),
        ]
        
        for width, height, x, y in platform_positions:
            p = Platform(width, height, x, y)
            self.platforms.add(p)
            self.all_sprites.add(p)
        
        # Tạo coins
        for _ in range(10):
            coin = Coin(random.randint(0, SCREEN_WIDTH-15),
                       random.randint(100, SCREEN_HEIGHT-100))
            self.coins.add(coin)
            self.all_sprites.add(coin)
            
        # Tạo enemies
        enemy_positions = [
            (400, SCREEN_HEIGHT - 100),
            (200, 150),
        ]
        
        for x, y in enemy_positions:
            e = Enemy(x, y)
            self.enemies.add(e)
            self.all_sprites.add(e)

    def get_player_name(self):
        input_box = pygame.Rect(SCREEN_WIDTH//4, SCREEN_HEIGHT//2, SCREEN_WIDTH//2, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        done = False
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode
            
            screen.fill(WHITE)
            txt_surface = font.render('Enter your name:', True, BLACK)
            input_txt = font.render(text, True, color)
            screen.blit(txt_surface, (SCREEN_WIDTH//4, SCREEN_HEIGHT//2 - 50))
            screen.blit(input_txt, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(screen, color, input_box, 2)
            pygame.display.flip()
        
        return text if text else "Player"

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_LEFT:
                        self.player.go_left()
                    if event.key == pygame.K_RIGHT:
                        self.player.go_right()
                    if event.key == pygame.K_r and self.game_over:
                        self.__init__()
                        
                if event.type == pygame.KEYUP:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        self.player.stop()
            
            if not self.game_over:
                # Update
                self.all_sprites.update()
                
                # Kiểm tra va chạm với coins
                coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
                for coin in coin_hits:
                    self.player.score += 10
                
                # Kiểm tra va chạm với enemies
                if not self.player.invulnerable:
                    enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
                    if enemy_hits:
                        self.game_over = self.player.die()
            
            # Vẽ
            screen.fill(WHITE)
            self.all_sprites.draw(screen)
            
            # Hiển thị điểm và mạng
            score_text = font.render(f'Score: {self.player.score}', True, BLACK)
            lives_text = font.render(f'Lives: {self.player.lives}', True, BLACK)
            name_text = font.render(f'Player: {self.player.name}', True, BLACK)
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (10, 50))
            screen.blit(name_text, (10, 90))
            
            if self.game_over:
                game_over_text = font.render('Game Over! Press R to restart', True, BLACK)
                screen.blit(game_over_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()