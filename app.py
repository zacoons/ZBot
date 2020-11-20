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

prefixes = 'z ', 'Z ', 'z', 'Z'
client = commands.Bot(command_prefix=prefixes)
client.remove_command('help')
reddit = praw.Reddit(client_id='9B_9EgNR0RblQQ', client_secret='de1ze7ZZ9q7GajWI5ZYkXv451vQ', user_agent='ZBot_v1')
pollUnpickledData = dict()
memberUnpickledData = dict()
setupUnpickledData = dict()
pollDataFilename = "pollData.pickle"
memberDataFilename = "memberData.pickle"
setupDataFilename = "setupData.pickle"
defaultLevelUpThreshold = 20

class PollData:
    def __init__(self, msgID, pollUpRole, pollDownRole):
        self.msgID = msgID
        self.pollUpRole = pollUpRole
        self.pollDownRole = pollDownRole

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
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='for Z help'))

    pollUnpickledData = TryLoadSavedDict(pollDataFilename)
    memberUnpickledData = TryLoadSavedDict(memberDataFilename)
    setupUnpickledData = TryLoadSavedDict(setupDataFilename)

@client.command()
async def help(message):
    embedVar = discord.Embed(title="ZBot Help", description="", color=0x6495ED)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
    embedVar.add_field(name="Setup", value="`z helpsetup`")
    embedVar.add_field(name="Levels", value="`z helplvls`")
    embedVar.add_field(name="Moderator", value="`z helpmod`")
    embedVar.add_field(name="Other", value="`z helpmisc`")
    await message.channel.send(embed=embedVar)

@client.command()
async def helpsetup(message):
    embedVar = discord.Embed(title="ZBot Setup Commands", description="", color=0x6495ED)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
    embedVar.add_field(name="`z setlvlupchannel`", value="Sets a specific channel for the level up message", inline=False)
    embedVar.add_field(name="`z setlvlupmsg`", value="Syntax example: z setlvlupmsg `Nice job [mention]! You're now level [level]!`", inline=False)
    embedVar.add_field(name="`z setwelcomechannel`", value="Sets a specific channel for the welcome message", inline=False)
    embedVar.add_field(name="`z setwelcomemsg`", value="Syntax example: z setwelcomemsg `Welcome to the server [mention]!`", inline=False)
    await message.channel.send(embed=embedVar)

@client.command()
async def helpmod(message):
    embedVar = discord.Embed(title="ZBot Moderator Commands", description="", color=0x6495ED)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
    embedVar.add_field(name="`z warn [Username]`", value="(Moderators only) Warns a member, once they recieve three warns and they're kicked", inline=False)
    embedVar.add_field(name="`z pardon [Username]`", value="(Moderators only) Clears a member's warns", inline=False)
    embedVar.add_field(name="`z pardonall`", value="(Moderators only) Clears everyone's warns", inline=False)
    embedVar.add_field(name="`z mute [time](Seconds)`", value="(Moderators only) Mutes a member for a number of seconds", inline=False)
    await message.channel.send(embed=embedVar)

@client.command()
async def helpmisc(message):
    embedVar = discord.Embed(title="ZBot Other Commands", description="", color=0x6495ED)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)  
    embedVar.add_field(name="`z meme`", value="Fetches a meme from reddit", inline=False)
    embedVar.add_field(name="`z joke`", value="Send you a normal joke", inline=False)
    embedVar.add_field(name="`z conversationstarter`", value="(AKA convostart) Sends you a conversation starter", inline=False)
    embedVar.add_field(name="`z poll [ThumbsUpRole] [ThumbsDownRole] [Message Content]`", value="Sets a poll, the variables you set determine the content of the poll", inline=False)
    await message.channel.send(embed=embedVar)

@client.command()
async def helplvls(message):
    embedVar = discord.Embed(title="ZBot Other Commands", description="", color=0x6495ED)
    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)   
    embedVar.add_field(name="`z level [Username](Optional)`", value="(AKA lvl) Tells you your/someone else's level and xp", inline=False)
    embedVar.add_field(name="`z levels`", value="(AKA lvls) Gives you the rank of all ranked members", inline=False)
    embedVar.add_field(name="`z clearlevels [Username]`", value="(AKA clvls) (Moderators only) Clears a member's levels and xp", inline=False)
    embedVar.add_field(name="`z purgelevels`", value="(AKA plvls) (Moderators only) Clears everyone's levels and xp", inline=False)
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

    embedVar = discord.Embed(title=content, color=0x6495ED)
    embedVar.set_thumbnail(url="https://i.imgur.com/FZKHNYE.png")
    msg = await message.channel.send(embed=embedVar)
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')
    serverPolls[str(msg.id)] = PollData(msg.id, pollUpRoleName, pollDownRoleName)
    
    with open(pollDataFilename, "wb") as file:
        pickle.dump(serverPolls, file)

#Setup
@client.command()
@commands.has_permissions(kick_members=True)
async def setlvlupchannel(message):
    setLevelUpChannel(message.guild, message.channel)

    await message.message.add_reaction('👍')

@client.command()
@commands.has_permissions(kick_members=True)
async def setlvlupmsg(message, msg:str):
    setLevelUpMessage(message.guild, msg)

    await message.message.add_reaction('👍')

@client.command()
@commands.has_permissions(kick_members=True)
async def setwelcomechannel(message):
    setWelcomeChannel(message.guild, message.channel)

    await message.message.add_reaction('👍')

@client.command()
@commands.has_permissions(kick_members=True)
async def setwelcomemsg(message, msg:str):
    setWelcomeMessage(message.guild, msg)

    await message.message.add_reaction('👍')

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
    servers = memberUnpickledData

    if str(message.guild) in servers:
        members = servers[str(message.guild)]
    else:
        members = dict()
        servers[str(message.guild)] = members
    
    if servers[str(message.guild)] == None:
        return

    if members[str(member)] == None:
        return

    members[str(member)].warns = 0
    await message.message.add_reaction('👍')

    with open(memberDataFilename, "wb") as file:
        pickle.dump(memberUnpickledData, file)

@client.command()
@commands.has_permissions(kick_members=True)
async def pardonall(message):
    servers = memberUnpickledData

    if str(message.guild) in servers:
        members = servers[str(message.guild)]
    else:
        members = dict()
        servers[str(message.guild)] = members
    
    if servers[str(message.guild)] == None:
        return

    for member in members:
        if members[member] == None:
            return
        members[member].warns = 0
    
    await message.message.add_reaction('👍')

    with open(memberDataFilename, "wb") as file:
        pickle.dump(memberUnpickledData, file)

@client.command()
@commands.has_permissions(kick_members=True)
async def mute(message, member:discord.Member, time:int):
    if member == client.user:
        await message.channel.send("Why are you trying to mute me")
        return

    await muteMember(message.guild, member, time)

    await message.message.add_reaction('👍')

#Lvls
@client.command(aliases=['lvl'])
async def level(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author

    memberInfo = await getMemberLevel(message, member)

    embedVar = discord.Embed(title="", description="", color=0x6495ED)
    embedVar.set_thumbnail(url=member.avatar_url)  
    embedVar.add_field(name="Level", value=str(memberInfo.level), inline=False)
    embedVar.add_field(name="XP", value=str(int(memberInfo.xp)), inline=False)
    embedVar.add_field(name="Rank", value="#" + str(memberInfo.rank), inline=False)
    await message.channel.send(embed=embedVar)

@client.command(aliases=['lvls'])
async def levels(message):
    members = populateMembersDict(message)
    sortedMembers = sorted(members.items(), key = lambda kv: kv[1].rank)

    embedVar = discord.Embed(title="Leaderboard", description="", color=0x6495ED)

    for memberName, data in sortedMembers:
        embedVar.add_field(name='#'+str(data.rank)+' - '+memberName, value='level '+str(data.level), inline=False)

    embedVar.set_thumbnail(url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)

    await message.channel.send(embed=embedVar)

@client.command(aliases=['clvls'])
@commands.has_permissions(kick_members=True)
async def clearlevels(message, member:discord.Member):
    if member == None:
        await message.channel.send((str(member) + " isn't a member bro"))
        return

    clearLevels(message, member)
    await message.message.add_reaction('👍')

    with open(memberDataFilename, "wb") as file:
        pickle.dump(memberUnpickledData, file)

@client.command(aliases=['plvls'])
@commands.has_permissions(kick_members=True)
async def purgelevels(message):
    servers = memberUnpickledData

    if str(message.guild) in servers:
        members = servers[str(message.guild)]
    else:
        members = dict()
        servers[str(message.guild)] = members
    
    if servers[str(message.guild)] == None:
        return

    for member in members:
        if members[str(member)] == None:
            return
        else:
            clearLevels(message, member)
    
    await message.message.add_reaction('👍')

    with open(memberDataFilename, "wb") as file:
        pickle.dump(memberUnpickledData, file)

@client.event
async def on_member_join(member):
    setupData = loadSetupData(member.guild)
    welcomeMsg = setupData.welcomeMsg.replace('[mention]', member.mention)
    channel = client.get_channel(setupData.welcomeChannel)
    
    if channel == None or welcomeMsg == "":
        return

    await channel.send(welcomeMsg)

@client.event
async def on_message(message):
    modRole = discord.utils.get(message.guild.roles, name="Moderator")
    if message.content.lower().startswith('!d bump'):
        await asyncio.sleep(7200)
        await message.channel.send(modRole.mention + ' pls type the command `!d bump`')

    if message.author == client.user:
        return
    
    await giveMemberXP(1, message)

    #Checks for swear words
    # msgSwearCheckTxt = message.content.lower()
    # swearWords = ['shit', 'fuck', 'dick', 'cunt', 'bitch', 'penis', 'vagina'] #These are all the swear words I know
    # for word in swearWords:
    #     if re.search(word, msgSwearCheckTxt) != None:
    #         # await warnMember(message, message.author)
    #         await message.delete()
    #         await muteMember(message.guild, message.author, 60)
    #         return

    await client.process_commands(message)

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

async def assignRole(role, user):
    await user.add_roles(role, reason=None, atomic=False)
async def removeRole(role, user):
    await user.remove_roles(role, reason=None, atomic=False)

async def warnMember(message, member):
    if member != None:
        if member.id != client.user.id:
            if member.id != message.guild.owner_id and member.id:
                servers = memberUnpickledData
                if str(message.guild) in servers:
                    members = servers[str(message.guild)]
                else:
                    members = dict()
                    servers[str(message.guild)] = members

                if not str(member) in members:
                    members[str(member)] = MemberData(0, 0, 0, 0, defaultLevelUpThreshold)

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
                
                with open(memberDataFilename, "wb") as file:
                    pickle.dump(memberUnpickledData, file)
            else:
                await message.channel.send(member.name + " is the owner, he wouldn't break his own rules so he is immune")
        else:
            await message.channel.send("Bruh, I'm a bot. If you have a problem with me, take it up with the owner")
    else:
        await message.channel.send(str(member) + " doesn't exist bro")

async def muteMember(guild, member, muteTime):
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False)

    await member.add_roles(mutedRole, reason=None)
    await member.send("RIP, you were muted for " + str(muteTime) + " seconds :/")

    await asyncio.sleep(muteTime)

    await member.remove_roles(mutedRole)

def populateMembersDict(message):
    if str(message.guild) in memberUnpickledData:
        return memberUnpickledData[str(message.guild)]
    else:
        memberUnpickledData[str(message.guild)] = dict()
        return memberUnpickledData[str(message.guild)]
async def giveMemberXP(xpAmount, message):
    if message.author.bot:
        return
    
    members = populateMembersDict(message)

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
            lvlUpMsg = msg.replace('[mention]', message.author.mention)
            memberInfo = await getMemberLevel(message, message.author)
            lvlUpMsg = msg.replace('[level]',  str(memberInfo.level))
        channel = client.get_channel(setupData.lvlUpChannel)
        if channel == None:
            channel = message.channel
        if lvlUpMsg == None:
            lvlUpMsg = (message.author.mention + " you leveled up! You are now level " + str(members[str(message.author)].level))
        await channel.send(lvlUpMsg)

    setMemberRanks(message, message.guild)

    with open(memberDataFilename, "wb") as file:
        pickle.dump(memberUnpickledData, file)
async def getMemberLevel(message, member):
    members = populateMembersDict(message)

    if not str(member) in members:
        members[str(member)] = MemberData(0, 0, 0, 0, defaultLevelUpThreshold)

    if message.guild.get_member_named(str(member)) == None:
        await message.channel.send("That's not a member bro")
        return None

    setMemberRanks(message, message.guild)

    return members[str(member)]
    
def setMemberRanks(message, guild):
    members = populateMembersDict(message)
    
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
    
    with open(memberDataFilename, "wb") as file:
        pickle.dump(memberUnpickledData, file)
def clearLevels(message, member):
    members = populateMembersDict(message)

    members[str(member)].rank = 0
    members[str(member)].xp = 0    
    members[str(member)].level = 0
    members[str(member)].levelUpThreshold = defaultLevelUpThreshold

    with open(memberDataFilename, "wb") as file:
        pickle.dump(memberUnpickledData, file)

#Setup data functions
def saveSetupData(guild):
    with open(setupDataFilename, "wb") as file:
        pickle.dump(setupUnpickledData, file)
def loadSetupData(guild):
    if not str(guild) in setupUnpickledData:
        setupUnpickledData[str(guild)] = SetupData(None, "", None, "")

    return setupUnpickledData[str(guild)]

def setLevelUpChannel(guild, channel):
    setupData = loadSetupData(guild)
    setupData.lvlUpChannel = channel.id
    saveSetupData(guild)
def setLevelUpMessage(guild, msg):
    setupData = loadSetupData(guild)
    setupData.lvlUpMsg = msg
    saveSetupData(guild)

def setWelcomeChannel(guild, channel):
    setupData = loadSetupData(guild)
    setupData.welcomeChannel = channel.id
    saveSetupData(guild)
def setWelcomeMessage(guild, msg):
    setupData = loadSetupData(guild)
    setupData.welcomeMsg = msg
    saveSetupData(guild)

client.run(key)