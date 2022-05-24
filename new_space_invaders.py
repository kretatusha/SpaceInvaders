import pygame, sys
import pickle
import os.path
from menu.usertable import UserTable
from menu.userdata import UserData
from menu.inputbox import InputBox
from objects.Player import Player
from objects import obstacle
from objects.Alien import Alien, Extra
from random import choice, randint
from objects.laser import Laser
from menu.button import Button


class Game:
    def __init__(self, table=UserTable('data/table.txt'), name='Player', game_cycle=True, WIDTH=600, HEIGHT=600,
                 lives=3, current_level=1, kol_aliens_x=2, kol_aliens_y=2,
                 current_velocity_alien=1,
                 current_score=0):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        # установка игрока
        player_sprite = Player((self.WIDTH / 2, self.HEIGHT), self.WIDTH, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)
        self.lost = False

        # установка здоровья и очков
        self.name = name
        self.table = table
        self.lives = lives
        self.level = current_level
        self.lives_surf = pygame.image.load('graphics/player.png')
        self.live_x_start_pos = WIDTH - (self.lives_surf.get_size()[0] * 2 + 20)
        self.score = current_score
        self.font = pygame.font.Font('font/Pixeled.ttf', 20)
        self.game_cycle = game_cycle
        # установка укрытий
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (WIDTH / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(WIDTH / 15, 480, *self.obstacle_x_positions)

        # установка чужих
        self.aliens = pygame.sprite.Group()
        self.kol_aliens_x = kol_aliens_x
        self.kol_aliens_y = kol_aliens_y
        self.alien_setup(self.kol_aliens_x, self.kol_aliens_y)
        self.aliens_velocity = current_velocity_alien
        self.alien_direction = current_velocity_alien
        self.alien_lasers = pygame.sprite.Group()

        # extra
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400, 800)

        # audio
        self.music = pygame.mixer.Sound('audio/music.wav')
        self.music.set_volume(0.2)
        self.music.play(loops=-1)
        self.laser_sound = pygame.mixer.Sound('audio/laser.wav')
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
        self.explosion_sound.set_volume(0.3)

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size, (241, 79, 80), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, x_start, y_start, *offset):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_offset=70, y_offset=100, x_distance=60, y_distance=40):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0:
                    alien_sprite = Alien('yellow', x, y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien('green', x, y)
                else:
                    alien_sprite = Alien('red', x, y)
                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= WIDTH:
                self.alien_direction = -self.aliens_velocity
                self.alien_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = self.aliens_velocity
                self.alien_move_down(2)

    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(HEIGHT, random_alien.rect.center, 6)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['right', 'left']), WIDTH))
            self.extra_spawn_time = randint(400, 800)

    def collision_checks(self):
        # лазеры игрока
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle коллизия
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                # alien
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()
                # extra
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    laser.kill()
                    self.score += 500

        # лазеры чужого
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle коллизия
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                    # alien коллизия
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, False):
                    self.lives -= 1

    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.lives_surf.get_size()[0] + 10))
            screen.blit(self.lives_surf, (x, 8))

    def display_score_and_name(self):
        score_surf = self.font.render(f'score:{self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft=(10, -10))
        screen.blit(score_surf, score_rect)
        name_surf = self.font.render(self.name, False, 'white')
        name_rect = score_surf.get_rect(topleft=(10, 50))
        screen.blit(name_surf, name_rect)

    def next_level(self):
        level_surf = self.font.render(f'level:{self.level}', False, 'white')
        level_rect = level_surf.get_rect(topleft=(10, 20))
        screen.blit(level_surf, level_rect)
        if not self.aliens.sprites():
            if self.level == 2:
                self.gameover(f'You won! Your score:{self.score} Enter - restart')
            else:
                self.level += 1
                self.aliens = pygame.sprite.Group()
                self.kol_aliens_x += 2
                self.kol_aliens_y += 3
                self.alien_setup(self.kol_aliens_x, self.kol_aliens_y)
                self.aliens_velocity += 1
                self.alien_direction = self.aliens_velocity
                self.alien_lasers = pygame.sprite.Group()

    def save_results(self):
        self.table.table.append(UserData(f'{self.name},{self.score},{self.level}'))
        self.table.sort()
        self.table.write()

    def check_lives(self):
        if self.lives <= 0:
            self.gameover(f'Your score:{self.score} Enter - restart')

    def gameover(self, text):
        over = True
        self.lost = True
        self.music.stop()
        self.save_results()
        self.save_data()
        while over:
            win_surf = self.font.render(text, False, 'white')
            win_rect = win_surf.get_rect(center=(self.WIDTH / 2, self.HEIGHT / 2))
            screen.blit(win_surf, win_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                over = False
                self.__init__(name = self.name, table = self.table, game_cycle = self.game_cycle)
            if keys[pygame.K_ESCAPE]:
                over = False
                self.game_cycle = False
                screen.fill((30, 30, 30))
                pygame.display.flip()

    def pause(self):
        keys = pygame.key.get_pressed()
        paused = False
        if keys[pygame.K_LALT]:
            paused = True
        while paused:
            self.music.stop()
            keys = pygame.key.get_pressed()
            win_surf = self.font.render('Enter - continue, ESC - exit', False, 'white')
            win_rect = win_surf.get_rect(center=(self.WIDTH / 2, self.HEIGHT / 2))
            screen.blit(win_surf, win_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_data()
                    pygame.quit()
                    sys.exit()
            if keys[pygame.K_RETURN]:
                paused = False
                self.music.play(loops=-1)
            pygame.display.update()
            if keys[pygame.K_ESCAPE]:
                self.save_data()
                paused = False
                self.game_cycle = False
                screen.fill((30, 30, 30))
                pygame.display.flip()

    def save_data(self):
        with open('data/data.pickle', 'wb') as f:
            data = {'name': self.name, 'lives': self.lives, 'current_level': self.level,
                    'kol_aliens_x': self.kol_aliens_x,
                    'kol_aliens_y': self.kol_aliens_y, 'current_velocity_alien': self.aliens_velocity,
                    'score': self.score, 'lost': self.lost}
            pickle.dump(data, f)

    def run(self):
        self.player.update()
        self.aliens.update(self.alien_direction)
        self.extra.update()
        self.alien_lasers.update()

        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.alien_lasers.draw(screen)
        self.aliens.draw(screen)
        self.extra.draw(screen)

        self.next_level()
        self.alien_position_checker()
        self.display_lives()
        self.display_score_and_name()
        self.collision_checks()
        self.extra_alien_timer()
        self.check_lives()
        self.pause()


def main_menu():
    screen.fill((30, 30, 30))
    pygame.display.flip()
    button_start = Button(150, 100)
    button_load = Button(150, 100)
    button_res = Button(150, 100)
    run = True
    input_box1 = InputBox(100, 100, 140, 32)
    while run:
        button_start.draw(50, 50, "Start", screen, input_text)
        button_load.draw(50, 250, "Load", screen, load_game)
        button_res.draw(50, 450, "Res", screen, check_results)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    pygame.quit()
    sys.exit()


def load_game():
    if os.path.exists('data/data.pickle'):
        with open('data/data.pickle', 'rb') as f:
            data = pickle.load(f)
            if data['lost']:
                input_text()
            else:
                main('ddd', data)
    else:
        input_text()


def check_results():
    pygame.init()
    button_load = Button(150, 100)
    run = True
    input_box1 = InputBox(100, 100, 140, 32)

    table = UserTable('data/table.txt')
    while run:
        button_load.draw(250, 450, "Return", screen, main_menu)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        i = 0
        while i < table.COUNT:
            user = table.table[i]
            if table.table[i].name == '':
                break
            win_surf = font.render(f'{table.table[i].name},{table.table[i].score},{table.table[i].level}', False,
                                   'white')
            win_rect = win_surf.get_rect(center=(WIDTH / 2, 10 + i * 40))
            screen.blit(win_surf, win_rect)
            i += 1
        pygame.display.update()
        screen.fill((30, 30, 30))
    pygame.quit()
    sys.exit()


def input_text():
    run = True
    input_box1 = InputBox(150, 250, 140, 32)
    while input_box1.go:
        keys = pygame.key.get_pressed()
        win_surf = font.render('Type your name,than press enter', False, 'white')
        win_rect = win_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(win_surf, win_rect)
        win_surf = font.render('ESC - return', False, 'white')
        win_rect = win_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 40))
        screen.blit(win_surf, win_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                input_box1.go = False
                sys.exit()
            input_box1.handle_event(event)
        if keys[pygame.K_ESCAPE]:
            input_box1.go = False
            main_menu()
        input_box1.update()
        input_box1.draw(screen)
        pygame.display.update()
        screen.fill((30, 30, 30))
    if input_box1.text == '':
        main('Player')
    else:
        main(input_box1.text)


def main(name, data=None):
    clock = pygame.time.Clock()
    game_cycle = True
    if data is None:
        game = Game(name=name, game_cycle=game_cycle, WIDTH=WIDTH, HEIGHT=HEIGHT)
    else:
        game = Game(name=data['name'], game_cycle=game_cycle, WIDTH=WIDTH, HEIGHT=HEIGHT, lives=data['lives'],
                    current_level=data['current_level'], kol_aliens_x=data['kol_aliens_x'],
                    kol_aliens_y=data['kol_aliens_y'],
                    current_velocity_alien=data['current_velocity_alien'], current_score=data['score'])

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    while game.game_cycle:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.save_data()
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()
        screen.fill((30, 30, 30))
        game.run()

        pygame.display.flip()
        clock.tick(60)
    main_menu()


if __name__ == '__main__':
    pygame.init()
    infoObject = pygame.display.Info()
    WIDTH, HEIGHT = 600, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SPACE INVADERS")
    font = pygame.font.Font('font/Pixeled.ttf', 20)
    main_menu()
