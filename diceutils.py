import discord
from discord.ext import commands
import asyncio
import os
import os.path
import sqlite3
import datetime
import random
import logging
import pickle
import multiprocessing

taglimit = 0
overflow = False

def roll_dice(q,dsize,ndice):
    result = []
    for i in range(ndice):
        q.put(random.randint(1,dsize))
    return result


if __name__ == '__main__':

    tbhlist = ["Tbh", "Tbh is overused, tbh.", "*Tbh*", ":regional_indicator_t: :regional_indicator_b: :regional_indicator_h:", "**Tbh**", "Tbh, like I don’t like the phrase tbh as like tbh I hate it."]

    prefix='-'

    bot = commands.Bot(command_prefix=prefix, description="Rolls dice for you.")

    cmds = []

    def load_listing(fname, arr):
        with open(fname) as f:
            g = f.read()
            lore_raw = g.split("\n")
            for line in lore_raw:
                entry_raw = line.split("\t")
                if len(entry_raw) < 2:
                    continue
                arr.append(entry_raw)


    def load_data():
        global cmds
        cmds = []
        load_listing("cmds.tsv", cmds)

    def split_args(args):
        i = 0
        argsl = []
        inquote = False
        for char in args:
            if char == "\"":
                inquote = not inquote
                continue
            if char == " " and not inquote:
                i = i + 1
                continue
            if len(argsl) == i + 1:
                argsl[i] = argsl[i] + char
            else:
                argsl.append(char)

        return argsl

    def valid_dice_roll(roll):
        if len(roll) != 2:
            return False
        if roll[0].isnumeric() and roll[1].isnumeric() and int(roll[1]) > 0:
            return True
        return False

    def too_many_dice(roll):
        if len(roll) > 0 and roll[0].isnumeric():
            if int(roll[0]) > 2000:
                return True
            return False
        return False

    def roll_dice_old(roll):
        result = []
        for i in range(int(roll[0])):
            result.append(random.randint(1,int(roll[1])))
        return result

    def roll_dice_all(roll):
        result = []
        for i in range(int(roll[0])):
            result.append(random.randint(1,int(roll[1])))
        return result

    tobjs = []

    def roll_all_dice(ndice, dsize):
        tobjs = []
        results = []
        q = multiprocessing.Queue()
        for i in range(10):
            nd = ndice//10
            if i == 9:
                nd += ndice%10
            t = multiprocessing.Process(target=roll_dice, args=(q,dsize,nd))
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

    def tokenize(text):
        tokens = []
        paren_token = ""
        paren_level = 0
        cur_token_str = ""
        for char in text:
            if char == "(":
                if paren_level == 0:
                    if cur_token_str != "":
                        tokens.append(cur_token_str[:])
                        cur_token_str = ""
                else:
                    paren_token = paren_token + "("
                paren_level +=1
            elif char == ")":
                paren_level -=1
                if paren_level == 0:
                    tokens.append(tokenize(paren_token))
                    paren_token = ""
                else:
                    paren_token = paren_token + ")"
            elif paren_level>0:
                paren_token = paren_token+char
            elif not is_operator(char):
                if cur_token_str != "" and is_operator(cur_token_str[-1]):
                    tokens.append(cur_token_str[:])
                    cur_token_str = ""
                cur_token_str = cur_token_str+char
            else:
                if cur_token_str != "":
                    tokens.append(cur_token_str[:])
                cur_token_str = char

        if cur_token_str != "":
            tokens.append(cur_token_str[:])
        return tokens


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
                if token == "^":
                    last_op = "^"
                elif last_op != "":
                    #tokens_pass2.append(str(float(last_token)**float(token)))
                    last_token = str(float(token)**float(last_token))
                    last_op = ""
                else:
                    if last_token != "":
                        tokens_pass2.append(last_token)
                    last_token = token
            if last_token != "":
                tokens_pass2.append(last_token)
            tokens_pass1 = tokens_pass2[:]
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
                if token == "*":
                    last_op = "*"
                elif token == "/":
                    last_op = "/"
                elif last_op == "*":
                    #tokens_pass3.append(str(float(last_token)*float(token)))
                    last_token = str(float(last_token)*float(token))
                    last_op = ""
                elif last_op == "/":
                    #tokens_pass3.append(str(float(last_token)/float(token)))
                    last_token = str(float(last_token)/float(token))
                    last_op = ""
                else:
                    if last_token != "":
                        tokens_pass3.append(last_token)
                    last_token = token
            if last_token != "":
                tokens_pass3.append(last_token)
            tokens_pass2 = tokens_pass3[:]
        return tokens_pass3

    def eval_add_sub(tokens):
        tokens_pass3 = tokens[:]
        tokens_pass4 = []
        first_pass = True
        while "+" in tokens_pass3 or "-" in tokens_pass3 or first_pass:
            first_pass = False
            print("tokens_pass3 is "+str(tokens_pass3))
            last_token = ""
            last_op = ""
            tokens_pass4 = []
            for token in tokens_pass3:
                if token == "+":
                    last_op = "+"
                elif token == "-":
                    last_op = "-"
                elif last_op == "+":
                    #tokens_pass4.append(str(float(last_token)+float(token)))
                    last_token = str(float(last_token)+float(token))
                    last_op = ""
                elif last_op == "-":
                    #tokens_pass4.append(str(float(last_token)-float(token)))
                    last_token = str(float(last_token)-float(token))
                    last_op = ""
                else:
                    if last_token != "":
                        tokens_pass4.append(last_token)
                    last_token = token
            if last_token != "":
                tokens_pass4.append(last_token)
            tokens_pass3 = tokens_pass4[:]
        return tokens_pass4


    def process_dice(token):
        if token[0].isnumeric():
            token = "sum"+token

        func = token[:3]
        token = token[3:]
        token = token.split("d")
        print(func)
        print(token)
        rollvals = roll_all_dice(int(token[0]), int(token[1]))
        print(rollvals)
        result = 0

        if func == "adv":
            result = max(rollvals)
        elif func == "dis":
            result = min(rollvals)
        elif func == "avg":
            result = sum(rollvals)/float(len(rollvals))
        else:
            result = sum(rollvals)

        return str(result)

    def evaluate(tokens_pass0):
        print("Pass 0: "+str(tokens_pass0))

        tokens_pass1 = []
        for token in tokens_pass0:
            if type(token) == type([]):
                tokens_pass1.append(str(evaluate(token)))
            else:
                tokens_pass1.append(token)

        print("Pass 1: "+str(tokens_pass1))

        tokens_pass1b = []
        for token in tokens_pass1:
            if "d" in token:
                tokens_pass1b.append(process_dice(token))
            else:
                tokens_pass1b.append(token)


        print("Pass 1b: "+str(tokens_pass1b))

        tokens_pass2 = eval_exp(tokens_pass1b)

        print("Pass 2: "+str(tokens_pass2))

        tokens_pass3 = eval_mul_div(tokens_pass2)

        print("Pass 3: "+str(tokens_pass3))   

        tokens_pass4 = eval_add_sub(tokens_pass3)    

        print("Pass 4: "+str(tokens_pass4))

        return tokens_pass4[0]   


    @bot.command(hidden=True)
    async def calc(ctx):
        expr = "".join(ctx.message.content.split(" ")[1:])
        tokens_all = tokenize("".join(ctx.message.content.split(" ")[1:]))
        result = evaluate(tokens_all)
        await ctx.send("`"+expr+" -> "+str(tokens_all)+" -> "+str(result)+"`")

    @bot.command(hidden=True)
    async def roll(ctx):
        text = " ".join(ctx.message.content.split(" ")[1:])
        """Rolls dice."""
        mod = 0
        if text.startswith("d"):
            text = "1"+text
        roll_phase1 = text.split("d")
        print(roll_phase1)
        if "+" in roll_phase1[1]:
            foo = roll_phase1[1].split("+")
            if foo[1].isnumeric():
                roll = [roll_phase1[0], foo[0]]
                mod = int(foo[1])
            else:
                roll = roll_phase1
        elif "-" in roll_phase1[1]:
            foo = roll_phase1[1].split("-")
            if foo[1].isnumeric():
                roll = [roll_phase1[0], foo[0]]
                mod = int(foo[1])*-1
            else:
                roll = roll_phase1
        else:
            roll = roll_phase1
        if valid_dice_roll(roll) and not too_many_dice(roll):
            results_raw = roll_all_dice(int(roll[0]), int(roll[1]))
            results = ""
            if mod != 0:
                for result in results_raw:
                    results += str(result+mod)+" *("+str(result)+")*,  "
                results = results[:-3]
            else:
                results = str(results_raw)[1:-1]
            outstr = "Rolled "+text+":\n"+results
            outlen = len(outstr)
            while len(outstr) > 2000:
                await ctx.send(outstr[:2000])
                outstr = outstr[2000:]
                outlen-=2000
            await ctx.send(outstr)
            #await bot.delete_message(ctx.message)
        elif too_many_dice(roll):
            await ctx.send("Error: `"+text+"` rolls more than 2000 dice.")
        else:
            await ctx.send("Error: `"+text+"` is not a valid dice roll.")


    @bot.command(hidden=True)
    async def r(ctx):
        text = " ".join(ctx.message.content.split(" ")[1:])
        await roll(ctx, text) #alias

    is_ready = False


    load_data()

    @bot.event
    async def on_ready():
        global is_ready
        await bot.change_presence(activity=discord.Game(name='Prefix: '+prefix))
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
        is_ready = True

    @bot.command()
    async def alive(ctx):
        await ctx.send("I'm a bot, how can you kill a bot? What a grand and intoxicating innocence.")

    @bot.command()
    async def catgif(ctx):
        await ctx.send("https://imgur.com/QZGHA0i")


    @bot.command()  
    async def spike(ctx):
            await ctx.send("MFVFLVLLPLVSSQCVNLTTRTQLPPAYTNSFTRGVYYPDKVFRSSVLHSTQDLFLPFFSNVTWFHAIHVSGTNGTKRFDNPVLPFNDGVYFASTEKSNIIRGWIFGTTLDSKTQSLLIVNNATNVVIKVCEFQFCNDPFLGVYYHKNNKSWMESEFRVYSSANNCTFEYVSQPFLMDLEGKQGNFKNLREFVFKNIDGYFKIYSKHTPINLVRDLPQGFSALEPLVDLPIGINITRFQTLLALHRSYLTPGDSSSGWTAGAAAYYVGYLQPRTFLLKYNENGTITDAVDCALDPLSETKCTLKSFTVEKGIYQTSNFRVQPTESIVRFPNITNLCPFGEVFNATRFASVYAWNRKRISNCVADYSVLYNSASFSTFKCYGVSPTKLNDLCFTNVYADSFVIRGDEVRQIAPGQTGKIADYNYKLPDDFTGCVIAWNSNNLDSKVGGNYNYLYRLFRKSNLKPFERDISTEIYQAGSTPCNGVEGFNCYFPLQSYGFQPTNGVGYQPYRVVVLSFELLHAPATVCGPKKSTNLVKNKCVNFNFNGLTGTGVLTESNKKFLPFQQFGRDIADTTDAVRDPQTLEILDITPCSFGGVSVITPGTNTSNQVAVLYQDVNCTEVPVAIHADQLTPTWRVYSTGSNVFQTRAGCLIGAEHVNNSYECDIPIGAGICASYQTQTNSPRRARSVASQSIIAYTMSLGAENSVAYSNNSIAIPTNFTISVTTEILPVSMTKTSVDCTMYICGDSTECSNLLLQYGSFCTQLNRALTGIAVEQDKNTQEVFAQVKQIYKTPPIKDFGGFNFSQILPDPSKPSKRSFIEDLLFNKVTLADAGFIKQYGDCLGDIAARDLICAQKFNGLTVLPPLLTDEMIAQYTSALLAGTITSGWTFGAGAALQIPFAMQMAYRFNGIGVTQNVLYENQKLIANQFNSAIGKIQDSLSSTASALGKLQDVVNQNAQALNTLVKQLSSNFGAISSVLNDILSRLDKVEAEVQIDRLITGRLQSLQTYVTQQLIRAAEIRASANLAATKMSECVLGQSKRVDFCGKGYHLMSFPQSAPHGVVFLHVTYVPAQEKNFTTAPAICHDGKAHFPREGVFVSNGTHWFVTQRNFYEPQIITTDNTFVSGNCDVVIGIVNNTVYDPLQPELDSFKEELDKYFKNHTSPDVDLGDISGINASVVNIQKEIDRLNEVAKNLNESLIDLQELGKYEQYIKWPWYIWLGFIAGLIAIVMVTIMLCCMTSCCSCLKGCCSCGSCCKFDEDDSEPVLKGVKLHYT")

    @bot.command()
    async def flamingo(ctx):
        await ctx.send(random.choice(["https://tenor.com/view/fabulous-flamingo-gif-7529738", "https://tenor.com/view/flamingos-group-observant-gif-3535692", "https://tenor.com/view/flamingo-hoverboard-collage-animation-loop-gif-14625448", "https://media.discordapp.net/attachments/764804741292752898/770682285980385310/Mc.Mingo.gif", "https://tenor.com/view/birds-flamingos-spin-loop-dance-gif-3483877", "https://media.giphy.com/media/xUPGcAq8idp4tCSMYE/giphy.gif", "https://media.giphy.com/media/uTsG4q5Brun16/giphy.gif", "https://media.giphy.com/media/IFTHx4yEK8o24/giphy.gif", "https://media.giphy.com/media/60rGUCzVNBm7dJWlMj/giphy.gif", "https://media.giphy.com/media/idqa2k5xfkiztiwbnD/giphy.gif", "https://media.giphy.com/media/cir6DQ90LQv2Ccgyte/giphy.gif", "https://media.giphy.com/media/1AiqaeQkzipjnyVHlR/giphy.gif", "https://media.giphy.com/media/dIPv1HC8CacBBYvHUi/giphy.gif", "https://media.giphy.com/media/WOrXn7bffbdjByB8RP/giphy.gif", "https://media.giphy.com/media/3orifj6swylIeuxqRG/giphy.gif", "https://media.giphy.com/media/VaqFVAm7tGlF9hPNus/giphy.gif", "https://media.giphy.com/media/FiKW7YCFJjtNm/giphy.gif", "https://media.giphy.com/media/2tSTBHGEJNlLe1rqQV/giphy.gif", "https://media.giphy.com/media/3o7TKDkvyTb75CkIJa/giphy.gif", "https://media.giphy.com/media/1wrzPbtfyN8jLS07D3/giphy.gif", "https://media.giphy.com/media/3oriNL7HkrKQkZwpu8/giphy.gif", "https://media.giphy.com/media/1BeZUvPQyw0KroGIxm/giphy.gif", "https://media.giphy.com/media/ckCH0ztALHrhnsZ8br/giphy.gif", "https://media.giphy.com/media/12UUnm0znMSmyY/giphy.gif"]))


    @bot.remove_command('help')
    @bot.command()
    async def help(ctx):
        page = ctx.message.content.lower().split(" ")
        if len(page) < 2:
            page = "1"
        else:
            page = page[1]
        if (not page.isnumeric()) or len(cmds) <= (5 * (int(page) - 1) or int(page) < 1):
            embed = discord.Embed(title="Help Error", description="Error: Invalid help page.", color=0xe03e4b)
            embed.set_author(name="DiceUtils", icon_url="")
            await ctx.send(embed=embed)
        else:
            page = int(page)
            embed = discord.Embed(title="Commands", description="DiceUtils commands are as follows:", color=0x4f64f7)
            embed.set_author(name="DiceUtils", icon_url="")

            for i in range(5 * (page - 1), 5 * page):
                try:
                    embed.add_field(name=prefix+cmds[i][0], value=cmds[i][1], inline=False)
                except IndexError:
                    break
            if len(cmds) > 5 * int(page):
                embed.set_footer(text="Type "+prefix+"help " + str(page + 1) + " to view the next page of help!")
            await ctx.send(embed=embed)

    @bot.command()
    async def hello(ctx):
        """Says hello."""
        await ctx.send("I am DiceUtils, I roll dice.")


    @bot.command()
    async def tbh(ctx):
        """Says tbh."""
        await ctx.send(random.choice(tbhlist))

    @bot.command()
    async def hi(ctx):
        """Says hello."""
        await ctx.send("I am DiceUtils, I roll dice.")

    @bot.command(hidden=True)
    async def reload(ctx):
        """Reloads the bot's data files."""
        if ctx.message.author.name == "Valiec":
            await ctx.send("Reloading data files...")
            load_data()
            await ctx.send("Done.")
        else:
            await ctx.send("I'm sorry, "+ctx.message.author.name+", but you don't have permission to use this command.")

    @bot.command(hidden=True)
    async def say(ctx):
        text = " ".join(ctx.message.content.split(" ")[1:])
        """Says the message inputted."""
        await ctx.send(text)
        await bot.delete_message(ctx.message)
        await ctx.send("I'm sorry, "+ctx.message.author.name+", but you don't have permission to use this command.")

    def alpha_only(msg):
        new = ""
        for char in msg.lower():
            if char.isalpha():
                new = new + char
        return new

    @bot.event
    async def on_message(message):
        global taglimit
        global overflow
        global minor_fixes_emoji
        
        if message.author == bot.user:
            return

        '''if ("guten morgen" in message.content.strip().replace(".", "").lower() and message.author.name != "DiceUtils") or ("guten tag" in message.content.strip().replace(".", "").lower() and message.author.name != "DiceUtils") or ("good morning" in message.content.strip().replace(".", "").lower() and message.author.name != "DiceUtils"):
            await message.channel.send("What do you mean? Do you wish me a good morning, or mean that it is a good morning whether I want it or not; or that you feel good this morning; or that it is a morning to be good on?")

        if ("don't tag me" in message.content.strip().replace(".", "").lower() and message.author.name != "DiceUtils") or ("don't ping me" in message.content.strip().replace(".", "").lower() and message.author.name != "DiceUtils"):
            if (taglimit < 100 and not overflow) or (taglimit < 50 and overflow):
                overflow = False
                taglimit = taglimit+10
                await message.channel.send("<@"+str(message.author.id)+">")
        if ("scp" in message.content.strip().replace(".", "").lower().split()[0] or "marvin" in message.content.strip().replace(".", "").lower().split()[0]) and len(message.content.strip().replace(".", "").replace("-", " ").lower().split()) > 1 and message.author.name != "DiceUtils":
            num = message.content.strip().replace(".", "").replace("-", " ").lower().split()[1].zfill(4)
            if int(num) < 1000:
                num = num[1:]
            await message.channel.send("http://www.scp-wiki.net/scp-"+"-".join([num]+message.content.strip().replace(".", "").replace("-", "").lower().split()[2:]))
        '''
        await bot.process_commands(message)

    #if __name__ == '__main__':
    #bot.loop.create_task(tick_update())
    token = ""
    with open("token.txt") as f:
        token = f.read().strip()
    bot.run(token) 
    print("Bot is shutting down...")
