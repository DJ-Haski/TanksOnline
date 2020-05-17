import pygame
import json
from GameSet import screen, clock, FPS, small_font, medium_font,large_font, poster
    #,bt_sd
from TankControll import ButtonPressed
from SoloGame import solo
repeat = True
gamemode = ''

def start(txt):
    #bt_sd.play()
    if txt == 'Solo game': return 's'
    #if txt == 'Multiplayer': return 'm'

def menu():
    global screen, clock, gamemode
    hello_text = ''
    hello_text = large_font.render(hello_text, True, (50, 50, 50))
    buttons = []
    solo = ButtonPressed('Solo game', 100, 500, large_font, (0, 0, 0), (125, 255, 125), (10, 100, 10), start)
    buttons.append(solo)
    Mplayer = ButtonPressed('Multiplayer', 430, 500, large_font, (0, 0, 0), (255, 255, 0), (10, 100, 10), start)
    buttons.append(Mplayer)
    auto = ButtonPressed('AI - Mod', 800, 500, large_font, (0, 0, 0), (255, 125, 125), (10, 100, 10), start)
    buttons.append(auto)
    """ auto = ButtonPressed('Controls', 900, 500, large_font, (0, 0, 0), (255, 125, 125), (10, 100, 10), start)
    buttons.append(auto)"""

    menuloop = True
    while menuloop:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menuloop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menuloop = False
            pos = pygame.mouse.get_pos()
            for button in buttons:
                dist_x = pos[0] - button.button_x
                dist_y = pos[1] - button.button_y
                if 0 <= dist_x <= button.button_w and 0 <= dist_y <= button.button_h:
                    button.is_active = True
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        gamemode = button.run(button.text)
                        menuloop = False
                else:
                    button.is_active = False

        screen.blit(poster, (0, 0))
        screen.blit(hello_text, (screen.get_size()[0] // 2 - hello_text.get_size()[0] // 2, 80))
        for button in buttons:
            button.draw()

        pygame.display.flip()

def again(winner, lost, kicked):
    global repeat
    if kicked:
        text = large_font.render("You were kicked!", True, (10, 10, 10))
    elif lost:
        text = large_font.render("You lost!", True, (10, 10, 10))
    elif winner != '':
        text = large_font.render(winner, True, (10, 10, 10))
    else:
        text = large_font.render("It's a draw!", True, (10, 10, 10))

    x = screen.get_size()[0] // 2 - text.get_size()[0] // 2
    y = screen.get_size()[1] // 2 - text.get_size()[1] // 2

    text_r = medium_font.render('Press R to play again', True, (150, 150, 150))
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

        screen.fill((255, 255, 255))
        screen.blit(text, (x, y))
        screen.blit(text_r, (x1, y1))
        pygame.display.flip()

while repeat:
    repeat = False
    gamemode = ''
    game_over = False
    menu()
    if gamemode == 's': game_over, winner, lost, kicked = solo()
    if game_over: again(winner, lost, kicked)

pygame.quit()