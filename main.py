from Materials import *

surfaceSize = (1280,720)

pygame.init()
surface = pygame.display.set_mode(surfaceSize)

origin = (200,50)
rows = 10
cols = 10
space = 20

swatch = Swatch(surfaceSize, origin, rows, cols, space)

swatch.points[0].static = True
swatch.points[cols-1].static = True
swatch.points[cols*(rows-1)].static = True
swatch.points[-1].static = True

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    surface.fill((0,0,0))

    # TODO: allow user to cut lines

    swatch.update()
    swatch.draw(surface)

    pygame.display.flip()
