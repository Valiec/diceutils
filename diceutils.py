import json
import os
import random

import discord
from discord import app_commands

import cards
from cards import CardsData, Deck, Game, Hand, ChipPot
from dice import too_many_dice, evaluate, tokenize, DiceError, valid_dice_roll, roll_all_dice, roll_init_cmd_helper

tbhlist = ["Tbh", "Tbh is overused, tbh.", "*Tbh*",
           ":regional_indicator_t: :regional_indicator_b: :regional_indicator_h:", "**Tbh**",
           "Tbh, like I don’t like the phrase tbh as like tbh I hate it."]

class DiceUtils(discord.Client):
    async def on_ready(self):
        """Runs when the bot logs into Discord"""
        # update slash commands
        await tree.sync()
        print('Logged on as', self.user)

intents = discord.Intents.default()
client = DiceUtils(intents=intents)
# intents.message_content = True

tree = app_commands.CommandTree(client)


@tree.command(
    name="calc",
    description="compute a mathematical expression including dice rolls",
)
async def calc(interaction, expr: str):
    tokens_all = []
    try:
        tokens_all = tokenize(expr)
        result = evaluate(tokens_all)
        await interaction.response.send_message("`" + expr + " -> " + str(tokens_all) + " -> " + str(result) + "`")
    except DiceError as err:
        await interaction.response.send_message("Error: `" + expr + " -> " + str(tokens_all) + "`:\n" + err.message,
                                                ephemeral=True)


@tree.command(
    name="roll",
    description="roll dice",
)
async def roll(interaction, text: str):
    """Rolls dice."""
    mod = 0
    if text.startswith("d"):
        text = "1" + text
    roll_phase1 = text.split("d")
    print(roll_phase1)
    if "+" in roll_phase1[1]:
        foo = roll_phase1[1].split("+")
        if foo[1].isnumeric():
            dice_roll = [roll_phase1[0], foo[0]]
            mod = int(foo[1])
        else:
            dice_roll = roll_phase1
    elif "-" in roll_phase1[1]:
        foo = roll_phase1[1].split("-")
        if foo[1].isnumeric():
            dice_roll = [roll_phase1[0], foo[0]]
            mod = int(foo[1]) * -1
        else:
            dice_roll = roll_phase1
    else:
        dice_roll = roll_phase1
    if valid_dice_roll(dice_roll) and not too_many_dice(dice_roll):
        results_raw = roll_all_dice(int(dice_roll[0]), int(dice_roll[1]))
        results = ""
        if mod != 0:
            for result in results_raw:
                results += str(result + mod) + " *(" + str(result) + ")*,  "
            results = results[:-3]
        else:
            results = str(results_raw)[1:-1]
        outstr = "Rolled " + text + ":\n" + results
        outlen = len(outstr)
        while outlen > 2000:
            await interaction.response.send_followup(outstr[:2000])
            outstr = outstr[2000:]
            outlen -= 2000
        await interaction.response.send_message(outstr)
    elif too_many_dice(dice_roll):
        await interaction.response.send_message("Error: `" + text + "` rolls more than 2000 dice.", ephemeral=True)
    else:
        await interaction.response.send_message("Error: `" + text + "` is not a valid dice roll.", ephemeral=True)

@tree.command(
    name="init",
    description="roll initiative",
)
async def roll_init(interaction, turns: int, starting_totals: str, additives: str, names: str):
    """Rolls dice."""
    await roll_init_cmd_helper(interaction, turns, starting_totals, additives, names, False)

@tree.command(
    name="initdb",
    description="roll initiative (debug)",
)
async def roll_init_db(interaction, turns: int, starting_totals: str, additives: str, names: str):
    """Rolls dice."""
    await roll_init_cmd_helper(interaction, turns, starting_totals, additives, names, True)

@tree.command(
    name="alive",
    description="check the bot is alive",
)
async def alive(interaction):
    await interaction.response.send_message("I'm a bot, how can you kill a bot? What a grand and intoxicating "
                                            + "innocence.")

@tree.command(
    name="catgif",
    description="sends the cat GIF that shows if you have no favorites",
)
async def catgif(interaction):
    await interaction.response.send_message("https://imgur.com/QZGHA0i")


@tree.command(
    name="spike",
    description="sends the SARS-CoV-2 spike protein sequence because why not",
)
async def spike(interaction):
    await interaction.response.send_message(
        "MFVFLVLLPLVSSQCVNLTTRTQLPPAYTNSFTRGVYYPDKVFRSSVLHSTQDLFLPFFSNVTWFHAIHVSGTNGTKRFDNPVLPFNDGVYFASTEKSNIIRGWIFGTT"
        + "LDSKTQSLLIVNNATNVVIKVCEFQFCNDPFLGVYYHKNNKSWMESEFRVYSSANNCTFEYVSQPFLMDLEGKQGNFKNLREFVFKNIDGYFKIYSKHTPINLVRDL"
        + "PQGFSALEPLVDLPIGINITRFQTLLALHRSYLTPGDSSSGWTAGAAAYYVGYLQPRTFLLKYNENGTITDAVDCALDPLSETKCTLKSFTVEKGIYQTSNFRVQPT"
        + "ESIVRFPNITNLCPFGEVFNATRFASVYAWNRKRISNCVADYSVLYNSASFSTFKCYGVSPTKLNDLCFTNVYADSFVIRGDEVRQIAPGQTGKIADYNYKLPDDFT"
        + "GCVIAWNSNNLDSKVGGNYNYLYRLFRKSNLKPFERDISTEIYQAGSTPCNGVEGFNCYFPLQSYGFQPTNGVGYQPYRVVVLSFELLHAPATVCGPKKSTNLVKNK"
        + "CVNFNFNGLTGTGVLTESNKKFLPFQQFGRDIADTTDAVRDPQTLEILDITPCSFGGVSVITPGTNTSNQVAVLYQDVNCTEVPVAIHADQLTPTWRVYSTGSNVFQ"
        + "TRAGCLIGAEHVNNSYECDIPIGAGICASYQTQTNSPRRARSVASQSIIAYTMSLGAENSVAYSNNSIAIPTNFTISVTTEILPVSMTKTSVDCTMYICGDSTECSN"
        + "LLLQYGSFCTQLNRALTGIAVEQDKNTQEVFAQVKQIYKTPPIKDFGGFNFSQILPDPSKPSKRSFIEDLLFNKVTLADAGFIKQYGDCLGDIAARDLICAQKFNGL"
        + "TVLPPLLTDEMIAQYTSALLAGTITSGWTFGAGAALQIPFAMQMAYRFNGIGVTQNVLYENQKLIANQFNSAIGKIQDSLSSTASALGKLQDVVNQNAQALNTLVKQ"
        + "LSSNFGAISSVLNDILSRLDKVEAEVQIDRLITGRLQSLQTYVTQQLIRAAEIRASANLAATKMSECVLGQSKRVDFCGKGYHLMSFPQSAPHGVVFLHVTYVPAQE"
        + "KNFTTAPAICHDGKAHFPREGVFVSNGTHWFVTQRNFYEPQIITTDNTFVSGNCDVVIGIVNNTVYDPLQPELDSFKEELDKYFKNHTSPDVDLGDISGINASVVNI"
        + "QKEIDRLNEVAKNLNESLIDLQELGKYEQYIKWPWYIWLGFIAGLIAIVMVTIMLCCMTSCCSCLKGCCSCGSCCKFDEDDSEPVLKGVKLHYT")


@tree.command(
    name="flamingo",
    description="sends a random flamingo GIF",
)
async def flamingo(interaction):
    await interaction.response.send_message(
        random.choice([
            "https://tenor.com/view/fabulous-flamingo-gif-7529738",
            "https://tenor.com/view/flamingos-group-observant-gif-3535692",
            "https://tenor.com/view/flamingo-hoverboard-collage-animation-loop-gif-14625448",
            "https://media.discordapp.net/attachments/764804741292752898/770682285980385310/Mc.Mingo.gif",
            "https://tenor.com/view/birds-flamingos-spin-loop-dance-gif-3483877",
            "https://media.giphy.com/media/xUPGcAq8idp4tCSMYE/giphy.gif",
            "https://media.giphy.com/media/uTsG4q5Brun16/giphy.gif",
            "https://media.giphy.com/media/IFTHx4yEK8o24/giphy.gif",
            "https://media.giphy.com/media/60rGUCzVNBm7dJWlMj/giphy.gif",
            "https://media.giphy.com/media/idqa2k5xfkiztiwbnD/giphy.gif",
            "https://media.giphy.com/media/cir6DQ90LQv2Ccgyte/giphy.gif",
            "https://media.giphy.com/media/1AiqaeQkzipjnyVHlR/giphy.gif",
            "https://media.giphy.com/media/dIPv1HC8CacBBYvHUi/giphy.gif",
            "https://media.giphy.com/media/WOrXn7bffbdjByB8RP/giphy.gif",
            "https://media.giphy.com/media/3orifj6swylIeuxqRG/giphy.gif",
            "https://media.giphy.com/media/VaqFVAm7tGlF9hPNus/giphy.gif",
            "https://media.giphy.com/media/FiKW7YCFJjtNm/giphy.gif",
            "https://media.giphy.com/media/2tSTBHGEJNlLe1rqQV/giphy.gif",
            "https://media.giphy.com/media/3o7TKDkvyTb75CkIJa/giphy.gif",
            "https://media.giphy.com/media/1wrzPbtfyN8jLS07D3/giphy.gif",
            "https://media.giphy.com/media/3oriNL7HkrKQkZwpu8/giphy.gif",
            "https://media.giphy.com/media/1BeZUvPQyw0KroGIxm/giphy.gif",
            "https://media.giphy.com/media/ckCH0ztALHrhnsZ8br/giphy.gif",
            "https://media.giphy.com/media/12UUnm0znMSmyY/giphy.gif"
        ])
    )


@tree.command(
    name="hello",
    description="Says hello",
)
async def hello(interaction):
    """Says hello."""
    await interaction.response.send_message("I am DiceUtils, I roll dice.")


@tree.command(
    name="tbh",
    description="Says tbh",
)
async def tbh(interaction):
    """Says tbh."""
    await interaction.response.send_message(random.choice(tbhlist))


@tree.command(
    name="say",
    description="Says the message input",
)
async def say(interaction, text: str):
    """Says the message input."""
    await interaction.response.send_message(text)


@tree.command(
    name="createpot",
    description="Creates a new chip pot",
)
async def createpot(interaction, name: str, red: int = 25, white: int = 50, blue: int = 10):
    """Creates a deck."""
    new_pot = ChipPot.init_pot(name, red, white, blue)
    new_pot.name = name
    card_data.add_pot(new_pot)
    await interaction.response.send_message(f"Pot {name} created with {white} white chips, {red} red chips, and {blue} blue chips.")

@tree.command(
    name="delpot",
    description="Deletes a chip pot",
)
async def delpot(interaction, name: str):
    """Creates a deck."""
    if name not in card_data.pots:
        await interaction.response.send_message(f"Pot {name} does not exist.", ephemeral=True)
    else:
        del card_data.pots[name]
        await interaction.response.send_message(f"Pot {name} has been cast into the Void.")


@tree.command(
    name="cdraw",
    description="Draws a chip",
)
async def cdraw(interaction, pot: str, color: str, count: int = 1):
    """Draws a card."""
    if card_data.pots[pot].get_chip_count() == 0:
        await interaction.response.send_message("The pot is empty.", ephemeral=True)
    elif color not in cards.valid_chip_colors:
        await interaction.response.send_message(f"Invalid color {color}", ephemeral=True)
    elif card_data.pots[pot].chips[color] == 0:
        await interaction.response.send_message(f"The pot has no {color} chips.", ephemeral=True)
    elif card_data.pots[pot].chips[color] < count:
        await interaction.response.send_message(f"The pot has insufficient {color} chips.", ephemeral=True)
    else:
        card_data.pots[pot].draw_chips(color, count)
        if interaction.user.id not in card_data.pots[pot].hands:
            card_data.pots[pot].hands[interaction.user.id] = cards.ChipHand(pot, interaction.user.id, {})
        card_data.pots[pot].hands[interaction.user.id].add_chips(color, count)
        await interaction.response.send_message(f"{count} {color} chips drawn.", ephemeral=True)

@tree.command(
    name="cplay",
    description="Plays a chip",
)
async def cplay(interaction, pot: str, color: str, count: int = 1):
    """Draws a card."""
    if pot not in card_data.pots:
        await interaction.response.send_message(f"Pot {pot} does not exist.", ephemeral=True)
    elif interaction.user.id not in card_data.pots[pot].hands:
        await interaction.response.send_message(f"You have no hand for this pot.", ephemeral=True)
    elif color not in cards.valid_chip_colors:
        await interaction.response.send_message(f"Invalid color {color}", ephemeral=True)
    elif card_data.pots[pot].hands[interaction.user.id].chips[color] == 0:
        await interaction.response.send_message(f"You have no {color} chips.", ephemeral=True)
    elif card_data.pots[pot].hands[interaction.user.id].chips[color] < count:
        await interaction.response.send_message(f"The pot has insufficient {color} chips.", ephemeral=True)
    else:
        for _ in range(count):
            card_data.pots[pot].hands[interaction.user.id].play_chip(color, pot)
        await interaction.response.send_message(f"{count} {color} chips played.", ephemeral=True)

@tree.command(
    name="cview",
    description="Views your chips",
)
async def cview(interaction, pot: str):
    """Draws a card."""
    if pot not in card_data.pots:
        await interaction.response.send_message(f"Pot {pot} does not exist.", ephemeral=True)
    elif interaction.user.id not in card_data.pots[pot].hands:
        await interaction.response.send_message(f"You have no hand for this pot.", ephemeral=True)
    hand_chips = card_data.pots[pot].hands[interaction.user.id].chips
    await interaction.response.send_message(f"You have {hand_chips['white']} white chips, {hand_chips['red']} red chips, and {hand_chips['blue']} blue chips", ephemeral=True)

@tree.command(
    name="crdraw",
    description="Draws a chip randomly",
)
async def crdraw(interaction, pot: str, count: int = 1):
    """Draws a card."""
    chip_counts = {}
    if card_data.pots[pot].get_chip_count() == 0:
        await interaction.response.send_message("The pot is empty.", ephemeral=True)
    elif card_data.pots[pot].get_chip_count() < count:
        await interaction.response.send_message(f"The pot has insufficient chips.", ephemeral=True)
    else:
        chips_drawn = card_data.pots[pot].draw_chips_rand(count)
        if interaction.user.id not in card_data.pots[pot].hands:
            card_data.pots[pot].hands[interaction.user.id] = cards.ChipHand(pot, interaction.user.id, {})
        for chip in chips_drawn:
            card_data.pots[pot].hands[interaction.user.id].add_chips(chip, 1)
            if chip not in chip_counts:
                chip_counts[chip] = 0
            chip_counts[chip] += 1
        await interaction.response.send_message(f"{count} chips drawn, {chip_counts['white']} white, "
                                                f"{chip_counts['red']} red, {chip_counts['blue']} blue.",
                                                ephemeral=True)

@tree.command(
    name="createdeck",
    description="Creates a new deck",
)
async def createdeck(interaction, name: str, jokers: bool = False, shuffle: bool = True):
    """Creates a deck."""
    new_deck = Deck.init_cards_default(name, jokers)
    new_deck.name = name
    if shuffle:
        new_deck.shuffle()
    new_game = Game(name, {}, {})
    new_game.add_deck(new_deck)
    card_data.add_game(new_game)
    await interaction.response.send_message(f"Deck {name} created.")


@tree.command(
    name="draw",
    description="Draws a card",
)
async def draw(interaction, deck: str, count: int = 1):
    """Draws a card."""
    if len(card_data.games[deck].decks[deck].cards) == 0:
        await interaction.response.send_message("The deck is empty.", ephemeral=True)
    else:
        drawn_cards = []
        for _ in range(count):
            drawn_card = card_data.games[deck].decks[deck].draw()
            if drawn_card is None:
                break  # deck is empty
            drawn_cards.append(drawn_card)
            if interaction.user.id not in card_data.games[deck].hands:
                card_data.games[deck].hands[interaction.user.id] = Hand([], interaction.user.id)
            card_data.games[deck].hands[interaction.user.id].add_card(drawn_card)
        await interaction.response.send_message(", ".join([str(card) for card in drawn_cards]), ephemeral=True)

@tree.command(
    name="drawdiscard",
    description="Draws a card from the discard pile",
)
async def drawdiscard(interaction, deck: str, count: int = 1):
    """Draws a card."""
    if len(card_data.games[deck].decks[deck].discarded) == 0:
        await interaction.response.send_message("The discard pile is empty.", ephemeral=True)
    else:
        drawn_cards = []
        for _ in range(count):
            drawn_card = card_data.games[deck].decks[deck].draw_discard()
            if drawn_card is None:
                break  # deck is empty
            drawn_cards.append(drawn_card)
            if interaction.user.id not in card_data.games[deck].hands:
                card_data.games[deck].hands[interaction.user.id] = Hand([], interaction.user.id)
            card_data.games[deck].hands[interaction.user.id].add_card(drawn_card)
        await interaction.response.send_message(", ".join([str(card) for card in drawn_cards]), ephemeral=True)

@tree.command(
    name="peekdiscard",
    description="Shows the top card on the discard pile",
)
async def peekdiscard(interaction, deck: str):
    """Draws a card."""
    if len(card_data.games[deck].decks[deck].discarded) == 0:
        await interaction.response.send_message("The discard pile is empty.")
    else:
        await interaction.response.send_message(card_data.games[deck].decks[deck].discarded[-1])

@tree.command(
    name="hand",
    description="See your hand",
)
async def hand(interaction, deck: str):
    """Shows your hand."""
    if deck not in card_data.games or deck not in card_data.games[deck].decks:
        await interaction.response.send_message(f"Deck {deck} does not exist.", ephemeral=True)
    if interaction.user.id not in card_data.games[deck].hands:
        await interaction.response.send_message("You do not have a hand for this deck.", ephemeral=True)
    else:
        display_hand = card_data.games[deck].hands[interaction.user.id]
        await interaction.response.send_message(display_hand if len(display_hand.cards) > 0
                                                else "Your hand is empty.", ephemeral=True)


@tree.command(
    name="shuffle",
    description="Shuffles a deck",
)
async def shuffle(interaction, deck: str):
    """Draws a card."""
    if deck not in card_data.games or deck not in card_data.games[deck].decks:
        await interaction.response.send_message(f"Deck {deck} does not exist.", ephemeral=True)
    card_data.games[deck].decks[deck].shuffle()
    await interaction.response.send_message(f"Deck {deck} shuffled.")

@tree.command(
    name="forceshuffle",
    description="Shuffles a deck, removing all its cards from hands",
)
async def forceshuffle(interaction, deck: str):
    """Draws a card."""
    if deck not in card_data.games or deck not in card_data.games[deck].decks:
        await interaction.response.send_message(f"Deck {deck} does not exist.", ephemeral=True)
    hands_to_delete = []
    for hand in card_data.games[deck].hands.values():
        new_cards = []
        for card in hand.cards:
            if card.deck != deck:
                new_cards.append(card)
        hand.cards = new_cards
        if len(hand.cards) == 0:
            hands_to_delete.append(hand.member)
    for del_hand in hands_to_delete:
        del card_data.games[deck].hands[del_hand]
    card_data.games[deck].decks[deck].shuffle(include_drawn=True)
    await interaction.response.send_message(f"Deck {deck} shuffled, including cards in hands.")


@tree.command(
    name="discard",
    description="Discards a card",
)
async def discard(interaction, deck: str, index: int):
    """Discards a card."""
    if interaction.user.id not in card_data.games[deck].hands:
        await interaction.response.send_message("You do not have a hand for this deck.", ephemeral=True)
    elif index < 1 or index > len(card_data.games[deck].hands[interaction.user.id].cards):
        await interaction.response.send_message("Card index out of range.", ephemeral=True)
    else:
        card = card_data.games[deck].hands[interaction.user.id].discard(index-1, card_data.games[deck].decks[deck])
        await interaction.response.send_message(f"{card} discarded.", ephemeral=True)

@tree.command(
    name="reveal",
    description="Reveals a card",
)
async def reveal(interaction, deck: str, index: int):
    """Reveals a card."""
    if interaction.user.id not in card_data.games[deck].hands:
        await interaction.response.send_message("You do not have a hand for this deck.", ephemeral=True)
    elif index < 1 or index > len(card_data.games[deck].hands[interaction.user.id].cards):
        await interaction.response.send_message("Card index out of range.", ephemeral=True)
    else:
        card = card_data.games[deck].hands[interaction.user.id].cards[index-1]
        await interaction.response.send_message(card)


@tree.command(
    name="discardhand",
    description="Discards all cards in your hand",
)
async def discardhand(interaction, deck: str):
    """Discards all cards in your hand."""
    if interaction.user.id not in card_data.games[deck].hands:
        await interaction.response.send_message("You do not have a hand for this deck.", ephemeral=True)
    else:
        for _ in card_data.games[deck].hands[interaction.user.id].cards:
            card_data.games[deck].hands[interaction.user.id].discard(0, card_data.games[deck].decks[deck])
        del card_data.games[deck].hands[interaction.user.id]
        await interaction.response.send_message(f"Hand discarded.", ephemeral=True)


@tree.command(
    name="revealhand",
    description="Reveals all cards in your hand",
)
async def revealhand(interaction, deck: str):
    """Reveals all cards in your hand."""
    if interaction.user.id not in card_data.games[deck].hands:
        await interaction.response.send_message("You do not have a hand for this deck.", ephemeral=True)
    else:
        await interaction.response.send_message(", ".join([str(card) for card in card_data.games[deck].hands[interaction.user.id].cards]))


@tree.command(
    name="deldeck",
    description="Deletes a deck",
)
async def deldeck(interaction, deck: str):
    """Deletes a deck."""
    if deck not in card_data.games or deck not in card_data.games[deck].decks:
        await interaction.response.send_message(f"Deck {deck} does not exist.", ephemeral=True)
    else:
        for del_hand in card_data.games[deck].hands.values():
            for card in del_hand.cards:
                if card.deck == deck:
                    del_hand.cards.remove(card)
        del card_data.games[deck].decks[deck]
        if len(card_data.games[deck].decks) == 0:
            del card_data.games[deck]
        await interaction.response.send_message(f"Deck {deck} has been cast into the Void.")


with open("token.txt") as f:
    discord_api_token = f.read().strip()

if os.path.exists("cards.json"):
    with open("cards.json") as f:
        card_data = CardsData.deserialize(json.load(f))
    pass  # this is here because my IDE is being strange with the nested blocks
else:
    card_data = CardsData.setup()


if __name__ == '__main__':
    client.run(discord_api_token)

# this is outside the with block so that this failing doesn't wipe the file
cards_dict = card_data.serialize()
with open("cards.json", "w") as f:
    json.dump(cards_dict, f)
