import random

class CardsData:
    def __init__(self, games):
        self.games = games

    def add_game(self, game):
        self.games[game.name] = game

    def serialize(self):
        return [game.serialize() for game in self.games]

    @staticmethod
    def deserialize(cards_data):
        loaded_games = {}
        for game in cards_data:
            loaded_game = Game.deserialize(game)
            loaded_games[loaded_game.name] = loaded_game
        return CardsData(loaded_games)

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
        return {"name": self.name, "decks": [deck.serialize() for deck in self.decks],
                "hands": [hand.serialize() for hand in self.hands]}

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

    def serialize(self):
        return {"member": self.member, "cards": [card.serialize() for card in self.cards]}

    @staticmethod
    def deserialize(hand_data):
        loaded_cards = []
        for card in hand_data:
            loaded_cards.append(Card.deserialize(card))
        return Hand(loaded_cards, hand_data["member"])

class Deck:
    def __init__(self, name, cards, drawn, discard):
        self.name = name
        self.cards = cards
        self.drawn = drawn
        self.discard = discard

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        drawn_card = self.cards.pop()
        self.drawn.append(drawn_card)
        return drawn_card

    def discard(self, card):
        self.discard.append(card)

    def serialize(self):
        return {"name": self.name, "cards": [card.serialize() for card in self.cards],
                "drawn": [card.serialize() for card in self.drawn],
                "discard": [card.serialize() for card in self.drawn]}

    @staticmethod
    def init_cards_default(name, jokers=True):
        cards = []
        for suit in ["Hearts", "Diamonds", "Spades", "Clubs"]:
            for num in ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]:
                cards.append(Card(suit, num))
        if jokers:
            cards.append(Card("red", "Joker"))
            cards.append(Card("black", "Joker"))

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
    def __init__(self, suit, num):
        self.suit = suit
        self.num = num
        self.color = ""
        self.joker = False

        if self.suit == "Hearts" or self.suit == "Diamonds" or self.suit == "red":
            self.color = "Red"
        if self.suit == "Spades" or self.suit == "Clubs" or self.suit == "black":
            self.color = "Black"
        if self.num == -1:
            self.joker = True

    def full_name(self):
        if not self.joker:
            return f"{self.num} of {self.suit}"
        else:
            return f"{self.color} Joker"

    def __str__(self):
        if not self.joker:
            suits = {"Hearts": ":hearts:", "Diamonds":":diamonds:", "Spades":":spades:", "Clubs":":clubs:"}
            short_names = {"Ace":"A", "2":"2", "3":"3", "4":"4", "5":"5", "6":"6", "7":"7", "8":"8",
                           "9":"9", "10":"10", "Jack":"J", "Queen":"Q", "King":"K"}
            return f"{short_names[self.num]}{suits[self.suit]}"
        else:
            return f"J{':red_circle:' if self.color == 'Red' else ':black_circle:'}"


    def serialize(self):
        return {"suit": self.suit, "num": self.num}

    @staticmethod
    def deserialize(card_data):
        return Card(card_data["suit"], card_data["num"])


