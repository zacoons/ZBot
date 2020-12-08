import discord
from discord.ext import commands
import random
import re
import os
from key import key
from jokes import jokes
from convostarters import convostarters
import pickle
import praw
import time
import typing
import asyncio
from PIL import Image, ImageDraw, ImageFilter
import requests
from io import BytesIO

class MemberData:
    def __init__(self, warns, xp, level, rank, levelUpThreshold):
        self.warns = warns
        self.xp = xp
        self.level = level
        self.rank = rank
        self.levelUpThreshold = levelUpThreshold

class CurrencyData:
    def __init__(self, wallet, bank, bankSize, netWorth, rank, inventory):
        self.wallet = wallet
        self.bank = bank
        self.bankSize = bankSize
        self.netWorth = netWorth
        self.rank = rank
        self.inventory = inventory

class Item:
    def __init__(self, description, cost, use):
        self.description = description
        self.cost = cost
        self.use = use

class SetupData:
    def __init__(self, lvlUpChannel, lvlUpMsg, welcomeChannel, welcomeMsg):
        self.lvlUpChannel = lvlUpChannel
        self.lvlUpMsg = lvlUpMsg
        self.welcomeChannel = welcomeChannel
        self.welcomeMsg = welcomeMsg

prefixes = 'z ', 'Z '
client = commands.Bot(command_prefix=prefixes)
client.remove_command('help')
reddit = praw.Reddit(client_id='9B_9EgNR0RblQQ', client_secret='de1ze7ZZ9q7GajWI5ZYkXv451vQ', user_agent='ZBot_v1')
memberDataFilename = "memberData.pickle"
setupDataFilename = "setupData.pickle"
currencyDataFilename = "currencyData.pickle"
defaultLevelUpThreshold = 20
defaultBankSize = 20
embedColour = 0x6495ED
serverCount = 0
embedFooters = []

def TryLoadSavedDict(filename):
    if os.path.isfile(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)
    else:
        return dict()

@client.event
async def on_ready():
    global memberUnpickledData
    global setupUnpickledData
    global currencyUnpickledData
    global embedFooters
    global items

    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='for z help'))

    memberUnpickledData = TryLoadSavedDict(memberDataFilename)
    setupUnpickledData = TryLoadSavedDict(setupDataFilename)
    currencyUnpickledData = TryLoadSavedDict(currencyDataFilename)

    embedFooters = ["Potato Gang is good, Pineapple Gang is evil",
    "Check out the creator's discord at: https://discord.gg/9nP75tN",
    "Add ZBot to your server at: zacoons.com/code/zbot",
    "Made by Zacoons, feel free to join the help server: https://discord.gg/9nP75tN",
    "Watching over "+str(len(client.guilds))+" servers for free"]
    items = {'christmas box': Item(description="Use `z use christmas box` to open it and find a suprise inside", cost=150, use=useChristmasBox),
    'bank note': Item(description="Use `z use bank note` to increase the capacity of your bank", cost=50, use=useBankNote),
    'rifle': Item(description="Use `z use rifle` to go on a hunt and earn some coins, this item also protects you from being robbed", cost=250, use=useRifle)}

@client.command()
async def help(message, helpType:typing.Optional[str]):
    if helpType == None:
        embedVar = discord.Embed(title="ZBot Help", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
        embedVar.add_field(name="Setup", value="`z help setup`")
        embedVar.add_field(name="Levels", value="`z help lvls`")
        embedVar.add_field(name="Currency", value="`z help currency`")
        embedVar.add_field(name="Moderator", value="`z help mod`")
        embedVar.add_field(name="Other", value="`z help misc`")
        await message.channel.send(embed=embedVar)
    elif helpType == "setup":
        embedVar = discord.Embed(title="ZBot Setup Commands", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
        embedVar.add_field(name="`z setlvlupchannel`", value="Sets a specific channel for the level up message", inline=False)
        embedVar.add_field(name="`z setlvlupmsg`", value='Syntax example: z setlvlupmsg Nice job [mention]! You are now level [level]!"', inline=False)
        embedVar.add_field(name="`z setwelcomechannel`", value="Sets a specific channel for the welcome message", inline=False)
        embedVar.add_field(name="`z setwelcomemsg`", value='Syntax example: z setwelcomemsg "Welcome to the server [mention]!"', inline=False)
        embedVar.add_field(name="`z serverconfiguration`", value='(AKA serverconf) Shows you the your server setup configuration', inline=False)
        await message.channel.send(embed=embedVar)
    elif helpType == "mod":
        embedVar = discord.Embed(title="ZBot Moderator Commands", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
        embedVar.add_field(name="`z warn [Member]`", value="(Moderators only) Warns a member, once they recieve three warns and they're kicked", inline=False)
        embedVar.add_field(name="`z pardon [Member]`", value="(Moderators only) Clears a member's warns", inline=False)
        embedVar.add_field(name="`z pardonall`", value="(Moderators only) Clears everyone's warns", inline=False)
        embedVar.add_field(name="`z mute [Member] [time](Seconds)`", value="(Moderators only) Mutes a member for a number of seconds", inline=False)
        await message.channel.send(embed=embedVar)
    elif helpType == "misc":
        embedVar = discord.Embed(title="ZBot Other Commands", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
        embedVar.add_field(name="`z slap [Member]`", value="Slaps someone", inline=False)
        embedVar.add_field(name="`z hug [Member]`", value="Hugs someone", inline=False)
        embedVar.add_field(name="`z throne [Member]`", value="LONG LIVE THE KING", inline=False)
        embedVar.add_field(name="`z wave [Member]`", value="Send someone a wave", inline=False)
        embedVar.add_field(name="`z high5 [Member]`", value="High five someone", inline=False)
        embedVar.add_field(name="`z meme`", value="Fetches a meme from reddit", inline=False)
        embedVar.add_field(name="`z joke`", value="Send you a normal joke", inline=False)
        embedVar.add_field(name="`z conversationstarter`", value="(AKA convostart) Sends you a conversation starter", inline=False)
        await message.channel.send(embed=embedVar)
    elif helpType == "lvls":
        embedVar = discord.Embed(title="ZBot Level Commands", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)   
        embedVar.add_field(name="`z level [Username](Optional)`", value="(AKA lvl) Tells you your/someone else's level and xp", inline=False)
        embedVar.add_field(name="`z levels`", value="(AKA lvls) Gives you the rank of all ranked members", inline=False)
        embedVar.add_field(name="`z clearlevels [Username]`", value="(AKA clvls) (Moderators only) Clears a member's levels and xp", inline=False)
        embedVar.add_field(name="`z purgelevels`", value="(AKA plvls) (Moderators only) Clears everyone's levels and xp", inline=False)
        await message.channel.send(embed=embedVar)
    elif helpType == "currency":
        embedVar = discord.Embed(title="ZBot Currency Commands", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)   
        embedVar.add_field(name="`z work`", value="(5 min cooldown) Earns you some money", inline=False)
        embedVar.add_field(name="`z deposit [Amount](Can be 'all' or a number)`", value="(AKA dep) Deposits your money in the bank for safekeeping", inline=False)
        embedVar.add_field(name="`z buy [Item]`", value="Buys an item with the name given", inline=False)
        embedVar.add_field(name="`z withdraw [Amount](Can be 'all' or a number)`", value="(AKA with) Takes your money out of the bank to use", inline=False)
        embedVar.add_field(name="`z steal [Member]`", value="(5 min cooldown)(AKA rob) Steals a member's coins... Or not", inline=False)
        embedVar.add_field(name="`z donate [Member] [Amount]`", value="(AKA don) Donate a member some coins", inline=False)
        embedVar.add_field(name="`z upgradebank`", value="Gives you a bigger bank", inline=False)
        embedVar.add_field(name="`z balance [Member](Optional)`", value="(AKA bal) Shows you how many coins you have in your wallet *and* you bank", inline=False)
        embedVar.add_field(name="`z inventory [Member](Optional)`", value="(AKA inv) Shows you the items that you own", inline=False)
        embedVar.add_field(name="`z shop`", value="(AKA store) Shows you the items that you can buy", inline=False)
        embedVar.add_field(name="`z leaderboard`", value="(AKA lb) Shows you the global leaderboard", inline=False)
        await message.channel.send(embed=embedVar)

#Misc
@client.command()
async def joke(message):
    await message.channel.send(random.choice(jokes))

@client.command(aliases=['convostart'])
async def conversationstarter(message):
    await message.channel.send(random.choice(convostarters))

@client.command()
async def meme(message):
    meme_submissions = reddit.subreddit('memes').hot()
    post_to_pick = random.randint(1, 25)
    for i in range(0, post_to_pick):
        submission = next(x for x in meme_submissions if not x.stickied)

    await message.channel.send(submission.url)

@client.command()
async def slap(message, member:discord.Member):
    response1 = requests.get(message.author.avatar_url)
    response2 = requests.get(member.avatar_url)
    img = Image.open("c:/users/zacha/source/repos/zbot/slapBG.jpg")
    member1 = Image.open(BytesIO(response1.content))
    member1Resized = member1.resize((250, 250)) 
    member2 = Image.open(BytesIO(response2.content))
    member2Resized = member2.resize((250, 250)) 

    mainImg = img.copy()
    mainImg.paste(member1Resized, (500, 100))
    mainImg.paste(member2Resized, (850, 350))

    mainImgBytes = BytesIO()
    mainImg.save(mainImgBytes, "jpeg")

    mainImg.save("c:/users/zacha/source/repos/zbot/slap.jpg", quality=25)
    await message.channel.send(file=discord.File("c:/users/zacha/source/repos/zbot/slap.jpg"))

@client.command()
async def hug(message, member:discord.Member):
    response1 = requests.get(message.author.avatar_url)
    response2 = requests.get(member.avatar_url)
    img = Image.open("c:/users/zacha/source/repos/zbot/hugBG.jpg")
    member1 = Image.open(BytesIO(response1.content))
    member1Resized = member1.resize((250, 250)) 
    member2 = Image.open(BytesIO(response2.content))
    member2Resized = member2.resize((250, 250)) 

    mainImg = img.copy()
    mainImg.paste(member2Resized, (240, 150))
    mainImg.paste(member1Resized, (650, 150))

    mainImgBytes = BytesIO()
    mainImg.save(mainImgBytes, "jpeg")

    mainImg.save("c:/users/zacha/source/repos/zbot/hug.jpg", quality=25)
    await message.channel.send(file=discord.File("c:/users/zacha/source/repos/zbot/hug.jpg"))

@client.command()
async def throne(message, member:discord.Member):
    response = requests.get(member.avatar_url)
    img = Image.open("c:/users/zacha/source/repos/zbot/throneBG.jpg")
    member = Image.open(BytesIO(response.content))
    memberResized = member.resize((100, 100)) 

    mainImg = img.copy()
    mainImg.paste(memberResized, (185, 110))

    mainImgBytes = BytesIO()
    mainImg.save(mainImgBytes, "jpeg")

    mainImg.save("c:/users/zacha/source/repos/zbot/throne.jpg", quality=25)
    await message.channel.send(file=discord.File("c:/users/zacha/source/repos/zbot/throne.jpg"))

@client.command()
async def wave(message, member:discord.Member):
    response1 = requests.get(message.author.avatar_url)
    response2 = requests.get(member.avatar_url)
    img = Image.open("c:/users/zacha/source/repos/zbot/waveBG.jpg")
    member1 = Image.open(BytesIO(response1.content))
    member1Resized = member1.resize((150, 150)) 
    member2 = Image.open(BytesIO(response2.content))
    member2Resized = member2.resize((100, 100)) 

    mainImg = img.copy()
    mainImg.paste(member1Resized, (120, 45))
    mainImg.paste(member2Resized, (540, 140))

    mainImgBytes = BytesIO()
    mainImg.save(mainImgBytes, "jpeg")

    mainImg.save("c:/users/zacha/source/repos/zbot/wave.jpg", quality=25)
    await message.channel.send(file=discord.File("c:/users/zacha/source/repos/zbot/wave.jpg"))

@client.command()
async def high5(message, member:discord.Member):
    response1 = requests.get(message.author.avatar_url)
    response2 = requests.get(member.avatar_url)
    img = Image.open("c:/users/zacha/source/repos/zbot/highfiveBG.png")
    member1 = Image.open(BytesIO(response1.content))
    member1Resized = member1.resize((150, 150)) 
    member2 = Image.open(BytesIO(response2.content))
    member2Resized = member2.resize((100, 100)) 

    mainImg = img.copy()
    mainImg.paste(member1Resized, (120, 45))
    mainImg.paste(member2Resized, (540, 140))

    mainImgBytes = BytesIO()
    mainImg.save(mainImgBytes, "png")

    mainImg.save("c:/users/zacha/source/repos/zbot/highfive.png", quality=25)
    await message.channel.send(file=discord.File("c:/users/zacha/source/repos/zbot/highfive.png"))

#Setup
@client.command()
@commands.has_permissions(kick_members=True)
async def setlvlupchannel(message):
    setLevelUpChannel(message.guild, message.channel)

    await message.message.add_reaction('👍')

@client.command()
@commands.has_permissions(kick_members=True)
async def setlvlupmsg(message):
    msg = message.message.content.replace(message.message.content[:14], "", 1)
    setLevelUpMessage(message.guild, msg)

    await message.message.add_reaction('👍')

@client.command()
@commands.has_permissions(kick_members=True)
async def setwelcomechannel(message):
    setWelcomeChannel(message.guild, message.channel)

    await message.message.add_reaction('👍')

@client.command()
@commands.has_permissions(kick_members=True)
async def setwelcomemsg(message):
    msg = message.message.content.replace(message.message.content[:16], "", 1)
    setWelcomeMessage(message.guild, msg)

    await message.message.add_reaction('👍')

@client.command(aliases=['serverconf'])
async def serverconfiguration(message):
    data = loadSetupData(message.guild)
    welcomeChannel = client.get_channel(data.welcomeChannel)
    lvlUpChannel = client.get_channel(data.lvlUpChannel)
    if lvlUpChannel == None:
        lvlUpChannelName = 'None'
    else:
        lvlUpChannelName = lvlUpChannel.name
    if welcomeChannel == None:
        welcomeChannelName = 'None'
    else:
        welcomeChannelName = welcomeChannel.name
    if data.lvlUpMsg == None:
        lvlUpChannelName = 'None'
    if data.welcomeMsg == None:
        welcomeChannelName = 'None'

    embedVar = discord.Embed(title=message.guild.name+" Server Configuration", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=message.guild.icon_url)   
    embedVar.add_field(name="Welcome message", value=data.welcomeMsg, inline=False)
    embedVar.add_field(name="Welcome channel", value=welcomeChannelName, inline=False)
    embedVar.add_field(name="Level up message", value=data.lvlUpMsg, inline=False)
    embedVar.add_field(name="Level up channel", value=lvlUpChannelName, inline=False)
    await message.channel.send(embed=embedVar)    

#Mod
@client.command()
@commands.has_permissions(kick_members=True)
async def warn(message, member:discord.Member):
    if member != None:
        if member.id != message.author.id:
            await warnMember(message, member)
        else:
            await message.channel.send("That's you dumb dumb")
    else:
        await message.channel.send(str(member) + " isn't a member bro")

@client.command()
@commands.has_permissions(kick_members=True)
async def pardon(message, member:discord.Member):
    members = loadMemberData(message.guild)

    if str(member) not in members:
        return

    members[str(member)].warns = 0
    await message.message.add_reaction('👍')

    saveMemberData()

@client.command()
@commands.has_permissions(kick_members=True)
async def pardonall(message):
    members = loadMemberData(message.guild)

    for member in members:
        if members[member] == None:
            return
        members[member].warns = 0
    
    await message.message.add_reaction('👍')

    saveMemberData()

@client.command()
@commands.has_permissions(kick_members=True)
async def mute(message, member:discord.Member, time:int):
    if member == client.user:
        await message.channel.send("Why are you trying to mute me")
        return

    await muteMember(message.guild, member, time, message.channel)

    await message.message.add_reaction('👍')

#Lvls
@client.command(aliases=['lvl'])
async def level(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author

    memberInfo = await getMemberInfo(message, member)

    embedVar = discord.Embed(title="", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    embedVar.add_field(name="XP", value=str(memberInfo.xp)+"/"+str(memberInfo.levelUpThreshold), inline=False)
    embedVar.add_field(name="Level", value=str(memberInfo.level), inline=False)
    embedVar.add_field(name="Rank", value="#" + str(memberInfo.rank), inline=False)
    await message.channel.send(embed=embedVar)

@client.command(aliases=['lvls'])
async def levels(message):
    members = loadMemberData(message.guild)
    sortedMembers = sorted(members.items(), key = lambda kv: kv[1].rank)

    embedVar = discord.Embed(title="Levels Leaderboard", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.icon_url))

    for memberName, data in sortedMembers:
        embedVar.add_field(name='#'+str(data.rank)+' - '+memberName, value='level '+str(data.level), inline=False)

    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)

    await message.channel.send(embed=embedVar)

@client.command()
@commands.has_permissions(kick_members=True)
async def clearlevels(message, member:discord.Member):
    if member == None:
        await message.channel.send((str(member) + " isn't a member bro"))
        return

    clearLevels(message, member)
    await message.message.add_reaction('👍')

    saveMemberData()

@client.command(aliases=['plvls'])
@commands.has_permissions(kick_members=True)
async def purgelevels(message):
    members = loadMemberData(message.guild)

    for member in members:
        if members[str(member)] == None:
            return
        else:
            clearLevels(message, member)
    
    await message.message.add_reaction('👍')

    saveMemberData()

#Currency
# @client.command(aliases=['lb'])
# async def leaderboard(message):
#     setCurrencyRanks()
#     data = currencyUnpickledData()
#     sortedData = list(reversed(sorted(data.items(), key = lambda kv: kv[1].rank)))
    
#     embedVar = discord.Embed(title="Currency Leaderboard", description="", color=embedColour)
#     embedVar.set_footer(text="You are #"+str(loadCurrencyData(message.author).rank), icon_url=discord.utils.get(message.guild.members, name=str(message.author)).avatar_url)
#     embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
#     for data in sortedData[:3]:
#         embedVar.add_field(name="#"+str(data), value=data)

#     await message.channel.send(embed=embedVar)

# @client.command(aliases=['globallb'])
# async def globalleaderboard(message):
    

@client.command(aliases=['bal'])
async def balance(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author
    
    memberInfo = loadCurrencyData(member)

    embedVar = discord.Embed(title="", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    embedVar.add_field(name="Wallet", value=str(memberInfo.wallet), inline=False)
    embedVar.add_field(name="Bank", value=str(memberInfo.bank)+"/"+str(memberInfo.bankSize), inline=False)
    embedVar.add_field(name="Net Worth", value=str(memberInfo.netWorth), inline=False)
    await message.channel.send(embed=embedVar)

@client.command()
@commands.cooldown(1, 300, commands.BucketType.user)
async def work(message):
    amount = random.randint(10, 25)
    member = loadCurrencyData(message.author)
    member.wallet += amount
    getsBonusItem = random.randint(0, 15)
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
        message.channel.send(message.author.mention+" has a rifle, I don't think you want to mess with him")

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

    member1Data.wallet -= amount
    member2Data.wallet += amount

    await message.channel.send("You just donated **"+str(amount)+"** coins to "+member.mention+". What a lucky guy \:D")
    
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
async def use(message, item:str):
    member = loadCurrencyData(message.author)
    itemName = message.message.content.lower().replace("z use ", "")
    if itemName in member.inventory:
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
    for itemName in data.inventory:
        embedVar.add_field(name=itemName, value=items[itemName].description, inline=False)
    if data.inventory == dict():
        embedVar.add_field(name="You don't have any items", value="You can go find some by typing the command `z work`")
    
    await message.channel.send(embed=embedVar)

@client.command(aliases=["store"])
async def shop(message):
    embedVar = discord.Embed(title="ZBot Shop", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  

    for item in items:
        embedVar.add_field(name=item+" - "+str(items[item].cost)+" coins", value=items[item].description, inline=False)
    
    await message.channel.send(embed=embedVar)

#Events
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # await giveMemberXP(1, message)

    await client.process_commands(message)

@client.event
async def on_member_join(member):
    setupData = loadSetupData(member.guild)
    welcomeMsg = setupData.welcomeMsg.replace('[mention]', member.mention)
    channel = client.get_channel(setupData.welcomeChannel)
    
    if channel == None or welcomeMsg == "":
        return

    await channel.send(welcomeMsg)

@client.event
async def on_command_error(message, error):
    if isinstance(error, commands.MissingPermissions):
        await message.channel.send("You don't have the perms to use that command :/")
    elif isinstance(error, commands.MissingRequiredArgument):
        await message.channel.send("You haven't provided the required amount of arguments, try looking at the help menu with `z help`")
    elif isinstance(error, commands.CommandOnCooldown):
        if error.cooldown.per > 3600:
            cooldown = "**"+str(int(error.cooldown.per/3600))+"** hour"
        elif int(error.cooldown.per) > 60:
            cooldown = "**"+str(int(error.cooldown.per/60))+"** minute"
        else:
            cooldown = "**"+str(int(error.cooldown.per))+"** second"
        if error.retry_after > 3600:
            retryAfter = "**"+str(int(error.retry_after/3600))+"** hours"
        elif int(error.retry_after) > 60:
            retryAfter = "**"+str(int(error.retry_after/60))+"** minutes"
        else:
            retryAfter = "**"+str(int(error.retry_after))+"** seconds"
        
        await message.channel.send("Woah slow down there man, that command has a "+str(cooldown)+" cooldown. Try again in "+str(retryAfter))

#Functions
async def assignRole(role, user):
    await user.add_roles(role, reason=None, atomic=False)
async def removeRole(role, user):
    await user.remove_roles(role, reason=None, atomic=False)

#Member functions
def loadMemberData(guild):
    if str(guild) in memberUnpickledData:
        return memberUnpickledData[str(guild)]
    else:
        memberUnpickledData[str(guild)] = dict()
        return memberUnpickledData[str(guild)]
def saveMemberData():
    with open(memberDataFilename, "wb") as file:
        pickle.dump(setupUnpickledData, file)
async def muteMember(guild, member, muteTime, channel):
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_messages=False)

    await member.add_roles(mutedRole, reason=None)
    await channel.send("RIP "+member.mention+" was muted for " + str(muteTime) + " seconds :/")

    await asyncio.sleep(muteTime)

    await member.remove_roles(mutedRole)
#Warns
async def warnMember(message, member:discord.Member):
    if member != None:
        if member.id != client.user.id:
            if member.id != message.guild.owner_id and member.id:
                members = loadMemberData(message.guild)

                members[str(member)].warns += 1

                if members[str(member)].warns >= 3 and member.id != message.guild.owner_id:
                    try:
                        await member.send("Too many warns and you were kicked from the server! If you wish to rejoin maybe reread the rules")
                    except:
                        pass
                    members[str(member)].warns = 0
                    await member.kick(reason=None)
                else:
                    await message.channel.send(member.mention + ' you have been warned! ' + str(members[str(member)].warns) + "/3")
                
                saveMemberData()
            else:
                await message.channel.send(member.name + " is the owner, he wouldn't break his own rules so he is immune")
        else:
            await message.channel.send("Bruh, I'm a bot. If you have a problem with me, take it up with the owner")
    else:
        await message.channel.send(str(member) + " doesn't exist bro")
#Levels
async def giveMemberXP(xpAmount, message):
    if message.author.bot:
        return
    
    members = loadMemberData(message.guild)

    if not str(message.author) in members:
        members[str(message.author)] = MemberData(0, 0, 0, 0, defaultLevelUpThreshold)

    members[str(message.author)].xp += xpAmount
    # member.levelUpThreshold = defaultLevelUpThreshold

    if members[str(message.author)].xp >= members[str(message.author)].levelUpThreshold:
        members[str(message.author)].level += 1
        members[str(message.author)].xp = 0
        members[str(message.author)].levelUpThreshold += 10

        setupData = loadSetupData(message.guild)
        msg = setupData.lvlUpMsg
        lvlUpMsg = None
        if msg != None:
            lvlUpMsg = msg.replace('[mention]', "**"+message.author.mention+"**")
            # memberInfo = await getMemberInfo(message, message.author)
            # lvlUpMsg = lvlUpMsg.replace('[level]',  str(memberInfo.level))
            lvlUpMsg = lvlUpMsg.replace('[level]',  str(members[str(message.author)].level))
        channel = client.get_channel(setupData.lvlUpChannel)
        if channel == None:
            channel = message.channel
        if lvlUpMsg == "":
            lvlUpMsg = ("**" + message.author.mention + "** you leveled up! You are now level " + str(members[str(message.author)].level))
        await channel.send(lvlUpMsg)

    setMemberRanks(message, message.guild)

    saveMemberData()
async def getMemberInfo(message, member):
    members = loadMemberData(message.guild)

    if not str(member) in members:
        members[str(member)] = MemberData(0, 0, 0, 0, defaultLevelUpThreshold, dict())

    if message.guild.get_member_named(str(member)) == None:
        await message.channel.send("That's not a member bro")
        return None

    setMemberRanks(message, message.guild)

    return members[str(member)]
def setMemberRanks(message, guild):
    members = loadMemberData(message.guild)
    
    for member in members:
        members[str(member)].rank = len(members)

        for checkMember in members:
            if members[str(member)].level > members[str(checkMember)].level:
                members[str(member)].rank -= 1
            elif members[str(member)].level == members[str(checkMember)].level:
                if members[str(member)].xp > members[str(checkMember)].xp:
                    members[str(member)].rank -= 1
                elif members[str(member)].xp == members[str(checkMember)].xp:
                    members[str(member)].rank = members[str(checkMember)].rank
    
    saveMemberData()
def clearLevels(message, member):
    members = loadMemberData(message.guild)

    members[str(member)].rank = 0
    members[str(member)].xp = 0    
    members[str(member)].level = 0
    members[str(member)].levelUpThreshold = defaultLevelUpThreshold

    saveMemberData()

#Setup data functions
def saveSetupData():
    with open(setupDataFilename, "wb") as file:
        pickle.dump(setupUnpickledData, file)
def loadSetupData(guild):
    if not str(guild) in setupUnpickledData:
        setupUnpickledData[str(guild)] = SetupData(None, "", None, "")

    return setupUnpickledData[str(guild)]

def setLevelUpChannel(guild, channel):
    setupData = loadSetupData(guild)
    setupData.lvlUpChannel = channel.id
    saveSetupData()
def setLevelUpMessage(guild, msg):
    setupData = loadSetupData(guild)
    setupData.lvlUpMsg = msg
    saveSetupData()

def setWelcomeChannel(guild, channel):
    setupData = loadSetupData(guild)
    setupData.welcomeChannel = channel.id
    saveSetupData()
def setWelcomeMessage(guild, msg):
    setupData = loadSetupData(guild)
    setupData.welcomeMsg = msg
    saveSetupData()

#Currency data functions
def saveCurrencyData():
    member.netWorth = member.wallet + member.bank
    with open(currencyDataFilename, "wb") as file:
        pickle.dump(currencyUnpickledData, file)
def loadCurrencyData(member):
    if not str(member) in currencyUnpickledData:
        currencyUnpickledData[str(member)] = CurrencyData(0, 0, defaultBankSize, 0, 0, dict())

    return currencyUnpickledData[str(member)]
def setCurrencyRanks():
    for member in currencyUnpickledData:
        memberData = currencyUnpickledData[member]
        memberData = len(currencyUnpickledData)

        for checkMember in currencyUnpickledData:
            checkMemberData = currencyUnpickledData[checkMember]
            if memberData.netWorth > checkMemberData.netWorth:
                memberData.rank -= 1

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
    await msg.edit(content=kwargs["member"].mention+" you got **"+str(coins)+"** coins from your **Christmas Box**")
    kwargs["member"].netWorh = kwargs["member"].wallet + kwargs["member"].bank
    saveCurrencyData()

async def useBankNote(**kwargs):
    data = loadCurrencyData(kwargs["member"])
    data.inventory.pop("bank note")
    amount = random.randint(20, 50)
    data.bankSize += amount
    await kwargs["channel"].send("Your bank size has been increased by **"+str(amount)+"** coins")
    saveCurrencyData()

async def useRifle(**kwargs):
    data = loadCurrencyData(kwargs["member"])
    amount = random.randint(20, 50)
    data.wallet += amount
    responses=["You shot a rabbit and sold it for **"+str(amount)+"** coins",
    "You shot a skunk and sold it for **"+str(amount)+"** coins",]
    await kwargs["channel"].send(random.choice(responses))
    saveCurrencyData()

client.run(key)