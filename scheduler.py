import random

import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np

from scrimish import Scrimish, Move
from strategy import RandomStrategy, DQNStrategy
from utils import smooth, random_deck, print_deck

new_deck = [['1', '1', '6', '3', 'S'], ['6', '4', '2', '2', '1'], ['C', '2', 'A', '1', '5'], ['2', '5', '4', '2', 'A'], ['3', '4', '3', '1', 'S']]

env = Scrimish(battle=True)
dqn = DQNStrategy(env, name="DQN_bt_ds_v4", deck=new_deck, trainable=False)
rand = DQNStrategy(env, name="DQN_bt_ds_v4", deck="standard", trainable=False)
#rand = RandomStrategy(env)

epochs = 1
epoch_games = 100
deck_selection = False

phases = [(epoch_games, dqn, rand) for _ in range(epochs)]

total_frames = 0
total_games = 0
last_won = False
p1_wins = []

e = Scrimish()
best_score = np.NINF



for (games, p1, p2) in tqdm(phases, position=0, leave=True):
    players = [p1, p2]

    for game in range(1, games + 1):
        tqdm.write(f"{p1.name} won {p1_wins.count(1)}/{total_games}. WR: {round(p1_wins.count(1) * 100 / max(1,total_games),1)} %. {'+' if last_won else ' '}")
        starting_player = random.randint(0, 1)
        env.reset(first_player_deck=players[starting_player].deck, second_player_deck=players[int(not starting_player)].deck)
        active_player = starting_player
        while not env.done:
            state = env.state
            action = players[active_player].act(env, state)
            new_state, reward, done = env.step(action)
            players[active_player].callback(game, state, action, reward, new_state, done)

            if done:
                last_won = starting_player == env.winner
                p1_wins.append(int(last_won))

            total_frames += 1
            active_player = int(not active_player)
        
        total_games += 1

    if deck_selection:
        # Evaluate next best deck
        print("Evaluating next epoch deck...")
        best_score = p1.agent.score_state(e.reset(first_player_deck=p1.deck))
        print(f"Current deck score: {best_score}")
        for _ in range(100000):
            deck = random_deck()
            state = e.reset(first_player_deck=deck)
            score = p1.agent.score_state(state)
            if score > best_score:
                best_deck = deck
                best_score = score
        p1.deck = best_deck
        print(f"Current deck score: {best_score}")
        print(best_deck)
    

print(p1_wins)
print(f"Frames: {total_frames}")
plt.plot(smooth(p1_wins, int(total_games/20)))
plt.show()

p1.summary()
p2.summary()