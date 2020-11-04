import copy
import random
import numpy as np
from utils import random_deck

FIRST_PLAYER = 0
SECOND_PLAYER = 1

class Move(object):
    def __init__(self, attacker_pile=None, defender_pile=None, discard_pile=None):
        # Standard attack
        self._attacker_pile = attacker_pile
        self._defender_pile = defender_pile
        # Discarding a card
        self._discard_pile = discard_pile

    def is_discard(self):
        return not self._discard_pile is None

    def get_discard_pile(self):
        return self._discard_pile

    def get_piles(self):
        return self._attacker_pile, self._defender_pile

    def __str__(self):
        if self.is_discard():
            return f"Discarded a card from pile {self._discard_pile}"
        return f"Attacked pile {self._defender_pile} from pile {self._attacker_pile}"

class Event(object):
    def __init__(self, player, move, attacker_card=None, defender_card=None, attacker_pile=None, defender_pile=None, attacker_lost_card=False, defender_lost_card=False, discard=False, invalid=False):
        self.player = player
        self.move = move
        self.attacker_card = attacker_card
        self.defender_card = defender_card
        self.attacker_pile = attacker_pile
        self.defender_pile = defender_pile
        self.attacker_lost_card = attacker_lost_card
        self.defender_lost_card = defender_lost_card
        self.discard = discard

    def __str__(self):
        return f"Player {self.player} {self.move}: {self.attacker_card} vs {self.defender_card}"
                
class Scrimish(object):
    def __init__(self, first_player_deck=None, second_player_deck=None, battle=False):
        self._turn = 0
        self._attacker = FIRST_PLAYER
        self._defender = SECOND_PLAYER
        self._battle = battle
        self._history = []
        empty_known_top_deck = ["N" for _ in range(5)]
        self._player_known_top_decks = [copy.deepcopy(empty_known_top_deck), copy.deepcopy(empty_known_top_deck)]
        empty_known_lost_cards = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "A": 0, "S": 0, "C": 0, "N": 0}
        self._player_known_lost_cards = [copy.deepcopy(empty_known_lost_cards), copy.deepcopy(empty_known_lost_cards)]

        if first_player_deck is None:
            first_player_deck = random_deck()
        if second_player_deck is None:
            second_player_deck = random_deck()
        self._player_decks = [copy.deepcopy(first_player_deck), copy.deepcopy(second_player_deck)]

    def _is_move_valid(self, move):
        if move.is_discard():
            discard_pile = move.get_discard_pile()
            # Discard from empty pile or discard crown
            if len(self._player_decks[self._attacker][discard_pile]) == 0 or self._player_decks[self._attacker][discard_pile][-1] == 'C':
                return False
            return True

        attacker_pile, defender_pile = move.get_piles()
        if len(self._player_decks[self._attacker][attacker_pile]) == 0 or len(self._player_decks[self._defender][defender_pile]) == 0 or self._player_decks[self._attacker][attacker_pile][-1] == 'S':
            return False
        return True

    def _execute(self, move):
        if self.done:
            raise RuntimeError("Game has already finished!")
        
        if not self._is_move_valid(move):
            raise RuntimeError("Made an illegal move!")

        attacker_pile, defender_pile = move.get_piles()
        attacker_lost_card = False
        defender_lost_card = False

        if move.is_discard():
            attacker_pile = move.get_discard_pile()
            attacker_lost_card = True
        else:
            attacker_card = self._player_decks[self._attacker][attacker_pile][-1]
            defender_card = self._player_decks[self._defender][defender_pile][-1]
            # Special cards
            if attacker_card == "A" and defender_card == "S":
                pass # Nobody loses a card
            elif attacker_card == "C" and defender_card == "C":
                defender_lost_card = True
            elif attacker_card == "C" and defender_card != "C":
                attacker_lost_card = True
            elif defender_card == "C":
                defender_lost_card = True
            elif attacker_card == "A":
                defender_lost_card = True
            elif defender_card == "A":
                defender_lost_card = True
            elif defender_card == "S":
                attacker_lost_card = True
                defender_lost_card = True
            else:
                # Normal 1-6 power cards
                attacker_power = int(attacker_card)
                defender_power = int(defender_card)
                if attacker_power > defender_power:
                    defender_lost_card = True
                elif attacker_power == defender_power:
                    attacker_lost_card = True
                    defender_lost_card = True
                else:
                    attacker_lost_card = True
            
        if attacker_lost_card:
            self._player_decks[self._attacker][attacker_pile].pop()
        if defender_lost_card:
            self._player_decks[self._defender][defender_pile].pop()

        if move.is_discard():
            event = Event(self._attacker, move, attacker_pile=attacker_pile, attacker_lost_card=True, discard=True)
        else:
            event = Event(self._attacker, move, attacker_card, defender_card, attacker_pile, defender_pile, attacker_lost_card, defender_lost_card, discard=move.is_discard())
        self._history.append(event)

        attacker_pile_empty = len(self._player_decks[self._attacker][attacker_pile]) == 0
        defender_pile_empty = None
        if not move.is_discard():
            defender_pile_empty = len(self._player_decks[self._defender][defender_pile]) == 0
        
        if move.is_discard():
            self._player_known_top_decks[self._attacker][attacker_pile] = "E" if attacker_pile_empty else "N" 
            self._player_known_lost_cards[self._attacker]["N"] += 1
        else:
            if attacker_lost_card:
                self._player_known_top_decks[self._attacker][attacker_pile] = "E" if attacker_pile_empty else "N" 
                self._player_known_lost_cards[self._attacker][attacker_card] += 1
            else:
                self._player_known_top_decks[self._attacker][attacker_pile] = attacker_card
            if defender_lost_card:
                self._player_known_top_decks[self._defender][defender_pile] = "E" if defender_pile_empty else "N" 
                self._player_known_lost_cards[self._defender][defender_card] += 1
            else:
                self._player_known_top_decks[self._defender][defender_pile] = defender_card

        if not self.done:
            self._turn += 1
            self._attacker, self._defender = self._defender, self._attacker

        return event

    @property
    def action_num(self):
        return 30

    @property
    def obs_num(self):
        return 66

    @property
    def _ALL_MOVES(self):
        return [Move(discard_pile=x) for x in range(5)] + [Move(x, y) for x in range(5) for y in range(5)]

    def is_action_valid(self, action):
        return self._is_move_valid(self._ALL_MOVES[action])

    def is_action_discard(self, action):
        return self._ALL_MOVES[action].is_discard()

    def valid_actions(self):
        return list(filter(lambda action: self.is_action_valid(action), range(self.action_num)))

    def valid_nondiscard_actions(self):
        return list(filter(lambda action: self.is_action_valid(action) and not self.is_action_discard(action), range(self.action_num)))

    def valid_actions_mask(self):
        return list(map(lambda action: 1 if self.is_action_valid(action) else 0, range(self.action_num)))

    @property
    def done(self):
        # Game has ended if one of the players lost his crown
        flatten = lambda l: [item for sublist in l for item in sublist]
        return flatten(self._player_decks[0]).count('C') == 0 or flatten(self._player_decks[1]).count('C') == 0 

    @staticmethod
    def prepare_deck(deck):
        out_deck = []
        for pile in deck:
            pile = pile + ["E" for _ in range(5 - len(pile))]
            pile = [7 if x == "A" else x for x in pile]
            pile = [8 if x == "S" else x for x in pile]
            pile = [9 if x == "C" else x for x in pile]
            pile = [0 if x == "E" else x for x in pile]
            pile = [int(x) for x in pile]
            out_deck += pile
        return out_deck

    @staticmethod
    def prepare_lost_cards(lost_cards):
        return list(lost_cards.values())

    @staticmethod
    def prepare_top_deck(top_deck):
        top_deck = [7 if x == "A" else x for x in top_deck]
        top_deck = [8 if x == "S" else x for x in top_deck]
        top_deck = [9 if x == "C" else x for x in top_deck]
        top_deck = [10 if x == "N" else x for x in top_deck]
        top_deck = [0 if x == "E" else x for x in top_deck]
        top_deck = [int(x) for x in top_deck]
        return top_deck

    @staticmethod
    def get_top_deck(deck):
        return [pile[-1] if len(pile) else "E" for pile in deck]

    @property
    def state(self):
        # State is 25 + 5 + 5 + 5 + 5 + 10 + 10 + 1 = 66 ints. Returns concatinated (current player deck, our top deck, number of cards in opponents piles, our known top deck, opponent known top deck, our known lost cards, opponent known lost cards, turn)
        deck = self._player_decks[self._attacker]
        our_top_deck = self.get_top_deck(deck)
        opp_piles_sizes = [len(pile) for pile in self._player_decks[self._defender]]
        our_known_top_deck = self._player_known_top_decks[self._attacker]
        opp_known_top_deck = self._player_known_top_decks[self._defender]
        our_known_lost_cards = self._player_known_lost_cards[self._attacker]
        opp_known_lost_cards = self._player_known_lost_cards[self._defender]
        turn = [self._turn]

        state = np.array(self.prepare_deck(deck) + self.prepare_top_deck(our_top_deck) + opp_piles_sizes + self.prepare_top_deck(our_known_top_deck) + self.prepare_top_deck(opp_known_top_deck) + self.prepare_lost_cards(our_known_lost_cards) + self.prepare_lost_cards(opp_known_lost_cards) + turn).reshape(-1, self.obs_num)
        return state

    @property
    def winner(self):
        if not self.done:
            return None
        flatten = lambda l: [item for sublist in l for item in sublist]
        p2_crown = flatten(self._player_decks[SECOND_PLAYER]).count('C')
        return p2_crown

    def step(self, action):
        if self._player_decks[FIRST_PLAYER] is None or self._player_decks[SECOND_PLAYER] is None:
            raise RuntimeError("No decks defined!")

        active_player = self._attacker
        move = self._ALL_MOVES[action]
        event = self._execute(move)

        reward = 0
        if self.done:
            if self.winner == active_player:
                reward = 1
            else:
                reward = -1
        elif self._battle:
            if event.attacker_lost_card and not event.defender_lost_card:
                reward = -0.1
            elif not event.attacker_lost_card and event.defender_lost_card:
                reward = 0.1
        
        
        return (self.state, reward, self.done)

    def reset(self, first_player_deck=None, second_player_deck=None):
        self.__init__(first_player_deck, second_player_deck, battle=self._battle)
        return self.state