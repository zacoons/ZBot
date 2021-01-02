import discord
from discord.ext import commands
import pickle
import random
import asyncio
import typing
from common import tryLoadSavedDict, client, embedColour, embedFooters, completedReaction, errorReaction, nonExistentItemError, badSelfActionError, nullItemError, notEnoughItemsError
import datetime
from enum import Enum, auto

class CurrencyData:
    def __init__(self, wallet, bank, bankSize, rank, inventory):
        self.wallet = wallet
        self.bank = bank
        self.bankSize = bankSize
        self.rank = rank
        self.inventory = inventory
    @property
    def netWorth(self):
        netWorth = self.wallet + self.bank
        for item in self.inventory:
            netWorth += items[item].cost
        return netWorth

class ItemType(Enum):
    tool = auto()
    collectable = auto()

class Item:
    def __init__(self, description, icon, cost, use, cooldown, type):
        self.description = description
        self.icon = icon
        self.cost = cost
        self.use = use
        self.cooldown = cooldown
        self.type = type

global items
global currencyUnpickledData

defaultBankSize = 50

#Commands
@client.command(aliases=['lb'])
async def leaderboard(message):
    setCurrencyRanks()
    sortedData = list(sorted(currencyUnpickledData.items(), key = lambda kv: kv[1].rank))
    
    embedVar = discord.Embed(title="Currency Leaderboard", description="", color=embedColour)
    embedVar.set_footer(text="You are #{rank}".format(rank=currencyUnpickledData[str(message.author.id)].rank), icon_url=message.author.avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    for data in sortedData[:3]:
        member = await message.guild.fetch_member(data[0])
        embedVar.add_field(name="#{rank} - {name}".format(rank=str(data[1].rank), name=member.display_name), value="Net worth: {netWorth} zbucks".format(netWorth=str(data[1].netWorth)), inline=False)

    await message.channel.send(embed=embedVar)

@client.command(aliases=['bal'])
async def balance(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author
    
    memberInfo = loadCurrencyData(member)

    embedVar = discord.Embed(title="", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters()), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    embedVar.add_field(name="Wallet", value=str(memberInfo.wallet), inline=False)
    embedVar.add_field(name="Bank", value="{bank}/{bankSize}".format(bank=str(memberInfo.bank), bankSize=str(memberInfo.bankSize)), inline=False)
    embedVar.add_field(name="Net Worth", value=str(memberInfo.netWorth), inline=False)
    await message.channel.send(embed=embedVar)

@client.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(message):
    amount = random.randint(10, 25)
    member = loadCurrencyData(message.author)
    getsBonusItem = random.randint(0, 25)
    if getsBonusItem == 0:
        itemName = random.choice(list(items.items()))[0]
        
    challenges = [memoryChallenge, scrambleChallenge]
    challenge = random.choice(challenges)
    if await challenge(message) == False:
        return

    amount = applyMultipliers(member, amount)
    member.wallet += amount
    if getsBonusItem == 0:
        giveMemberItems(member, itemName, 1)
        await message.channel.send("Well done, you earned **{amount}** zbucks. You also found a **{item}**".format(amount=str(amount), item=itemName))
    else:
        await message.channel.send("Well done, you earned **{amount}** zbucks".format(amount=str(amount)))
    
    await message.message.add_reaction(completedReaction)

    saveCurrencyData()

@client.command()
async def buy(message):
    member = loadCurrencyData(message.author)
    itemName = message.message.content.lower()[6:]
    itemName = ''.join([i for i in itemName if not i.isdigit()])
    amount = tryParseInt(message.message.content.lower()[6:].replace(itemName, ""))
    if amount[0] == True:
        itemName = itemName[:-1]
        amount = amount[1]
    else:
        amount = 1

    if amount < 0:
        await message.channel.send("You can't buy negative items lol")
        await message.message.add_reaction(errorReaction)
        return

    if itemName not in items:
        await message.channel.send(nonExistentItemError(itemName))
        await message.message.add_reaction(errorReaction)
        return
    if member.wallet < items[itemName].cost or items[itemName].cost * amount > member.wallet:
        await message.channel.send("You don't have enough money for that my dude, type `z work` to earn yourself some zbucks")
        await message.message.add_reaction(errorReaction)
        return
    
    giveMemberItems(member, itemName, amount)
    member.wallet -= items[itemName].cost * amount
    
    if amount == 1:
        await message.channel.send("You just bought a **{item}** for **{cost}** zbucks".format(item=itemName, cost=str(items[itemName].cost)))
    else:
        await message.channel.send("You just bought **{amount}** **{item}s** for **{cost}** zbucks".format(amount=str(amount), item=itemName, cost=str(items[itemName].cost)))
    await message.message.add_reaction(completedReaction)

    saveCurrencyData()

@client.command(aliases=['dep'])
async def deposit(message, amount:str):
    member = loadCurrencyData(message.author)

    if amount.lower() == 'all' or int(amount) > member.wallet:
        if member.bank == member.bankSize:
            await message.channel.send("Your bank is too full, you can upgrade it by using a bank note")
            await message.message.add_reaction(errorReaction)
            return
        if member.wallet < (member.bankSize - member.bank):
            dep = member.wallet
        elif member.bank > 0:
            dep = member.bankSize - member.bank
        elif member.wallet > member.bankSize:
            dep = member.wallet - (member.wallet - member.bankSize)
        else:
            dep = member.bankSize
        member.bank += dep
        member.wallet -= dep
        await message.channel.send("**{deposit}** zbucks have been deposited".format(deposit=str(dep)))
    else:
        if int(amount) < 0:
            await message.channel.send("You can't deposit negative money, smh")
            await message.message.add_reaction(errorReaction)
            return
        
        if (int(amount) + member.bank) > member.bankSize:
            await message.channel.send("That won't fit in your bank... Maybe deposit a bit less")
            await message.message.add_reaction(errorReaction)
            return

        member.bank += int(amount)
        member.wallet -= int(amount)
    
    await message.message.add_reaction(completedReaction)

    saveCurrencyData()

@client.command(aliases=['with'])
async def withdraw(message, amount:str):
    member = loadCurrencyData(message.author)

    if amount.lower() == 'all':
        dep = member.bank
        member.bank -= dep
        member.wallet += dep
        await message.channel.send("**{deposit}** zbucks have been withdrawn".format(deposit=str(dep)))
    else:
        if int(amount) < 0:
            await message.channel.send("You can't withdraw negative money, smh")
            await message.message.add_reaction(errorReaction)
            return
        
        if int(amount) > member.bank:
            await message.channel.send("Lol you wish, you don't have that many zbucks")
            await message.message.add_reaction(errorReaction)
            return
        
        member.bank -= int(amount)
        member.wallet += int(amount)
    
    await message.message.add_reaction(completedReaction)

    saveCurrencyData()

@client.command(aliases=['rob'])
@commands.cooldown(1, 300, commands.BucketType.user)
async def steal(message, member:discord.Member):
    if member == message.author:
        message.channel.send(badSelfActionError)
        await message.message.add_reaction(errorReaction)
        return
    
    member1Data = loadCurrencyData(message.author)
    member2Data = loadCurrencyData(member)

    if "rifle" in member2Data.inventory:
        await message.channel.send("{member} has a rifle, I don't think you want to mess with him".format(member=member.mention))
        await message.message.add_reaction(errorReaction)
        return

    didFail = random.randint(0, 1)
    
    if didFail == 0:
        stealDivide = random.randint(2, 3)
        stealAmount = int(member2Data.wallet/stealDivide)
        responses = ["You knocked {member} out cold and stole **{amount}** zbucks from his wallet".format(member=member.mention, amount=str(stealAmount)),
        "You tripped {member}, **{amount}** zbucks fell out of his wallet. You took them".format(member=member.mention, amount=str(stealAmount))]
        msg = await message.channel.send(random.choice(responses))
        await msg.message.add_reaction(completedReaction)
    else:
        stealDivide = random.randint(2, 3)
        stealAmount = int(-member1Data.wallet/stealDivide)
        responses = ["It turns out that {member} is a martial arts expert and overpowered you, taking **{amount}** coins from your wallet".format(member=member.mention, amount=str(-stealAmount)),
        "You tripped on the gutter as you were about to attack and **{amount}** zbucks fell out of your wallet. {member} took them".format(member=member.mention, amount=str(stealAmount))]
        msg = await message.channel.send(random.choice(responses))
        await msg.message.add_reaction(errorReaction)
    
    member1Data.wallet += stealAmount
    member2Data.wallet -= stealAmount

    saveCurrencyData()
    await message.message.add_reaction(completedReaction)

@client.command()
async def give(message, member:discord.Member):
    if member.bot:
        await message.channel.send("You can't give stuff to bots dood")
        await message.message.add_reaction(errorReaction)
        return

    input = message.message.content[30:]
    isInt, intValue = tryParseInt(input)

    if str(message.author) != "Zacoons#2407":
        if member == message.author:
            await message.channel.send(badSelfActionError)
            await message.message.add_reaction(errorReaction)
            return
    
    member1Data = loadCurrencyData(message.author)
    member2Data = loadCurrencyData(member)

    if isInt:
        if str(message.author) != "Zacoons#2407":
            if intValue < 0:
                await message.channel.send("You can't donate negative money, smh")
                await message.message.add_reaction(errorReaction)
                return

            if member1Data.wallet < intValue:
                await message.channel.send("Nice try, you don't have that many zbucks")
                await message.message.add_reaction(errorReaction)
                return

            member1Data.wallet -= intValue

        member2Data.wallet += intValue

        await message.channel.send("You just gave **{zbucks}** zbucks to {member}. What a lucky guy :D".format(zbucks=str(intValue), member=member.mention))
        await message.message.add_reaction(completedReaction)
    else:
        itemName = message.message.content[30:]
        itemName = ''.join([i for i in itemName if not i.isdigit()])
        amount = tryParseInt(message.message.content[30:].replace("{itemName}".format(itemName=itemName), ""))
        if amount[0] == True:
            amount = amount[1]
            itemName = itemName[:-1]
        else:
            amount = 1

        if itemName not in items:
            await message.channel.send(nonExistentItemError(itemName))
            await message.message.add_reaction(errorReaction)
            return

        if amount < 0:
            await message.channel.send("You can't give negative items lol")
            await message.message.add_reaction(errorReaction)
            return
        
        if str(message.author) != "Zacoons#2407":
            if itemName not in member1Data.inventory:
                await message.channel.send(nullItemError)
                await message.message.add_reaction(errorReaction)
                return
            
            if member1Data.inventory[itemName] < amount:
                await message.channel.send(notEnoughItemsError)
                await message.message.add_reaction(errorReaction)
                return

            removeMemberItems(member1Data, itemName, amount)
        
        giveMemberItems(member2Data, itemName, amount)
        if amount == 1:
            await message.channel.send("You just gave a **{itemName}** to {member}".format(itemName=itemName, member=member.mention))
        else:
            await message.channel.send("You just gave **{amount}** **{itemName}s** to {member}".format(amount=str(amount), itemName=itemName, member=member.mention))

    saveCurrencyData()
    await message.message.add_reaction(completedReaction)

@client.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(message):
    amount = random.randint(20, 50)
    member = loadCurrencyData(message.author)
    amount = applyMultipliers(member, amount)
    member.wallet += amount
    giveMemberItems(member, "bank note", 1)
    await message.channel.send("Your daily reward is **{amount}** zbucks and a **bank note**".format(amount=str(amount)))
    await message.message.add_reaction(completedReaction)
    saveCurrencyData()

@client.command()
async def use(message):
    member = loadCurrencyData(message.author)
    itemName = message.message.content.lower()[6:]
    itemName = ''.join([i for i in itemName if not i.isdigit()])
    amount = tryParseInt(message.message.content.lower()[6:].replace(itemName, ""))
    if items[itemName].type == ItemType.collectable:
        await message.channel.send("You can't use that item :/")
        await message.message.add_reaction(errorReaction)
        return

    if amount[0] == True:
        itemName = itemName[:-1]
        amount = amount[1]
    else:
        amount = 1

    if amount < 0:
        await message.channel.send("You can't use negative items lol")
        await message.message.add_reaction(errorReaction)
        return
    if member.inventory[itemName] < amount:
        await message.channel.send(notEnoughItemsError)
        await message.message.add_reaction(errorReaction)
        return
    
    if itemName not in items:
        await message.channel.send(nonExistentItemError(itemName))
        await message.message.add_reaction(errorReaction)
        return
    if itemName not in member.inventory:
        await message.channel.send(nullItemError)
        await message.message.add_reaction(errorReaction)
        return
    
    if cooldown(message, items[itemName].use, items[itemName].cooldown):
        await items[itemName].use(member=message.author, channel=message.channel, amount=amount)
        await message.message.add_reaction(completedReaction)
    else:
        await message.message.add_reaction(errorReaction)

@client.command()
async def sell(message):
    member = loadCurrencyData(message.author)
    itemName = message.message.content.lower()[7:]
    itemName = ''.join([i for i in itemName if not i.isdigit()])
    amount = tryParseInt(message.message.content.lower()[7:].replace(itemName, ""))

    if amount[0] == True:
        itemName = itemName[:-1]
        amount = amount[1]
    else:
        amount = 1

    if amount < 0:
        await message.channel.send("You can't sell negative items lol")
        await message.message.add_reaction(errorReaction)
        return
    if member.inventory[itemName] < amount:
        await message.channel.send(notEnoughItemsError)
        await message.message.add_reaction(errorReaction)
        return
    
    if itemName not in items:
        await message.channel.send(nonExistentItemError(itemName))
        await message.message.add_reaction(errorReaction)
        return
    if itemName not in member.inventory:
        await message.channel.send(nullItemError)
        await message.message.add_reaction(errorReaction)
        return

    removeMemberItems(member, itemName, amount)
    zbucks = items[itemName].cost * amount
    member.wallet += zbucks

    if amount == 1:
        await message.channel.send("You just sold a **{itemName}** for **{zbucks}** zbucks".format(itemName=itemName, zbucks=zbucks))
    else:
        await message.channel.send("You just sold **{amount} {itemName}s** for **{zbucks}** zbucks".format(amount=str(amount), itemName=itemName, zbucks=zbucks))
    await message.message.add_reaction(completedReaction)

@client.command(aliases=["inv"])
async def inventory(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author

    embedVar = discord.Embed(title="{member}'s Inventory".format(member=member.display_name), description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters()), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    
    member = loadCurrencyData(member)
    for itemName in member.inventory:
        embedVar.add_field(name="{icon} {item} - {amount}".format(icon=items[itemName].icon, item=itemName, amount=str(member.inventory[itemName])), value=items[itemName].description, inline=False)
    if member.inventory == dict():
        embedVar.add_field(name="You don't have any items", value="You can go find some by typing the command `z work`")
    
    await message.channel.send(embed=embedVar)

@client.command(aliases=["store"])
async def shop(message):
    embedVar = discord.Embed(title="ZBot Shop", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters()), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  

    for itemName in items:
        embedVar.add_field(name="{icon} {itemName} - {cost} zbucks".format(icon=items[itemName].icon, itemName=itemName, cost=str(items[itemName].cost)), value=items[itemName].description, inline=False)
    
    await message.channel.send(embed=embedVar)


#Functions
def saveCurrencyData():
    with open(currencyDataFilename, "wb") as file:
        pickle.dump(currencyUnpickledData, file)

def loadCurrencyData(member):
    if not str(member.id) in currencyUnpickledData:
        currencyUnpickledData[str(member.id)] = CurrencyData(0, 0, defaultBankSize, 0, dict())

    return currencyUnpickledData[str(member.id)]

def applyMultipliers(member, amount):
    multiplier = 1
    if "cool llama token" in member.inventory:
        index = member.inventory["cool llama token"]
        while index > 0:
            multiplier += 0.1
            index -= 1
    if "epic llama token" in member.inventory:
        index = member.inventory["epic llama token"]
        while index > 0:
            multiplier += 0.5
            index -= 1
    if "legendary llama token" in member.inventory:
        index = member.inventory["legendary llama token"]
        while index > 0:
            multiplier += 1
            index -= 1
    return int(amount * multiplier)

def setCurrencyRanks():
    for member in currencyUnpickledData:
        data = currencyUnpickledData[member]
        data.rank = len(currencyUnpickledData)

        for checkMember in currencyUnpickledData:
            checkMemberData = currencyUnpickledData[checkMember]
            if data.netWorth > checkMemberData.netWorth:
                data.rank -= 1

    saveCurrencyData()

class DummyCooldown:
    def __init__(self, per, rate = 1, type = commands.BucketType.user):
        self.per = per
        self.rate = rate
        self.type = type

on_cooldown = {}
def cooldown(message, useFunc, seconds):
    key = (message.author, useFunc)
    now = datetime.datetime.now()
    cooldown_end = on_cooldown.get(key)
    if cooldown_end is None or cooldown_end < now:
        on_cooldown[key] = now + datetime.timedelta(seconds=seconds)
        return True

    raise commands.CommandOnCooldown(DummyCooldown(seconds), (cooldown_end - now).seconds)

def tryParseInt(input):
    try:
        return True, int(input)
    except ValueError:
        return False, input


#Work challenges
async def memoryChallenge(message):
    words = ["zacoons", "bot", "discord", "potato", "pineapple", "broccoli"]
    random.shuffle(words)
    word1 = words[0]
    word2 = words[1]
    word3 = words[2]
    thingToRemember = "{word1} {word2} {word3}".format(word1=word1, word2=word2, word3=word3)
    msg = await message.channel.send("Remember these words: `{thingToRemember}`".format(thingToRemember=thingToRemember))
    await asyncio.sleep(3)
    await msg.edit(content="Now type the words in the chat below")

    def check(m):
        return m.channel == msg.channel and m.author == message.author
    response = await client.wait_for("message", check=check)
    responseWords = response.content.split()
    if responseWords[0].lower() == word1 and responseWords[1].lower() == word2 and responseWords[2].lower() == word3:
        await response.add_reaction(completedReaction)
        return True
    else:
        await response.add_reaction(errorReaction)
        return False

async def scrambleChallenge(message):
    unscrambledWords = ["potato", "pineapple", "broccoli", "milk"]
    scrambledWords = []
    i = 0
    for word in unscrambledWords:
        word = list(word)
        random.shuffle(word)
        word = ''.join(word)
        scrambledWords.append(word)
        i += 1
    rand = random.randint(0, len(scrambledWords))
    msg = await message.channel.send("Unscramble this word: `{word}`".format(word=scrambledWords[rand]))

    def check(m):
        return m.channel == msg.channel and m.author == message.author
    response = await client.wait_for("message", check=check)
    if response.content.lower() == unscrambledWords[rand]:
        await response.add_reaction(completedReaction)
        return True
    else:
        await response.add_reaction(errorReaction)
        return False


#Item commands
def giveMemberItems(member, itemName, amount):
    if amount == 0 or amount == None:
        amount = 1
    
    if itemName not in member.inventory:
        member.inventory[itemName] = amount
    else:
        member.inventory[itemName] += amount
    saveCurrencyData()

def removeMemberItems(member, itemName, amount):
    if amount == 0 or amount == None:
        amount = 1
    
    member.inventory[itemName] -= 1
    if member.inventory[itemName] <= 0:
        member.inventory.pop(itemName)
    saveCurrencyData()

async def useChristmasBox(**kwargs):
    member = loadCurrencyData(kwargs["member"])
    amount = kwargs["amount"]
    if amount == 1:
        msg = await kwargs["channel"].send(":sparkles: Opening {member}'s **Christmas Box** :sparkles:".format(member=kwargs["member"].mention))
    else:
        msg = await kwargs["channel"].send(":sparkles: Opening **{amount}** of {member}'s **Christmas Boxes** :sparkles:".format(amount=amount, member=kwargs["member"].mention))
    zbucks = 0
    i = amount
    while i > 0:
        removeMemberItems(member, "christmas box", 1)
        rand = random.randint(75, 200)
        zbucks = applyMultipliers(member, rand)
        zbucks += rand
        member = loadCurrencyData(kwargs["member"])
        i -= 1
    await asyncio.sleep(3)
    member.wallet += zbucks
    if amount == 1:
        endMsg = "{member} you got **{amount}** zbucks from your christmas box".format(member=kwargs["member"].mention, amount=str(zbucks))
    else:
        endMsg = "{member} you got **{amount}** zbucks from your christmas boxes".format(member=kwargs["member"].mention, amount=str(zbucks))
    await msg.edit(content=endMsg, amount=str(zbucks))
    saveCurrencyData()

async def useBankNote(**kwargs):
    member = loadCurrencyData(kwargs["member"])
    amount = kwargs["amount"]
    i = amount
    increase = 0
    while i > 0:
        removeMemberItems(member, "bank note", 1)
        increase += random.randint(20, 50)
        member.bankSize += increase
        saveCurrencyData()
        i -= 1
    if amount > 1:
        await kwargs["channel"].send("You used **{amount}** bank notes and your bank size was increased by **{increase}** zbucks".format(amount=str(amount), increase=str(increase)))
    else:
        await kwargs["channel"].send("Your bank size was increased by **{increase}** zbucks".format(increase=str(increase)))

async def useRifle(**kwargs):
    member = loadCurrencyData(kwargs["member"])
    amount = random.randint(20, 50)
    amount = applyMultipliers(member, amount)
    member.wallet += amount
    responses=["You shot a rabbit and sold it for **{amount}** zbucks".format(amount=str(amount)),
    "You shot a skunk and sold it for **{amount}** zbucks".format(amount=str(amount)),]
    await kwargs["channel"].send(random.choice(responses))
    kwargs["member"].netWorh = kwargs["member"].wallet + kwargs["member"].bank
    saveCurrencyData()

items = {'christmas box': Item("Use `z use christmas box` to open it and find a suprise inside", "<:christmasbox:794434356290387989>", 150, useChristmasBox, 0, ItemType.tool),
'bank note': Item("Use `z use bank note` to increase the capacity of your bank", "<:banknote:794434356549517312>", 50, useBankNote, 0, ItemType.tool),
'rifle': Item("Use `z use rifle` to go on a hunt and earn some zbucks, this item also protects you from being robbed", "<:rifle:794447075831316513>", 250, useRifle, 60, ItemType.tool),
'cool token': Item("Multiplies how many zbucks you earn through any command (except for withdrawing, depositing and selling) by 110%", "<:coolllamatoken:794457418654285824>", 150, None, 0, ItemType.collectable),
'epic token': Item("Multiplies how many zbucks you earn through any command (except for withdrawing, depositing and selling) by 150%", "<:epicllamatoken:794457418637246484>", 500, None, 0, ItemType.collectable),
'legendary token': Item("Multiplies how many zbucks you earn through any command (except for withdrawing, depositing and selling) by 200%", "<:legendaryllamatoken:794457418611294249>", 1000, None, 0, ItemType.collectable)}

currencyDataFilename = "currencyData.pickle"
currencyUnpickledData = tryLoadSavedDict(currencyDataFilename)