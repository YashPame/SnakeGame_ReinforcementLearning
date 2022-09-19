import pygame
import random
from collections import namedtuple
from enum import Enum

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

        self.direction = Direction.RIGHT

        self.head = Point(100, 100)
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._placeFood()

    def _placeFood(self):
        x = random.randint(0, (SCREEN_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (SCREEN_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._placeFood()

    def playStep(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if self.direction != Direction.RIGHT:
                        self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    if self.direction != Direction.LEFT:
                        self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    if self.direction != Direction.DOWN:
                        self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    if self.direction != Direction.UP:
                        self.direction = Direction.DOWN

        self._move(self.direction)
        self.snake.insert(0, self.head)

        gameOverBool = False
        if self._isCollision():
            gameOverBool = True
            return gameOverBool, self.score

        if self.head == self.food:
            self.score += 1
            self._placeFood()
        else:
            self.snake.pop()

        self._updateUI()
        self.clock.tick(SPEED)

        return gameOverBool, self.score

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def _updateUI(self):
        self.display.fill(WHITE)

        pt = self.snake[0]
        pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x-2, pt.y-2, BLOCK_SIZE+4, BLOCK_SIZE+4))
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

    def _isCollision(self):
        if self.head.x > SCREEN_WIDTH - BLOCK_SIZE or self.head.x < 0 or self.head.y > SCREEN_HEIGHT - BLOCK_SIZE or self.head.y < 0:
            return True

        if self.head in self.snake[1:]:
            return True
        return False


if __name__ == '__main__':
    game = SnakeGame()
    while True:
        gameOver, score = game.playStep()

        if gameOver:
            print('Final Score: ', score)
            break
