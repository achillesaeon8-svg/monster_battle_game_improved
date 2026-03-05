from settings import *
from support import *
from timer import Timer
from monster import *
from random import choice
from ui import *
from attack import AttackAnimationSprite
import pygame, sys
from button import Button

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Monster Battle")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load Menu Assets
        # Ensure this path is correct based on your folder sidebar
        self.menu_bg = pygame.image.load('mbg_pedia/images/game_menu/gmb_pic.png')
        
        # Load Game Assets
        self.import_assets()

        # Audio
        if 'music' in self.audio:
            self.audio['music'].play(-1) 

        # Game State
        self.player_active = True
        self.all_sprites = pygame.sprite.Group()

        # Data setup
        player_monster_list = ['Blazedillo', 'Seagon', 'Gengharoo', 'Bermudrac', 'Dragoshell','Lustar']
        # Note: self.back_surfs comes from import_assets() called above
        self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]
        self.monster = self.player_monsters[0]
        self.all_sprites.add(self.monster)
        
        opponent_name = choice(list(MONSTER_DATA.keys()))
        self.opponent = Opponent(opponent_name, self.front_surfs[opponent_name], self.all_sprites)

        # UI 
        self.ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)
        self.opponent_ui = OpponentUI(self.opponent)

        # Timers
        self.timers = {
            'player end': Timer(1000, func = self.opponent_turn), 
            'opponent end': Timer(1000, func = self.player_turn)
        }

    def import_assets(self):
        current_folder = 'mbg_pedia'
        # Fixed: Based on your previous errors, ensure these folders match your .png files
        self.back_surfs = folder_importer(current_folder, 'images', 'front')
        self.front_surfs = folder_importer(current_folder, 'images', 'reverse')
        self.bg_surfs = folder_importer(current_folder, 'images', 'other')
        self.simple_surfs = folder_importer(current_folder, 'images', 'simple')
        self.attack_frames = tile_importer(4, current_folder, 'images', 'attacks')
        self.audio = audio_importer(current_folder, 'audio')

    def game_menu(self):
        while True:
            self.display_surface.blit(self.menu_bg, (0, 0))
            menu_mouse_pos = pygame.mouse.get_pos()

            # Text and Buttons
            # Make sure get_font() is defined in your settings or support file
            game_menu_text = get_font(100).render('GAME MENU', True, '#b68f40')
            game_menu_rect = game_menu_text.get_rect(center=(640, 100))
            self.display_surface.blit(game_menu_text, game_menu_rect)

            play_button = Button(
                image=pygame.image.load("mbg_pedia/images/game_menu/Play Rect.png"), 
                pos=(640, 250), text_input='PLAY', font=get_font(75), 
                base_color='#d7fcd4', hovering_color='White'
            )
            quit_button = Button(
                image=pygame.image.load('mbg_pedia/images/game_menu/Quit Rect.png'), 
                pos=(640, 550), text_input='QUIT', font=get_font(75), 
                base_color='#d7fcd4', hovering_color='White'
            )

            for button in [play_button, quit_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.display_surface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.checkForInput(menu_mouse_pos):
                        self.run() # This starts the actual battle loop
                    if quit_button.checkForInput(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

    # --- Battle Logic Methods ---
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
            opponent_name = choice(list(MONSTER_DATA.keys()))
            self.opponent = Opponent(opponent_name, self.front_surfs[opponent_name], self.all_sprites)
            self.opponent_ui.monster = self.opponent
        else:
            attack = choice(self.opponent.abilities)
            self.apply_attack(self.monster, attack)
            self.timers['opponent end'].activate()

    def player_turn(self):
        self.player_active = True
        if self.monster.health <= 0:
            available_monsters = [m for m in self.player_monsters if m.health > 0]
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

    def draw_monster_floor(self):
        for sprite in self.all_sprites:
            if isinstance(sprite, Creature):
                floor_rect = self.bg_surfs['floor'].get_rect(center = sprite.rect.midbottom + pygame.Vector2(0, -10))
                self.display_surface.blit(self.bg_surfs['floor'], floor_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.update_timers()
            self.all_sprites.update(dt)
            
            # Drawing
            self.display_surface.blit(self.bg_surfs['bg'], (0,0))
            self.draw_monster_floor()
            self.all_sprites.draw(self.display_surface)
            
            if self.player_active:
                self.ui.update()
            
            self.ui.draw()
            self.opponent_ui.draw()
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.game_menu() # Start with the menu