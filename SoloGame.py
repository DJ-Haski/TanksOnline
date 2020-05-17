import pygame
from Settings import screen, clock, FPS, s_font, poster, explosion_sound, button_sound, shoot_sound,bg
from TankHelperScript import Tank, Bullet, Wall, Direction, Button
from MapGenerator import map
# столкновения
def checkCollisions(obj1, obj2, is_list1, is_list2):
    return pygame.Rect(obj1.coord if is_list1 else (obj1.x, obj1.y), obj1.size).colliderect(pygame.Rect(obj2.coord if is_list2 else (obj2.x, obj2.y), obj2.size))

#Сингл
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
