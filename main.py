# Game Guide:
# 1. There are 2 monsters that are shown in the window which the one on the bottom left is your monster, while the
# opposing monster is the opponent.
# 2. The battle sequence portrays a health bar which indicates of how much does your monster health is remaining,
# below the health bar portrays the menu which you can choose what option you want to do during your battle.
# 3. Up, Down, Left, and Right Keys are the keys that can move through the menu which allows you to choose an 
# option.
# 4. There are 4 options that you can choose Attack, Switch, Heal, and Escape.
# 5. Press Spacebar if you wanted to choose that option.
# 6. Each attack moves are much stronger, weaker, or has a neutral damage depends in what the opposing monster's
# element.
# 7. The battle conditions are easy, kill the opposing monster and you win, if all of your monsters are killed
# then you lose the battle.

from settings import *
from support import *
from timer import Timer
from monster import *
from random import choice
from ui import *
from attack import AttackAnimationSprite
import pygame, sys
from button import Button

window_width, window_height = 1280, 720
pygame.init()

window_starting_screen = pygame.display.set_mode((1280,720))

game_menu_background = pygame.image.load('mbg_pedia/images/game_menu/gmb_pic.png')

class Game:  
    def __init__(self):
        pygame.init()
        self.window_starting_screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Game Menu")
        self.game_menu_background = pygame.image.load('mbg_pedia/images/game_menu/gmb_pic')

    def game_menu():

        while True:
            window_starting_screen.blit(game_menu_background, 0, 0)
                
            menu_mouse_pos = pygame.mouse.get_post()

            game_menu_text = get_font(100).render('GAME MENU', True, '#b68f40')
            game_menu_rect = game_menu_text.get_rect(center=(640, 100))

            play_button = Button(image=pygame.image.load('mbg_pedia/images/game_menu/play_button'), pos=(640, 250))
                                text_input = 'PLAY', font=get_font(75), base_color='#d7fcd4', hovering_color='White'
            help_button = Button(image=pygame.image.load('mbg_pedia/images/game_menu/help_button'), pos=(640, 400))
                                text_input = 'PLAY', font=get_font(75), base_color='#d7fcd4', hovering_color='White'
            quit_button = Button(image=pygame.image.load('mbg_pedia/images/game_menu/quit_button'), pos=(640, 550))
                                text_input = 'QUIT', font=get_font(75), base_color='#d7fcd4', hovering_color='White'
                
            window_starting_screen.blit(game_menu_text, game_menu_rect)

            for button in [play_button, quit_button]:
                button.changecolor(menu_mouse_pos)
                button.update(window_starting_screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.check_for_input(menu_mouse_pos):
                        play()
                    if quit_button.check_for_input(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()
                    
              
    def play():
                    pygame.display.set_caption('Play')

                    while True:
                        
                        menu_mouse_pos = pygame.mouse.get_pos()

                        window_starting_screen.fill('Black')

                        play_text = get_font(45).render('Starting Game', True, 'White')
                        play_rect = play_text.get_rect(center=(640, 260))
                        window_starting_screen.blit(play_text, play_rect)

                    

    def __init__(self):
                pygame.init()
                self.display_surface = pygame.display.set_mode((window_width, window_height))
                pygame.display.set_caption('Monster Battle')
                self.clock = pygame.time.Clock()
                self.running = True
                self.import_assets()

                if 'music' in self.audio:
                    self.audio['music'].play(-1) 

                self.player_active = True

                self.all_sprites = pygame.sprite.Group()

                # data 
                player_monster_list = ['Blazedillo', 'Seagon', 'Gengharoo', 'Bermudrac', 'Dragoshell','Lustar']
                self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]
                self.monster = self.player_monsters[0]
                self.all_sprites.add(self.monster)
                opponent_name = choice(list(MONSTER_DATA.keys()))
                self.opponent = Opponent(opponent_name, self.front_surfs[opponent_name], self.all_sprites)

                # ui 
                self.ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)
                self.opponent_ui = OpponentUI(self.opponent)

                # timers
                self.timers = {'player end': Timer(1000, func = self.opponent_turn), 'opponent end': Timer(1000, func = self.player_turn)}

    def get_input(self, state, data = None):
                if state == 'attack':
                    self.apply_attack(self.opponent, data)
                elif state == 'heal':
                    self.monster.health += 50
                    AttackAnimationSprite(self.monster, self.attack_frames['green'], self.all_sprites)
                    if 'green' in self.audio: self.audio['green'].play()
                elif state == 'switch':
                    self.monster.kill()
                    self.monster = data
                    self.all_sprites.add(self.monster)
                    self.ui.monster = self.monster

                elif state == 'escape':
                    self.running = False
                self.player_active = True
                self.timers['player end'].activate()

    def apply_attack(self, target, attack):
                attack_data = ABILITIES_DATA[attack]
                attack_multiplier = ELEMENT_DATA[attack_data['element']][target.element]
                target.health -= attack_data['damage'] * attack_multiplier
                AttackAnimationSprite(target, self.attack_frames[attack_data['animation']], self.all_sprites)
                if attack_data['animation'] in self.audio:
                    self.audio[attack_data['animation']].play()

    def opponent_turn(self):
                if self.opponent.health <= 0:
                    self.player_active = True
                    self.opponent.kill()
                    monster_name = choice(list(MONSTER_DATA.keys()))
                    self.opponent = Opponent(monster_name, self.front_surfs[monster_name], self.all_sprites)
                    self.opponent_ui.monster = self.opponent
                else:
                    attack = choice(self.opponent.abilities)
                    self.apply_attack(self.monster, attack)
                    self.timers['opponent end'].activate()

    def player_turn(self):
                self.player_active = True
                if self.monster.health <= 0:
                    available_monsters = [monster for monster in self.player_monsters if monster.health > 0]
                    if available_monsters:
                        self.monster.kill()
                        self.monster = available_monsters[0]
                        self.all_sprites.add(self.monster)
                        self.ui.monster = self.monster
                    else:
                        self.running = False

    def update_timers(self):
                for timer in self.timers.values():
                    timer.update()

    def import_assets(self):
                current_folder = 'mbg_pedia'
                self.back_surfs = folder_importer(current_folder, 'images', 'front')
                self.front_surfs = folder_importer(current_folder, 'images', 'reverse')
                self.bg_surfs = folder_importer(current_folder, 'images', 'other')
                self.simple_surfs = folder_importer(current_folder, 'images', 'simple')
                self.attack_frames = tile_importer(4, current_folder, 'images', 'attacks')
                self.audio = audio_importer(current_folder, 'audio')
                self.text_input = folder_importer(current_folder, 'images', 'game_menu')

    def draw_monster_floor(self):
                for sprite in self.all_sprites:
                    if isinstance(sprite, Creature):
                        floor_rect = self.bg_surfs['floor'].get_frect(center = sprite.rect.midbottom + pygame.Vector2(0, -10))
                        self.display_surface.blit(self.bg_surfs['floor'], floor_rect)

    def run(self):
                while self.running:
                    dt = self.clock.tick() / 1000
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                    
                    self.update_timers()
                    self.all_sprites.update(dt)
                    if self.player_active:
                        self.ui.update()
                        
                    self.display_surface.blit(self.bg_surfs['bg'], (0,0))
                    self.draw_monster_floor()
                    self.all_sprites.draw(self.display_surface)
                    self.ui.draw()
                    self.opponent_ui.draw()
                    pygame.display.update()
            
                pygame.quit()
            
if __name__ == '__main__':
    game = Game()
    game.run()   