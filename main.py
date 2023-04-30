import pygame
import math
from pygame.math import Vector2

# TODO: move constants to another file

color = (240,240,240)

FRICTION = 0.95
GRAVITY = 9.8

surfaceSize = (1280,720)

# TODO: move class definitions to another file

class Point:
    def __init__(self, position: Vector2, static=False):
        self.position = position
        self.previousPosition = position
        self.radius = 3
        self.static = static
        self.clicked = False
        self.rightClicked = False

    def __sub__(self, b):
        return self.position - b.position

    def draw(self, surface):
        pygame.draw.circle(surface, color, self.position, self.radius)

    def update(self):
        if self.static or self.clicked:
            # self.previousPosition = self.position
            return
        # calculate velocity of point, use to update position
        velocity = self.position - self.previousPosition
        velocity.x *= FRICTION
        velocity.y += GRAVITY
        velocity.y *= FRICTION

        self.previousPosition = self.position
        self.position = self.position + velocity
        self.position.x = pygame.math.clamp(self.position.x, 0, surfaceSize[0])
        self.position.y = pygame.math.clamp(self.position.y, 0, surfaceSize[1])

    def drag(self, mousePosition):
        dist = (self.position - mousePosition).length()
        if dist < 10 or self.clicked:
            self.position = mousePosition
            self.clicked = True

    def toggleStatic(self, mousePosition):
        dist = (self.position - mousePosition).length()
        if dist < 10 and not self.rightClicked:
            self.static = not self.static
            self.rightClicked = True


class Line:
    def __init__(self, point1: Point, point2: Point):
        self.point1 = point1
        self.point2 = point2
        self.trueLength = (point2.position - point1.position).length()

    def draw(self, surface):
        pygame.draw.line(surface, color, self.point1.position, self.point2.position)

    def update(self):
        # calculate effect of line on points
        ELASTICITY = 0.95
        dPosition = self.point1 - self.point2
        length = dPosition.length()

        # if points overlap exactly, move them slightly
        if length == 0:
            if self.point2.previousPosition[0] < self.point2.position[0]:
                self.point2.position[0] -= 1
            elif self.point2.previousPosition[0] > self.point2.position[0]:
                self.point2.position[0] += 1

            if self.point2.previousPosition[1] < self.point2.position[1]:
                self.point2.position[1] -= 1
            elif self.point2.previousPosition[1] > self.point2.position[1]:
                self.point2.position[1] += 1

            dPosition = self.point1 - self.point2
            length = dPosition.length()


        dLength = self.trueLength - length
        delta = ELASTICITY * 0.5 * dPosition * dLength / length

        if not self.point1.static and not self.point1.clicked:
            self.point1.position += delta
        if not self.point2.static and not self.point2.clicked:
            self.point2.position -= delta


class Swatch:
    def __init__(self, origin, rows, cols, space):
        # create points
        self.points = []
        for i in range(rows):
            for j in range(cols):
                self.points.append(
                        Point(Vector2(origin[0] + space * j, origin[1] + space * i))
                    )

        for i in range(2, cols - 1):
            self.points[i].static = True

        # create lines
        # TODO: generate lines based on user input
        self.lines = []
        for ind, point in enumerate(self.points):
            x, y = point.position
            if x + space < origin[0] + space * cols:
                self.lines.append(Line(point, self.points[ind + 1]))
            if y + space < origin[1] + space * rows:
                self.lines.append(Line(point, self.points[ind + cols]))

        # currently selected point
        self.selected = None

    def draw(self, surface):
        for point in self.points:
            point.draw(surface)

        for line in self.lines:
            line.draw(surface)

    def update(self):
        for point in self.points:
            point.update()

        for line in self.lines:
            line.update()

    # handle events
    def events(self):
        # drag points
        if pygame.mouse.get_pressed()[0]:
            mouseTuple = pygame.mouse.get_pos()
            mousePosition = Vector2(mouseTuple[0], mouseTuple[1])
            # only drag the selected point
            if self.selected is not None:
                self.selected.drag(mousePosition)
            else:
                for point in self.points:
                    point.drag(mousePosition)
                    if point.clicked:
                        self.selected = point
                        break
        else:
            for point in self.points:
                point.clicked = False

        # toggle static
        if pygame.mouse.get_pressed()[2]:
            mouseTuple = pygame.mouse.get_pos()
            mousePosition = Vector2(mouseTuple[0], mouseTuple[1])
            if self.selected is not None:
                self.selected.toggleStatic(mousePosition)
            else:
                for point in self.points:
                    point.toggleStatic(mousePosition)
                    if point.rightClicked:
                        self.selected = point
                        break
        else:
            for point in self.points:
                point.rightClicked = False

        if not (pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]):
            self.selected = None


pygame.init()
surface = pygame.display.set_mode(surfaceSize)

swatch = Swatch((200,50), 20, 10, 5)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    surface.fill((0,0,0))

    # TODO: allow user to fix points, cut lines

    swatch.update()
    swatch.events()
    swatch.draw(surface)

    pygame.display.flip()
