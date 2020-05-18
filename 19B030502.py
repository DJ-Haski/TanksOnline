import pika
import uuid
import json
import pygame
import random
from threading import Thread
from enum import Enum

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
FPS = 30
screen = pygame.display.set_mode((1200, 640))
icon = pygame.image.load('TanksRss/Tank1.png')
pygame.display.set_icon(icon)
pygame.display.set_caption('Tanks by DJHaski 2D V1.0')

#Изображения-----------------------------------------------------------------------------

bg = pygame.image.load('TanksRss/B1.png')
poster = pygame.image.load('TanksRss/PosterByDJHaski.png')
tank1 = pygame.image.load('TanksRss/Tank1.png')#ЦВЕТ ТАНКА (62, 132, 45)
tank2 = pygame.image.load('TanksRss/Tank1.png') # перересовть танк 1 под анимацию и сделать квадратным.

#-------------------------------------------------

tankAnim = (tank1, tank2)
# для анимации
wall1 = pygame.image.load('TanksRss/Wall2.png')
box1 = pygame.image.load('TanksRss/Box2.png')

#Звуки-----------------------------------------------------------------------------

explosion_sound = pygame.mixer.Sound('TanksRss/Sounds/explosion.wav')
explosion_sound.set_volume(0.1)
shoot_sound = pygame.mixer.Sound('TanksRss/Sounds/bullet.wav')
shoot_sound.set_volume(0.1)
button_sound = pygame.mixer.Sound('TanksRss/Sounds/button.wav')
button_sound.set_volume(0.2)

#Шрифты. Roboto не является базовым шрифтом. При проблемах изменить на удобный или скачать----

s_font = pygame.font.SysFont('Roboto', 12, bold=True)
m_font = pygame.font.SysFont('Roboto', 24, bold=True)
l_font = pygame.font.SysFont('Roboto', 48, bold=True)

repeat = True
Gmode = ''

Checker = 300

class RpcClient():

    def __init__(self):
        self.credentials = pika.PlainCredentials('dar-tanks', password='5orPLExUYnyVYZg48caMpX')
        self.parameters = pika.ConnectionParameters('34.254.177.17', 5672, 'dar-tanks', self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True, auto_delete=True)
        self.callback_queue = result.method.queue
        self.channel.exchange_declare('X:routing.topic', 'topic', durable=True)

        self.channel.queue_bind(exchange='X:routing.topic', queue=self.callback_queue)
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.token = None
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self, key, msg=''):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='X:routing.topic',
            routing_key=key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id),
            body=msg
        )
        while self.response is None:
            self.connection.process_data_events()

    def room_register(self, room):
        request = json.dumps({'roomId': room})
        self.call('tank.request.register', request)
        try:
            self.token = self.response['token']
        except:
            pass
        return self.response

    def turn_tank(self, direction):
        request = json.dumps({'token': self.token, 'direction': direction})
        self.call('tank.request.turn', request)
        return self.response

    def fire(self):
        request = json.dumps({'token': self.token})
        self.call('tank.request.fire', request)
        return self.response
class RoomEvents(Thread):
    def __init__(self, room):
        super().__init__()
        self.room = room
        self.ready = False
        self.kill = False
        self.response = None
        self.new = False

#isRunning-----------------------------------------------------------------------------------------

    def run(self):
        self.credentials = pika.PlainCredentials('dar-tanks', password='5orPLExUYnyVYZg48caMpX')
        self.parameters = pika.ConnectionParameters('34.254.177.17', 5672, 'dar-tanks', self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True, auto_delete=True)
        self.events_queue = result.method.queue
        self.channel.exchange_declare('X:routing.topic', 'topic', durable=True)
        self.channel.queue_bind(exchange='X:routing.topic', queue=self.events_queue, routing_key=f'event.state.{self.room}')


        def on_response(ch, method, props, body):
            if self.kill:
                raise Exception('Consumer thread is killed')
            self.response = json.loads(body)
            self.new = True
            self.ready = True
        self.channel.basic_consume(
            queue=self.events_queue,
            on_message_callback=on_response,
            auto_ack=True)
        try:
            self.channel.start_consuming()
        except Exception as e:
            print(e)
_max_lifes = 10
class Direction(Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

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
#Стены----------------------------------------------------------------------
class Wall:

    def __init__(self, coord):
        self.image = wall1
        self.size = self.image.get_size()
        self.coord = coord

    def draw(self):
        screen.blit(self.image, self.coord)
#Кнопк---------------------------------------------------------------------
class AI:
    def __init__(self, name):
        self.name = name
        self.fire = False
        self.turn_direction = 'UP'

    def start(self, tanks, bullets):
        me = next((x for x in tanks if x['id'] == self.name), None)
        if not me: return
        bullets = [i for i in bullets if i['owner'] != self.name]
        warning = [] # Опасность, пуля либо танк
        sense = create_rect(100, **me)
        for bullet in bullets:
            bullet_rects = create_rect(100, **bullet)
            dist_x = bullet['x'] - me['x']
            dist_y = bullet['y'] - me['y']

            if bullet['direction'] == 'UP' and\
                    (me['direction'] == 'UP' or me['direction'] == 'DOWN'):
                if 0 < dist_y < Checker + me['height'] and\
                        -bullet['width'] < dist_x < me['width']:
                    direction = 'RIGHT' \
                        if dist_x + bullet['width'] // 2 < me['width'] // 2 \
                        else 'LEFT'
                    warning.append({'distance': dist_y - me['height'], 'turn': direction})
                    self.turn_direction = direction

            elif bullet['direction'] == 'DOWN' and\
                    (me['direction'] == 'UP' or me['direction'] == 'DOWN'):
                if -bullet['height'] - Checker < dist_y < 0 and\
                        -bullet['width'] < dist_x < me['width']:
                    direction = 'RIGHT'\
                        if dist_x + bullet['width'] // 2 < me['width'] // 2 \
                        else 'LEFT'
                    warning.append({'distance': -dist_y - bullet['height'], 'turn': direction})
                    self.turn_direction = direction

            elif bullet['direction'] == 'LEFT' and\
                    (me['direction'] == 'LEFT' or me['direction'] == 'RIGHT'):
                if 0 < dist_x < Checker + me['width'] and\
                        -bullet['height'] < dist_y < me['height']:
                    direction = 'DOWN' \
                        if dist_y + bullet['height'] // 2 < me['height'] // 2 \
                        else 'UP'
                    warning.append({'distance': dist_x - me['width'], 'turn': direction})
                    self.turn_direction = direction

            elif bullet['direction'] == 'RIGHT' and\
                    (me['direction'] == 'LEFT' or me['direction'] == 'RIGHT'):
                if -Checker - bullet['width'] < dist_x < 0 and\
                        -bullet['height'] < dist_y < me['height']:
                    direction = 'DOWN' \
                        if dist_y + bullet['height'] // 2 < me['height'] // 2 \
                        else 'UP'
                    warning.append({'distance': -dist_x - bullet['width'], 'turn': direction})
                    self.turn_direction = direction

            elif any(sense[i].colliderect(bullet_rects[i]) for i in range(10)):
                direction = opposite_direction(me['direction'])
                warning.append({'distance': 0, 'turn': direction})
                self.turn_direction = direction

        for tank in tanks:
            dist_x = tank['x'] - me['x']
            dist_y = tank['y'] - me['y']
            if tank['direction'] == 'UP' and\
                    me['direction'] == 'DOWN':
                if 0 < dist_y < Checker + me['height'] and\
                        -tank['width'] < dist_x < me['width']:
                    direction = 'RIGHT' \
                        if dist_x + tank['width'] // 2 < me['width'] // 2\
                        else 'LEFT'
                    warning.append({'distance': dist_y - me['height'], 'turn': direction})
                    self.fire = True
                    self.turn_direction = direction

            elif tank['direction'] == 'DOWN' and\
                    me['direction'] == 'UP':
                if -tank['height'] - Checker < dist_y < 0 and\
                        -tank['width'] < dist_x < me['width']:
                    direction = 'RIGHT' \
                        if dist_x + tank['width'] // 2 < me['width'] // 2 \
                        else 'LEFT'
                    warning.append({'distance': -dist_y - tank['height'], 'turn': direction})
                    self.fire = True
                    self.turn_direction = direction

            elif tank['direction'] == 'LEFT' and\
                    me['direction'] == 'RIGHT':
                if 0 < dist_x < Checker + me['width'] and\
                        -tank['height'] < dist_y < me['height']:
                    direction = 'DOWN' \
                        if dist_y + tank['height'] // 2 < me['height'] // 2 \
                        else 'UP'
                    warning.append({'distance': dist_x - me['width'], 'turn': direction})
                    self.fire = True
                    self.turn_direction = direction

            elif tank['direction'] == 'RIGHT' and\
                    me['direction'] == 'LEFT':
                if -Checker - tank['width'] < dist_x < 0 and\
                        -tank['height'] < dist_y < me['height']:
                    direction = 'DOWN' \
                        if dist_y + tank['height'] // 2 < me['height'] // 2 \
                        else 'UP'
                    warning.append({'distance': -dist_x - tank['width'], 'turn': direction})
                    self.fire = True
                    self.turn_direction = direction

def start(txt):
    button_sound.play()
    if txt == 'Solo Game':
        map()
        return 'solo'#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    if txt == 'Online       ': return 'online'#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    if txt == 'AI mod      ': return 'aiM'#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    if txt == 'Quit          ': pygame.quit()

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

def drawScoreboard(name, tanks, room):
    global screen
    pygame.draw.rect(screen, (255, 255, 255), (1000, 0, 200, 600))
    pygame.draw.line(screen, (0, 0, 0), (1000, 0), (1000, 600), 2)
    info_text = m_font.render('Scoreboard', True, (0, 0, 0))
    screen.blit(info_text, (1100 - info_text.get_size()[0] // 2, 10))

    tanks.sort(key=lambda x: x['score'], reverse=True)
    prev_y = 10 + info_text.get_size()[1]
    for tank in tanks:
        t_name = 'You' if tank['id'] == name else tank['id']
        score_text = s_font.render("{}: {}, {} HP".format(t_name, tank['score'], tank['health']), True, (0, 0, 0))
        screen.blit(score_text, (1100 - score_text.get_size()[0] // 2, prev_y + 10))
        prev_y += score_text.get_size()[1]

    CRoom = s_font.render(f"You in room number {room[5:]}", True, (0, 0, 0))
    screen.blit(CRoom, (1100 - CRoom.get_size()[0] // 2, screen.get_size()[1] - CRoom.get_size()[1] - 10))
def draw_tank(seconds, name, x, y, id, width, height, direction, **kwargs):
    color = (255, 0, 0) if id == name else (0, 255, 0)
    cur_image = int(seconds * 30) % len(tankAnim)
    body = pygame.Surface((width, height))
    pygame.draw.rect(body, color, (0, 0, width, height))
    body.set_colorkey((255, 255, 255))
    body.blit(tankAnim[cur_image], (0, 0))

    if direction == 'RIGHT':
        body = pygame.transform.rotate(body, -90)
    if direction == 'LEFT':
        body = pygame.transform.rotate(body, 90)
    if direction == 'UP':
        body = pygame.transform.rotate(body, 0)
    if direction == 'DOWN':
        body = pygame.transform.rotate(body, 180)
    screen.blit(body, (x, y))

    txt = s_font.render('YOU' if id == name else id, True, (0, 0, 0))
    screen.blit(txt, (x + width // 2 - txt.get_size()[0] // 2, y + width + 2))
def draw_bullet(name, x, y, owner, width, height, **kwargs):
    color = (168, 19, 19) if owner == name else (0, 0, 0)
    pygame.draw.rect(screen, color, (x, y, width, height))



def opposite_direction(direction):
    if direction == 'LEFT':
        return 'RIGHT'
    if direction == 'RIGHT':
        return 'LEFT'
    if direction == 'UP':
        return 'DOWN'
    if direction == 'DOWN':
        return 'UP'


def create_rect(speed, x, y, width, height, direction, **kwargs):
    rects = []
    for i in range(1, 11):
        if direction == 'LEFT':
            rects.append(pygame.Rect(int(x - speed * i / 10), y, width, height))
        if direction == 'RIGHT':
            rects.append(pygame.Rect(int(x + speed * i / 10), y, width, height))
        if direction == 'UP':
            rects.append(pygame.Rect(x, int(y - speed * i / 10), width, height))
        if direction == 'DOWN':
            rects.append(pygame.Rect(x, int(y + speed * i / 10), width, height))
    return rects
# Искусственный интелект, но туповатый. ( очень )


# Часть из ОНЛАЙНА

def checkCollisions(obj1, obj2, is_list1, is_list2):
    return pygame.Rect(obj1.coord if is_list1 else (obj1.x, obj1.y), obj1.size).colliderect(pygame.Rect(obj2.coord if is_list2 else (obj2.x, obj2.y), obj2.size))


def opposite_direction(direction):
    if direction == 'LEFT':
        return 'RIGHT'
    if direction == 'RIGHT':
        return 'LEFT'
    if direction == 'UP':
        return 'DOWN'
    if direction == 'DOWN':
        return 'UP'


def create_rect(speed, x, y, width, height, direction, **kwargs):
    rects = []
    for i in range(1, 11):
        if direction == 'LEFT':
            rects.append(pygame.Rect(int(x - speed * i / 10), y, width, height))
        if direction == 'RIGHT':
            rects.append(pygame.Rect(int(x + speed * i / 10), y, width, height))
        if direction == 'UP':
            rects.append(pygame.Rect(x, int(y - speed * i / 10), width, height))
        if direction == 'DOWN':
            rects.append(pygame.Rect(x, int(y + speed * i / 10), width, height))
    return rects
# Искусственный интелект, но туповатый. ( очень )


# Часть из ОНЛАЙНА

def checkCollisions(obj1, obj2, is_list1, is_list2):
    return pygame.Rect(obj1.coord if is_list1 else (obj1.x, obj1.y), obj1.size).colliderect(pygame.Rect(obj2.coord if is_list2 else (obj2.x, obj2.y), obj2.size))


def map():
    f = open('TanksRss/Maps/map2.txt', 'w')
    w = 20 # перепутал w и  h
    h = 36
    i = 0
    j = 0
    counter = 0
    while i < w:
        while j < h:
            if random.randint(1,5) != 5:
                if counter<2 and random.randint(1,100) == 10:
                    print("P", end="")
                    f.write('P')
                    counter=counter+1
                else:
                    print(" ",end="")
                    f.write(' ')
            else:
                print("W",end="")
                f.write('W')
            j=j+1
        i=i+1
        print()
        f.write('\n')
        j=0
    f.close()

def solo():
    global clock, screen
    bullets, tanks, walls = [], [], []
    spawnpoints = []
    free_spaces = []
    #
    # КАРТЫ МЕНЯТЬ В РУЧНУЮ 1-10 #UPD добавил генератор на вторую карту, меняется всегда.
    #
    #.txt формат. W - walls, P - players, Пробел = Пробел :/
    # Карты 38x20 символов
    with open('TanksRss/Maps/map2.txt') as map:
        lines = map.readlines()
        i = 0
        for line in lines:
            j = 0
            for symb in line:
                if symb == 'W':
                    walls.append(Wall([j*32, i*32]))
                elif symb == 'P':
                    spawnpoints.append([j*32, i*32])
                elif symb == ' ':
                    free_spaces.append([j*32, i*32])
                j += 1
            i += 1
    tank1 = Tank(spawnpoints[0][0], spawnpoints[0][1], 800//6, (62, 132, 45), 32, 'Player 1', fire=pygame.K_RETURN) #ЦВЕТ ТАНКА (62, 132, 45)
    tank2 = Tank(spawnpoints[1][0], spawnpoints[1][1], 800//6, (62, 132, 45), 32, 'Player 2', #ЦВЕТ ТАНКА (62, 132, 45)
                 d_right=pygame.K_d,
                 d_left=pygame.K_a,
                 d_up=pygame.K_w,
                 d_down=pygame.K_s)
    tanks += [tank1, tank2]
    box = 0,0
    cycle = 0
    winner = ''
    game_over = False
    mainloop = True
    while mainloop:
        millis = clock.tick(FPS)
        seconds = millis / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
                    game_over = True
                for tank in tanks:
                    if event.key == tank.fire_key:
                        bullets.append(Bullet(tank))

        pressed = pygame.key.get_pressed()
        for tank in tanks:
            # print(tank.direction)
            # stay = True
            for key in tank.KEY.keys():
                if pressed[key]:
                    tank.changeDirection(tank.KEY[key])
                    tank.is_static = False
                    # stay = False
            # if stay:
            #     tank.is_static = True

        screen.fill((200, 150, 200))
        screen.blit(bg, (0, 0))
        for wall in walls:
            wall.draw()


        for i in range(len(tanks)):
            tanks[i].move(seconds, box, tanks)
            txt = s_font.render(f'{tanks[i].name}: {tanks[i].lifes} lifes, {tanks[i].score} points', True, (0, 0, 0))
            screen.blit(txt, (5, i*txt.get_size()[1] + 5))
            for j in range(len(walls)):
                if checkCollisions(tanks[i], walls[j], False, True):
                    tanks[i].lifes -= 1
                    del walls[j]
                    break
            for j in range(len(bullets)):
                if checkCollisions(tanks[i], bullets[j], False, False):
                    explosion_sound.play()
                    bullets[j].tank.score += 1
                    tanks[i].lifes -= 1
                    del bullets[j]
                    break
            if tanks[i].lifes <= 0:
                del tanks[i]
                break

        for i in range(len(bullets)):
            bullets[i].move(seconds)
            if bullets[i].lifetime > bullets[i].destroytime:
                del bullets[i]
                break
            for j in range(len(walls)):
                if checkCollisions(bullets[i], walls[j], False, True):
                    bullets[i].lifetime = 10
                    del walls[j]
                    break

        pygame.display.flip()

        if len(tanks) == 0:
            winner = ''
            game_over = True
            mainloop = False
        if len(tanks) == 1:
            win_tank = tanks[0]
            winner = f'Congrats! Score: {win_tank.score}. Winner(-s): {win_tank.name}'
            game_over = True
            mainloop = False

    return game_over, winner, False, False

def online():
    global clock, screen
    screen = pygame.display.set_mode((1200, 640))
    rpc = RpcClient()
    rpc_response = {}
    for i in range(1, 31):
        rpc_response = rpc.room_register(f'room-{i}')
        if rpc_response.get('status', 200) == 200: break
        else: print(rpc_response)
    room, name = rpc_response['roomId'], rpc_response['tankId']
    room_state = RoomEvents(room)
    room_state.start()

#КНОПОЧКИ------------------------------------

    KEYS = {
        pygame.K_w: 'UP',
        pygame.K_a: 'LEFT',
        pygame.K_d: 'RIGHT',
        pygame.K_s: 'DOWN'
    }

#СТРЕЛЬБА.

    FIRE_KEY = pygame.K_SPACE

    counter = 0
    seconds = 0
    winner = ''
    lost = False
    kicked = False
    game_over = False
    mainloop = True
    while mainloop:
        millis = clock.tick(FPS)
        seconds += millis / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
                    game_over = True
                if event.key == FIRE_KEY:
                    rpc_response = rpc.fire()
                if event.key in KEYS:
                    direction = KEYS[event.key]
                    rpc_response = rpc.turn_tank(direction)

#ЗАГРУЗКА

        if not room_state.ready:
            wait_text = 'Hold on.Game is Loading...'
            wait_text = l_font.render(wait_text, True, (250, 250, 250))

            screen.fill((0, 0, 0)) #НАРИСОВАТЬ ЗАГР. ЭКРАН!


            text_rect = wait_text.get_rect(center=(screen.get_size()[0] // 2, screen.get_size()[1] // 2))
            screen.blit(wait_text, text_rect)

        elif room_state.response:
            screen.fill((125,125, 125))
            screen.blit(bg, (0, 0))
            cur_state = room_state.response
            tanks = cur_state['gameField']['tanks']
            bullets = cur_state['gameField']['bullets']

            remaining_time = cur_state.get('remainingTime', 0)
            text = m_font.render(f'Time Left: {remaining_time}', True, (255, 0, 0))

            text_rect = text.get_rect(center=(600, 75))
            screen.blit(text, text_rect)

#ТАБЛИЦА СЧЕТА, НЕ ТРОГАТЬ, МОГУТ БЫТЬ ОШИБКИ

            drawScoreboard(name, tanks, room)
            for tank in tanks:
                draw_tank(seconds, name, **tank)

#СТРЕЛЬБА

            for bullet in bullets:
                draw_bullet(name, **bullet)
            if len(bullets) > counter: shoot_sound.play(maxtime=1600)
            counter = len(bullets)

#ЗВУК ПОПАДАНИЯ

            if room_state.new and cur_state['hits']:
                room_state.new = False
                explosion_sound.play()

#ПРОИГРАВШИЕ

            if next((x for x in cur_state['losers'] if x['tankId'] == name), None):
                lost = True
                mainloop = False
                game_over = True

#КИКНУТЫЕ

            elif next((x for x in cur_state['kicked'] if x['tankId'] == name), None):
                kicked = True
                mainloop = False
                game_over = True

#ПОБЕДИТЕЛИ

            elif cur_state['winners']:
                mainloop = False
                game_over = True
                win_text = 'Good game! Winner with score: {} is : '.format(cur_state["winners"][0]["score"])
                winner = win_text + ', '.join(map(lambda i: i['tankId'] if i['tankId'] != name else 'YOU', cur_state['winners']))

            elif not next((x for x in tanks if x['id'] == name), None):
                lost = True
                mainloop = False
                game_over = True

        pygame.display.flip()

#ВОЗВРАТ В МЕНЮ ПОСЛЕ ИГРЫ

    room_state.kill = True
    room_state.join()
    screen = pygame.display.set_mode((1200, 640))
    return game_over, winner, lost, kicked

def aiM():
    global clock, screen
    screen = pygame.display.set_mode((1200, 640))

    rpc = RpcClient()
    rpc_response = {}
    for i in range(1, 31):
        rpc_response = rpc.room_register(f'room-{i}')
        if rpc_response.get('status', 200) == 200: break
        else: print(rpc_response)
    room, name = rpc_response['roomId'], rpc_response['tankId']
    room_state = RoomEvents(room)
    room_state.start()

    ai = AI(name)

    counter = 0
    seconds = 0

    winner = ''
    lost = False
    kicked = False
    game_over = False
    mainloop = True
    while mainloop:
        millis = clock.tick(FPS)
        seconds += millis / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
                    game_over = True

        if not room_state.ready:
            wait_text = 'Wait, loading in progress.'
            wait_text = l_font.render(wait_text, True, (255, 255, 255))
            screen.fill((50, 50, 50))
            text_rect = wait_text.get_rect(center=(screen.get_size()[0] // 2, screen.get_size()[1] // 2))
            screen.blit(wait_text, text_rect)

        elif room_state.response:
            screen.fill((200, 200, 200))
            screen.blit(bg, (0, 0))
            cur_state = room_state.response
            tanks = cur_state['gameField']['tanks']
            bullets = cur_state['gameField']['bullets']

            ai.start(tanks, bullets)
            if ai.fire:
                rpc_response = rpc.fire()
                ai.fire = False
            if ai.turn_direction:
                print(ai.turn_direction)
                rpc_response = rpc.turn_tank(ai.turn_direction)
                ai.turn_direction = ''

            remaining_time = cur_state.get('remainingTime', 0)
            text = m_font.render(f'Remaining time: {remaining_time}', True, (0, 0, 0))
            text_rect = text.get_rect(center=(400, 50))
            screen.blit(text, text_rect)

            drawScoreboard(name, tanks, room)
            for tank in tanks:
                draw_tank(seconds, name, **tank)

            for bullet in bullets:
                draw_bullet(name, **bullet)
            if len(bullets) > counter: shoot_sound.play(maxtime=1600)
            counter = len(bullets)

            if room_state.new and cur_state['hits']:
                room_state.new = False
                explosion_sound.play()

            if next((x for x in cur_state['losers'] if x['tankId'] == name), None):
                lost = True
                mainloop = False
                game_over = True

            elif next((x for x in cur_state['kicked'] if x['tankId'] == name), None):
                kicked = True
                mainloop = False
                game_over = True

            elif cur_state['winners']:
                mainloop = False
                game_over = True
                win_text = 'Congrats! Score: {}. Winner(-s): '.format(cur_state["winners"][0]["score"])
                winner = win_text + ', '.join(map(lambda i: i['tankId'] if i['tankId'] != name else 'You', cur_state['winners']))

            elif not next((x for x in tanks if x['id'] == name), None):
                lost = True
                mainloop = False
                game_over = True
        pygame.display.flip()
    room_state.kill = True
    room_state.join()
    screen = pygame.display.set_mode((1200, 640))
    return game_over, winner, lost, kicked


"""
НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
"""
#Главное меню --------------------------------------------------------------------


def menu():
    global screen, clock, Gmode
    buttons = []
    solo = Button('Solo Game', 100, 200, l_font, (0, 0, 0), (100, 255, 100), (16, 128, 16), start)
    buttons.append(solo)#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    online = Button('Online       ', 100, 250, l_font, (0, 0, 0), (200, 200, 50), (128, 128, 16), start)
    buttons.append(online)#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    aiM = Button('AI mod      ', 100, 300, l_font, (0, 0, 0), (100, 100, 255), (16, 16, 128), start)
    buttons.append(aiM)#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    quit = Button('Quit          ', 100, 350, l_font, (0, 0, 0), (255, 100, 100), (128, 16, 16), start)
    buttons.append(quit)#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    LoopMenu = True
    while LoopMenu:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                LoopMenu = False
            pos = pygame.mouse.get_pos()
            for button in buttons:
                dist_x = pos[0] - button.button_x
                dist_y = pos[1] - button.button_y
                if 0 <= dist_x <= button.button_w and 0 <= dist_y <= button.button_h:
                    button.is_active = True
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        Gmode = button.run(button.text)
                        LoopMenu = False
                else:
                    button.is_active = False

        screen.blit(poster, (0, 0))
        for button in buttons:
            button.draw()

        pygame.display.flip()

def again(winner, lost, kicked):
    global repeat
    if kicked:
        text = m_font.render("You timed outed!", True, (10, 10, 10))
    elif lost:
        text = m_font.render("Sorry,You lost!", True, (10, 10, 10))
    elif winner != '':
        text = m_font.render(winner, True, (10, 10, 10))
    else:
        text = m_font.render("GAME OVER", True, (10, 10, 10))
    x = screen.get_size()[0] // 2 - text.get_size()[0] // 2
    y = screen.get_size()[1] // 2 - text.get_size()[1] // 2
    text_r = m_font.render('Press "R" key to reload session', True, (0, 0, 0))
    x1 = screen.get_size()[0] // 2 - text_r.get_size()[0] // 2
    y1 = y + text.get_size()[1] + 25

    rep_loop = True
    while rep_loop:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rep_loop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    rep_loop = False
                if event.key == pygame.K_r:
                    rep_loop = False
                    repeat = True

        screen.fill((200, 200, 200))
        screen.blit(text, (x, y))
        screen.blit(text_r, (x1, y1))
        pygame.display.flip()

while repeat:
    repeat = False
    Gmode = ''
    game_over = False
    menu()
    if Gmode == 'solo': game_over, winner, lost, kicked = solo()
    elif Gmode == 'online': game_over, winner, lost, kicked = online()
    elif Gmode == 'aiM': game_over, winner, lost, kicked = aiM()
    if game_over: again(winner, lost, kicked)

#Сингл
pygame.quit()
