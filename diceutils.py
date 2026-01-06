import random
import multiprocessing

import discord
from discord import app_commands

tbhlist = ["Tbh", "Tbh is overused, tbh.", "*Tbh*",
           ":regional_indicator_t: :regional_indicator_b: :regional_indicator_h:", "**Tbh**",
           "Tbh, like I don’t like the phrase tbh as like tbh I hate it."]


class DiceError(Exception):
    """dice error"""

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class DiceUtils(discord.Client):
    async def on_ready(self):
        """Runs when the bot logs into Discord"""
        # update slash commands
        await tree.sync()
        print('Logged on as', self.user)


def float_or_error(num):
    try:
        return float(num)
    except ValueError:
        raise DiceError("Invalid expression syntax")


def roll_dice(q, dsize, ndice):
    result = []
    for i in range(ndice):
        q.put(random.randint(1, dsize))
    return result


def valid_dice_roll(test_roll):
    if len(test_roll) != 2:
        return False
    if test_roll[0].isnumeric() and test_roll[1].isnumeric() and int(test_roll[1]) > 0:
        return True
    return False


def too_many_dice(test_roll):
    if len(test_roll) > 0 and test_roll[0].isnumeric():
        if int(test_roll[0]) > 2000:
            return True
        return False
    return False


def roll_all_dice(ndice, dsize):
    tobjs = []
    results = []
    q = multiprocessing.Queue()
    for i in range(10):
        nd = ndice // 10
        if i == 9:
            nd += ndice % 10
        t = multiprocessing.Process(target=roll_dice, args=(q, dsize, nd))
        tobjs.append(t)
        t.start()
    for t in tobjs:
        t.join()
    for i in range(ndice):
        results.append(q.get())
    return results


def is_operator(char):
    operators = ["+", "-", "*", "/", "^"]
    return char in operators


def combine_ops(cur, prev):
    print("combining: "+str(cur)+", "+str(prev)+"?")
    if cur == "+" and prev == "-" or cur == "-" and prev == "+":
        return "-"
    elif cur == "-" and prev == "-":
        return "+"
    elif cur == "+" and prev == "+":
        return "+"
    else:
        return None


def collapse_repeated_ops(tokens):
    final = []
    new = ""
    i = len(tokens)-1
    while i >= 0:
        cur = tokens[i]
        skip_prepend = False
        print("testing, cur: " + str(cur)+", final: " + str(final)+" cur is op: "+str(is_operator(cur))
              +" final[-1] is op: "+str(is_operator(final[0] if len(final) > 0 else "None")))
        if is_operator(cur) and len(final) > 0 and is_operator(final[0]):
            print("trying to combine, final is: "+str(final))
            new_op = combine_ops(cur, final[0])
            if new_op is not None:
                final[0] = new_op
                print("combined, final is now: " + str(final))
                skip_prepend = True

        if not skip_prepend:
            final = [cur] + final  # prepend cur to final
        i -= 1
    return final


def tokenize(text):
    tokens = []
    paren_token = ""
    paren_level = 0
    cur_token_str = ""
    for char in text:
        if char.isspace():
            continue
        elif char == "(":
            if paren_level == 0:
                if cur_token_str != "":
                    tokens.append(cur_token_str[:])
                    cur_token_str = ""
            else:
                paren_token = paren_token + "("
            paren_level += 1
        elif char == ")":
            paren_level -= 1
            if paren_level == 0:
                tokens.append(tokenize(paren_token))
                paren_token = ""
            else:
                paren_token = paren_token + ")"
        elif paren_level > 0:
            paren_token = paren_token + char
        elif not is_operator(char):
            if cur_token_str != "" and is_operator(cur_token_str[-1]):
                tokens.append(cur_token_str[:])
                cur_token_str = ""
            cur_token_str = cur_token_str + char
        else:
            if cur_token_str != "":
                tokens.append(cur_token_str[:])
            cur_token_str = char

    if cur_token_str != "":
        tokens.append(cur_token_str[:])

    collapsed = collapse_repeated_ops(tokens)
    return collapsed


def eval_exp(tokens):
    tokens_pass1 = (tokens[:])
    tokens_pass1.reverse()
    tokens_pass2 = []
    first_pass = True
    while "^" in tokens_pass1 or first_pass:
        first_pass = False
        last_token = ""
        last_op = ""
        tokens_pass2 = []
        for token in tokens_pass1:
            if token == "^" and last_op != "":
                raise DiceError("Invalid expression syntax")
            elif token == "^":
                last_op = "^"
            elif last_op != "":
                # tokens_pass2.append(str(float(last_token)**float(token)))
                if last_token == "" or token == "":
                    raise DiceError("Invalid expression syntax")
                last_token = str(float_or_error(token) ** float_or_error(last_token))
                last_op = ""
            else:
                if last_token != "":
                    tokens_pass2.append(last_token)
                last_token = token
        if last_token != "":
            tokens_pass2.append(last_token)
        tokens_pass1 = tokens_pass2[:]
        if last_op != "":
            raise DiceError("Invalid expression syntax")
    tokens_pass2.reverse()
    return tokens_pass2


def eval_mul_div(tokens):
    tokens_pass2 = tokens[:]
    tokens_pass3 = []
    first_pass = True
    while "*" in tokens_pass2 or "/" in tokens_pass2 or first_pass:
        first_pass = False
        last_token = ""
        last_op = ""
        tokens_pass3 = []
        for token in tokens_pass2:
            if (token == "*" or token == "/") and last_op != "":
                raise DiceError("Invalid expression syntax")
            elif token == "*":
                last_op = "*"
            elif token == "/":
                last_op = "/"
            elif last_op == "*":
                # tokens_pass3.append(str(float(last_token)*float(token)))
                if last_token == "" or token == "":
                    raise DiceError("Invalid expression syntax")
                last_token = str(float_or_error(last_token) * float_or_error(token))
                last_op = ""
            elif last_op == "/":
                # tokens_pass3.append(str(float(last_token)/float(token)))
                if last_token == "" or token == "":
                    raise DiceError("Invalid expression syntax")
                last_token = str(float_or_error(last_token) / float_or_error(token))
                last_op = ""
            else:
                if last_token != "":
                    tokens_pass3.append(last_token)
                last_token = token
        if last_token != "":
            tokens_pass3.append(last_token)
        tokens_pass2 = tokens_pass3[:]
        if last_op != "":
            raise DiceError("Invalid expression syntax")
    return tokens_pass3


def eval_add_sub(tokens):
    tokens_pass3 = tokens[:]
    tokens_pass4 = []
    first_pass = True
    while "+" in tokens_pass3 or "-" in tokens_pass3 or first_pass:
        first_pass = False
        print("tokens_pass3 is " + str(tokens_pass3))
        last_token = ""
        last_op = ""
        tokens_pass4 = []
        for token in tokens_pass3:
            if token == "+":
                last_op = "+"
            elif token == "-":
                last_op = "-"
            elif last_op == "+":
                # tokens_pass4.append(str(float(last_token)+float(token)))
                if last_token == "":
                    last_token = "0"
                if token == "":
                    raise DiceError("Invalid expression syntax")
                print("A")
                last_token = str(float_or_error(last_token) + float_or_error(token))
                last_op = ""
            elif last_op == "-":
                if last_token == "":
                    last_token = "0"
                if token == "":
                    raise DiceError("Invalid expression syntax")
                # tokens_pass4.append(str(float(last_token)-float(token)))
                print("S")
                last_token = str(float_or_error(last_token) - float_or_error(token))
                last_op = ""
            else:
                if last_token != "":
                    tokens_pass4.append(last_token)
                last_token = token
        if last_token != "":
            tokens_pass4.append(last_token)
        tokens_pass3 = tokens_pass4[:]
        if last_op != "":
            raise DiceError("Invalid expression syntax")
    return tokens_pass4


def process_dice(token):
    if token[0].isnumeric():
        token = "sum" + token

    func = token[:3]
    token = token[3:]
    token_str = token
    token = token.split("d")
    print(func)
    print(token)

    valid = valid_dice_roll(token)
    too_many = too_many_dice(token)

    if valid and not too_many:
        rollvals = roll_all_dice(int(token[0]), int(token[1]))
    elif not valid:
        raise DiceError("Invalid dice roll: " + token_str)
    elif too_many:
        raise DiceError("Too many dice: " + token_str)
    else:
        raise DiceError("Error: " + token_str)

    print(rollvals)

    if func == "adv":
        result = max(rollvals)
    elif func == "dis":
        result = min(rollvals)
    elif func == "avg":
        result = sum(rollvals) / float(len(rollvals))
    else:
        result = sum(rollvals)

    return str(result)


def evaluate(tokens_pass0):
    print("Pass 0: " + str(tokens_pass0))

    tokens_pass1 = []
    for token in tokens_pass0:
        if isinstance(token, list):
            tokens_pass1.append(str(evaluate(token)))
        else:
            tokens_pass1.append(token)

    print("Pass 1: " + str(tokens_pass1))

    tokens_pass1b = []
    for token in tokens_pass1:
        if "d" in token:
            tokens_pass1b.append(process_dice(token))
        else:
            tokens_pass1b.append(token)

    print("Pass 1b: " + str(tokens_pass1b))

    tokens_pass2 = eval_exp(tokens_pass1b)

    print("Pass 2: " + str(tokens_pass2))

    tokens_pass3 = eval_mul_div(tokens_pass2)

    print("Pass 3: " + str(tokens_pass3))

    tokens_pass4 = eval_add_sub(tokens_pass3)

    print("Pass 4: " + str(tokens_pass4))

    if len(tokens_pass4) != 1:
        raise DiceError("Invalid expression")

    return tokens_pass4[0]


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


def get_max_initiative(totals, additives):
    max_val = -1 # initiative totals are nonnegative
    max_inds = [] # indices where the maximum value occurs
    for i in range(len(totals)):
        # new maximum, reset occurences
        if totals[i] > max_val: 
            max_val = totals[i]
            max_inds = [i]
        # repeat of current max, add to list
        elif totals[i] == max_val:
            max_inds.append(i)

    # if there is only one maximum, return it
    if len(max_inds) == 1:
        return max_inds[0]

    # if there is a tie, try to use the additive to break the tie

    max_add = 0 # additives are positive
    max_add_inds = [] # indices where max additive occurs

    for i in range(len(max_inds)):
        # new maximum, reset occurences
        if additives[max_inds[i]] > max_add:
            max_add = additives[max_inds[i]]
            max_add_inds = [max_inds[i]]
        # repeat of current max, add to list
        elif additives[max_inds[i]] == max_add:
            max_add_inds.append(max_inds[i])

    # if there is now only one maximum, return it
    if len(max_add_inds) == 1:
        return max_add_inds[0]
    
    # else, randomly pick among the remaining ties (tied with both total and additive)
    return random.choice(max_add_inds)


def roll_init_helper(turns, starts, incrs, names, debug):
        totals = starts[:]
        turn_order = []
        turn_totals_pre = []
        turn_totals_post = []
        round_starts = [0] # turn numbers (zero-based) just before which a new round starts
        taken_turns = [False]*len(names)
        for i in range(turns):
            current = get_max_initiative(totals, incrs)
            turn_totals_pre.append("["+(",".join([str(val) for val in totals]))+"]")
            turn_order.append(current)
            totals = [totals[j] + incrs[j] for j in range(len(totals))]
            totals[current] = 0
            turn_totals_post.append("["+(",".join([str(val) for val in totals]))+"]")
            taken_turns[current] = True # has taken a turn
            if False not in taken_turns: # everyone has taken a turn, round over
                round_starts.append(len(turn_order)) # record round start after this turn
                taken_turns = [False]*len(names) # reset taken_turns


        turn_log = []
        for i in range(len(turn_order)):
            new_turn = ""
            if i in round_starts:
                new_turn += "=== NEW ROUND ===\n"
            new_turn += "Turn "+str(i+1)+": "+names[turn_order[i]]
            if debug:
                new_turn += " (debug: "+turn_totals_pre[i]+" -> "+turn_totals_post[i]+")"
            turn_log.append(new_turn)

        return "\n".join(turn_log)


async def roll_init_cmd_helper(interaction, turns, starts, increments, names, debug):
    try:
        incrs_l = [int(val) for val in increments.split(",")]
        if "," in starts:
            starts_l = [int(val) for val in starts.split(",")]
        elif starts == "-":
            starts_l = incrs_l[:]
        else:
            raise ValueError("oops")

        names_l = names.split(",")
        turn_order = roll_init_helper(turns, starts_l, incrs_l, names_l, debug)
        if len(turn_order) < 2000:
            await interaction.response.send_message(turn_order)
        else:
            await interaction.response.send_message("Output would exceed 2000 characters", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Argument syntax error", ephemeral=True)
        

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


with open("token.txt") as f:
    discord_api_token = f.read().strip()

if __name__ == '__main__':
    client.run(discord_api_token)
