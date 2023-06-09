import pygame
from pygame.math import Vector2
import threading

# TODO: more colors

COLOR = (240,240,240)
RADIUS = 3

# TODO: move constants to another file

FRICTION = 0.85
GRAVITY = 0.420
ELASTICITY = 1
T_DELTA = 0.69

class Point:
    def __init__(self, position: Vector2, static=False):
        self.position = position
        self.previousPosition = position
        self.nextPosition = position
        self.static = static
        # TODO: get rid of clicked and rightClicked
        self.clicked = False
        self.rightClicked = False
        self.lines = []

    def __sub__(self, b):
        return self.position - b.position

    def draw(self, surface):
        pygame.draw.circle(surface, COLOR, self.position, RADIUS)

    def update(self, surfaceSize):
        if self.static or self.clicked:
            self.previousPosition = self.position
            self.position = self.nextPosition
            return

        # calculate velocity of point, use to update position
        velocity = self.position - self.previousPosition
        velocity.x *= FRICTION
        velocity.y *= FRICTION

        self.nextPosition = self.position + velocity
        self.nextPosition.y += GRAVITY * T_DELTA ** 2

        for line, sign in self.lines:
            self.nextPosition += sign * line.force * T_DELTA ** 2

        self.nextPosition.x = pygame.math.clamp(
                                  self.nextPosition.x,
                                  0,
                                  surfaceSize[0]
                              )
        self.nextPosition.y = pygame.math.clamp(
                                  self.nextPosition.y,
                                  0,
                                  surfaceSize[1]
                              )

        self.previousPosition = self.position
        self.position = self.nextPosition

    def events(self, swatch):
        # TODO: allow user to cut lines
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
        # drag only if there is a collision, set self.clicked if so
        dist = (self.position - mousePosition).length()
        if dist < 10 or self.clicked:
            self.nextPosition = mousePosition
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
        # second element of tuple is sign of force
        point1.lines.append((self, 1))
        point2.lines.append((self, -1))
        self.force = None

    def draw(self, surface):
        pygame.draw.line(
            surface,
            COLOR,
            self.point1.position,
            self.point2.position
        )

    def update(self):
        # calculate effect of line on points
        dPosition = self.point1 - self.point2
        length = dPosition.length()

        # if points overlap exactly, move them slightly
        # TODO: make this happen before updating each point
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
        self.force = ELASTICITY * dPosition * dLength / length


class Swatch:
    def __init__(self, surfaceSize, origin, rows, cols, space):
        self.surfaceSize = surfaceSize

        # create points
        # TODO: allow user to specify point size
        self.points = []
        for i in range(rows):
            for j in range(cols):
                self.points.append(
                    Point(
                        Vector2(origin[0] + space * j,
                        origin[1] + space * i)
                    )
                )
        self.numPoints = len(self.points)

        # create lines
        # TODO: generate lines based on user input
        self.lines = []
        for ind, point in enumerate(self.points):
            x, y = point.position
            if x + space < origin[0] + space * cols:
                self.lines.append(Line(point, self.points[ind + 1]))
            if y + space < origin[1] + space * rows:
                self.lines.append(Line(point, self.points[ind + cols]))
        self.numLines = len(self.lines)

        # currently selected point
        self.selected = None

    def draw(self, surface):
        for point in self.points:
            point.draw(surface)

        for line in self.lines:
            line.draw(surface)

    def updateLinesThread(self, first, last):
        for ind in range(first, last + 1):
            line = self.lines[ind]
            line.update()

    def updatePointsThread(self, first, last):
        for ind in range(first, last + 1):
            point = self.points[ind]
            point.events(self)
            point.update(self.surfaceSize)

    def update(self):
        # TODO: handle events more efficiently
        threshold = round(self.numLines / 2)
        t1 = threading.Thread(target=self.updateLinesThread, args=(0, threshold,))
        t2 = threading.Thread(target=self.updateLinesThread, args=(threshold + 1, self.numLines - 1,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        threshold = round(self.numPoints / 2)
        t1 = threading.Thread(target=self.updatePointsThread, args=(0, threshold,))
        t2 = threading.Thread(target=self.updatePointsThread, args=(threshold + 1, self.numPoints - 1,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
