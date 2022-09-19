import pygame
import random
from collections import namedtuple
from enum import Enum
import numpy as np

pygame.init()

font = pygame.font.SysFont('arial', 25)

WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

BLOCK_SIZE = 20
SPEED = 10

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

Point = namedtuple('Point', 'x, y')


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


class SnakeGame:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT

        self.head = Point(100, 100)
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._placeFood()
        self.frameIteration = 0

    def _placeFood(self):
        x = random.randint(0, (SCREEN_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (SCREEN_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._placeFood()

    def playStep(self, action):
        self.frameIteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move(action)
        self.snake.insert(0, self.head)

        reward = 0
        gameOverBool = False
        if self.isCollision() or self.frameIteration > 100 * len(self.snake):
            gameOverBool = True
            reward = -10
            return reward, gameOverBool, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._placeFood()
        else:
            self.snake.pop()

        self._updateUI()
        self.clock.tick(SPEED)

        return reward, gameOverBool, self.score

    def _move(self, action):
        clockWise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clockWise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            newDir = clockWise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            nextIdx = (idx + 1) % 4
            newDir = clockWise[nextIdx]
        else:
            nextIdx = (idx - 1) % 4
            newDir = clockWise[nextIdx]

        self.direction = newDir
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def _updateUI(self):
        self.display.fill(WHITE)

        pt = self.snake[0]
        pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x - 2, pt.y - 2, BLOCK_SIZE + 4, BLOCK_SIZE + 4))
        pygame.draw.rect(self.display, GRAY, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        for pt in self.snake[1:]:
            pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, GRAY, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        pygame.draw.circle(self.display, RED, [self.food.x + BLOCK_SIZE // 2, self.food.y + BLOCK_SIZE // 2],
                           BLOCK_SIZE // 2)
        # pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        text = font.render("Score: " + str(self.score), True, BLACK)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def isCollision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x > SCREEN_WIDTH - BLOCK_SIZE or pt.x < 0 or pt.y > SCREEN_HEIGHT - BLOCK_SIZE or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True

        return False
