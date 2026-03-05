from settings import *
from support import *
from timer import Timer
from monster import *
from random import choice
from ui import *
from attack import AttackAnimationSprite
import pygame, sys
from button import Button


def get_font(size):
    return pygame.font.Font(None, size)


class Game:  
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Monster Battle")
        self.clock = pygame.time.Clock()
       
        # Scale Menu Background
        raw_bg = pygame.image.load('mbg_pedia/images/game_menu/gmb_pic.png')
        self.menu_bg = pygame.transform.scale(raw_bg, (1280, 720))
       
        self.import_assets()
        # We don't call setup() here anymore, we call it in run()


    def import_assets(self):
        current_folder = 'mbg_pedia'
        self.back_surfs = folder_importer(current_folder, 'images', 'reverse')
        self.front_surfs = folder_importer(current_folder, 'images', 'front')
        self.bg_surfs = folder_importer(current_folder, 'images', 'other')
        self.bg_surfs['bg'] = pygame.transform.scale(self.bg_surfs['bg'], (1280, 720))
        self.simple_surfs = folder_importer(current_folder, 'images', 'simple')
        self.attack_frames = tile_importer(4, current_folder, 'images', 'attacks')
        self.audio = audio_importer(current_folder, 'audio')


    def setup(self):
        """ This method resets the game state entirely for a fresh battle """
        self.all_sprites = pygame.sprite.Group()
       
        # Player Setup
        player_monster_list = ['Blazedillo', 'Seagon', 'Gengharoo', 'Bermudrac', 'Dragoshell', 'Lustar']
        self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]
        self.monster = self.player_monsters[0]
        self.all_sprites.add(self.monster)
       
        # Opponent Setup
        opponent_name = choice(list(MONSTER_DATA.keys()))
        self.opponent = Opponent(opponent_name, self.front_surfs[opponent_name], self.all_sprites)


        # UI Setup
        self.ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)
        self.opponent_ui = OpponentUI(self.opponent)
       
        # Logic state
        self.player_active = True
        self.timers = {
            'player end': Timer(1000, func=self.opponent_turn),
            'opponent end': Timer(1000, func=self.player_turn)
        }


    def game_menu(self):
        btn_size = (350, 100)
        play_img = pygame.transform.scale(pygame.image.load('mbg_pedia/images/game_menu/play_button.png'), btn_size)
        quit_img = pygame.transform.scale(pygame.image.load('mbg_pedia/images/game_menu/quit_button.png'), btn_size)


        while True:
            self.display_surface.blit(self.menu_bg, (0, 0))
            m_pos = pygame.mouse.get_pos()
            menu_text = get_font(100).render('GAME MENU', True, '#b68f40')
            menu_rect = menu_text.get_rect(center=(640, 100))


            play_btn = Button(image=play_img, pos=(640, 300), text_input='START',
                              font=get_font(75), base_color='#d7fcd4', hovering_color='White')
            quit_btn = Button(image=quit_img, pos=(640, 500), text_input='QUIT',
                              font=get_font(75), base_color='#d7fcd4', hovering_color='White')
               
            self.display_surface.blit(menu_text, menu_rect)


            for btn in [play_btn, quit_btn]:
                btn.change_color(m_pos)
                btn.update(self.display_surface)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_btn.checkForInput(m_pos):
                        self.run()
                    if quit_btn.checkForInput(m_pos):
                        pygame.quit()
                        sys.exit()


            pygame.display.update()


    def get_input(self, state, data=None):
        if state == 'attack': self.apply_attack(self.opponent, data)
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
            if 'music' in self.audio:
                self.audio['music'].stop()
            self.running = False
       
        if self.running:
            self.player_active = False
            self.timers['player end'].activate()


    def apply_attack(self, target, attack):
        attack_data = ABILITIES_DATA[attack]
        multiplier = ELEMENT_DATA[attack_data['element']][target.element]
        target.health -= attack_data['damage'] * multiplier
        AttackAnimationSprite(target, self.attack_frames[attack_data['animation']], self.all_sprites)
        if attack_data['animation'] in self.audio: self.audio[attack_data['animation']].play()


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
            available = [m for m in self.player_monsters if m.health > 0]
            if available:
                self.monster.kill()
                self.monster = available[0]
                self.all_sprites.add(self.monster)
                self.ui.monster = self.monster
            else:
                if 'music' in self.audio: self.audio['music'].stop()
                self.running = False


    def update_timers(self):
        for timer in self.timers.values(): timer.update()


    def draw_monster_floor(self):
        for sprite in self.all_sprites:
            if isinstance(sprite, Creature):
                floor_rect = self.bg_surfs['floor'].get_frect(center = sprite.rect.midbottom + pygame.Vector2(0, -10))
                self.display_surface.blit(self.bg_surfs['floor'], floor_rect)


    def run(self):
        # IMPORTANT: Call setup() every time the battle runs to reset everything
        self.setup()
        self.running = True
        if 'music' in self.audio:
            self.audio['music'].play(-1)


        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
           
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


if __name__ == '__main__':
    game = Game()
    game.game_menu()
