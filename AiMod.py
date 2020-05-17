import pygame
from Settings import screen, clock, FPS, l_font, m_font, s_font, shoot_sound, explosion_sound,bg
from TankRpcClient import RpcClient
from Events import RoomEvents
from TankDrawScript import draw_tank, draw_bullet, drawScoreboard
Checker = 300
#Направление
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
# Часть из ОНЛАЙНА
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
