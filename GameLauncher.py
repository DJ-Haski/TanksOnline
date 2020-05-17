#База -----------------------------------------------------------------------------
import pygame
import json
from Settings import screen, clock, FPS, l_font, m_font, poster, button_sound,bg
from TankHelperScript import Button
from SoloGame import solo
from MultiplayerGameScript import online
from AiMod import aiM
from MapGenerator import map
repeat = True
Gmode = ''
def start(txt):
    button_sound.play()
    if txt == 'Solo Game':
        map()
        return 'solo'#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    if txt == 'Online       ': return 'online'#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    if txt == 'AI mod      ': return 'aiM'#НИ В КОЕМ СЛУЧАЕ НЕ ТРОГАТЬ ПРОБЕЛЫ В ТЕКСТЕ, ВСЕ СЛОМАЕТСЯ
    if txt == 'Quit          ': pygame.quit()
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
pygame.quit()
