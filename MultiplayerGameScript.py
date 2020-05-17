import pygame
from Settings import screen, clock, FPS, l_font, m_font, s_font, shoot_sound, explosion_sound,bg
from TankRpcClient import RpcClient
from Events import RoomEvents
from TankDrawScript import draw_tank, draw_bullet, drawScoreboard

#ОНЛАЙН--------------------------------------------------------

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
