import discord
from discord.ext import commands
from app import client, embedColour, TryLoadSavedDict
import pickle
import random
import asyncio
import typing

class CurrencyData:
    def __init__(self, wallet, bank, bankSize, netWorth, rank, inventory):
        self.wallet = wallet
        self.bank = bank
        self.bankSize = bankSize
        self.netWorth = netWorth
        self.rank = rank
        self.inventory = inventory

class Item:
    def __init__(self, description, icon, cost, use, cooldown):
        self.description = description
        self.icon = icon
        self.cost = cost
        self.use = use
        self.cooldown = cooldown

global items
global currencyUnpickledData

currencyDataFilename = "currencyData.pickle"
currencyUnpickledData = TryLoadSavedDict(currencyDataFilename)

defaultBankSize = 50
items = {'christmas box': Item("Use `z use christmas box` to open it and find a suprise inside", "<:christmasbox:786371826028249118>", 150, useChristmasBox, 0),
'bank note': Item("Use `z use bank note` to increase the capacity of your bank", "<:banknote:786366797897007134>", 50, useBankNote, 0),
'rifle': Item("Use `z use rifle` to go on a hunt and earn some coins, this item also protects you from being robbed", "<:rifle:786360915041583134>", 250, useRifle, 60)}


#Commands
@client.command(aliases=['lb'])
async def leaderboard(message):
    setCurrencyRanks()
    sortedData = list(sorted(currencyUnpickledData.items(), key = lambda kv: kv[1].rank))
    
    embedVar = discord.Embed(title="Currency Leaderboard", description="", color=embedColour)
    embedVar.set_footer(text="You are #"+str(loadCurrencyData(message.author).rank), icon_url=message.author.avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    for data in sortedData[:3]:
        data[1].netWorth = data[1].wallet + data[1].bank
        embedVar.add_field(name="#"+str(data[1].rank)+" "+data[0][:-5], value="Net worth: "+str(data[1].netWorth)+" coins", inline=False)

    await message.channel.send(embed=embedVar)

@client.command(aliases=['bal'])
async def balance(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author
    
    memberInfo = loadCurrencyData(member)
    memberInfo.netWorth = memberInfo.wallet + memberInfo.bank

    embedVar = discord.Embed(title="", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    embedVar.add_field(name="Wallet", value=str(memberInfo.wallet), inline=False)
    embedVar.add_field(name="Bank", value=str(memberInfo.bank)+"/"+str(memberInfo.bankSize), inline=False)
    embedVar.add_field(name="Net Worth", value=str(memberInfo.netWorth), inline=False)
    await message.channel.send(embed=embedVar)

@client.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(message):
    amount = random.randint(10, 25)
    member = loadCurrencyData(message.author)
    member.wallet += amount
    getsBonusItem = random.randint(0, 25)
    item = None
    if getsBonusItem == 0:
        itemName = random.choice(list(items.items()))[0]
        item = items[itemName]
        member.inventory[itemName] = item
    thingsToSay = ["You asked your grandma for money and she gave you **"+str(amount)+"** coins",
    "You farted on such a harmonic note that a nearby strager gave you **"+str(amount)+"** coins",
    "You went shopping and the clerk, under the impression of your dashing looks, payed *you* **"+str(amount)+"** coins instead of the other way around",
    "You mowed your neighbours lawn and he gave you **"+str(amount)+"** coins",
    "You found some spare change under your couch which amounts to **"+str(amount)+"** coins",
    "You searched the air infront of you and found **"+str(amount)+"** coins. Wait **what**",
    "You cut open a potato and found **"+str(amount)+"** coins, wow, the wonders of potato gang I guess",
    "You found some spare change under your couch which amounts to **"+str(amount)+"** coins",
    "You searched your underpants and found **"+str(amount)+"** coins, wtf have you been eating"]
    if getsBonusItem == 0:
        await message.channel.send(random.choice(thingsToSay)+". You also found a **"+itemName+"**")
    else:
        await message.channel.send(random.choice(thingsToSay))

    member.netWorth = member.wallet + member.bank
    saveCurrencyData()

@client.command()
async def buy(message, itemName:str):
    member = loadCurrencyData(message.author)
    itemName = message.message.content.lower().replace("z buy ", "")

    if itemName not in items:
        await message.channel.send("What the heck is a **"+itemName+"**")
        return
    if member.wallet < items[itemName].cost:
        await message.channel.send("You don't have enough money for that my dude, type `z work` to earn yourself some coins")
        return
    
    member.inventory[itemName] = items[itemName]
    member.wallet -= items[itemName].cost
    
    await message.channel.send("You just bought a **"+itemName+"** for **"+str(items[itemName].cost)+"** coins")

    member.netWorth = member.wallet + member.bank
    saveCurrencyData()

@client.command(aliases=['dep'])
async def deposit(message, amount:str):
    member = loadCurrencyData(message.author)

    if amount.lower() == 'all':
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
        await message.channel.send("**"+str(dep)+"** coins have been deposited")
    else:
        if int(amount) < 0:
            await message.channel.send("You can't deposit negative money, smh")
            return
        if not (int(amount) + member.bank) > member.bankSize:
            member.bank += int(amount)
            member.wallet -= int(amount)
            await message.message.add_reaction('👍')
        else:
            await message.channel.send("That won't fit in your bank... Maybe deposit a bit less")

    member.netWorth = member.wallet + member.bank
    saveCurrencyData()

@client.command(aliases=['with'])
async def withdraw(message, amount:str):
    member = loadCurrencyData(message.author)

    if amount.lower() == 'all':
        dep = member.bank
        member.bank -= dep
        member.wallet += dep
        await message.channel.send("**"+str(dep)+"** coins have been withdrawn")
    else:
        if int(amount) < 0:
            await message.channel.send("You can't withdraw negative money, smh")
            return
        if not int(amount) > member.bank:
            member.bank -= int(amount)
            member.wallet += int(amount)
            await message.message.add_reaction('👍')
        else:
            await message.channel.send("Lol you wish, you don't have that many coins")

    member.netWorth = member.wallet + member.bank
    saveCurrencyData()

@client.command(aliases=['rob'])
@commands.cooldown(1, 300, commands.BucketType.user)
async def steal(message, member:discord.Member):
    if member == message.author:
        message.channel.send("That's you dumbdumb")
        return
    
    member1Data = loadCurrencyData(message.author)
    member2Data = loadCurrencyData(member)

    if "rifle" in member2Data.inventory:
        await message.channel.send(member.mention+" has a rifle, I don't think you want to mess with him")
        return

    didFail = random.randint(0, 1)
    
    if didFail == 0:
        stealDivide = random.randint(2, 3)
        stealAmount = int(member2Data.wallet/stealDivide)
        responses = ["You knocked "+member.mention+" out cold and stole **"+str(stealAmount)+"** coins from his wallet",
        "You tripped "+member.mention+" with your leg, **"+str(stealAmount)+"** coins fell out of his wallet. You took them"]
        await message.channel.send(random.choice(responses))
    else:
        stealDivide = random.randint(2, 3)
        stealAmount = int(-member1Data.wallet/stealDivide)
        responses = ["It turns out that "+member.mention+" is a martial arts expert and overpowered you, taking **"+str(-stealAmount)+"** coins from your wallet",
        "You tripped on the gutter as you were about to attack "+member.mention+" and **"+str(stealAmount)+"** coins fell out of your wallet. "+member.mention+" took them"]
        await message.channel.send(random.choice(responses))
    
    member1Data.wallet += stealAmount
    member2Data.wallet -= stealAmount

    member.netWorth = member.wallet + member.bank
    saveCurrencyData()

@client.command()
async def donate(message, member:discord.Member, amount:int):
    if int(amount) < 0:
        await message.channel.send("You can't donate negative money, smh")
        return

    if member == message.author:
        message.channel.send("That's you dumbdumb")
    
    member1Data = loadCurrencyData(message.author)
    member2Data = loadCurrencyData(member)

    if member1Data.wallet < amount:
        await message.channel.send("Nice try, you don't have that many coins")
        return

    member1Data.wallet -= amount
    member2Data.wallet += amount

    await message.channel.send("You just donated **"+str(amount)+"** coins to "+member.mention+". What a lucky guy \:D")
    
    member.netWorth = member.wallet + member.bank
    saveCurrencyData()

@client.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(message):
    coinAmount = random.randint(20, 50)
    member = loadCurrencyData(message.author)
    member.wallet += coinAmount
    member.inventory["bank note"] = items["bank note"]
    await message.channel.send("Your daily reward is **"+str(coinAmount)+"** coins and a **bank note**")
    saveMemberData()

@client.command()
async def use(message):
    member = loadCurrencyData(message.author)
    itemName = message.message.content.lower().replace("z use ", "")
    if itemName in member.inventory:
        # useFunc = commands.cooldown(1, items[itemName].cooldown, commands.BucketType.user)(items[itemName].use)
        # await useFunc(member=message.author, channel=message.channel)
        await items[itemName].use(member=message.author, channel=message.channel)
    elif itemName not in items:
        await message.channel.send("What the heck is a **"+itemName+"**")
    else:
        await message.channel.send("Lol nice try, you don't have that item")

@client.command(aliases=["inv"])
async def inventory(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author

    embedVar = discord.Embed(title=member.display_name+"'s Inventory", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    
    data = loadCurrencyData(member)
    for item in data.inventory:
        embedVar.add_field(name=items[item].icon+" "+item, value=items[item].description, inline=False)
    if data.inventory == dict():
        embedVar.add_field(name="You don't have any items", value="You can go find some by typing the command `z work`")
    
    await message.channel.send(embed=embedVar)

@client.command(aliases=["store"])
async def shop(message):
    embedVar = discord.Embed(title="ZBot Shop", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  

    for item in items:
        embedVar.add_field(name=items[item].icon+" "+item+" - "+str(items[item].cost)+" coins", value=items[item].description, inline=False)
    
    await message.channel.send(embed=embedVar)


#Functions
def saveCurrencyData():
    with open(currencyDataFilename, "wb") as file:
        pickle.dump(currencyUnpickledData, file)

def loadCurrencyData(member):
    if not str(member) in currencyUnpickledData:
        currencyUnpickledData[str(member)] = CurrencyData(0, 0, defaultBankSize, 0, 0, dict())

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


#Item commands
async def useChristmasBox(**kwargs):
    data = loadCurrencyData(kwargs["member"])
    data.inventory.pop("christmas box")
    msg = await kwargs["channel"].send(":sparkles: Opening "+kwargs["member"].mention+"'s **Christmas Box** :sparkles:")
    await asyncio.sleep(3)
    coins = random.randint(75, 200)
    data = loadCurrencyData(kwargs["member"])
    data.wallet += coins
    await msg.edit(content=kwargs["member"].mention+" you got **"+str(coins)+"** coins from your christmas box")
    kwargs["member"].netWorh = kwargs["member"].wallet + kwargs["member"].bank
    saveCurrencyData()

async def useBankNote(**kwargs):
    data = loadCurrencyData(kwargs["member"])
    data.inventory.pop("bank note")
    amount = random.randint(20, 50)
    data.bankSize += amount
    await kwargs["channel"].send("Your bank size has been increased by **"+str(amount)+"** coins")
    kwargs["member"].netWorh = kwargs["member"].wallet + kwargs["member"].bank
    saveCurrencyData()

async def useRifle(**kwargs):
    data = loadCurrencyData(kwargs["member"])
    amount = random.randint(20, 50)
    data.wallet += amount
    responses=["You shot a rabbit and sold it for **"+str(amount)+"** coins",
    "You shot a skunk and sold it for **"+str(amount)+"** coins",]
    await kwargs["channel"].send(random.choice(responses))
    kwargs["member"].netWorh = kwargs["member"].wallet + kwargs["member"].bank
    saveCurrencyData()