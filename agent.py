import torch
import random
import numpy as np
from collections import deque
from main import SnakeGame, Direction, Point
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self):
        self.nGames = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def getState(self, game):
        head = game.snake[0]
        pointL = Point(head.x - 20, head.y)
        pointR = Point(head.x + 20, head.y)
        pointU = Point(head.x, head.y - 20)
        pointD = Point(head.x, head.y + 20)

        dirL = game.direction == Direction.LEFT
        dirR = game.direction == Direction.RIGHT
        dirU = game.direction == Direction.UP
        dirD = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dirR and game.isCollision(pointR)) or
            (dirL and game.isCollision(pointL)) or
            (dirU and game.isCollision(pointU)) or
            (dirD and game.isCollision(pointD)),

            # Danger right
            (dirU and game.isCollision(pointR)) or
            (dirD and game.isCollision(pointL)) or
            (dirL and game.isCollision(pointU)) or
            (dirR and game.isCollision(pointD)),

            # Danger left
            (dirD and game.isCollision(pointR)) or
            (dirU and game.isCollision(pointL)) or
            (dirR and game.isCollision(pointU)) or
            (dirL and game.isCollision(pointD)),

            # Move direction
            dirL,
            dirR,
            dirU,
            dirD,

            # Food location
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def trainLongMemory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.trainStep(states, actions, rewards, next_states, dones)

    def trainShortMemory(self, state, action, reward, next_state, done):
        self.trainer.trainStep(state, action, reward, next_state, done)

    def getAction(self, state):
        self.epsilon = 80 - self.nGames
        finalMove = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            finalMove[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            finalMove[move] = 1
        return finalMove


def train():
    plotScores = []
    plotMeanScores = []
    totalScore = 0
    record = 0
    agent = Agent()
    game = SnakeGame()
    while True:
        # get old state
        stateOld = agent.getState(game)

        # get move
        finalMove = agent.getAction(stateOld)

        # perform move and get new state
        reward, done, score = game.playStep(finalMove)
        stateNew = agent.getState(game)

        # train short memory
        agent.trainShortMemory(stateOld, finalMove, reward, stateNew, done)

        # remember
        agent.remember(stateOld, finalMove, reward, stateNew, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.nGames += 1
            agent.trainLongMemory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.nGames, 'Score', score, 'Record:', record)
            plotScores.append(score)
            totalScore += score
            meanScore = totalScore / agent.nGames
            plotMeanScores.append(meanScore)
            print('Mean score:', meanScore)


if __name__ == '__main__':
    train()
