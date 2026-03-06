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
       
        raw_bg = pygame.image.load('mbg_pedia/images/game_menu/gmb_pic.png')
        self.menu_bg = pygame.transform.scale(raw_bg, (1280, 720))
       
        self.import_assets()

        player_monster_list = ['Blazedillo', 'Seagon', 'Gengharoo', 'Bermudrac', 'Dragoshell', 'Lustar']
        self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]
        self.monster = self.player_monsters[0]

    def import_assets(self):
        current_folder = 'mbg_pedia'
        self.back_surfs = folder_importer(current_folder, 'images', 'front')
        self.front_surfs = folder_importer(current_folder, 'images', 'reverse')
        self.bg_surfs = folder_importer(current_folder, 'images', 'other')
        self.bg_surfs['bg'] = pygame.transform.scale(self.bg_surfs['bg'], (1280, 720))
        self.simple_surfs = folder_importer(current_folder, 'images', 'simple')
        self.attack_frames = tile_importer(4, current_folder, 'images', 'attacks')
        self.audio = audio_importer(current_folder, 'audio')

    def help_screen(self):
        help_running = True
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(245)
        overlay.fill((10, 10, 15))


        temp_ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)

        left_anchor = 120  
        right_anchor = 1160  
        center_screen = 640

        while help_running:
            m_pos = pygame.mouse.get_pos()
            self.display_surface.blit(self.menu_bg, (0, 0))
            self.display_surface.blit(overlay, (0,0))


            title_surf = get_font(70).render('MONSTER ELEMENT GUIDE', True, "#ffd47e")
            self.display_surface.blit(title_surf, (center_screen - title_surf.get_width()//2, 40))

            y_ptr = 150
            h_font = get_font(35)
           
            self.display_surface.blit(h_font.render("MOVE", True, '#d7fcd4'), (left_anchor, y_ptr))
            type_h = h_font.render("TYPE", True, '#d7fcd4')
            self.display_surface.blit(type_h, (center_screen - type_h.get_width()//2, y_ptr))
            dmg_h = h_font.render("DMG", True, '#d7fcd4')
            self.display_surface.blit(dmg_h, (right_anchor - dmg_h.get_width(), y_ptr))

            y_ptr += 60
            for move, data in ABILITIES_DATA.items():
                icon = temp_ui.icon_surfs.get(data['element'])
                if icon: self.display_surface.blit(icon, (left_anchor - 45, y_ptr))
               
                m_color = ELEMENT_COLORS.get(data['element'], 'white')
                m_surf = get_font(30).render(move.upper(), True, m_color)
                self.display_surface.blit(m_surf, (left_anchor + 15, y_ptr))

                t_surf = get_font(30).render(data['element'].capitalize(), True, 'white')
                self.display_surface.blit(t_surf, (center_screen - t_surf.get_width()//2, y_ptr))

                d_surf = get_font(30).render(str(data['damage']), True, 'white')
                self.display_surface.blit(d_surf, (right_anchor - d_surf.get_width(), y_ptr))
                y_ptr += 45

            chart_y = 500
            elemental_colors = [center_screen - 240, center_screen, center_screen + 240]
           
            v_heads = ["VS WATER", "VS PLANT", "VS FIRE"]
            for i, vh in enumerate(v_heads):
                vh_s = get_font(28).render(vh, True, '#AAAAAA')
                self.display_surface.blit(vh_s, (elemental_colors[i] - vh_s.get_width()//2, chart_y))


            for row_idx, attacker in enumerate(['fire', 'water', 'plant']):
                row_y = chart_y + 50 + (row_idx * 45)
               
                l_color = ELEMENT_COLORS[attacker]
                l_surf = get_font(32).render(f"{attacker.upper()}:", True, l_color)
                self.display_surface.blit(l_surf, (left_anchor + 15, row_y))

                for col_idx, defender in enumerate(['water', 'plant', 'fire']):
                    mult = ELEMENT_DATA[attacker][defender]
                    v_color = '#00FF00' if mult > 1 else ('#FF4422' if mult < 1 else 'white')
                    v_surf = get_font(32).render(f"{mult}x", True, v_color)
                    self.display_surface.blit(v_surf, (elemental_colors[col_idx] - v_surf.get_width()//2, row_y))

            back_btn = Button(image=None, pos=(center_screen, 685), text_input='BACK TO MENU',
                              font=get_font(45), base_color='White', hovering_color='#3399FF')
            back_btn.change_color(m_pos)
            back_btn.update(self.display_surface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_btn.checkForInput(m_pos): help_running = False

            pygame.display.update()

    def game_menu(self):
        if 'music' in self.audio: self.audio['music'].stop()

        btn_size = (350, 90)
        play_img = pygame.transform.scale(pygame.image.load('mbg_pedia/images/game_menu/play_button.png'), btn_size)
        help_img = pygame.transform.scale(pygame.image.load('mbg_pedia/images/game_menu/help_button.png'), btn_size)
        quit_img = pygame.transform.scale(pygame.image.load('mbg_pedia/images/game_menu/quit_button.png'), btn_size)

        while True:
            self.display_surface.blit(self.menu_bg, (0, 0))
            m_pos = pygame.mouse.get_pos()
           
            title = get_font(100).render('MONSTER BATTLE', True, '#b68f40')
            self.display_surface.blit(title, (640 - title.get_width()//2, 100))

            play_btn = Button(image=play_img, pos=(640, 260), text_input='START BATTLE',
                              font=get_font(50), base_color='White', hovering_color='Yellow')
            help_btn = Button(image=help_img, pos=(640, 410), text_input='HELP',
                              font=get_font(50), base_color='White', hovering_color='Yellow')
            quit_btn = Button(image=quit_img, pos=(640, 560), text_input='QUIT GAME',
                              font=get_font(50), base_color='White', hovering_color='Yellow')
               
            for btn in [play_btn, help_btn, quit_btn]:
                btn.change_color(m_pos)
                btn.update(self.display_surface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_btn.checkForInput(m_pos):
                        if 'music' in self.audio: self.audio['music'].stop()
                        self.run()
                    if help_btn.checkForInput(m_pos): self.help_screen()
                    if quit_btn.checkForInput(m_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

    def setup(self):
        self.all_sprites = pygame.sprite.Group()
        for m in self.player_monsters:
            m.health = m.max_health
        self.monster = self.player_monsters[0]
        self.all_sprites.add(self.monster)
       
        opp_name = choice(list(MONSTER_DATA.keys()))
        self.opponent = Opponent(opp_name, self.front_surfs[opp_name], self.all_sprites)
        self.ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)
        self.opponent_ui = OpponentUI(self.opponent)
       
        self.player_active = True
        self.timers = {
            'player end': Timer(1000, func=self.opponent_turn),
            'opponent end': Timer(1000, func=self.player_turn)
        }

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
            if 'music' in self.audio: self.audio['music'].stop()
            self.running = False
       
        if self.running:
            self.player_active = False
            self.timers['player end'].activate()

    def apply_attack(self, target, attack):
        data = ABILITIES_DATA[attack]
        mult = ELEMENT_DATA[data['element']][target.element]
        target.health -= data['damage'] * mult
        AttackAnimationSprite(target, self.attack_frames[data['animation']], self.all_sprites)
        if data['animation'] in self.audio: self.audio[data['animation']].play()

    def opponent_turn(self):
        if self.opponent.health <= 0:
            self.player_active = True
            self.opponent.kill()
            name = choice(list(MONSTER_DATA.keys()))
            self.opponent = Opponent(name, self.front_surfs[name], self.all_sprites)
            self.opponent_ui.monster = self.opponent
        else:
            self.apply_attack(self.monster, choice(self.opponent.abilities))
            self.timers['opponent end'].activate()

    def player_turn(self):
        self.player_active = True
        if self.monster.health <= 0:
            avail = [m for m in self.player_monsters if m.health > 0]
            if avail:
                self.monster.kill()
                self.monster = avail[0]
                self.all_sprites.add(self.monster)
                self.ui.monster = self.monster
            else:
                if 'music' in self.audio: self.audio['music'].stop()
                self.running = False

    def update_timers(self):
        for timer in self.timers.values(): timer.update()

    def run(self):
        self.setup()
        self.running = True
        if 'music' in self.audio: self.audio['music'].play(-1)

        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.update_timers()
            self.all_sprites.update(dt)
            if self.player_active: self.ui.update()
            
            self.display_surface.blit(self.bg_surfs['bg'], (0,0))

            player_floor_rect = self.bg_surfs['floor'].get_rect(center = self.monster.rect.midbottom + pygame.Vector2(0, -10))
            self.display_surface.blit(self.bg_surfs['floor'], player_floor_rect)

            opp_floor_rect = self.bg_surfs['floor'].get_rect(center = self.opponent.rect.midbottom + pygame.Vector2(0, -10))
            self.display_surface.blit(self.bg_surfs['floor'], opp_floor_rect)
            
            self.all_sprites.draw(self.display_surface)
            self.ui.draw()
            self.opponent_ui.draw()
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.game_menu()