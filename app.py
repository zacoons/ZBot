import discord
from discord.ext.commands import Bot
import random
import re
import os
from key import key
from jokes import jokes
import pyjokes
import pickle
import praw

client = Bot(command_prefix="Z ")
reddit = praw.Reddit(client_id='9B_9EgNR0RblQQ', client_secret='de1ze7ZZ9q7GajWI5ZYkXv451vQ', user_agent='ZBot_v1')
vars = dict()
pollUnpickledData = dict()
warnUnpickledData = dict()
warnDataFilename = "warnData.pickle"
pollDataFilename = "pollData.pickle"

class PollData:
    def __init__(self, msgID, pollUpRole, pollDownRole):
        self.msgID = msgID
        self.pollUpRole = pollUpRole
        self.pollDownRole = pollDownRole

def TryLoadSavedDict(filename):
    if os.path.isfile(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)
    else:
        return dict()

@client.event
async def on_ready():
    global pollUnpickledData
    global warnUnpickledData

    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='for Z help'))
    
    pollUnpickledData = TryLoadSavedDict(pollDataFilename)

    warnUnpickledData = TryLoadSavedDict(warnDataFilename)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #Checks for swear words
    msgSwearCheckTxt = message.content.lower()
    swearWords = ['shit', 'fuc', 'dick', 'cunt', 'bitch'] #These are all the swear words I know
    for word in swearWords:
        if re.search(word, msgSwearCheckTxt) != None:
            await warn(message, message.author)
            pass

    # for swearWord in swearWords:
    #     if swearWord in message.content.lower():
    #         await warn(message, message.author)

    #Help command
    if message.content.lower().startswith('z help'):
        embedVar = discord.Embed(title="Commands", description="", color=0x07a0c3)
        embedVar.add_field(name="z meme", value="Fetches a meme from reddit", inline=False)
        embedVar.add_field(name="z joke", value="Send you a normal joke", inline=False)
        embedVar.add_field(name="z codejoke", value="Sends you a programmer joke", inline=False)
        embedVar.add_field(name="z poll [ThumbsUpRole] [ThumbsDownRole] [Message Content]", value="Sets a poll, the variables you set determine the content of the poll", inline=False)
        embedVar.add_field(name="z warn [Username]", value="(Moderators only) Warns a member, once they recieve three warns and they're kicked", inline=False)
        embedVar.add_field(name="z clearwarns [Username]", value="(Moderators only) Clears a member's warns", inline=False)
        embedVar.add_field(name="z clearallwarns", value="(Moderators only) Clears everyone's warns", inline=False)
        await message.channel.send(embed=embedVar)
        # await message.channel.send('```Z meme``````Z joke``````Z codejoke``````Z smile``````Z poll [ThumbsUpRole] [ThumbsDownRole] [Message Content]``````(Moderators only) Z warn [Username]``````(Moderators only) Z clearwarns [Username]``````(Moderators only) Z clearallwarns```')

    #Joke command
    if message.content.lower().startswith('z joke'):
        await message.channel.send(random.choice(jokes))

    #Code joke command
    if message.content.lower().startswith('z codejoke'):
        await message.channel.send(pyjokes.get_joke())

    #Meme command
    if message.content.lower().startswith('z meme'):
        meme_submissions = reddit.subreddit('meme').hot()
        post_to_pick = random.randint(1, 25)
        for i in range(0, post_to_pick):
            submission = next(x for x in meme_submissions if not x.stickied)

        await message.channel.send(submission.url)

    #Poll command
    if message.content.lower().startswith('z poll'):
        if str(message.guild) in pollUnpickledData:
            serverPolls = pollUnpickledData[str(message.guild)]
        else:
            serverData = dict()
            pollUnpickledData[str(message.guild)] = serverData
            serverPolls = serverData

        bracketsContent = re.findall(r"\[([A-Za-z0-9_?.!' ]+)\]", message.content)

        if bracketsContent[0] == " " and bracketsContent[1] == " ":
                await message.channel.send("You gotta put in at least one role")
                return

        pollUpRoleName = None
        pollUpRole = None
        if bracketsContent[0] != " ":
            pollUpRoleName = bracketsContent[0]
            pollUpRole = discord.utils.get(message.guild.roles, name=pollUpRoleName)
            if pollUpRole == None: 
                await message.channel.send(pollUpRoleName + " isn't a role my dude")
                return
        
        pollDownRoleName = None
        pollDownRole = None
        if bracketsContent[1] != " ":
            pollDownRoleName = bracketsContent[1]
            pollDownRole = discord.utils.get(message.guild.roles, name=pollDownRoleName)
            if pollDownRole == None:
                await message.channel.send(pollDownRoleName + " isn't a role my dude")
                return

        embedVar = discord.Embed(title=bracketsContent[2], description="React with a thumbs up or thumbs down to vote", color=0x07a0c3)
        msg = await message.channel.send(embed=embedVar)
        serverPolls[str(msg.id)] = PollData(msg.id, pollUpRoleName, pollDownRoleName)
        
        with open(pollDataFilename, "wb") as file:
            pickle.dump(serverPolls, file)

    #Warn command
    if message.content.lower().startswith('z warn'):
        isMod = bool(hasModRole(message.author))

        if isMod:
            bracketsContent = re.findall(r"\[([A-Za-z0-9_' ]+)\]", message.content)
            member = message.guild.get_member_named(bracketsContent[0])
            if member != None:
                if member.id != message.author.id:
                    await warn(message, member)
                else:
                    await message.channel.send("That's you dumb dumb")
            else:
                await message.channel.send(str(member) + " isn't a member bro")
        else:
            await message.channel.send("You don't have permission to do that")

    #Clear warn (specific user) command
    if message.content.lower().startswith('z clearwarns'):
        isMod = bool(hasModRole(message.author))

        if isMod:
            bracketsContent = re.findall(r"\[([A-Za-z0-9_' ]+)\]", message.content)
            member = message.guild.get_member_named(bracketsContent[0])
            servers = warnUnpickledData

            if str(message.guild) in servers:
                members = servers[str(message.guild)]
            else:
                members = dict()
                servers[str(message.guild)] = members
            
            if servers[str(message.guild)] == None:
                return

            if members[str(member)] == None:
                return

            if member == None:
                await message.channel.send((str(member) + "isn't a member bro"))
                return

            members[str(member)] = 0
            await message.add_reaction('👍')
            # await message.channel.send(("Cleared " + member.name + "'s warns."))

            with open(warnDataFilename, "wb") as file:
                pickle.dump(warnUnpickledData, file)
        else:
            await message.channel.send("You don't have permission to do that.")

    #Clear everyone's warns command
    if message.content.lower().startswith('z clearallwarns'):
        isMod = bool(hasModRole(message.author))

        if isMod:
            servers = warnUnpickledData

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
                members[member] = 0
            
            await message.add_reaction('👍')
            # await message.channel.send("Everyone is now free of their warns.")

            with open(warnDataFilename, "wb") as file:
                pickle.dump(warnUnpickledData, file)
        else:
            await message.channel.send("You don't have permission to do that.")

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

async def warn(message, member):
    if member != None:
        if member.id != client.user.id:
            if member.id != message.guild.owner_id and member.id:
                servers = warnUnpickledData
                if str(message.guild) in servers:
                    members = servers[str(message.guild)]
                else:
                    members = dict()
                    servers[str(message.guild)] = members

                if not str(member) in members:
                    members[str(member)] = 0

                members[str(member)] += 1

                if members[str(member)] >= 3 and member.id != message.guild.owner_id:
                    try:
                        await member.send("Too many warns and you were kicked from the server! If you wish to rejoin maybe reread the rules")
                    except:
                        pass
                    members[str(member)] = 0
                    await member.kick(reason=None)
                else:
                    await message.channel.send(member.mention + ' you have been warned! ' + str(members[str(member)]) + "/3")
                
                with open(warnDataFilename, "wb") as file:
                    pickle.dump(warnUnpickledData, file)
            else:
                await message.channel.send(member.name + " is the owner, he wouldn't break his own rules so he is immune")
        else:
            await message.channel.send("Bruh, I'm a bot. If you have a problem with me, take it up with the owner")
    else:
        await message.channel.send(str(member) + " doesn't exist bro")

def hasModRole(author):
    for role in author.roles:
        if role.permissions.kick_members:
            return True
        else:
            return False

client.run(key)
