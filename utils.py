import random

STANDARD_DECK = [['2', '3', '6', '5', '1'],
                ['3', '4', '1', 'A', '2'],
                ['2', '2', 'A', 'S', '1'],
                ['1', '1', '6', '5', '4'],
                ['C', 'S', '4', '3', '2']]

def random_deck():
    cards = ['1', '1', '1', '1', '1', '2', '2', '2', '2', '2', '3', '3', '3', '4', '4', '4', '5', '5', '6', '6', 'A', 'A', 'S', 'S']
    random.shuffle(cards)
    cards = ['C'] + cards
    deck = [cards[x:x+5] for x in range(0, len(cards), 5)]
    random.shuffle(deck)
    return deck

def print_deck(state):
    deck = state[0][:25]
    deck = ["A" if x == 7 else x for x in deck]
    deck = ["S" if x == 8 else x for x in deck]
    deck = ["C" if x == 9 else x for x in deck]
    deck = [str(x) for x in deck]

    piles = [deck[5*x:(5*x + 5)] for x in range(5)]
    for pile in piles:
        print(pile)

def smooth(data, h=10):
    return [sum(data[x:x+h])/h for x in range(len(data) - h)]