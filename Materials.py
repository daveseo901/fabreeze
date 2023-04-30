import pygame
from pygame.math import Vector2

# TODO: more colors

color = (240,240,240)

# TODO: move constants to another file

FRICTION = 0.95
GRAVITY = 9.8
ELASTICITY = 0.95

# TODO: move class definitions to another file

class Point:
    def __init__(self, surfaceSize, position: Vector2, static=False):
        self.surfaceSize = surfaceSize
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
            self.previousPosition = self.position
            return

        # calculate velocity of point, use to update position
        velocity = self.position - self.previousPosition
        velocity.x *= FRICTION
        velocity.y += GRAVITY
        velocity.y *= FRICTION

        self.previousPosition = self.position
        self.position = self.position + velocity
        self.position.x = pygame.math.clamp(self.position.x, 0, self.surfaceSize[0])
        self.position.y = pygame.math.clamp(self.position.y, 0, self.surfaceSize[1])

    def events(self, swatch):
        # can immediately return if no buttons are being pressed
        if not (pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]):
            self.clicked = False
            self.rightClicked = False
            swatch.selected = None
            return

        # if this point is not the previously selected one, ignore
        # TODO: change to select closest point (pass in local selected variable)
        if swatch.selected is not None and swatch.selected != self:
            self.clicked = False
            self.rightClicked = False
            return

        mouseTuple = pygame.mouse.get_pos()
        mousePosition = Vector2(mouseTuple[0], mouseTuple[1])

        # drag point
        if pygame.mouse.get_pressed()[0]:
            self.drag(mousePosition)
            if self.clicked:
                swatch.selected = self
        else:
            self.clicked = False

        # toggle static
        if pygame.mouse.get_pressed()[2]:
            self.toggleStatic(mousePosition)
            if self.rightClicked:
                swatch.selected = self
        else:
            self.rightClicked = False

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

        point1stoic = self.point1.static or self.point1.clicked
        point2stoic = self.point2.static or self.point2.clicked

        if not point1stoic and not point2stoic:
            self.point1.position += delta
            self.point2.position -= delta
        if point1stoic and not point2stoic:
            self.point2.position -= delta
        if point2stoic and not point1stoic:
            self.point1.position += delta


class Swatch:
    def __init__(self, surfaceSize, origin, rows, cols, space):
        self.surfaceSize = surfaceSize

        # create points
        self.points = []
        for i in range(rows):
            for j in range(cols):
                self.points.append(
                    Point(
                        self.surfaceSize,
                        Vector2(origin[0] + space * j,
                        origin[1] + space * i)
                    )
                )

        # create lines
        # TODO: generate lines based on user input
        self.lines = []
        for ind, point in enumerate(self.points):
            x, y = point.position
            if x + space < origin[0] + space * cols:
                self.lines.append(Line(point, self.points[ind + 1]))
            if y + space < origin[1] + space * rows:
                self.lines.append(Line(point, self.points[ind + cols]))
        self.lines = list(reversed(self.lines))

        # currently selected point
        self.selected = None

    def draw(self, surface):
        for point in self.points:
            point.draw(surface)

        for line in self.lines:
            line.draw(surface)

    def update(self):
        for point in self.points:
            point.events(self)
            point.update()

        for line in self.lines:
            line.update()
