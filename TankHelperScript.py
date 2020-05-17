import pygame
from enum import Enum
import random
from Settings import screen, wall1, box1, s_font, shoot_sound, tankAnim

class Direction(Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

# Заряд -----------------------------------------
class Bullet:
    def __init__(self, tank):
        shoot_sound.play(maxtime=1600)
        self.tank = tank
        self.color = (255, 0, 0)
        self.width = 6 #ширина
        self.height = 12 #длина
        self.direction = tank.direction
        self.speed = int(tank.speed * 4)
        self.lifetime = 0
        self.destroytime = 4  # Время самоуничтожения заряда ( в секундах )
        # Направление танка # ПРАВО
        if tank.direction == Direction.RIGHT:
            self.x = tank.x + 3*tank.width//2
            self.y = tank.y + tank.width//2
            self.height, self.width = self.width, self.height
        # Направление танка # ЛЕВО
        if tank.direction == Direction.LEFT:
            self.x = tank.x - tank.width//2
            self.y = tank.y + tank.width//2
            self.height, self.width = self.width, self.height
        # Направление танка # ВВЕРХ
        if tank.direction == Direction.UP:
            self.x = tank.x + tank.width//2
            self.y = tank.y - tank.width//2
        # Направление танка # ВНИЗ
        if tank.direction == Direction.DOWN:
            self.x = tank.x + tank.width//2
            self.y = tank.y + 3*tank.width//2

        self.size = [self.width, self.height]
# отрисовка выстрела----------------------------------------------------------------
    def draw(self):
        pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))

    def move(self, sec):
        self.lifetime += sec

        if self.direction == Direction.RIGHT:
            self.x += int(self.speed * sec)

        if self.direction == Direction.LEFT:
            self.x -= int(self.speed * sec)

        if self.direction == Direction.UP:
            self.y -= int(self.speed * sec)

        if self.direction == Direction.DOWN:
            self.y += int(self.speed * sec)
        self.draw()
#Танки и стрельба-----------------------------------------------------------
_max_lifes = 10


class Tank:

    def __init__(self, x, y, speed, color, width, name, direction=Direction.UP, d_right=pygame.K_RIGHT, d_left=pygame.K_LEFT, d_up=pygame.K_UP, d_down=pygame.K_DOWN, fire=pygame.K_SPACE):
        self.x = x
        self.y = y
        self.speed = speed
        self.countdown = 0
        self.color = color
        self.width = width
        self.cur_image = 0
        self.images = tankAnim
        self.size = [self.width, self.width]
        self.name = name
        self.txt = s_font.render(str(name), True, (0, 0, 0))
        self.lifes = _max_lifes
        self.score = 0
        self.direction = direction
        self.is_static = True
        self.fire_key = fire

        self.KEY = {d_right: Direction.RIGHT, d_left: Direction.LEFT,
                    d_up: Direction.UP, d_down: Direction.DOWN}

    def draw(self):
        self.cur_image = (self.cur_image + 1) % len(self.images)
        body = pygame.Surface((self.width, self.width))
        pygame.draw.rect(body, self.color, (0, 0, self.width, self.width))
        body.set_colorkey((255, 255, 255))
        body.blit(self.images[self.cur_image], (0, 0))

        if self.direction == Direction.RIGHT:
            body = pygame.transform.rotate(body, -90)

        if self.direction == Direction.LEFT:
            body = pygame.transform.rotate(body, 90)

        if self.direction == Direction.UP:
            body = pygame.transform.rotate(body, 0)

        if self.direction == Direction.DOWN:
            body = pygame.transform.rotate(body, 180)

        screen.blit(body, (self.x, self.y))

    def changeDirection(self, direction):
        self.direction = direction

    def move(self, sec, box, tanks):
        if self.countdown > 0:
            self.countdown -= sec
        if not self.is_static:
            dx = 0
            dy = 0
            change = int(self.speed * sec)
            if self.direction == Direction.RIGHT:
                dx = change
                if self.x + dx > screen.get_size()[0]:
                    dx = -self.x - self.width

            if self.direction == Direction.LEFT:
                dx = -change
                if self.x + dx < -self.width:
                    dx = -self.x + screen.get_size()[0]

            if self.direction == Direction.UP:
                dy = -change
                if self.y + dy < -self.width:
                    dy = -self.y + screen.get_size()[1]

            if self.direction == Direction.DOWN:
                dy = change
                if self.y + dy > screen.get_size()[1]:
                    dy = -self.y - self.width

            # Other tanks
            future_pos = pygame.Rect(self.x + dx, self.y + dy, self.width, self.width)
            if not any([future_pos.colliderect(pygame.Rect(tank.x, tank.y, tank.width, tank.width))
                        for tank in tanks if self != tank]):
                self.x, self.y = self.x + dx, self.y + dy

            # Power box
        self.draw()


##########################################    Walls    ##########################################


class Wall:

    def __init__(self, coord):
        self.image = wall1
        self.size = self.image.get_size()
        self.coord = coord

    def draw(self):
        screen.blit(self.image, self.coord)


##########################################    Buttons    ##########################################


class Button:

    def __init__(self, text, button_x, button_y, font, txt_col, colour, act_colour, func, size='auto',
                 color_per=(100, 100, 100)):
        global screen
        self.is_active = False
        self.text = text
        self.button_x = button_x
        self.button_y = button_y
        self.font = font
        self.txt = font.render(str(text), True, txt_col)
        self.txt_col = txt_col
        self.colour = colour
        self.act_colour = act_colour
        self.color_per = color_per
        self.run = func
        w, h = self.txt.get_size()
        self.button_w = size[0] if size != 'auto' else w + 8
        self.button_h = size[1] if size != 'auto' else h + 8
        self.txt_x = button_x + self.button_w // 2 - w // 2
        self.txt_y = button_y + self.button_h // 2 - h // 2

    def draw(self):
        # self.txt = self.font.render(str(self.text), True, self.txt_col)
        colour = self.colour if not self.is_active else self.act_colour
        but = pygame.Surface((self.button_w, self.button_h))
        but.fill(colour)
        but.set_alpha(180)
        screen.blit(but, (self.button_x, self.button_y))
        # pygame.draw.rect(screen, colour, (self.button_x, self.button_y, self.button_w, self.button_h))
        pygame.draw.rect(screen, self.color_per, (self.button_x, self.button_y, self.button_w, self.button_h), 2)
        screen.blit(self.txt, (self.txt_x, self.txt_y))
