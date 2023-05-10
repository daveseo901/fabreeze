from Materials import *
from FPS import *
import time
from datetime import datetime

surfaceSize = (1280,900)

pygame.init()
surface = pygame.display.set_mode(surfaceSize)

origin = (200,50)
rows = 15
cols = 30
space = 10

swatch = Swatch(surfaceSize, origin, rows, cols, space)

swatch.points[0].static = True
swatch.points[cols-1].static = True
swatch.points[cols*(rows-1)].static = True
swatch.points[-1].static = True

running = True

clock = pygame.time.Clock()

fps = FPScounter((surfaceSize[0] - 200, 30), 100)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    surface.fill((0,0,0))

    # TODO: allow user to cut lines

    swatch.update()
    swatch.draw(surface)
    fps.draw(surface)

    pygame.display.flip()

    fps.clock.tick(60)

with open("log.txt", 'a') as file:
    now = datetime.now()
    timestamp = now.strftime("%m/%d/%Y %H:%M:%S")
    averageFPS = round(fps.average(), 2)
    file.write("{0} rows:{1} cols:{2} avg_fps:{3}\n".format(
        timestamp, rows, cols, averageFPS))
