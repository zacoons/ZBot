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
from currency import leaderboard, deposit, buy, balance, buy, daily, give, inventory, steal, shop, withdraw
from moderator import warn, pardon, pardonall, mute
from io import BytesIO
from common import tryLoadSavedDict, client, embedColour, embedFooters, completedReaction, badArgsError, badBotPermsError, badMemberPermsError, nonExistentCommandError

class MemberData:
    def __init__(self, warns, xp, level, rank, levelUpThreshold):
        self.warns = warns
        self.xp = xp
        self.level = level
        self.rank = rank
        self.levelUpThreshold = levelUpThreshold

class SetupData:
    def __init__(self, lvlUpChannel, lvlUpMsg, welcomeChannel, welcomeMsg):
        self.lvlUpChannel = lvlUpChannel
        self.lvlUpMsg = lvlUpMsg
        self.welcomeChannel = welcomeChannel
        self.welcomeMsg = welcomeMsg

reddit = praw.Reddit(client_id='9B_9EgNR0RblQQ', client_secret='de1ze7ZZ9q7GajWI5ZYkXv451vQ', user_agent='ZBot_v1')
memberDataFilename = "memberData.pickle"
setupDataFilename = "setupData.pickle"
defaultLevelUpThreshold = 20

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='for z help'))

    global memberUnpickledData
    global setupUnpickledData

    memberUnpickledData = tryLoadSavedDict(memberDataFilename)
    setupUnpickledData = tryLoadSavedDict(setupDataFilename)

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
        embedVar.add_field(name="`z setlvlupchannel [Channel]`", value="Sets a specific channel for the level up message", inline=False)
        embedVar.add_field(name="`z setlvlupmsg [Message]`", value='Syntax example: z setlvlupmsg Nice job [mention]! You are now level [level]!"', inline=False)
        embedVar.add_field(name="`z setwelcomechannel [Channel]`", value="Sets a specific channel for the welcome message", inline=False)
        embedVar.add_field(name="`z setwelcomemsg [Message]`", value='Syntax example: z setwelcomemsg "Welcome to the server [mention]!"', inline=False)
        embedVar.add_field(name="`z configuration`", value='(AKA config) Shows you the your server setup configuration', inline=False)
        await message.channel.send(embed=embedVar)
    elif helpType == "mod":
        embedVar = discord.Embed(title="ZBot Moderator Commands", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
        embedVar.add_field(name="`z warn [Member] [Reason](Optional)`", value="(Moderators only) Warns a member, once they recieve three warns and they're kicked", inline=False)
        embedVar.add_field(name="`z pardon [Member]`", value="(Moderators only) Clears a member's warns", inline=False)
        embedVar.add_field(name="`z pardonall`", value="(Moderators only) Clears everyone's warns", inline=False)
        embedVar.add_field(name="`z mute [Member] [Time](Seconds)(Optional) [Reason](Optional)`", value="(Moderators only) Mutes a member for a number of seconds", inline=False)
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
    # elif helpType == "lvls":
    #     embedVar = discord.Embed(title="ZBot Level Commands", description="", color=embedColour)
    #     embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    #     embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)   
    #     embedVar.add_field(name="`z level [Username](Optional)`", value="(AKA lvl) Tells you your/someone else's level and xp", inline=False)
    #     embedVar.add_field(name="`z levels`", value="(AKA lvls) Gives you the rank of all ranked members", inline=False)
    #     await message.channel.send(embed=embedVar)
    elif helpType == "currency":
        embedVar = discord.Embed(title="ZBot Currency Commands", description="", color=embedColour)
        embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
        embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)   
        embedVar.add_field(name="`z work`", value="(1 min cooldown) Earns you some money", inline=False)
        embedVar.add_field(name="`z daily`", value="(24 hr cooldown) Gives you your daily reward", inline=False)
        embedVar.add_field(name="`z deposit [Amount](Can be 'all' or a number)`", value="(AKA dep) Deposits your money in the bank for safekeeping", inline=False)
        embedVar.add_field(name="`z buy [Item] [Amount](Optional)`", value="Buys an item with the name given", inline=False)
        embedVar.add_field(name="`z withdraw [Amount](Can be 'all' or a number)`", value="(AKA with) Takes your money out of the bank to use", inline=False)
        embedVar.add_field(name="`z steal [Member]`", value="(5 min cooldown)(AKA rob) Steals a member's coins... Or not", inline=False)
        embedVar.add_field(name="`z give [Member] [Amount/Item]`", value="Give a member some coins or an item", inline=False)
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
    mainImg.paste(member2Resized, (310, 200))
    mainImg.paste(member1Resized, (620, 150))

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
    imgPath = "{rootPath}\\highfiveBG.png".format(rootPath=os.path.realpath(__file__))
    img = Image.open(imgPath)
    member1 = Image.open(BytesIO(response1.content))
    member1Resized = member1.resize((200, 200)) 
    member2 = Image.open(BytesIO(response2.content))
    member2Resized = member2.resize((200, 200)) 

    mainImg = img.copy()
    mainImg.paste(member1Resized, (500, 400))
    mainImg.paste(member2Resized, (1450, 475))

    mainImgBytes = BytesIO()
    mainImg.save(mainImgBytes, "png")

    mainImg.save(imgPath, quality=25)
    await message.channel.send(file=discord.File(imgPath))

#Setup
@client.command()
@commands.has_permissions(kick_members=True)
async def setlvlupchannel(message):
    setLevelUpChannel(message.guild, message.channel)

    await message.message.add_reaction(completedReaction)

@client.command()
@commands.has_permissions(kick_members=True)
async def setlvlupmsg(message):
    msg = message.message.content.replace(message.message.content[:14], "", 1)
    setLevelUpMessage(message.guild, msg)

    await message.message.add_reaction(completedReaction)

@client.command()
@commands.has_permissions(kick_members=True)
async def setwelcomechannel(message):
    setWelcomeChannel(message.guild, message.channel)

    await message.message.add_reaction(completedReaction)

@client.command()
@commands.has_permissions(kick_members=True)
async def setwelcomemsg(message):
    msg = message.message.content.replace(message.message.content[:16], "", 1)
    setWelcomeMessage(message.guild, msg)

    await message.message.add_reaction(completedReaction)

@client.command(aliases=['config'])
async def configuration(message):
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
    if data.lvlUpMsg == '':
        lvlUpMsg = 'None'
    else:
        lvlUpMsg = data.lvlUpMsg
    if data.welcomeMsg == '':
        welcomeMsg = 'None'
    else:
        welcomeMsg = data.welcomeMsg

    embedVar = discord.Embed(title="{serverName} Configuration".format(serverName=message.guild.name), description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=message.guild.icon_url)   
    embedVar.add_field(name="Welcome message", value=welcomeMsg, inline=False)
    embedVar.add_field(name="Welcome channel", value=welcomeChannelName, inline=False)
    embedVar.add_field(name="Level up message", value=lvlUpMsg, inline=False)
    embedVar.add_field(name="Level up channel", value=lvlUpChannelName, inline=False)
    await message.channel.send(embed=embedVar)    

#Lvls
@client.command(aliases=['lvl'])
async def level(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author

    memberInfo = await getMemberInfo(message, member)

    embedVar = discord.Embed(title="", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    embedVar.add_field(name="XP", value="{xp}/{max}".format(xp=str(memberInfo.xp), max=str(memberInfo.levelUpThreshold)), inline=False)
    embedVar.add_field(name="Level", value=str(memberInfo.level), inline=False)
    embedVar.add_field(name="Rank", value="#{rank}".format(rank=str(memberInfo.rank)), inline=False)
    await message.channel.send(embed=embedVar)

@client.command(aliases=['lvls'])
async def levels(message):
    members = loadMemberData(message.guild)
    sortedMembers = sorted(members.items(), key = lambda kv: kv[1].rank)

    embedVar = discord.Embed(title="Levels Leaderboard", description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.icon_url))

    for memberName, data in sortedMembers:
        embedVar.add_field(name="#{rank} - {memberName}".format(rank=str(data.rank), memberName=memberName), value="level {level}".format(level=str(data.level)), inline=False)

    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)

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
        await message.channel.send(badMemberPermsError)
    elif isinstance(error, commands.MissingRequiredArgument):
        await message.channel.send(badArgsError)
    elif isinstance(error, commands.CommandOnCooldown):
        if error.cooldown.per > 3600:
            cooldown = "**{cooldown}** hour".format(cooldown=str(int(error.cooldown.per/3600)))
        elif error.cooldown.per > 60:
            cooldown = "**{cooldown}** minute".format(cooldown=str(int(error.cooldown.per/60)))
        else:
            cooldown = "**{cooldown}** second".format(cooldown=str(int(error.cooldown.per)))
        if error.retry_after > 3600:
            retryAfter = "**{cooldown}** hours".format(cooldown=str(int(error.retry_after/3600)))
        elif int(error.retry_after) > 60:
            retryAfter = "**{cooldown}** minutes".format(cooldown=str(int(error.retry_after/60)))
        else:
            retryAfter = "**{cooldown}** seconds".format(cooldown=str(int(error.retry_after)))
        
        await message.channel.send("Woah slow down there man, that command has a {cooldown} cooldown. Try again in {retryAfter}".format(cooldown=str(cooldown), retryAfter=str(retryAfter)))
    elif isinstance(error, commands.BotMissingPermissions):
        await message.channel.send(badBotPermsError)
    elif isinstance(error, commands.CommandNotFound):
        await message.channel.send(nonExistentCommandError)

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
        pickle.dump(memberUnpickledData, file)

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
            lvlUpMsg = msg.replace('[mention]', "**{mention}**".format(mention=message.author.mention))
            # memberInfo = await getMemberInfo(message, message.author)
            # lvlUpMsg = lvlUpMsg.replace('[level]',  str(memberInfo.level))
            lvlUpMsg = lvlUpMsg.replace('[level]',  str(members[str(message.author)].level))
        channel = client.get_channel(setupData.lvlUpChannel)
        if channel == None:
            channel = message.channel
        if lvlUpMsg == "":
            lvlUpMsg = ("**{mention}** you leveled up! You are now level {level}".format(mention=message.author.mention, level=str(members[str(message.author)].level)))
        await channel.send(lvlUpMsg)

    setMemberRanks(message, message.guild)

    saveMemberData()
async def getMemberInfo(message, member):
    members = loadMemberData(message.guild)

    if not str(member) in members:
        members[str(member)] = MemberData(0, 0, 0, 0, defaultLevelUpThreshold)

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

client.run(key)