import random
import gym
from gym import spaces
import numpy as np


class MazeEnv(gym.Env):
    def __init__(self):
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0,
                                            high=4,
                                            shape=(5, 4),
                                            dtype=np.int16)
        self.reward_range = (-200, 200)

        self.current_episode = 0
        self.success_episode = []

    def reset(self):
        self.current_player = 1
        self.disruptor = 2
        self.target = 4
        # P means the game is playable, W means somenone wins, L someone lose
        self.state = 'P'
        self.current_step = 0
        self.max_step = 30
        self.world = np.array([[0, 0, 4, 0],
                              [0, 0, 0, 0],
                              [0, 2, 0, 0],
                              [0, 0, 0, 1]])
        # disruptor is represented by number 2, player is represented by number 1

        target_pos = np.where(self.world == self.target)
        current_pos = np.where(self.world == self.current_player)
        disruptor_pos = np.where(self.world == self.disruptor)
        x = random.randint(0, 3)
        y = random.randint(0, 3)
        target_pos = (x, y)
        disruptor_pos = (2, y)
        while not (target_pos != disruptor_pos and target_pos != current_pos and disruptor_pos != current_pos):
            x = random.randint(0, 3)
            y = random.randint(0, 3)
            target_pos = (x, y)
            disruptor_pos = (2, y)
        self.world[disruptor_pos] = self.disruptor
        self.world[target_pos] = self.target
        if (2, 1) != disruptor_pos:
            self.world[2][1] = 0
        if (0, 2) != target_pos:
            self.world[0][2] = 0
        return self._next_observation()

    def _next_observation(self):
        obs = self.world

        obs = np.append(obs, [[self.current_player, 0, 0, 0]], axis=0)

        return obs

    def _take_action(self, action):

        target_pos = np.where(self.world == self.target)
        current_pos = np.where(self.world == self.current_player)
        disruptor_pos = np.where(self.world == self.disruptor)
        stay_still = self.current_step < 5 or len(disruptor_pos) == 0

        if stay_still:
                pass
        else:
            if target_pos[0] < disruptor_pos[0]:
                next_disruptor_pos = (disruptor_pos[0] - 1, disruptor_pos[1])
            elif target_pos[0] > disruptor_pos[0]:
                next_disruptor_pos = (disruptor_pos[0] + 1, disruptor_pos[1])
            else:
                if target_pos[1] < disruptor_pos[1]:
                    next_disruptor_pos = (disruptor_pos[0], disruptor_pos[1] - 1)
                elif target_pos[1] > disruptor_pos[1]:
                    next_disruptor_pos = (disruptor_pos[0], disruptor_pos[1] + 1)
                else:
                    next_disruptor_pos = disruptor_pos
                    self.state = 'L'
            self.world[next_disruptor_pos] = self.disruptor
            if disruptor_pos != next_disruptor_pos:
                self.world[disruptor_pos] = 0

        if action == 0:
            next_pos = (current_pos[0] - 1, current_pos[1])
            if next_pos[0] >= 0:
                self.world[next_pos] = self.current_player
                self.world[current_pos] = 0
            if next_pos[0] >= 0 and (int(self.world[next_pos]) == self.target):
                self.state = 'W'

        elif action == 1:
            next_pos = (current_pos[0], current_pos[1] + 1)

            if next_pos[1] <= 3:
                self.world[next_pos] = self.current_player
                self.world[current_pos] = 0

            if next_pos[1] <= 3 and (int(self.world[next_pos]) == self.target):
                self.state = 'W'

        elif action == 2:
            next_pos = (current_pos[0] + 1, current_pos[1])

            if next_pos[0] <= 3:
                self.world[next_pos] = self.current_player
                self.world[current_pos] = 0

            if next_pos[0] <= 3 and (int(self.world[next_pos]) == self.target):
                self.state = 'W'

        elif action == 3:
            next_pos = (current_pos[0], current_pos[1] - 1)

            if next_pos[1] >= 0:
                self.world[next_pos] = self.current_player
                self.world[current_pos] = 0

            if next_pos[1] >= 0 and (int(self.world[next_pos]) == self.target):
                self.state = 'W'

    def step(self, action):
        self._take_action(action)
        self.current_step += 1
        print(self.world)

        if self.state == "W":
            print(f'Player {self.current_player} won')
            reward = 200
            done = True
        elif self.state == 'L':
            print(f'Player {self.current_player} lost')
            reward = -200
            done = True
        elif self.state == 'P':
            reward = 0
            done = False

        if self.current_step >= self.max_step:
            reward = -200
            self.state = 'L'
            done = True

        if done:
            self.render_episode(self.state)
            self.current_episode += 1

        obs = self._next_observation()

        return obs, reward, done, {}

    def render_episode(self, win_or_lose):
        self.success_episode.append(
            'Success' if win_or_lose == 'W' else 'Failure')

        file = open('render/render.txt', 'a')
        file.write('-------------------------------------------\n')
        file.write(f'Episode number {self.current_episode}\n')
        file.write(f'{self.success_episode[-1]} in {self.current_step} steps\n')
        file.close()
