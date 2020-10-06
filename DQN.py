import copy
import gym
import numpy as np
import random
import keras

from keras.models import Sequential
from keras.layers import Dense, Dropout, InputLayer
from keras.optimizers import Adam

from collections import deque
import matplotlib.pyplot as plt
import os.path

class DQN:
    def __init__(self, env, name, trainable=True):
        self.env       = env
        self.name      = name
        self.trainable = trainable
        self.memory    = deque(maxlen=2000)
        
        self.gamma = 0.85
        self.epsilon = 0.05
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.005
        self.tau = .125

        self.model        = self.create_model()
        self.target_model = self.create_model()

    def create_model(self):
        if not os.path.exists(f"models/{self.name}"):
            os.mkdir(f"models/{self.name}")
        model_path = f"models/{self.name}/latest.model"
        if os.path.exists(model_path):
            return self.load_model(model_path)
        
        model = Sequential()
        model.add(Dense(100, activation='relu', input_shape=(self.env.obs_num,)))
        model.add(Dense(100, activation='relu'))
        model.add(Dense(30, activation='linear'))
        model.compile(loss='mse', optimizer='adam', metrics=['mae'])
        return model

    def act(self, state):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if self.trainable and np.random.random() < self.epsilon:
            return random.choice(self.env.valid_actions())
        # Mask out illegal moves
        masked_predictions = [prediction if mask == 1 else np.NINF for prediction, mask in zip(self.model.predict(state)[0], self.env.valid_actions_mask())]
        return np.argmax(masked_predictions)

    def remember(self, state, action, reward, new_state, done):
        self.memory.append([state, action, reward, new_state, done])

    def replay(self):
        batch_size = 32
        if len(self.memory) < batch_size: 
            return

        samples = random.sample(self.memory, batch_size)
        for sample in samples:
            state, action, reward, new_state, done = sample
            target = self.target_model.predict(state)
            if done:
                target[0][action] = reward
            else:
                Q_future = max(self.target_model.predict(new_state)[0])
                target[0][action] = reward + Q_future * self.gamma
            self.model.fit(state, target, epochs=1, verbose=0)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, fn):
        self.model.save(fn)

    def load_model(self, fn):
        return keras.models.load_model(fn)

    def score_state(self, state):
        # print(self.model.predict(state)[0])
        return np.max(self.model.predict(state)[0])