import random

valid_chip_colors = ["red", "white", "blue"]

class CardsData:
    def __init__(self, games, pots):
        self.games = games
        self.pots = pots

    def add_game(self, game):
        self.games[game.name] = game

    def add_pot(self, pot):
        self.pots[pot.name] = pot

    def serialize(self):
        return {"games": [game.serialize() for game in self.games.values()], "pots": [pot.serialize() for pot in self.pots.values()]}

    @staticmethod
    def deserialize(cards_data):
        loaded_games = {}
        for game in cards_data["games"]:
            loaded_game = Game.deserialize(game)
            loaded_games[loaded_game.name] = loaded_game
        loaded_pots = {}
        for pot in cards_data["pots"]:
            loaded_pot = ChipPot.deserialize(pot)
            loaded_pots[loaded_pot.name] = loaded_pot
        return CardsData(loaded_games, loaded_pots)

    @staticmethod
    def setup():
        return CardsData({})

class ChipPot:
    def __init__(self, name, chips, hands):
        self.name = name
        self.chips = chips
        self.hands = hands

    def draw_chips_rand(self, count=1):
        chips_drawn = []
        for _ in range(count):
            total_chip_count = sum(self.chips.values())
            if total_chip_count == 0:
                break
            rand_num = random.randint(1, total_chip_count)
            if rand_num <= self.chips["red"]:
                color = "red"
            elif rand_num <= self.chips["red"]+self.chips["white"]:
                color = "white"
            else:
                color = "blue"
            self.chips[color] -= 1
            chips_drawn.append(color)
        return chips_drawn


    def draw_chips(self, color, count=1):
        if color in self.chips and self.chips[color] >= count:
            self.chips[color] -= count
            return True
        return False

    def get_chip_count(self):
        return sum(self.chips.values())

    def serialize(self):
        return {"name": self.name, "chips": self.chips, "hands": [hand.serialize() for hand in self.hands.values()]}

    @staticmethod
    def init_pot(name, red, white, blue):
        return ChipPot(name, {"red": red, "white": white, "blue": blue}, {})

    @staticmethod
    def deserialize(pot_data):
        loaded_hands = {}
        for chip_hand in pot_data["hands"]:
            hand = ChipHand.deserialize(chip_hand)
            loaded_hands[hand.member] = hand
        loaded_chips = {}
        for chip_color in pot_data["chips"]:
                loaded_chips[chip_color] = pot_data["chips"][chip_color]
        return ChipPot(pot_data["name"], loaded_chips, loaded_hands)

class ChipHand:
    def __init__(self, pot, member, chips):
        self.pot = pot
        self.member = member
        self.chips = chips
        if self.chips == {}:
            for color in valid_chip_colors:
                self.chips[color] = 0

    def play_chip(self, color, pot):
        if color in self.chips and self.chips[color] > 0:
            self.chips[color] -= 1
            pot.chips[color] += 1

    def add_chips(self, color, count):
        if color not in self.chips:
            self.chips[color] = 0
        self.chips[color] += count

    def serialize(self):
        return {"pot": self.pot, "member": self.member, "chips": self.chips}

    @staticmethod
    def deserialize(hand_data):
        loaded_chips = {}
        for chip_color in hand_data["chips"]:
                loaded_chips[chip_color] = chip_color
        return ChipHand(hand_data["pot"], hand_data["member"], loaded_chips)


class Game:
    def __init__(self, name, decks, hands):
        self.name = name
        self.decks = decks
        self.hands = hands

    def add_deck(self, deck):
        self.decks[deck.name] = deck

    def add_hand(self, hand):
        self.hands[hand.member] = hand

    def serialize(self):
        return {"name": self.name, "decks": [deck.serialize() for deck in self.decks.values()],
                "hands": [hand.serialize() for hand in self.hands.values()]}

    @staticmethod
    def deserialize(game_data):
        loaded_decks = {}
        for deck in game_data["decks"]:
            loaded_deck = Deck.deserialize(deck)
            loaded_decks[loaded_deck.name] = loaded_deck
        loaded_hands = {}
        for hand in game_data["hands"]:
            loaded_hand = Hand.deserialize(hand)
            loaded_hands[loaded_hand.member] = loaded_hand
        return Game(game_data["name"], loaded_decks, loaded_hands)

class Hand:
    def __init__(self, cards, member):
        self.cards = cards
        self.member = member

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self, index):
        return self.cards.remove(self.cards[index])

    def discard(self, index, deck):
        card = self.cards[index]
        del self.cards[index]
        deck.discard(card)
        return card

    def __str__(self):
        return ", ".join([str(card) for card in self.cards])

    def serialize(self):
        return {"member": self.member, "cards": [card.serialize() for card in self.cards]}

    @staticmethod
    def deserialize(hand_data):
        loaded_cards = []
        for card in hand_data["cards"]:
            loaded_cards.append(Card.deserialize(card))
        return Hand(loaded_cards, hand_data["member"])

class Deck:
    def __init__(self, name, cards, drawn, discard):
        self.name = name
        self.cards = cards
        self.drawn = drawn
        self.discarded = discard

    def shuffle(self, include_discarded=True, include_drawn=False):
        if include_discarded:
            self.cards.extend(self.discarded)
            self.discarded = []
        if include_drawn:
            self.cards.extend(self.drawn)
            self.drawn = []
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) == 0:
            return None
        drawn_card = self.cards.pop()
        self.drawn.append(drawn_card)
        return drawn_card

    def draw_discard(self):
        if len(self.discarded) == 0:
            return None
        drawn_card = self.discarded.pop()
        self.drawn.append(drawn_card)
        return drawn_card

    def discard(self, card):
        self.discarded.append(card)
        self.drawn.remove(card)

    def serialize(self):
        return {"name": self.name, "cards": [card.serialize() for card in self.cards],
                "drawn": [card.serialize() for card in self.drawn],
                "discard": [card.serialize() for card in self.drawn]}

    @staticmethod
    def init_cards_default(name, jokers=True):
        cards = []
        for suit in ["Hearts", "Diamonds", "Spades", "Clubs"]:
            for num in ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]:
                cards.append(Card(suit, num, name))
        if jokers:
            cards.append(Card("red", "Joker", name))
            cards.append(Card("black", "Joker", name))

        return Deck(name, cards, [], [])

    @staticmethod
    def deserialize(deck_data):
        loaded_cards = []
        for card in deck_data["cards"]:
            loaded_cards.append(Card.deserialize(card))
        loaded_drawn = []
        for card in deck_data["drawn"]:
            loaded_drawn.append(Card.deserialize(card))
        loaded_discard = []
        for card in deck_data["discard"]:
            loaded_discard.append(Card.deserialize(card))
        return Deck(deck_data["name"], loaded_cards, loaded_drawn, loaded_discard)

class Card:
    def __init__(self, suit, num, deck):
        self.suit = suit
        self.num = num
        self.deck = deck
        self.color = ""
        self.joker = False

        if self.suit == "Hearts" or self.suit == "Diamonds" or self.suit == "red":
            self.color = "Red"
        if self.suit == "Spades" or self.suit == "Clubs" or self.suit == "black":
            self.color = "Black"
        if self.num == "Joker":
            self.joker = True

    def short_name(self):
        if not self.joker:
            suits = {"Hearts": ":hearts:", "Diamonds":":diamonds:", "Spades":":spades:", "Clubs":":clubs:"}
            short_names = {"Ace":"A", "2":"2", "3":"3", "4":"4", "5":"5", "6":"6", "7":"7", "8":"8",
                           "9":"9", "10":"10", "Jack":"J", "Queen":"Q", "King":"K"}
            return f"{short_names[self.num]}{suits[self.suit]}"
        else:
            return f"Jo{':red_circle:' if self.color == 'Red' else ':black_circle:'}"


    def __str__(self):
        if not self.joker:
            return f"{self.num} of {self.suit} ({self.short_name()})"
        else:
            return f"{self.color} Joker ({self.short_name()})"


    def serialize(self):
        return {"suit": self.suit, "num": self.num, "deck": self.deck}

    @staticmethod
    def deserialize(card_data):
        return Card(card_data["suit"], card_data["num"], card_data["deck"])