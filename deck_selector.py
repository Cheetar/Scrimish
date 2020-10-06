from scrimish import Scrimish
from utils import print_deck
from DQN import DQN
import random

env = Scrimish()
agent = DQN(env=env, name="DQN_bt_st_v2", trainable=False)
# agent = DQN(env=env, name="DQN_bt_st_v1_cont_rand_v2", trainable=False)
# agent = DQN(env=env, name="DQN_bt_sf_v1_2", trainable=False)

for i in range(10):
    state = env.reset()
    print_deck(state)
    print(f"DQN score: {agent.score_state(state)}")