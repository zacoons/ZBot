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
import pokezmon
from PIL import Image, ImageDraw, ImageFilter
import requests
from io import BytesIO

class Pokezmon:
    def __init__(self, cost, name, power):
        self.cost = cost
        self.name = name
        self.power = power

class PollData:
    def __init__(self, msgID, pollUpRole, pollDownRole):
        self.msgID = msgID
        self.pollUpRole = pollUpRole
        self.pollDownRole = pollDownRole

class MemberData:
    def __init__(self, warns, xp, level, rank, levelUpThreshold, pokezmon):
        self.warns = warns
        self.xp = xp
        self.level = level
        self.rank = rank
        self.levelUpThreshold = levelUpThreshold
        self.pokezmon = pokezmon

class CurrencyData:
    def __init__(self, wallet, bank, bankSize):
        self.wallet = wallet
        self.bank = bank
        self.bankSize = bankSize

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
pollDataFilename = "pollData.pickle"
memberDataFilename = "memberData.pickle"
setupDataFilename = "setupData.pickle"
defaultLevelUpThreshold = 20
defaultBankSize = 20
embedColour = 0x6495ED
embedFooters = ["Potato Gang is good, Pineapple Gang is evil",
"Check out the creator's discord at: https://discord.gg/9nP75tN",
"Add ZBot to your server at: zacoons.com/code/zbot",
"Made by Zacoons, feel free to join the help server: https://discord.gg/9nP75tN"]
pokezmons = {
    "potato lord": Pokezmon(4, "Potato Lord", 5),
    "pineapple lord": Pokezmon(4, "Pineapple Lord", 5),
    "jimmonkey": Pokezmon(4, "Jimmonkey", 4),
    "akayla": Pokezmon(4, "Akalya", 4),
    "matthpew": Pokezmon(3, "Matthpew", 3)}

def TryLoadSavedDict(filename):
    if os.path.isfile(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)
    else:
        return dict()

@client.event
async def on_ready():
    global pollUnpickledData
    global memberUnpickledData
    global setupUnpickledData

    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='for z help'))

    pollUnpickledData = TryLoadSavedDict(pollDataFilename)
    memberUnpickledData = TryLoadSavedDict(memberDataFilename)
    setupUnpickledData = TryLoadSavedDict(setupDataFilename)

@client.command()
async def help(message, helpType:typing.Optional[str]):
    if helpType == None:
        embedVar = discord.Embed(title="ZBot Help", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
        embedVar.add_field(name="Setup", value="`z help setup`")
        embedVar.add_field(name="Levels", value="`z help lvls`")
        embedVar.add_field(name="Currency", value="`z help currency`")
        embedVar.add_field(name="Pokezmon", value="`z help pokezmon`")
        embedVar.add_field(name="Moderator", value="`z help mod`")
        embedVar.add_field(name="Other", value="`z help misc`")
        await message.channel.send(embed=embedVar)
    elif helpType == "setup":
        embedVar = discord.Embed(title="ZBot Setup Commands", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
        embedVar.add_field(name="`z setlvlupchannel`", value="Sets a specific channel for the level up message", inline=False)
        embedVar.add_field(name="`z setlvlupmsg`", value='Syntax example: z setlvlupmsg "Nice job [mention]! You are now level [level]!"', inline=False)
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
        embedVar.add_field(name="`z poll [ThumbsUpRole] [ThumbsDownRole] [Message Content]`", value="Sets a poll, the variables you set determine the content of the poll", inline=False)
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
        embedVar.add_field(name="`z work`", value="Earns you some money", inline=False)
        embedVar.add_field(name="`z deposit [Amount](Can be 'all' or a number)`", value="(AKA dep) Deposits your money in the bank for safekeeping", inline=False)
        embedVar.add_field(name="`z withdraw [Amount](Can be 'all' or a number)`", value="(AKA with) Takes your money out of the bank to use", inline=False)
        embedVar.add_field(name="`z balance [Member](Optional)`", value="(AKA bal) Shows you how many coins you have in your wallet *and* you bank", inline=False)
        await message.channel.send(embed=embedVar)
    elif helpType == "pokezmon":
        embedVar = discord.Embed(title="ZBot Pokezmon Commands", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)   
        embedVar.add_field(name="`z pokezmonlist`", value="Shows you the list of pokezmon", inline=False)
        embedVar.add_field(name="`z buypokezmon [name]`", value='(AKA bpokezmon) Buys you the named pokezmon. Syntax example: z bpokezmon "Potato Lord"', inline=False)
        embedVar.add_field(name="`z inventory`", value="(AKA inv) Shows you a list of your pokezmon", inline=False)
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
async def poll(message, pollUpRoleName:str, pollDownRoleName:str, content:str):
    if str(message.guild) in pollUnpickledData:
        serverPolls = pollUnpickledData[str(message.guild)]
    else:
        serverData = dict()
        pollUnpickledData[str(message.guild)] = serverData
        serverPolls = serverData

    if pollUpRoleName.lower() == "none" and pollDownRoleName.lower() == "none":
            await message.channel.send("You gotta put in at least one role")
            return

    if pollUpRoleName.lower() != "none":
        pollUpRole = discord.utils.get(message.guild.roles, name=pollUpRoleName)
        if pollUpRole == None: 
            await message.channel.send(pollUpRoleName + " isn't a role my dude")
            return
    
    if pollDownRoleName.lower() != "none":
        pollDownRole = discord.utils.get(message.guild.roles, name=pollDownRoleName)
        if pollDownRole == None:
            await message.channel.send(pollDownRoleName + " isn't a role my dude")
            return

    embedVar = discord.Embed(title=content, color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url="https://i.imgur.com/FZKHNYE.png")
    msg = await message.channel.send(embed=embedVar)
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')
    serverPolls[str(msg.id)] = PollData(msg.id, pollUpRoleName, pollDownRoleName)
    
    with open(pollDataFilename, "wb") as file:
        pickle.dump(serverPolls, file)

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
    member1Resized = member1.resize((200, 200)) 
    member2 = Image.open(BytesIO(response2.content))
    member2Resized = member2.resize((200, 200)) 

    mainImg = img.copy()
    mainImg.paste(member2Resized, (240, 150))
    mainImg.paste(member1Resized, (610, 150))

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

    # await message.channel.send(data.welcomeMsg+', '+welcomeChannelName+', '+data.lvlUpMsg+', '+lvlUpChannelName)
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
    # with open(memberDataFilename, "wb") as file:
    #     pickle.dump(memberUnpickledData, file)

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
    # with open(memberDataFilename, "wb") as file:
    #     pickle.dump(memberUnpickledData, file)

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
    # members = loadMemberData(message.guild)
    # memberInfo = members[str(member)]

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

    embedVar = discord.Embed(title="Leaderboard", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)   

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
    # with open(memberDataFilename, "wb") as file:
    #     pickle.dump(memberUnpickledData, file)

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
    # with open(memberDataFilename, "wb") as file:
    #     pickle.dump(memberUnpickledData, file)

#Money
@client.command(aliases=['bal'])
async def balance(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author
    
    memberInfo = await getMemberInfo(message, member)

    embedVar = discord.Embed(title="", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    embedVar.add_field(name="Wallet", value=str(memberInfo.wallet), inline=False)
    embedVar.add_field(name="Bank", value=str(memberInfo.bank)+"/"+str(memberInfo.bankSize), inline=False)
    await message.channel.send(embed=embedVar)

    saveMemberData()

@client.command()
async def work(message):
    amount = random.choice([5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    member = await getMemberInfo(message, message.author)
    member.wallet += amount
    thingsToSay = ["You asked your grandma for money and she gave you **"+str(amount)+"** coins",
    "You farted on such a harmonic note that a nearby strager gave you **"+str(amount)+"** coins",
    "You went shopping and the clerk, under the impression of your dashing looks, payed *you* **"+str(amount)+"** coins instead of the other way around",
    "You mowed your neighbours lawn and he gave you **"+str(amount)+"** coins",
    "You found some spare change under your couch which amounts to **"+str(amount)+"** coins",
    "You searched the air infront of you and found **"+str(amount)+"** coins. Wait **what**",
    "You cut open a potato and found **"+str(amount)+"** coins, wow, the wonders of potato gang I guess",
    "You found some spare change under your couch which amounts to **"+str(amount)+"** coins"]
    await message.channel.send(random.choice(thingsToSay))

    saveMemberData()

@client.command(aliases=['dep'])
async def deposit(message, amount:str):
    member = await getMemberInfo(message, message.author)

    if amount == 'all':
        dep = member.bankSize - (member.bankSize - member.wallet)
        if dep > member.bankSize:
            depCache = dep
            dep = depCache - (depCache + member.bank - member.bankSize)
        member.bank += dep
        member.wallet -= dep
        await message.channel.send("**"+str(dep)+"** coins have been deposited")
    else:
        if not (int(amount) + member.bank) > member.bankSize:
            member.bank += int(amount)
            member.wallet -= int(amount)
            await message.message.add_reaction('👍')
        else:
            await message.channel.send("That won't fit in your bank... Maybe deposit a bit less")

    saveMemberData()

@client.command(aliases=['with'])
async def withdraw(message, amount:str):
    member = await getMemberInfo(message, message.author)

    if amount == 'all':
        dep = member.bank
        member.bank -= dep
        member.wallet += dep
        await message.channel.send("**"+str(dep)+"** coins have been deposited")
    else:
        if not amount > member.bank:
            member.bank -= int(amount)
            member.wallet += int(amount)
            await message.message.add_reaction('👍')
        else:
            await message.channel.send("Lol you wish, you don't have that many coins")

    saveMemberData()

#Pokezmon
@client.command()
async def buypokezmon(message):
    pokezmonName = message.message.content.replace(message.message.content[:14], "", 1)
    await message.channel.send(buyPokezmon(pokezmonName.lower(), message.author))
    #     ("")
    # else:
    #     await message.channel.send("You don't have enough levels for that :/")

async def tradepokezmon(message, member2:discord.Member):
    members = loadMemberData(message.guild)
    member1 = members[str(message.author)]
    initPokezmonTrade

@client.command()
async def pokezmonlist(message):
    embedVar = discord.Embed(title="Pokezmon", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    # embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.add_field(name=":gun: Matthpew", value="`Cost: "+str(pokezmons["matthpew"].cost)+" levels`, `Power: "+str(pokezmons["matthpew"].power)+"`", inline=False)
    embedVar.add_field(name=":sparkles: Akayla", value="`Cost: "+str(pokezmons["akayla"].cost)+" levels`, `Power: "+str(pokezmons["akayla"].power)+"`", inline=False)
    embedVar.add_field(name=":banana: Jimmonkey", value="`Cost: "+str(pokezmons["jimmonkey"].cost)+" levels`, `Power: "+str(pokezmons["jimmonkey"].power)+"`", inline=False)
    embedVar.add_field(name=":crown: Pineapple Lord", value="`Cost: "+str(pokezmons["pineapple lord"].cost)+" levels`, `Power: "+str(pokezmons["pineapple lord"].power)+"`", inline=False)
    embedVar.add_field(name=":crown: Potato Lord", value="`Cost: "+str(pokezmons["potato lord"].cost)+" levels`, `Power: "+str(pokezmons["potato lord"].power)+"`", inline=False)
    await message.channel.send(embed=embedVar)

@client.command(aliases=['inv'])
async def inventory(message, member:typing.Optional[discord.Member]):
    members = loadMemberData(message.guild)

    if member == None:
        memberName = str(message.author)
    else:
        memberName = str(member)

    embedVar = discord.Embed(title="Your Pokezmon", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)

    for pokezmon in members[memberName].pokezmon:
        embedVar.add_field(name=pokezmon.name, value="`Cost: "+str(pokezmons[pokezmon.lower()].cost)+" levels`" + "`Power: "+str(pokezmons[pokezmon.lower()].power+"`"), inline=False)
    if members[memberName].pokezmon == dict():
        embedVar.add_field(name="You don't have any pokezmon :/", value="Type `z helppokezmon` to find out more")

    await message.channel.send(embed=embedVar)

@client.command()
async def sellpokezmon(message):
    pokezmonName = message.message.content.replace(message.message.content[:15], "", 1)
    pokezmon = pokezmons[pokezmonName.lower()]
    member = getMemberInfo(message, message.author)

    member.levels += pokezmon.cost

    saveMemberData()

    await message.channel.send("You got **" + pokezmon.cost + "** levels for selling your **" + pokezmon.name + "**")

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
async def on_reaction_add(reaction, user):
    if user == client:
        return

    pollMsg = pollUnpickledData[str(reaction.message.guild)][str(reaction.message.id)]
    pollUpRole = discord.utils.get(reaction.message.guild.roles, name=pollMsg.pollUpRole)
    pollDownRole = discord.utils.get(reaction.message.guild.roles, name=pollMsg.pollDownRole)

    if reaction.message.id == pollMsg.msgID:
        if reaction.emoji == '👍':
            if pollUpRole != None:
                await assignRole(pollUpRole, user)
        if reaction.emoji == '👎':
            if pollDownRole != None:
                await assignRole(pollDownRole, user)

@client.event
async def on_reaction_remove(reaction, user):
    if user == client:
        return

    pollMsg = pollUnpickledData[str(reaction.message.guild)][str(reaction.message.id)]
    pollUpRole = discord.utils.get(reaction.message.guild.roles, name=pollMsg.pollUpRole)
    pollDownRole = discord.utils.get(reaction.message.guild.roles, name=pollMsg.pollDownRole)

    if reaction.message.id == pollMsg.msgID:
        if reaction.emoji == '👍':
            if pollUpRole != None:
                await removeRole(pollUpRole, user)
        if reaction.emoji == '👎':
            if pollDownRole != None:
                await removeRole(pollDownRole, user)

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
        members[str(message.author)] = MemberData(0, 0, 0, 0, defaultLevelUpThreshold, dict(), 0, 0, defaultBankSize)

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
        members[str(member)] = MemberData(0, 0, 0, 0, defaultLevelUpThreshold, dict(), 0, 0, defaultBankSize)

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
#Pokezmon
def buyPokezmon(pokezmonName, member):
    members = loadMemberData(member.guild)
    buyer = members[str(member)]

    if not pokezmonName in pokezmons:
        return "There is no such thing as a **" + pokezmonName + "** silly! Try checking your spelling"
    else:
        pokezmon = pokezmons[pokezmonName]
    if pokezmon.cost > buyer.level:
        return "You don't have enough levels for that :/"

    buyer.level -= pokezmon.cost
    buyer.pokezmon[str(pokezmon.name)] = pokezmon

    saveMemberData()
    return "Woaw! You just bought a **" + str(pokezmon.name) + "** for **"+str(pokezmon.cost)+"** levels!"
# def initPokezmonTrade(message, pokezmon1, member1, member2):
#     message.channel.send("Yo " + member2.mention + ", " + member1.mention + " wants to trade a " + pokezmon1.name + " with you. y/n")
#     def check(reaction, user):
#         return user == message.author and str(reaction.emoji) == '👍'
#     goahead = await client.wait_for('message', check=check)
#     if goahead:
#         message.channel.send("Enter the name of the pokezmon you want to trade")
#         pokezmon2 = pokezmons[await client.wait_for('message', check)]
#         if pokezmon2 in pokezmons and pokezmon2 in member2.pokezmon:
#             message.channel.send(member1.mention + "is that a good trade? y/n")
#             goahead = await client.wait_for('message', check)
#             if goahead == "y" or goahead == "yes" or goahead == "Y" or goahead == "Yes":
#                 tradePokezmon(pokezmon1, pokezmon2, member1, member2)
#                 message.channel.send("**Yeet**. It is done")

def tradePokezmon(pokezmon1, pokezmon2, member1, member2):
    member1.pokezmon[pokezmon1.lower()] = None
    member1.pokezmon[pokezmon2.lower()] = pokezmons[pokezmon2.lower()]
    member2.pokezmon[pokezmon2.lower()] = None
    member2.pokezmon[pokezmon1.lower()] = pokezmons[pokezmon1.lower()]

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

client.run(key)