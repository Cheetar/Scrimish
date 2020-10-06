import copy
import random

from DQN import DQN
from utils import STANDARD_DECK, smooth, random_deck

import matplotlib.pyplot as plt
from datetime import datetime


class Strategy(object):
    def __init__(self, env, name="", deck=None):
        self.env = env
        self.name = name
        self.deck = STANDARD_DECK if deck == "standard" else deck

    def act(self, env, state):
        return random.choice(env.valid_actions())

    def callback(self, game, state, action, reward, new_state, done):
        pass

    def summary(self):
        pass


class RandomStrategy(Strategy):
    def __init__(self, env, name="Random Strategy", deck=None):
        print("Initializing random strategy")
        super().__init__(env, name, deck)


class NoDiscardRandomStrategy(Strategy):
    def __init__(self, env, name="NoDiscardRandomStrategy", deck=None):
        print("Initializing random strategy with no discards")
        super().__init__(env, name, deck)

    def act(self, env, state):
        # TODO
        return random.choice(env.valid_actions())


class DQNStrategy(Strategy):
    def __init__(self, env, name, deck=None, trainable=True):
        print(f"Initializing DQN strategy {name}")
        super().__init__(env, name, deck)

        self.agent = DQN(env, name)
        self.trainable = trainable

    def act(self, env, state):
        return self.agent.act(state)

    def callback(self, game, state, action, reward, new_state, done):
        if self.trainable:
            self.agent.remember(state, action, reward, new_state, done)
            self.agent.replay()       # internally iterates default (prediction) model
            self.agent.target_train() # iterates target model

            if game % 100 == 0:
                self.agent.save_model(f"models/{self.name}/{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.model")
                self.agent.save_model(f"models/{self.name}/latest.model")
            
"""
class InputStrategy(Strategy):
    def __init__(self):
        self._opp_top_deck = ["*" for _ in range(5)]
        self._our_top_deck = ["*" for _ in range(5)]
        self._opp_lost_cards = {"1": 0,
                                "2": 0,
                                "3": 0,
                                "4": 0,
                                "5": 0,
                                "6": 0,
                                "A": 0,
                                "S": 0,
                                "N": 0}
        self._our_lost_cards = {"1": 0,
                                "2": 0,
                                "3": 0,
                                "4": 0,
                                "5": 0,
                                "6": 0,
                                "A": 0,
                                "S": 0,
                                "N": 0}

    def act(self, game_state):
        deck, opp_deck, history, _ = game_state

        if len(history) >= 2:
            print(history[-2])
            print(history[-1])

            ev = history[-2]
            if ev.discard:
                self._our_top_deck[ev.attacker_pile] = "*"
                self._our_lost_cards["N"] += 1
            else:
                if ev.attacker_lost_card:
                    self._our_top_deck[ev.attacker_pile] = "*"
                    self._our_lost_cards[ev.attacker_card] += 1
                else:
                    self._our_top_deck[ev.attacker_pile] = ev.attacker_card
                if ev.defender_lost_card:
                    self._opp_top_deck[ev.defender_pile] = "*"
                    self._opp_lost_cards[ev.defender_card] += 1
                else:
                    self._opp_top_deck[ev.defender_pile] = ev.defender_card
            
            ev = history[-1]
            if ev.discard:
                self._opp_top_deck[ev.attacker_pile] = "*"
                self._opp_lost_cards["N"] += 1
            else:
                if ev.attacker_lost_card:
                    self._opp_top_deck[ev.attacker_pile] = "*"
                    self._opp_lost_cards[ev.attacker_card] += 1
                else:
                    self._opp_top_deck[ev.attacker_pile] = ev.attacker_card
                if ev.defender_lost_card:
                    self._our_top_deck[ev.defender_pile] = "*"
                    self._our_lost_cards[ev.defender_card] += 1
                else:
                    self._our_top_deck[ev.defender_pile] = ev.defender_card

        print(f"\nOur top deck: {self._our_top_deck}")
        print(f"Opp top deck: {self._opp_top_deck}\n")

        print(f"Our lost cards: {self._our_lost_cards}")
        print(f"Opp lost cards: {self._opp_lost_cards}\n")

        for pile in deck:
            print(pile)
        print("--------------------------------")
        for pile_size in opp_deck:
            print(['*' for _ in range(pile_size)])
        print("--------------------------------")

        raw_move = input()
        assert(len(raw_move) == 2)
        if raw_move.startswith("d"):
            move = Move(discard_pile=int(raw_move[1]))
        else:
            move = Move(int(raw_move[0]), int(raw_move[1]))
        return move
"""