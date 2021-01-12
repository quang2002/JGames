from os import path

import pygame

from vector import vector_t

THIS_FOLDER = path.dirname(path.abspath(__file__))

pygame.init()
pygame.font.init()

font = pygame.font.SysFont('Tahoma', 40)


class CJFight:
    sprites = {
        'background': pygame.image.load(path.join(THIS_FOLDER, 'sprites/background.jpg')),
        'heroes': {
            'turtle': pygame.image.load(path.join(THIS_FOLDER, 'sprites/hero-1.png')),
            'ninja': pygame.image.load(path.join(THIS_FOLDER, 'sprites/hero-2.png')),
        },
        'bullets': {
            'shuriken': pygame.image.load(path.join(THIS_FOLDER, 'sprites/bullet-shuriken.png')),
            'virus': pygame.image.load(path.join(THIS_FOLDER, 'sprites/bullet-virus.png')),
        },
        'monsters': {
            'cyclopes': pygame.image.load(path.join(THIS_FOLDER, 'sprites/monster-1.png')),
            'retarded': pygame.image.load(path.join(THIS_FOLDER, 'sprites/monster-2.png')),
            'squid': pygame.image.load(path.join(THIS_FOLDER, 'sprites/monster-3.png')),
            'rokurokubi': pygame.image.load(path.join(THIS_FOLDER, 'sprites/monster-4.png')),
        },
        'viruses': {
            'bad-1': pygame.image.load(path.join(THIS_FOLDER, 'sprites/virus-1.png')),
            'bad-2': pygame.image.load(path.join(THIS_FOLDER, 'sprites/virus-3.png')),
            'medicine': pygame.image.load(path.join(THIS_FOLDER, 'sprites/virus-2.png')),
        }
    }

    sounds = {
        'background': pygame.mixer.Sound(path.join(THIS_FOLDER, 'sounds/background.wav')),
        'bullet': pygame.mixer.Sound(path.join(THIS_FOLDER, 'sounds/bullet.wav')),
        'game-over': pygame.mixer.Sound(path.join(THIS_FOLDER, 'sounds/game-over.wav')),
        'hit': pygame.mixer.Sound(path.join(THIS_FOLDER, 'sounds/hit.wav')),
    }

    keys_state = {
        'A': False,
        'D': False,
    }

    texts = {
        'BLACK': {
            'PLAY': font.render('PLAY', False, (0, 0, 0)),
            'EXIT': font.render('EXIT', False, (0, 0, 0)),
            'RESUME': font.render('RESUME', False, (0, 0, 0)),
            'MAINMENU': font.render('BACK TO MAIN MENU', False, (0, 0, 0)),
            'AGAIN': font.render('PLAY AGAIN', False, (0, 0, 0)),
        },
        'RED': {
            'PLAY': font.render('PLAY', False, (255, 0, 0)),
            'EXIT': font.render('EXIT', False, (255, 0, 0)),
            'RESUME': font.render('RESUME', False, (255, 0, 0)),
            'MAINMENU': font.render('BACK TO MAIN MENU', False, (255, 0, 0)),
            'AGAIN': font.render('PLAY AGAIN', False, (255, 0, 0)),
        }
    }

    class GameState:
        MENU = 0
        PLAY = 1
        PAUSE = 2
        GAMEOVER = 3

    class Focus:
        NONE = 0

        class Menu:
            PLAY = 1
            EXIT = 2

        class Pause:
            RESUME = 1
            MAINMENU = 2

        class GameOver:
            PLAYAGAIN = 1
            MAINMENU = 2

    state = GameState.MENU
    focus = Focus.NONE

    screen = None
    player = None

    class CEntityBase:
        instances = []

        def __init__(self, position=vector_t(), velocity=vector_t(), collider=vector_t(), sprite=None):
            self.position = position
            self.velocity = velocity
            self.collider = collider
            self.sprite = sprite
            self.sprite_size = vector_t(sprite.get_size())
            CJFight.CEntityBase.instances.append(self)

            if collider == vector_t():
                self.collider = vector_t(sprite.get_size()) / 2

        def release(self):
            CJFight.CEntityBase.instances.remove(self)

        def render(self, screen):
            self.position += self.velocity
            real_pos = self.position + CJFight.get_origin() - self.sprite_size / 2
            screen.blit(self.sprite, real_pos.__tuple__())

        def __is_impact_single_side__(self, obj):
            vec = obj.position - self.position
            point = None
            if vec.x >= 0:
                point = self.position + self.collider
                if vec.y < 0:
                    point.y = point.y - 2 * self.collider.y
            else:
                point = self.position - self.collider
                if vec.y >= 0:
                    point.y = point.y + 2 * self.collider.y

            if obj.position.x - obj.collider.x <= point.x <= obj.position.x + obj.collider.x:
                if obj.position.y - obj.collider.y <= point.y <= obj.position.y + obj.collider.y:
                    return True
            return False

        def is_impact(self, obj):
            return self.__is_impact_single_side__(obj) or obj.__is_impact_single_side__(self)

    class CHero(CEntityBase):
        TYPE_TURTLE = 0
        TYPE_NINJA = 1

        speed = 4
        gravity = 5
        health = 100
        max_health = health

        def __init__(self, hero_type, position=vector_t(), velocity=vector_t()):
            super().__init__(
                position, velocity,
                sprite=CJFight.sprites['heroes']['turtle' if hero_type == CJFight.CHero.TYPE_TURTLE else 'ninja']
            )
            self.is_flip = False
            self.old_direction_x = -1
            self.max_height = 200
            self.max_jump_time = 200
            self.jump_time_counter = self.max_jump_time
            # triple-jump
            self.jump_time = 2

            self.screen = None

        def jump(self):
            if self.jump_time > 0:
                self.jump_time_counter = 0
                self.jump_time -= 1

        def attack(self):
            CJFight.CBullet(
                bullet_type=CJFight.CBullet.TYPE_SHURIKEN,
                position=self.position,
                direction=vector_t((1, 0) if self.is_flip else (-1, 0))
            )

        def render(self, screen):
            screen_size = vector_t(screen.get_size())
            self.position += self.velocity

            if self.jump_time_counter < self.max_jump_time:
                h_t = self.max_height / self.max_jump_time
                self.velocity.y = 4 * h_t * (2 * self.jump_time_counter / self.max_jump_time - 1)
                self.jump_time_counter += 1
            else:
                self.velocity.y = self.gravity

            if self.velocity.x * self.old_direction_x < 0:
                self.is_flip = not self.is_flip
                self.old_direction_x = self.velocity.x
                self.sprite = pygame.transform.flip(self.sprite, True, False)

            # check bound left
            if self.position.x - self.sprite_size.x / 2 < 0:
                self.position.x = self.sprite_size.x / 2

            # check bound right
            if self.position.x + self.sprite_size.x / 2 > screen_size.y * (2048 / 819):
                self.position.x = screen_size.y * (2048 / 819) - self.sprite_size.x / 2

            # check on ground
            if self.position.y + self.sprite_size.y / 2 > screen_size.y:
                self.position.y = screen_size.y - self.sprite_size.y / 2
                self.jump_time = 2

            # earn damage
            for entity in CJFight.CEntityBase.instances:
                if self != entity and self.is_impact(entity):
                    if isinstance(entity, CJFight.CBullet):
                        if entity.bullet_type == CJFight.CBullet.TYPE_VIRUS:
                            self.health -= 10
                            entity.release()
                            CJFight.sounds['hit'].stop()
                            CJFight.sounds['hit'].play()

            # check health
            real_pos = self.position + CJFight.get_origin() - self.sprite_size / 2
            pygame.draw.rect(screen, (255, 0, 0), (real_pos.x, real_pos.y - 25, self.sprite_size.x, 20))
            pygame.draw.rect(screen, (0, 255, 0),
                             (real_pos.x, real_pos.y - 25, self.health / self.max_health * self.sprite_size.x, 20))
            if self.health <= 0:
                self.release()
                CJFight.state = CJFight.GameState.GAMEOVER
                CJFight.sounds['background'].stop()
                CJFight.sounds['game-over'].play()

            screen.blit(
                self.sprite,
                ((screen_size.x - self.sprite_size.x) / 2, self.position.y - self.sprite_size.y / 2)
            )

    class CMonsterBase(CEntityBase):
        def __init__(self, health, attack_cooldown, sprite, position=vector_t()):
            super().__init__(position=position, sprite=sprite)
            self.health = health
            self.max_health = self.health
            self.attack_cooldown = attack_cooldown
            self.attack_tcounter = self.attack_cooldown

            self.is_flip = False
            self.old_direction_x = -1

        def attack(self):
            pass

        def render(self, screen):
            super().render(screen)
            if self.attack_tcounter < self.attack_cooldown:
                self.attack_tcounter += 1
            else:
                self.attack()
                self.attack_tcounter = 0

            if self.velocity.x * self.old_direction_x < 0:
                self.is_flip = not self.is_flip
                self.old_direction_x = self.velocity.x
                self.sprite = pygame.transform.flip(self.sprite, True, False)

            for entity in CJFight.CEntityBase.instances:
                if isinstance(entity, CJFight.CBullet):
                    if entity.bullet_type == CJFight.CBullet.TYPE_SHURIKEN and self.is_impact(entity):
                        self.health -= 10
                        entity.release()
            if self.health <= 0:
                self.release()

            real_pos = self.position + CJFight.get_origin() - self.sprite_size / 2
            pygame.draw.rect(screen, (255, 0, 0), (real_pos.x, real_pos.y - 25, self.sprite_size.x, 20))
            pygame.draw.rect(screen, (0, 255, 0),
                             (real_pos.x, real_pos.y - 25, self.health / self.max_health * self.sprite_size.x, 20))

    class CMonsterCyclopes(CMonsterBase):
        def __init__(self, position=vector_t((0, 0))):
            super().__init__(
                position=position,
                sprite=CJFight.sprites['monsters']['cyclopes'],
                health=100,
                attack_cooldown=100
            )
            self.speed = 1

        def attack(self):
            if self.is_impact(CJFight.player):
                CJFight.player.health -= 10
                CJFight.sounds['hit'].stop()
                CJFight.sounds['hit'].play()

        def render(self, screen):
            self.velocity.x = CJFight.player.position.x - self.position.x
            self.velocity.x = self.speed if self.velocity.x > 0 else -self.speed if self.velocity.x < 0 else self.speed
            self.velocity.y = 0

            self.position.y = CJFight.screen.get_size()[1] - self.sprite_size.y / 2
            super().render(screen)

    class CMonsterRetarded(CMonsterBase):
        def __init__(self, position=vector_t((0, 0))):
            super().__init__(
                position=position,
                sprite=CJFight.sprites['monsters']['retarded'],
                health=200,
                attack_cooldown=70
            )
            self.speed = 2

        def attack(self):
            if self.is_impact(CJFight.player):
                CJFight.player.health -= 5
                CJFight.sounds['hit'].stop()
                CJFight.sounds['hit'].play()

        def render(self, screen):
            self.velocity.x = CJFight.player.position.x - self.position.x
            self.velocity.x = self.speed if self.velocity.x > 0 else -self.speed if self.velocity.x < 0 else self.speed
            self.velocity.y = 0

            self.position.y = CJFight.screen.get_size()[1] - self.sprite_size.y / 2
            super().render(screen)

    class CBullet(CEntityBase):
        TYPE_SHURIKEN = 0
        TYPE_VIRUS = 1

        speed = 6

        def __init__(self, bullet_type, position, direction):
            super().__init__(
                position=position,
                sprite=CJFight.sprites['bullets'][
                    'shuriken' if bullet_type == CJFight.CBullet.TYPE_SHURIKEN else 'virus'],
                velocity=direction / direction.length() * self.speed
            )

            self.bullet_type = bullet_type

    def __init__(self, resolution):
        self.is_run = False
        self.resolution = vector_t(resolution)
        self.level = 1

        CJFight.screen = pygame.display.set_mode(resolution)
        pygame.display.set_caption('JGames - JFight')
        background_size = vector_t(self.sprites['background'].get_size())
        self.sprites['background'] = pygame.transform.scale(
            self.sprites['background'],
            (background_size * resolution[1] / background_size.y).__tuple__()
        )

    @staticmethod
    def get_origin():
        return vector_t((CJFight.screen.get_size()[0] // 2 - CJFight.player.position.x, 0))

    def reset(self):
        self.level = 1
        CJFight.CEntityBase.instances.clear()
        CJFight.player = CJFight.CHero(CJFight.CHero.TYPE_NINJA,
                                       position=vector_t((self.sprites['background'].get_size()[0] / 2, 0)))

        CJFight.CMonsterCyclopes()
        CJFight.CMonsterCyclopes(position=vector_t((500, 1)))

    def menu(self):
        self.screen.blit(self.sprites['background'],
                         (self.resolution.x // 2 - self.sprites['background'].get_size()[0] // 2, 0))

        texts_position = {
            'PLAY': (self.resolution.x // 2 - self.texts['BLACK']['PLAY'].get_size()[0] // 2, self.resolution.y // 2 - 40),
            'EXIT': (self.resolution.x // 2 - self.texts['BLACK']['EXIT'].get_size()[0] // 2, self.resolution.y // 2 + 40),
        }

        def in_area(text):
            text_pos = texts_position[text]
            text_size = self.texts['BLACK'][text].get_size()
            mouse_pos = pygame.mouse.get_pos()
            return text_pos[0] < mouse_pos[0] < text_pos[0] + text_size[0] and text_pos[1] < mouse_pos[1] < text_pos[1] + text_size[1]

        CJFight.focus = CJFight.Focus.NONE
        if in_area('PLAY'):
            self.screen.blit(self.texts['RED']['PLAY'], texts_position['PLAY'])
            CJFight.focus = CJFight.Focus.Menu.PLAY
        else:
            self.screen.blit(self.texts['BLACK']['PLAY'], texts_position['PLAY'])

        if in_area('EXIT'):
            self.screen.blit(self.texts['RED']['EXIT'], texts_position['EXIT'])
            CJFight.focus = CJFight.Focus.Menu.EXIT
        else:
            self.screen.blit(self.texts['BLACK']['EXIT'], texts_position['EXIT'])

    def play(self):
        # real - local = origin
        self.screen.blit(self.sprites['background'], (self.resolution.x // 2 - self.player.position.x, 0))
        self.screen.blit(
            font.render('LEVEL: {level}'.format(level=self.level), False, (255, 0, 0)),
            (20, 20)
        )

        counter = 0
        for entity in CJFight.CEntityBase.instances:
            entity.render(self.screen)
            if not isinstance(entity, (CJFight.CBullet, CJFight.CHero)):
                counter += 1
        if counter == 0:
            self.level += 1
            for _ in range(self.level):
                CJFight.CMonsterCyclopes(vector_t((0, 0)))


    def gameover(self):
        self.screen.blit(self.sprites['background'],
                         (self.resolution.x // 2 - self.sprites['background'].get_size()[0] // 2, 0))

        texts_position = {
            'AGAIN': (
            self.resolution.x // 2 - self.texts['BLACK']['AGAIN'].get_size()[0] // 2, self.resolution.y // 2 - 40),
            'MAINMENU': (
            self.resolution.x // 2 - self.texts['BLACK']['MAINMENU'].get_size()[0] // 2, self.resolution.y // 2 + 40),
        }

        def in_area(text):
            text_pos = texts_position[text]
            text_size = self.texts['BLACK'][text].get_size()
            mouse_pos = pygame.mouse.get_pos()
            return text_pos[0] < mouse_pos[0] < text_pos[0] + text_size[0] and text_pos[1] < mouse_pos[1] < text_pos[
                1] + text_size[1]

        CJFight.focus = CJFight.Focus.NONE
        if in_area('AGAIN'):
            self.screen.blit(self.texts['RED']['AGAIN'], texts_position['AGAIN'])
            CJFight.focus = CJFight.Focus.GameOver.PLAYAGAIN
        else:
            self.screen.blit(self.texts['BLACK']['AGAIN'], texts_position['AGAIN'])

        if in_area('MAINMENU'):
            self.screen.blit(self.texts['RED']['MAINMENU'], texts_position['MAINMENU'])
            CJFight.focus = CJFight.Focus.GameOver.MAINMENU
        else:
            self.screen.blit(self.texts['BLACK']['MAINMENU'], texts_position['MAINMENU'])

    def pause(self):
        self.screen.blit(self.sprites['background'],
                         (self.resolution.x // 2 - self.sprites['background'].get_size()[0] // 2, 0))

        texts_position = {
            'RESUME': (
                self.resolution.x // 2 - self.texts['BLACK']['RESUME'].get_size()[0] // 2, self.resolution.y // 2 - 40),
            'MAINMENU': (
                self.resolution.x // 2 - self.texts['BLACK']['MAINMENU'].get_size()[0] // 2,
                self.resolution.y // 2 + 40),
        }

        def in_area(text):
            text_pos = texts_position[text]
            text_size = self.texts['BLACK'][text].get_size()
            mouse_pos = pygame.mouse.get_pos()
            return text_pos[0] < mouse_pos[0] < text_pos[0] + text_size[0] and text_pos[1] < mouse_pos[1] < text_pos[
                1] + text_size[1]

        CJFight.focus = CJFight.Focus.NONE
        if in_area('RESUME'):
            self.screen.blit(self.texts['RED']['RESUME'], texts_position['RESUME'])
            CJFight.focus = CJFight.Focus.Pause.RESUME
        else:
            self.screen.blit(self.texts['BLACK']['RESUME'], texts_position['RESUME'])

        if in_area('MAINMENU'):
            self.screen.blit(self.texts['RED']['MAINMENU'], texts_position['MAINMENU'])
            CJFight.focus = CJFight.Focus.Pause.MAINMENU
        else:
            self.screen.blit(self.texts['BLACK']['MAINMENU'], texts_position['MAINMENU'])

    def render(self):
        self.screen.fill((0, 0, 0))
        if CJFight.state == CJFight.GameState.MENU:
            self.menu()
        elif CJFight.state == CJFight.GameState.PLAY:
            self.play()
        elif CJFight.state == CJFight.GameState.GAMEOVER:
            self.gameover()
        elif CJFight.state == CJFight.GameState.PAUSE:
            self.pause()

    def event_handler(self, e):
        if e.type == pygame.QUIT:
            self.is_run = False

        if CJFight.state == CJFight.GameState.PLAY:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: CJFight.state = CJFight.GameState.PAUSE
                if e.key == pygame.K_a: self.keys_state['A'] = True
                if e.key == pygame.K_d: self.keys_state['D'] = True
                if e.key == pygame.K_SPACE: self.player.jump()
                if e.key == pygame.K_RETURN:
                    CJFight.sounds['bullet'].stop()
                    CJFight.sounds['bullet'].play()
                    self.player.attack()
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_a: self.keys_state['A'] = False
                if e.key == pygame.K_d: self.keys_state['D'] = False

            self.player.velocity.x = 0
            if self.keys_state['A']: self.player.velocity.x -= self.player.speed
            if self.keys_state['D']: self.player.velocity.x += self.player.speed

        if CJFight.state == CJFight.GameState.MENU:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if CJFight.focus == CJFight.Focus.Menu.PLAY:
                    CJFight.state = CJFight.GameState.PLAY
                    self.reset()
                if CJFight.focus == CJFight.Focus.Menu.EXIT:
                    self.is_run = False

        if CJFight.state == CJFight.GameState.PAUSE:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if CJFight.focus == CJFight.Focus.Pause.RESUME:
                    CJFight.state = CJFight.GameState.PLAY
                if CJFight.focus == CJFight.Focus.Pause.MAINMENU:
                    CJFight.state = CJFight.GameState.MENU

        if CJFight.state == CJFight.GameState.GAMEOVER:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if CJFight.focus == CJFight.Focus.GameOver.PLAYAGAIN:
                    CJFight.state = CJFight.GameState.PLAY
                    CJFight.sounds['game-over'].stop()
                    CJFight.sounds['background'].play(loops=-1)
                    self.reset()
                if CJFight.focus == CJFight.Focus.GameOver.MAINMENU:
                    CJFight.state = CJFight.GameState.MENU
                    CJFight.sounds['game-over'].stop()
                    CJFight.sounds['background'].play(loops=-1)

    def run(self):
        self.is_run = True
        self.sounds['background'].play(loops=-1)
        while self.is_run:
            for e in pygame.event.get():
                self.event_handler(e)
            self.render()
            pygame.display.update()
        self.sounds['background'].stop()
