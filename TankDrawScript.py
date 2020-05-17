import pygame
from Settings import screen, m_font, s_font, tankAnim
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