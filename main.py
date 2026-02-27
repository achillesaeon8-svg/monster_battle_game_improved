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

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
        current_folder = 'MBGpedia'
        self.back_surfs = folder_importer(current_folder, 'images', 'front')
        self.front_surfs = folder_importer(current_folder, 'images', 'reverse')
        self.bg_surfs = folder_importer(current_folder, 'images', 'other')
        self.simple_surfs = folder_importer(current_folder, 'images', 'simple')
        self.attack_frames = tile_importer(4, current_folder, 'images', 'attacks')
        self.audio = audio_importer(current_folder, 'audio')

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