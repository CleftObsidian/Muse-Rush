import pygame
from pygame.locals import *
import os
import time
import random

TITLE = "Muse Rush"                                             # default setting
WIDTH = 1280
HEIGHT = 720
FPS = 60
DEFAULT_FONT = "Excludeditalic-jEr99.ttf"

WHITE = (255, 255, 255)                                         # color setting
BLACK = (32, 36, 32)
RED = (246, 36, 74)
BLUE = (32, 105, 246)
ALPHA_MAX = 255     # do not change (fix 255)

class MuseRush:
    def __init__(self):                                         # Game Start
        pygame.init()
        pygame.mixer.init()                                     # sound mixer
        pygame.display.set_caption(TITLE)                       # title name
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # screen size
        self.screen_mode = 0        # screen mode (0: logo1, 1: logo2, 2: main, 3: stage select, 4: play, 5: score)
        self.screen_value = [-ALPHA_MAX, 0, 0, 0]               # screen management value
        self.clock = pygame.time.Clock()                        # FPS timer
        self.start_tick = 0                                     # game timer
        self.running = True                                     # game initialize boolean value
        self.language_mode = 0                                  # 0: english
        self.song_select = 1                                    # select song
        self.load_data()                                        # data loading
        self.new()
        pygame.mixer.music.load(self.bg_main)                   # bgm

    def load_data(self):                                        #Data Loading
        self.dir = os.path.dirname(__file__)

        # font
        self.font_dir = os.path.join(self.dir, "font")
        self.gameFont = os.path.join(self.font_dir, DEFAULT_FONT)

        with open(os.path.join(self.font_dir, "language.ini"), 'r', encoding="UTF-8") as language_file:
            language_lists = language_file.read().split('\n')

        self.language_list = [n.split('_') for n in language_lists]

        # image
        self.image_dir = os.path.join(self.dir, "image")
        pygame.display.set_icon(pygame.image.load(os.path.join(self.image_dir, "icon.png")))    # set icon
        self.spr_powered= pygame.image.load(os.path.join(self.image_dir, "powered.png"))
        self.spr_logoback = pygame.image.load(os.path.join(self.image_dir, "logoback.png"))
        self.spr_logo = pygame.image.load(os.path.join(self.image_dir, "logo.png"))
        self.spr_enemy1 = pygame.image.load(os.path.join(self.image_dir, "enemy1.png"))
        self.spr_enemy2 = pygame.image.load(os.path.join(self.image_dir, "enemy2.png"))
        self.spr_enemy3 = pygame.image.load(os.path.join(self.image_dir, "enemy3.png"))
        self.spr_playerIdle = pygame.image.load(os.path.join(self.image_dir, "playerIdle.png"))
        self.spr_playerAttack = pygame.image.load(os.path.join(self.image_dir, "playerattack.png"))
        self.spr_playerAttackUp = pygame.image.load(os.path.join(self.image_dir, "playerattackup.png"))
        self.spr_playerAttackDown = pygame.image.load(os.path.join(self.image_dir, "playerattackdown.png"))
        self.spr_target = pygame.image.load(os.path.join(self.image_dir, "target.png"))
        self.spr_background = pygame.image.load(os.path.join(self.image_dir, "background.png"))
        self.rolling_bg = BackGround(self)

        # sound
        self.sound_dir = os.path.join(self.dir, "sound")
        self.bg_main = os.path.join(self.sound_dir, "bg_main.wav")
        self.sound_click = pygame.mixer.Sound(os.path.join(self.sound_dir, "click.wav"))
        self.sound_hit = pygame.mixer.Sound(os.path.join(self.sound_dir, "hit.wav"))
        self.sound_miss = pygame.mixer.Sound(os.path.join(self.sound_dir, "miss.wav"))
        self.sound_damage = pygame.mixer.Sound(os.path.join(self.sound_dir, "damage.wav"))

        # song
        self.song_dir = os.path.join(self.dir, "song")
        music_type = ["ogg", "mp3", "wav"]
        song_lists = [i for i in os.listdir(self.song_dir) if i.split('.')[-1] in music_type]
        self.song_list = list()                                 # song name list
        self.song_path = list()                                 # song path list

        for song in song_lists:
            try:
                pygame.mixer.music.load(os.path.join(self.song_dir, song))
                self.song_list.append(song.split('.')[0])
                self.song_path.append(os.path.join(self.song_dir, song))
            except:
                print("error: " + str(song) + "is unsupported format music file")

        self.song_num = len(self.song_list)                     # available song number
        self.song_dataPath = list()                             # song data file path list
        self.song_highScore = list()                            # song highscore list
        self.song_perfectScore = list()                         # song maxscore list

        for song in self.song_list:
            song_dataCoord = os.path.join(self.song_dir, song + ".ini")

            try:
                with open(song_dataCoord, 'r', encoding="UTF-8") as song_file:
                    song_scoreList = song_file.read().split('\n')[0]

                self.song_highScore.append(int(song_scoreList.split(':')[1]))
                self.song_perfectScore.append(int(song_scoreList.split(':')[2]))
                self.song_dataPath.append(song_dataCoord)
            except:
                print("error: " + str(song) + "'s song data file is damaged or does not exist.")
                self.song_highScore.append(-1)
                self.song_perfectScore.append(-1)
                self.song_dataPath.append(-1)

    def new(self):                                              # Game Initialize
        self.song_data = list()                                 # song data list
        self.song_dataLength = 0                                # song data length
        self.song_dataIndex = 0                                 # song data index
        self.score = 0                                          # current game score
        self.all_sprites = pygame.sprite.Group()                # sprite group
        self.enemys = pygame.sprite.Group()
        self.player = Player(self)

    def run(self):                                              # Game Loop
        self.playing = True

        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            pygame.display.flip()

        pygame.mixer.music.fadeout(600)

    def update(self):                                           # Game Loop - Update
        self.all_sprites.update()                               # screen update
        self.game_tick = pygame.time.get_ticks() - self.start_tick      # play time calculation
        self.rolling_bg.update()

    def events(self):                                           # Game Loop - Events
        mouse_coord = pygame.mouse.get_pos()                    # mouse coord value
        mouse_move = False                                      # mouse move boolean value
        mouse_click = 0                                         # mouse click value
        key_click = 0                                           # key value

        for event in pygame.event.get():                        # Event Check
            if event.type == pygame.QUIT:                       # exit
                if self.playing:
                    self.playing = False
                    self.running = False
            elif event.type == pygame.KEYDOWN:                  # keyboard check
                key_click = event.key

                if self.screen_mode < 4:
                    self.sound_click.play()
            elif event.type == pygame.MOUSEMOTION:
                if event.rel[0] != 0 or event.rel[1] != 0:      # mouse move
                    mouse_move = True
            elif event.type == pygame.MOUSEBUTTONDOWN:          # mouse click
                mouse_click = event.button

                if self.screen_mode < 4:
                    self.sound_click.play()

        if self.screen_mode == 0:                               # Logo Screen1
            self.screen_value[0] += ALPHA_MAX / 51

            if self.screen_value[0] == ALPHA_MAX:
                self.screen_value[0] = 0
                self.screen_mode = 1
                pygame.mixer.music.play(loops=-1)
        elif self.screen_mode == 1:                             # Logo Screen2
            if self.screen_value[3] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 51
                else:
                    if mouse_click == 1 or key_click != 0:
                        self.screen_value[3] = 1
            else:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 15
                else:
                    self.screen_mode = 2
                    self.screen_value[1] = 2
                    self.screen_value[2] = 0
                    self.screen_value[3] = 0

            if self.screen_value[1] > -10:
                self.screen_value[1] -= 1
            else:
                if self.screen_value[2] == 0:
                    self.screen_value[1] = random.randrange(0, 10)
                    self.screen_value[2] = random.randrange(5, 30)
                else:
                    self.screen_value[2] -= 1
        elif self.screen_mode == 2:                             # Main Screen
            if self.screen_value[2] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 15

                    if self.screen_value[3] > 0:
                        self.screen_value[3] -= ALPHA_MAX / 15
                else:
                    for i in range(4):
                        # mouse cursor check
                        if mouse_move and (WIDTH / 4 * 3 - 150) < mouse_coord[0] < (WIDTH / 4 * 3 + 150)\
                                and 150 + (i * 100) < mouse_coord[1] < 220 + (i * 100):
                            self.screen_value[1] = i + 1

                    if (key_click == pygame.K_UP or mouse_click == 4) and self.screen_value[1] > 1:     # key up check
                        self.screen_value[1] -= 1
                    elif (key_click == pygame.K_DOWN or mouse_click == 5) and self.screen_value[1] < 4: # key down check
                        self.screen_value[1] += 1

                    # key enter, key right check
                    if mouse_click == 1 or key_click == pygame.K_RETURN or key_click == pygame.K_RIGHT:
                        if self.screen_value[1] == 1:           # START
                            self.screen_value[2] = 1
                        elif self.screen_value[1] == 2:         # HELP
                            self.screen_value[0] = ALPHA_MAX / 3
                            self.screen_value[2] = 2
                        elif self.screen_value[1] == 3:         # EXIT
                            self.screen_value[2] = 3
                        else:                                   # Language
                            self.language_mode = self.language_mode + 1\
                                if self.language_mode < len(self.language_list) - 1 else 0
                            self.gameFont = os.path.join(self.font_dir, self.load_language(1))
            elif self.screen_value[2] == 1:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 15
                else:
                    self.screen_mode = 3
                    self.screen_value[1] = 0
                    self.screen_value[2] = 0

                    if self.song_highScore[self.song_select - 1] == -1:
                        pygame.mixer.music.fadeout(600)
                    else:
                        pygame.mixer.music.load(self.song_path[self.song_select - 1])
                        pygame.mixer.music.play(loops=-1)
            elif self.screen_value[2] == 2:
                if mouse_click == 1 or key_click != 0:
                    self.screen_value[2] = 0
            elif self.screen_value[2] == 3:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 15
                else:
                    self.playing = False
                    self.running = False
        elif self.screen_mode == 3:                             # Song Select Screen
            if self.screen_value[2] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 15

                self.screen_value[1] = 0
                songChange = False

                if round(0.31 * WIDTH - 75) < mouse_coord[0] < round(0.31 * WIDTH + 75):    # mouse coord check
                    if round(0.125 * HEIGHT + 30) > mouse_coord[1]:
                        self.screen_value[1] = 1
                    elif round(0.875 * HEIGHT - 30) < mouse_coord[1]:
                        self.screen_value[1] = 2
                elif round(0.69 * WIDTH - 75) < mouse_coord[0] < round(0.69 * WIDTH + 75)\
                        and round(HEIGHT / 2 + 25) < mouse_coord[1] < round(HEIGHT / 2 + 65):
                    self.screen_value[1] = 3
                elif round(0.73 * WIDTH - 75) < mouse_coord[0] < round(0.73 * WIDTH + 75)\
                        and round(HEIGHT / 2 + 85) < mouse_coord[1] < round(HEIGHT / 2 + 125):
                    self.screen_value[1] = 4

                if mouse_click == 1:                            # mouse click check
                    if self.screen_value[1] == 1:
                        if self.song_select > 1:
                            self.song_select -= 1
                            songChange = True
                    elif self.screen_value[1] == 2:
                        if self.song_select < self.song_num:
                            self.song_select += 1
                            songChange = True
                    elif self.screen_value[1] == 3:
                        if self.song_highScore[self.song_select - 1] != -1:
                            self.screen_value[2] = 1
                            pygame.mixer.music.fadeout(600)
                            pygame.time.delay(2000)
                            pygame.mixer.music.play()
                    elif self.screen_value[1] == 4:
                        self.screen_value[2] = 2
                elif key_click == pygame.K_UP or mouse_click == 4:  # key check
                    if self.song_select > 1:
                        self.song_select -= 1
                        songChange = True
                elif key_click == pygame.K_DOWN or mouse_click == 5:
                    if self.song_select < self.song_num:
                        self.song_select += 1
                        songChange = True
                elif key_click == pygame.K_RIGHT or key_click == 13:
                    if self.song_highScore[self.song_select - 1] != -1:
                        self.screen_value[2] = 1
                        pygame.mixer.music.fadeout(600)
                        pygame.time.delay(2000)
                        pygame.mixer.music.play()
                elif key_click == pygame.K_LEFT:
                    self.screen_value[2] = 2

                if songChange:
                    if self.song_highScore[self.song_select - 1] == -1:
                        pygame.mixer.music.fadeout(600)
                    else:
                        pygame.mixer.music.load(self.song_path[self.song_select - 1])
                        pygame.mixer.music.play(loops=-1)
            else:
                if self.screen_value[2] == 1:
                    self.screen_mode = 4
                    self.screen_value[1] = 0
                    self.screen_value[2] = 0
                    self.start_tick = pygame.time.get_ticks()
                    self.load_songData()
                else:
                    self.screen_mode = 2
                    self.screen_value[1] = 0
                    self.screen_value[2] = 0
                    self.screen_value[3] = ALPHA_MAX
                    pygame.mixer.music.load(self.bg_main)
                    pygame.mixer.music.play(loops=-1)
        elif self.screen_mode == 4:                             # Play Screen
            if self.screen_value[1] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 15

                self.all_sprites.add(self.player)
                self.all_sprites.add(self.player.upper_target)
                self.all_sprites.add(self.player.lower_target)
                self.create_enemy()                             # create enemy

                if key_click == pygame.K_s or key_click == pygame.K_d:          # key check
                    if self.player.position_down:
                        self.player.position_down = False
                        self.player.position_up = True
                        self.player.attacked = True
                        self.player.image = self.player.image_attack_up
                    else:
                        if self.player.attacked:
                            self.player.attacked = False
                            self.player.image = self.player.image_idle
                        else:
                            self.player.attacked = True
                            self.player.image = self.player.image_attack
                    self.player.upper_attack = True
                    self.player.rect.y = self.player.upper_y
                    IsBlank = True
                    for enemy in self.enemys.sprites():
                        IsBlank = False
                        if abs(enemy.rect.y - self.player.upper_target.rect.y) < 50:
                            if self.player.upper_target.rect.colliderect(enemy.rect):
                                self.score += 100
                                enemy.kill()
                                self.sound_hit.play()
                            elif abs(enemy.rect.x - self.player.upper_target.rect.x) < 100:
                                self.score += 50
                                enemy.kill()
                                self.sound_hit.play()
                            else:
                                self.sound_miss.play()
                        else:
                            self.sound_miss.play()
                    if IsBlank == True:
                        self.sound_miss.play()
                    self.player.upper_attack = False
                elif key_click == pygame.K_l or key_click == pygame.K_SEMICOLON:
                    if self.player.position_up:
                        self.player.position_down = True
                        self.player.position_up = False
                        self.player.attacked = True
                        self.player.image = self.player.image_attack_down
                    else:
                        if self.player.attacked:
                            self.player.attacked = False
                            self.player.image = self.player.image_idle
                        else:
                            self.player.attacked = True
                            self.player.image = self.player.image_attack
                    self.player.lower_attack = True
                    self.player.rect.y = self.player.lower_y
                    IsBlank = True
                    for enemy in self.enemys.sprites():
                        IsBlank = False
                        if abs(enemy.rect.y - self.player.lower_target.rect.y) < 50:
                            if self.player.lower_target.rect.colliderect(enemy.rect):
                                self.score += 100
                                enemy.kill()
                                self.sound_hit.play()
                            elif abs(enemy.rect.x - self.player.lower_target.rect.x) < 100:
                                self.score += 50
                                enemy.kill()
                                self.sound_hit.play()
                            else:
                                self.sound_miss.play()
                        else:
                            self.sound_miss.play()
                    if IsBlank == True:
                        self.sound_miss.play()
                    self.player.lower_attack = False
            else:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 85
                else:
                    pygame.mixer.music.fadeout(1200)
                    pygame.time.delay(2000)
                    pygame.mixer.music.play()
                    self.screen_mode = 5
                    self.screen_value[1] = 0
        else:                                                   # Score Screen
            self.all_sprites.empty()
            if self.screen_value[1] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 15

                if mouse_move:
                    if round(WIDTH / 2 - 160) < mouse_coord[0] < round(WIDTH / 2 - 40)\
                            and round(HEIGHT / 2 + 110) < mouse_coord[1] < round(HEIGHT / 2 + 170):
                        self.screen_value[2] = 1
                    elif round(WIDTH / 2 + 40) < mouse_coord[0] < round(WIDTH / 2 + 160)\
                            and round(HEIGHT / 2 + 110) < mouse_coord[1] < round(HEIGHT / 2 + 170):
                        self.screen_value[2] = 2

                if mouse_click == 1:                            # mouse click check
                    self.screen_value[1] = self.screen_value[2]
                elif key_click == pygame.K_LEFT or mouse_click == 4:   # key check
                    self.screen_value[2] = 1
                elif key_click == pygame.K_RIGHT or mouse_click == 5:
                    self.screen_value[2] = 2
                elif key_click == pygame.K_RETURN:
                    self.screen_value[1] = self.screen_value[2]
            else:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 15
                else:
                    self.new()

                    if self.screen_value[1] == 1:
                        self.screen_mode = 3
                    else:
                        self.screen_mode = 4
                        pygame.mixer.music.fadeout(600)
                        pygame.time.delay(2000)
                        pygame.mixer.music.play()
                        self.start_tick = pygame.time.get_ticks()
                        self.load_songData()

                    self.screen_value[1] = 0
                    self.screen_value[2] = 0

    def draw(self):                                             # Game Loop - Draw
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.background.blit(self.spr_background, (0, 0))
        self.screen.blit(self.background, (0, 0))
        self.draw_screen()                                      # draw screen
        self.all_sprites.draw(self.screen)
        pygame.display.update()

    def draw_screen(self):                                      # Draw Screen
        screen_alpha = self.screen_value[0]

        if self.screen_mode == 0:                               # logo screen1
            screen_alpha = ALPHA_MAX - min(max(self.screen_value[0], 0), ALPHA_MAX)
            self.draw_sprite((WIDTH / 5 - 50, HEIGHT / 2 - 70), self.spr_powered, screen_alpha)
        elif self.screen_mode == 1:                             # logo screen2
            spr_logobackRescale = pygame.transform.scale(self.spr_logoback,
                                                         (600 + self.screen_value[1], 600 + self.screen_value[1]))
            spr_logobackRescale.set_alpha(screen_alpha) if self.screen_value[3] == 0\
                                                        else self.spr_logoback.set_alpha(ALPHA_MAX)
            self.screen.blit(spr_logobackRescale, (0, 0))
            spr_logoRescale = pygame.transform.scale(self.spr_logo,
                                                     (600 + self.screen_value[1], 300 + self.screen_value[1]))
            self.draw_sprite(((WIDTH - self.screen_value[1]) / 2, (HEIGHT / 3 - 80) - self.screen_value[1] / 2),
                             spr_logoRescale, screen_alpha)
        elif self.screen_mode == 2:                             # main screen
            select_index = [True if self.screen_value[1] == i + 1 else False for i in range(4)]

            spr_logobackRescale = pygame.transform.scale(self.spr_logoback,
                                                         (600 + self.screen_value[1], 600 + self.screen_value[1]))
            if self.screen_value[2] == 0:
                self.draw_sprite((0, 0), spr_logobackRescale, ALPHA_MAX)
            else:
                spr_logobackRescale.set_alpha(screen_alpha)
                logoback_coord = 0 if self.screen_value[2] == 2 else round((screen_alpha - ALPHA_MAX) / 10)
                self.screen.blit(spr_logobackRescale, (logoback_coord, 0))

            if self.screen_value[2] == 2:
                help_surface = pygame.Surface((WIDTH - 60, HEIGHT - 60))
                help_surface.fill(WHITE)
                help_surface.set_alpha(255)
                self.screen.blit(help_surface, pygame.Rect(30, 30, 0, 0))
                self.draw_text("- " + self.load_language(5) + " -", 72, BLACK, WIDTH / 2, HEIGHT / 4, 255)
                self.draw_text(self.load_language(9), 32, BLACK, WIDTH / 2, HEIGHT / 3 + 100)
                self.draw_text(self.load_language(10), 32, BLACK, WIDTH / 2, HEIGHT / 3 + 170)
                self.draw_text(self.load_language(11), 32, BLACK, WIDTH / 2, HEIGHT / 3 + 240)
            else:
                self.draw_text(self.load_language(2), 72, WHITE, WIDTH / 4 * 3, 150, screen_alpha, select_index[0])
                self.draw_text(self.load_language(3), 72, WHITE, WIDTH / 4 * 3, 250, screen_alpha, select_index[1])
                self.draw_text(self.load_language(4), 72, WHITE, WIDTH / 4 * 3, 350, screen_alpha, select_index[2])
                self.draw_text(self.load_language(0), 48, WHITE, WIDTH / 4 * 3, 450, screen_alpha, select_index[3])
        elif self.screen_mode == 3:                             # song select screen
            surface = pygame.Surface((WIDTH, HEIGHT))
            surface.blit(self.spr_background, (0, 0))
            circle_coord = (round(WIDTH * 1.2), round(HEIGHT / 2))
            pygame.draw.circle(surface, WHITE, circle_coord, round(0.95 * WIDTH + screen_alpha), 1)
            pygame.draw.circle(surface, WHITE, circle_coord, round(0.50 * WIDTH + screen_alpha), 1)
            pygame.draw.circle(surface, WHITE, circle_coord, round(0.15 * WIDTH + screen_alpha), 1)
            pygame.draw.circle(surface, RED, circle_coord, round(0.125 * WIDTH + screen_alpha), 1)
            pygame.draw.circle(surface, BLUE, circle_coord, round(0.1 * WIDTH + screen_alpha), 1)
            self.screen.blit(surface, (0, 0))

            if self.song_select > 2:
                self.draw_text(self.song_list[self.song_select - 3], 32, WHITE, 0.29 * WIDTH, 0.25 * HEIGHT - 20,
                               max(screen_alpha - 220, 0))

            if self.song_select > 1:
                self.draw_text(self.song_list[self.song_select - 2], 36, WHITE, 0.27 * WIDTH, 0.375 * HEIGHT - 20,
                               max(screen_alpha - 180, 0))

            self.draw_text(self.song_list[self.song_select - 1], 48, WHITE, 0.25 * WIDTH, 0.5 * HEIGHT - 20,
                           screen_alpha)

            if self.song_select < self.song_num:
                self.draw_text(self.song_list[self.song_select], 36, WHITE, 0.27 * WIDTH, 0.625 * HEIGHT - 20,
                               max(screen_alpha - 180, 0))

            if self.song_select < self.song_num - 1:
                self.draw_text(self.song_list[self.song_select + 1], 32, WHITE, 0.29 * WIDTH, 0.75 * HEIGHT - 20,
                               max(screen_alpha - 220, 0))

            button_songUpScale = 36 if self.screen_value[1] == 1 else 32
            button_songDownScale = 36 if self.screen_value[1] == 2 else 32
            select_index = [True if self.screen_value[1] == i + 3 else False for i in range(2)]
            self.draw_text("UP", button_songUpScale, WHITE, 0.31 * WIDTH, 0.125 * HEIGHT - 20, screen_alpha)
            self.draw_text("DOWN", button_songDownScale, WHITE, 0.31 * WIDTH, 0.875 * HEIGHT - 30, screen_alpha)

            if self.song_highScore[self.song_select - 1] == -1:
                self.draw_text(self.load_language(12), 32, RED, 0.71 * WIDTH, HEIGHT / 2 - 100, screen_alpha)
            else:
                if self.song_highScore[self.song_select - 1] >= self.song_perfectScore[self.song_select - 1]:
                    try:
                        font = pygame.font.Font(self.gameFont, 36)
                    except:
                        font = pygame.font.Font(os.path.join(self.font_dir, DEFAULT_FONT), 36)

                    font.set_bold(True)
                    cleartext_surface = font.render(self.load_language(14), False, BLUE)
                    rotated_surface = pygame.transform.rotate(cleartext_surface, 25)
                    rotated_surface.set_alpha(max(screen_alpha - 180, 0))
                    cleartext_rect = rotated_surface.get_rect()
                    cleartext_rect.midtop = (round(0.71 * WIDTH), round(HEIGHT / 2 - 150))
                    self.screen.blit(rotated_surface, cleartext_rect)

                self.draw_text(self.load_language(8), 28, WHITE, 0.69 * WIDTH, HEIGHT / 2 - 130, screen_alpha)
                self.draw_text(str(self.song_highScore[self.song_select - 1]), 28, WHITE, 0.69 * WIDTH, HEIGHT / 2 - 70,
                               screen_alpha)
                self.draw_text(self.load_language(7), 32, WHITE, 0.69 * WIDTH, HEIGHT / 2 + 25, screen_alpha,
                               select_index[0])

            self.draw_text(self.load_language(6), 32, WHITE, 0.73 * WIDTH, HEIGHT / 2 + 85, screen_alpha,
                           select_index[1])
        elif self.screen_mode == 4:                         # play screen
            surface = pygame.Surface((WIDTH, HEIGHT))
            surface.blit(self.rolling_bg.image_background, (self.rolling_bg.x1, self.rolling_bg.y1))
            surface.blit(self.rolling_bg.image_background, (self.rolling_bg.x2, self.rolling_bg.y2))
            self.screen.blit(surface, (0, 0))
            time_m = self.game_tick // 60000
            time_s = str(round(self.game_tick / 1000) - time_m * 60)

            if len(time_s) == 1:
                time_s = "0" + time_s

            time_str = str(time_m) + " : " + time_s
            score_str = self.load_language(13) + " : " + str(self.score)
            self.draw_text(time_str, 24, WHITE, 10 + len(time_str) * 6, 15, screen_alpha)
            self.draw_text(score_str, 24, WHITE, WIDTH - 20 - len(score_str) * 6, 15, screen_alpha)
        else:                                               # score screen
            surface = pygame.Surface((WIDTH, HEIGHT))
            surface.blit(self.spr_background, (0, 0))
            circle_coord = (round(WIDTH / 2), round(HEIGHT / 2))
            pygame.draw.circle(surface, BLUE, circle_coord, round(HEIGHT / 2 - 30), 1)
            pygame.draw.circle(surface, WHITE, circle_coord, round(HEIGHT / 2), 1)
            pygame.draw.circle(surface, RED, circle_coord, round(HEIGHT / 2 + 30), 1)
            self.screen.blit(surface, (0, 0))
            self.draw_text(self.load_language(15) + " : " + str(self.song_perfectScore[self.song_select - 1]), 32,
                           WHITE, WIDTH / 2, HEIGHT / 2 - 65, screen_alpha)
            self.draw_text(self.load_language(13) + " : " + str(self.score), 32, WHITE, WIDTH / 2, HEIGHT / 2 - 5,
                           screen_alpha)
            select_index = [True if self.screen_value[2] == i + 1 else False for i in range(2)]
            self.draw_text(self.load_language(17), 24, WHITE, WIDTH / 2 - 100, HEIGHT / 2 + 125, ALPHA_MAX,
                           select_index[0])
            self.draw_text(self.load_language(16), 24, WHITE, WIDTH / 2 + 100, HEIGHT / 2 + 125, ALPHA_MAX,
                           select_index[1])

    def load_language(self, index):
        try:
            return self.language_list[self.language_mode][index]
        except:
            return "Font Error"

    def load_songData(self):
        with open(self.song_dataPath[self.song_select - 1], 'r', encoding="UTF-8") as data_file:
            data_fileLists = data_file.read().split('\n')

        for data_line in data_fileLists:
            if data_line != '' and data_line[0] != 's':
                data_fileList = data_line.split(" - ")
                time_list = data_fileList[0].split(':')
                enemy_list = data_fileList[1].split(", ")
                current_songData = list()
                current_songData.append(int(time_list[0]) * 60000 + int(time_list[1]) * 1000 + int(time_list[2]) * 10)

                for enemy in enemy_list:
                    if enemy[0] == 'E':
                        enemy_type = -1
                    elif enemy[0] == '1':
                        enemy_type = 1
                    elif enemy[0] == '2':
                        enemy_type = 2
                    else:           # 3
                        enemy_type = 3

                    if enemy_type != -1:
                        if enemy[1] == 'U':
                            enemy_line = 0
                        else:           # L
                            enemy_line = 270

                        enemy_data = (enemy_type, enemy_line, int(enemy[2]))
                        current_songData.append(enemy_data)
                    else:
                        enemy_data = -1
                        current_songData.append(enemy_data)

                self.song_data.append(current_songData)

    def create_enemy(self):
        if self.game_tick >= self.song_data[self.song_dataIndex][0]:
            if self.song_data[self.song_dataIndex][1] != -1:
                enemy_num = len(self.song_data[self.song_dataIndex]) - 1

                for enemy in range(enemy_num):
                    enemy_data = self.song_data[self.song_dataIndex][enemy + 1]

                    obj_enemy = Enemy(self, enemy_data[0], enemy_data[1], enemy_data[2])
                    self.all_sprites.add(obj_enemy)
                    self.enemys.add(obj_enemy)

                self.song_dataIndex += 1
            else:
                if self.score >= self.song_highScore[self.song_select - 1]:
                    with open(self.song_dataPath[self.song_select - 1], 'r', encoding="UTF-8") as file:
                        file_lists = file.read().split('\n')

                    file_list = "score:" + str(self.score) + ':'\
                                + str(self.song_perfectScore[self.song_select - 1]) + '\n'

                    for enemy_file in file_lists:
                        if enemy_file != '' and enemy_file[0] != 's':
                            file_list += '\n' + enemy_file

                    with open(self.song_dataPath[self.song_select - 1], "w+", encoding="UTF-8") as song_file:
                        song_file.write(file_list)

                    self.song_highScore[self.song_select - 1] = self.score

                self.screen_value[1] = 1

    def draw_sprite(self, coord, spr, alpha=ALPHA_MAX, rot=0):
        if rot == 0:
            spr.set_alpha(alpha)
            self.screen.blit(spr, (round(coord[0]), round(coord[1])))
        else:
            rotated_spr = pygame.transform.rotate(spr, rot)
            rotated_spr.set_alpha(alpha)
            self.screen.blit(rotated_spr, (round(coord[0] + spr.get_width() / 2 - rotated_spr.get_width() / 2),
                                           round(coord[1] + spr.get_height() / 2 - rotated_spr.get_height() / 2)))

    def draw_text(self, text, size, color, x, y, alpha=ALPHA_MAX, boldunderline=False):
        try:
            font = pygame.font.Font(self.gameFont, size)
        except:
            font = pygame.font.Font(os.path.join(self.font_dir, DEFAULT_FONT), size)

        font.set_underline(boldunderline)
        font.set_bold(boldunderline)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (round(x), round(y))

        if alpha == ALPHA_MAX:
            self.screen.blit(text_surface, text_rect)
        else:
            surface = pygame.Surface((len(text) * size, size + 20))
            surface.fill((0, 0, 0))
            surface.blit(text_surface, pygame.Rect(0, 0, 10, 10))
            surface.set_alpha(alpha)
            self.screen.blit(surface, text_rect)


class TargetPoint(pygame.sprite.Sprite):
    def __init__(self, game, line):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.line = line

        if self.line == 0:
            self.image = self.game.spr_target
        else:
            self.image = self.game.spr_target

        self.touch_coord = (round(self.image.get_width() / 2), round(self.image.get_height() / 2))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH / 8 + self.touch_coord[0] + 100

        if self.line == 0:
            self.rect.y = HEIGHT / 4 + self.touch_coord[1]
        else:
            self.rect.y = HEIGHT / 2 + self.touch_coord[1] + 40


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.alpha = ALPHA_MAX
        self.upper_attack = False
        self.lower_attack = False

        self.position_up = False
        self.position_down = True
        self.attacked = False

        self.image_idle = pygame.transform.scale(self.game.spr_playerIdle, (180, 180))
        self.image_attack = pygame.transform.scale(self.game.spr_playerAttack, (180, 180))
        self.image_attack_up = pygame.transform.scale(self.game.spr_playerAttackUp, (180, 180))
        self.image_attack_down = pygame.transform.scale(self.game.spr_playerAttackDown, (180, 180))

        self.image = self.image_idle

        self.touch_coord = (round(self.image.get_width() / 2), round(self.image.get_height() / 2))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH / 8
        self.rect.y = HEIGHT / 2

        self.rect.x += self.touch_coord[0] - 75
        self.rect.y += self.touch_coord[1] - 30

        self.upper_target = TargetPoint(game, 0)
        self.lower_target = TargetPoint(game, 1)

        self.upper_y = HEIGHT / 4 + 20
        self.lower_y = self.rect.y

        self.game.player = self


class Enemy(pygame.sprite.Sprite):                          # Enemy Class
    def __init__(self, game, type, line, speed):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.type = type
        self.line = line
        self.speed = speed * 10
        self.alpha = ALPHA_MAX
        self.correct_code = [1, 2, 3, 4]
        self.correct = -1

        if self.type == 1:
            enemy1 = pygame.transform.scale(self.game.spr_enemy1, (100, 100))
            self.image = enemy1
        elif self.type == 2:
            enemy2 = pygame.transform.scale(self.game.spr_enemy2, (120, 120))
            self.image = enemy2
        else:
            enemy3 = pygame.transform.scale(self.game.spr_enemy3, (120, 120))
            self.image = enemy3

        self.touch_coord = (50, 50)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH

        if self.line == 0:
            self.rect.y = HEIGHT / 4 - 30
        else:
            self.rect.y = HEIGHT / 2

        self.rect.x += self.touch_coord[0]
        self.rect.y += self.touch_coord[1]

    def update(self):
        self.image.set_alpha(self.alpha)

        if self.alpha > 0:
            self.rect.x -= self.speed

            if self.rect.x > WIDTH * 2 or self.rect.x < -WIDTH:
                self.kill()
        else:
            self.kill()

class BackGround():
    def __init__(self, game):
        self.game = game
        self.image_background = game.spr_background
        self.rect = self.image_background.get_rect()

        self.y1 = 0
        self.x1 = 0

        self.y2 = 0
        self.x2 = self.rect.width

        self.speed = 20

    def update(self):
        self.x1 -= self.speed
        self.x2 -= self.speed
        if self.x1 <= -self.rect.width:
            self.x1 = self.rect.width
        if self.x2 <= -self.rect.width:
            self.x2 = self.rect.width


if __name__ == "__main__":
    game = MuseRush()
    while game.running:
        game.run()
    pygame.quit()