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
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

# Font
font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.width = 30
        self.height = 60
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.initial_position = (50, SCREEN_HEIGHT - 120)
        self.rect.x = self.initial_position[0]
        self.rect.y = self.initial_position[1]
        
        self.change_x = 0
        self.change_y = 0
        self.jumping = False
        self.score = 0
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.screen_shake = 0
        self.death_effect = 0
        
    def update(self):
        # Gravity
        self.change_y += 0.5
        
        # Di chuyển theo trục y
        old_y = self.rect.y
        self.rect.y += self.change_y
        
        # Giới hạn màn hình
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.jumping = False
            self.change_y = 0
            
        if self.rect.top < 0:
            self.rect.top = 0
            self.change_y = 0
                
        # Di chuyển theo trục x
        self.rect.x += self.change_x
        
        # Giới hạn màn hình
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Thời gian bất tử
        if self.invulnerable:
            self.invulnerable_timer += 1
            if self.invulnerable_timer > 60:
                self.invulnerable = False
                self.invulnerable_timer = 0

        if self.screen_shake > 0:
            self.screen_shake -= 1
        if self.death_effect > 0:
            self.death_effect -= 1
            
        return old_y

    def jump(self):
        if not self.jumping:
            self.change_y = -20  # Tăng lực nhảy
            self.jumping = True
    
    def go_left(self):
        self.change_x = -8  # Tăng tốc độ di chuyển
        
    def go_right(self):
        self.change_x = 8  # Tăng tốc độ di chuyển
        
    def stop(self):
        self.change_x = 0
        
    def die(self):
        if not self.invulnerable:
            self.lives -= 1
            self.rect.x = self.initial_position[0]
            self.rect.y = self.initial_position[1]
            self.invulnerable = True
            self.screen_shake = 30
            self.death_effect = 60
            if self.lives <= 0:
                return True
        return False
    
    def reset_position(self):
        self.rect.x = self.initial_position[0]
        self.rect.y = self.initial_position[1]
        self.change_x = 0
        self.change_y = 0

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([15, 15])
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_y = -10
        self.gravity = 0.5

    def update(self):
        self.change_y += self.gravity
        self.rect.y += self.change_y
        
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.change_y = 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_x = random.choice([-2, 2])  # Random direction
        self.change_y = random.choice([-2, 2])  # Random vertical movement

    def update(self):
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        
        # Đổi hướng khi chạm biên
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.change_x *= -1
        if self.rect.top < 80 or self.rect.bottom > SCREEN_HEIGHT:  # 80 là khoảng cách từ top
            self.change_y *= -1

class Game:
    def __init__(self):
        self.game_over = False
        self.current_level = 1
        self.max_levels = 3
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Lấy tên người chơi
        self.player_name = self.get_player_name()
        
        # Khởi tạo player
        self.player = Player(self.player_name)
        
        # Khởi tạo level đầu tiên
        self.setup_level(self.current_level)

    def generate_random_enemies(self):
        enemies = []
        num_enemies = self.current_level * 5  # Tăng số lượng enemy theo level
        
        safe_zone_x = 150  # Khoảng an toàn xung quanh player
        safe_zone_y = 80   # Khoảng cách từ top
        
        for _ in range(num_enemies):
            # Tạo vị trí ngẫu nhiên, tránh khu vực player spawn và top map
            while True:
                x = random.randint(0, SCREEN_WIDTH - 30)
                y = random.randint(safe_zone_y, SCREEN_HEIGHT - 30)
                
                # Kiểm tra khoảng an toàn quanh player
                if (x < self.player.initial_position[0] - safe_zone_x or 
                    x > self.player.initial_position[0] + safe_zone_x or
                    y < self.player.initial_position[1] - safe_zone_x or 
                    y > self.player.initial_position[1] + safe_zone_x):
                    enemies.append((x, y))
                    break
                
        return enemies

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

    def setup_level(self, level):
        score = self.player.score if hasattr(self, 'player') else 0
        lives = self.player.lives if hasattr(self, 'player') else 3
        
        # Xóa tất cả sprites
        self.all_sprites.empty()
        self.coins.empty()
        self.enemies.empty()
        
        # Reset player về vị trí ban đầu và cập nhật lại điểm số
        self.player.reset_position()
        self.player.score = score
        self.player.lives = lives
        self.all_sprites.add(self.player)
        
        # Tạo enemies mới
        enemy_positions = self.generate_random_enemies()
        for x, y in enemy_positions:
            e = Enemy(x, y)
            self.enemies.add(e)
            self.all_sprites.add(e)

    def spawn_coins(self, x, y, amount=3):
        for _ in range(amount):
            coin = Coin(x + random.randint(-20, 20), y)
            self.coins.add(coin)
            self.all_sprites.add(coin)

    def apply_screen_shake(self):
        if self.player.screen_shake > 0:
            offset = random.randint(-5, 5)
            screen.blit(screen.copy(), (offset, offset))

    def convert_enemy_to_coins(self, enemy):
        # Tạo 3 coins tại vị trí của enemy
        for _ in range(3):
            coin = Coin(enemy.rect.x + random.randint(-10, 10),
                       enemy.rect.y + random.randint(-10, 10))
            self.coins.add(coin)
            self.all_sprites.add(coin)
        enemy.kill()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
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
                old_y = self.player.update()
                self.all_sprites.update()
                
                # Thu thập coins
                for coin in self.coins:
                    if pygame.sprite.collide_rect(self.player, coin):
                        coin.kill()
                        self.player.score += 10
                
                # Xử lý va chạm với enemies
                for enemy in self.enemies:
                    if pygame.sprite.collide_rect(self.player, enemy):
                        # Kiểm tra nếu nhảy lên đầu enemy
                        if (old_y + self.player.rect.height <= enemy.rect.top + 10 and 
                            self.player.rect.bottom >= enemy.rect.top):
                            self.convert_enemy_to_coins(enemy)
                            self.player.change_y = -10  # Nảy lên
                        else:
                            # Va chạm từ các hướng khác
                            self.game_over = self.player.die()
                
                # Kiểm tra hoàn thành level
                if len(self.enemies) == 0:
                    if self.current_level < self.max_levels:
                        self.current_level += 1
                        self.setup_level(self.current_level)
                    else:
                        self.game_over = True
            
            # Vẽ
            if self.player.death_effect > 0:
                screen.fill(RED)
            else:
                screen.fill(WHITE)
                
            self.all_sprites.draw(screen)
            
            # Áp dụng hiệu ứng rung màn hình
            self.apply_screen_shake()
            
            # Hiển thị thông tin
            score_text = font.render(f'Score: {self.player.score}', True, BLACK)
            lives_text = font.render(f'Lives: {self.player.lives}', True, BLACK)
            level_text = font.render(f'Level: {self.current_level}', True, BLACK)
            name_text = font.render(f'Player: {self.player.name}', True, BLACK)
            
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (10, 50))
            screen.blit(level_text, (10, 90))
            screen.blit(name_text, (10, 130))
            
            if self.game_over:
                if self.current_level > self.max_levels:
                    end_text = 'You Win! Press R to play again'
                else:
                    end_text = 'Game Over! Press R to restart'
                game_over_text = font.render(end_text, True, BLACK)
                screen.blit(game_over_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()