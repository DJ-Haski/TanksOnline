import pygame
#База-----------------------------------------------------------------------
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

