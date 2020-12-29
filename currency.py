import discord
from discord.ext import commands
import pickle
import random
import asyncio
import typing
from common import tryLoadSavedDict, client, embedColour, embedFooters, completedReaction, errorReaction, nonExistentItemError, badSelfActionError
import datetime

class CurrencyData:
    def __init__(self, wallet, bank, bankSize, rank, inventory):
        self.wallet = wallet
        self.bank = bank
        self.bankSize = bankSize
        self.rank = rank
        self.inventory = inventory
    @property
    def netWorth(self):
        return self.wallet + self.bank

class Item:
    def __init__(self, description, icon, cost, use, cooldown):
        self.description = description
        self.icon = icon
        self.cost = cost
        self.use = use
        self.cooldown = cooldown

global items
global currencyUnpickledData

defaultBankSize = 50

#Commands
@client.command(aliases=['lb'])
async def leaderboard(message):
    setCurrencyRanks()
    sortedData = list(sorted(currencyUnpickledData.items(), key = lambda kv: kv[1].rank))
    
    embedVar = discord.Embed(title="Currency Leaderboard", description="", color=embedColour)
    embedVar.set_footer(text="You are #{rank}", icon_url=message.author.avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    for data in sortedData[:3]:
        embedVar.add_field(name="#{rank} {name}".format(rank=str(data[1].rank), name=data[0][:-5]), value="Net worth: {netWorth} zbucks".format(netWorth=str(data[1].netWorth)), inline=False)

    await message.channel.send(embed=embedVar)

@client.command(aliases=['bal'])
async def balance(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author
    
    memberInfo = loadCurrencyData(member)

    embedVar = discord.Embed(title="", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
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

    member.wallet += amount
    if getsBonusItem == 0:
        giveMemberItem(member, itemName)
        await message.channel.send("Well done, you earned **{amount}** zbucks. You also found a **{item}**".format(amount=str(amount), item=itemName))
    else:
        await message.channel.send("Well done, you earned **{amount}** zbucks".format(amount=str(amount)))

    saveCurrencyData()

@client.command()
async def buy(message, itemName:str):
    member = loadCurrencyData(message.author)
    itemName = message.message.content.lower().replace("z buy ", "")

    if itemName not in items:
        await message.channel.send(nonExistentItemError(itemName))
        await message.message.add_reaction(errorReaction)
        return
    if member.wallet < items[itemName].cost:
        await message.channel.send("You don't have enough money for that my dude, type `z work` to earn yourself some zbucks")
        await message.message.add_reaction(errorReaction)
        return
    
    giveMemberItem(member, itemName)
    member.wallet -= items[itemName].cost
    
    await message.channel.send("You just bought a **{item}** for **{cost}** zbucks".format(item=itemName, cost=str(items[itemName].cost)))

    saveCurrencyData()

@client.command(aliases=['dep'])
async def deposit(message, amount:str):
    member = loadCurrencyData(message.author)

    if amount.lower() == 'all' or int(amount) > member.wallet:
        if member.bank == member.bankSize:
            await message.channel.send("Your bank is too full, you can upgrade it by using a bank note")
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

        if not (int(amount) + member.bank) > member.bankSize:
            member.bank += int(amount)
            member.wallet -= int(amount)
            await message.message.add_reaction(completedReaction)
        else:
            await message.channel.send("That won't fit in your bank... Maybe deposit a bit less")

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
        if not int(amount) > member.bank:
            member.bank -= int(amount)
            member.wallet += int(amount)
            await message.message.add_reaction(completedReaction)
        else:
            await message.channel.send("Lol you wish, you don't have that many zbucks")

    saveCurrencyData()

@client.command(aliases=['rob'])
@commands.cooldown(1, 300, commands.BucketType.user)
async def steal(message, member:discord.Member):
    if member == message.author:
        message.channel.send(badSelfActionError())
        await message.message.add_reaction(errorReaction)
        return
    
    member1Data = loadCurrencyData(message.author)
    member2Data = loadCurrencyData(member)

    if "rifle" in member2Data.inventory:
        await message.channel.send(member.mention+" has a rifle, I don't think you want to mess with him")
        await message.message.add_reaction(errorReaction)
        return

    didFail = random.randint(0, 1)
    
    if didFail == 0:
        stealDivide = random.randint(2, 3)
        stealAmount = int(member2Data.wallet/stealDivide)
        responses = ["You knocked "+member.mention+" out cold and stole **"+str(stealAmount)+"** zbucks from his wallet",
        "You tripped "+member.mention+" with your leg, **"+str(stealAmount)+"** zbucks fell out of his wallet. You took them"]
        await message.channel.send(random.choice(responses))
    else:
        stealDivide = random.randint(2, 3)
        stealAmount = int(-member1Data.wallet/stealDivide)
        responses = ["It turns out that "+member.mention+" is a martial arts expert and overpowered you, taking **"+str(-stealAmount)+"** coins from your wallet",
        "You tripped on the gutter as you were about to attack "+member.mention+" and **"+str(stealAmount)+"** zbucks fell out of your wallet. "+member.mention+" took them"]
        await message.channel.send(random.choice(responses))
    
    member1Data.wallet += stealAmount
    member2Data.wallet -= stealAmount

    saveCurrencyData()

@client.command()
async def give(message, member:discord.Member, input:str):
    if member.bot:
        await message.channel.send("You can't give stuff to bots dood")
        return

    isInt, intValue = tryParseInt(input)

    if member == message.author:
        await message.channel.send(badSelfActionError())
        await message.message.add_reaction(errorReaction)
        return
    
    member1Data = loadCurrencyData(message.author)
    member2Data = loadCurrencyData(member)

    if isInt:
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

        await message.channel.send("You just gave **"+str(intValue)+"** zbucks to "+member.mention+". What a lucky guy :D")
    else:
        itemName = message.message.content[30:]

        if itemName not in items:
            await message.channel.send(nonExistentItemError(itemName))
            await message.message.add_reaction(errorReaction)
            return
        
        if itemName not in member1Data.inventory:
            await message.channel.send("Lol nice try, you don't have that item")
            await message.message.add_reaction(errorReaction)
            return

        removeMemberItem(member1Data, itemName)
        giveMemberItem(member2Data, itemName)
        await message.channel.send("You just gave a **"+itemName+"** to "+member.mention)

    saveCurrencyData()
    await message.message.add_reaction(completedReaction)

@client.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(message):
    coinAmount = random.randint(20, 50)
    member = loadCurrencyData(message.author)
    member.wallet += coinAmount
    giveMemberItem(member, "bank note")
    await message.channel.send("Your daily reward is **"+str(coinAmount)+"** zbucks and a **bank note**")
    saveCurrencyData()

@client.command()
async def use(message):
    member = loadCurrencyData(message.author)
    itemName = message.message.content.lower().replace("z use ", "")
    if itemName in member.inventory:
        # useFunc = commands.cooldown(1, items[itemName].cooldown, commands.BucketType.user)(items[itemName].use)
        # await useFunc(member=message.author, channel=message.channel)
        # decoratedUse = cooldown(items[itemName].cooldown)(items[itemName].use)
        # await items[itemName].use(member=message.author, channel=message.channel)
        # await decoratedUse(member=message.author, channel=message.channel)

        if cooldown(message, items[itemName].use, items[itemName].cooldown):
            await items[itemName].use(member=message.author, channel=message.channel)

    elif itemName not in items:
        await message.channel.send(nonExistentItemError(itemName))
    else:
        await message.channel.send("Lol nice try, you don't have that item")

@client.command(aliases=["inv"])
async def inventory(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author

    embedVar = discord.Embed(title=member.display_name+"'s Inventory", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    
    member = loadCurrencyData(member)
    for itemName in member.inventory:
        embedVar.add_field(name=items[itemName].icon+" "+itemName+" - "+str(member.inventory[itemName]), value=items[itemName].description, inline=False)
    if member.inventory == dict():
        embedVar.add_field(name="You don't have any items", value="You can go find some by typing the command `z work`")
    
    await message.channel.send(embed=embedVar)

@client.command(aliases=["store"])
async def shop(message):
    embedVar = discord.Embed(title="ZBot Shop", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  

    for item in items:
        embedVar.add_field(name=items[item].icon+" "+item+" - "+str(items[item].cost)+" zbucks", value=items[item].description, inline=False)
    
    await message.channel.send(embed=embedVar)


#Functions
def saveCurrencyData():
    with open(currencyDataFilename, "wb") as file:
        pickle.dump(currencyUnpickledData, file)

def loadCurrencyData(member):
    if not str(member) in currencyUnpickledData:
        currencyUnpickledData[str(member)] = CurrencyData(0, 0, defaultBankSize, 0, dict())

    return currencyUnpickledData[str(member)]

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
    thingsToRemember = ["guppti tamberooly joortelsk", "potato pineapple broccoli"]
    rand = random.choice(thingsToRemember)
    msg = await message.channel.send("Remember these words: `"+rand+"`")
    await asyncio.sleep(5)
    await msg.edit(content="Now type the words in the chat below")

    def check(m):
        return m.channel == msg.channel and m.author == message.author
    response = await client.wait_for("message", check=check)
    if response.content.lower() == rand:
        await response.add_reaction(completedReaction)
        return True
    else:
        await response.add_reaction(errorReaction)
        return False

async def scrambleChallenge(message):
    scrambledWords = ["optato", "pniaeppel", "borccloi", "mlki"]
    unscrambledWords = ["potato", "pineapple", "broccoli", "milk"]
    rand = random.randint(0, len(scrambledWords))
    msg = await message.channel.send("Unscramble this word: `"+scrambledWords[rand]+"`")

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
def giveMemberItem(member, itemName):
    if itemName not in member.inventory:
        member.inventory[itemName] = 1
    else:
        member.inventory[itemName] += 1
    saveCurrencyData()

def removeMemberItem(member, itemName):
    member.inventory[itemName] -= 1
    if member.inventory[itemName] <= 0:
        member.inventory.pop(itemName)
    saveCurrencyData()

async def useChristmasBox(**kwargs):
    member = loadCurrencyData(kwargs["member"])
    removeMemberItem(member, "christmas box")
    msg = await kwargs["channel"].send(":sparkles: Opening "+kwargs["member"].mention+"'s **Christmas Box** :sparkles:")
    await asyncio.sleep(3)
    zbucks = random.randint(75, 200)
    member = loadCurrencyData(kwargs["member"])
    member.wallet += zbucks
    await msg.edit(content=kwargs["member"].mention+" you got **"+str(zbucks)+"** zbucks from your christmas box")
    kwargs["member"].netWorh = kwargs["member"].wallet + kwargs["member"].bank
    saveCurrencyData()

async def useBankNote(**kwargs):
    member = loadCurrencyData(kwargs["member"])
    removeMemberItem(member, "bank note")
    amount = random.randint(20, 50)
    member.bankSize += amount
    await kwargs["channel"].send("Your bank size has been increased by **"+str(amount)+"** zbucks")
    kwargs["member"].netWorh = kwargs["member"].wallet + kwargs["member"].bank
    saveCurrencyData()

async def useRifle(**kwargs):
    member = loadCurrencyData(kwargs["member"])
    amount = random.randint(20, 50)
    member.wallet += amount
    responses=["You shot a rabbit and sold it for **"+str(amount)+"** zbucks",
    "You shot a skunk and sold it for **"+str(amount)+"** zbucks",]
    await kwargs["channel"].send(random.choice(responses))
    kwargs["member"].netWorh = kwargs["member"].wallet + kwargs["member"].bank
    saveCurrencyData()

items = {'christmas box': Item("Use `z use christmas box` to open it and find a suprise inside", "<:christmasbox:791481944721326101>", 150, useChristmasBox, 0),
'bank note': Item("Use `z use bank note` to increase the capacity of your bank", "<:banknote:791501673930948629>", 50, useBankNote, 0),
'rifle': Item("Use `z use rifle` to go on a hunt and earn some zbucks, this item also protects you from being robbed", "<:rifle:791501684861829151>", 250, useRifle, 60)}

currencyDataFilename = "currencyData.pickle"
currencyUnpickledData = tryLoadSavedDict(currencyDataFilename)