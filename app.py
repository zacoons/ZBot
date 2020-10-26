import discord
import random
import re
import os
from key import key
import pickle

client = discord.Client()
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

@client.event
async def on_ready():
    global pollUnpickledData
    global warnUnpickledData
    print('We have logged in as {0.user}'.format(client))
    
    if os.path.isfile(pollDataFilename):
        with open(pollDataFilename, "rb") as file:
            pollUnpickledData = pickle.load(file)
    else:
        pollUnpickledData = dict()

    if os.path.isfile(warnDataFilename):
        with open(warnDataFilename, "rb") as file:
            warnUnpickledData = pickle.load(file)
    else:
        warnUnpickledData = dict()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('Z help'):
        await message.channel.send('```Z joke``````Z smile``````Z poll [ThumbsUpRole] [ThumbsDownRole] [Message Content]``````(Moderators only) Z warn [Username]``````(Moderators only) Z clearwarns [Username]``````(Moderators only) Z clearallwarns```')

    if message.content.startswith('Z joke'):
        responses = ['This is funny so laugh.', 
        'My dog used to chase people on a bike a lot. It got so bad, finally I had to take his bike away.',
        'I’m so good at sleeping. I can do it with my eyes closed.',
        'When you look really closely, all mirrors look like eyeballs.',
        'I couldn’t figure out why the baseball kept getting larger. Then it hit me.',
        'A blind man walks into a bar. And a table. And a chair.',
        'What did one hat say to the other? You stay here. I’ll go on ahead.']
        await message.channel.send(random.choice(responses))

    if message.content.startswith('Z smile'):
        await message.channel.send('########################')
        await message.channel.send('#######OO######OO#######')
        await message.channel.send('#######OO######OO#######')
        await message.channel.send('########################')
        await message.channel.send('########################')
        await message.channel.send('#######OO######OO#######')
        await message.channel.send('#######OO######OO#######')
        await message.channel.send('#########OOOOOO########')
        await message.channel.send('#########OOOOOO########')
        await message.channel.send('########################')

    if message.content.startswith('Z poll'):
        if str(message.guild) in pollUnpickledData:
            serverPolls = pollUnpickledData[str(message.guild)]
        else:
            serverData = dict()
            pollUnpickledData[str(message.guild)] = serverData
            serverPolls = serverData

        await message.channel.purge(limit=1)
        
        bracketsContent = re.findall(r"\[([A-Za-z0-9_ ]+)\]", message.content)

        pollUpRoleName = bracketsContent[0]
        pollUpRole = discord.utils.get(message.guild.roles, name=pollUpRoleName)
        if pollUpRole == None: 
            await message.channel.send(pollUpRoleName + " isn't a role my dude")
            return
            
        pollDownRoleName = bracketsContent[1]
        pollDownRole = discord.utils.get(message.guild.roles, name=pollDownRoleName)
        if pollDownRole == None:
            await message.channel.send(pollDownRoleName + " isn't a role my dude")
            return

        cntnt = bracketsContent[2] + ' ```React with a thumbs up or a thumbs down to vote!```'
        msg = await message.channel.send(cntnt)
        serverPolls[str(msg.id)] = PollData(msg.id, pollUpRoleName, pollDownRoleName)
        
        with open(pollDataFilename, "wb") as file:
            pickle.dump(serverPolls, file)

    if message.content.startswith('Z warn'):
        modRole = discord.utils.get(message.author.guild.roles, name="Moderator")
        if modRole in message.author.roles:
            bracketsContent = re.findall(r"\[([A-Za-z0-9_' ]+)\]", message.content)
            member = message.guild.get_member_named(bracketsContent[0])
            
            if member != None:
                if member.id != client.user.id:
                    if member.id != message.guild.owner_id and member.id:
                        if member.id != message.author.id:
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
                                    await member.send("Too many warns and you were kicked from the server! If you wish to rejoin maybe reread the rules.")
                                except:
                                    pass
                                members[str(member)] = 0
                                await member.kick(reason=None)
                            else:
                                await message.channel.send(member.mention + ' you have been warned! ' + str(members[str(member)]) + "/3")
                            
                            with open(warnDataFilename, "wb") as file:
                                pickle.dump(warnUnpickledData, file)
                        else:
                            await message.channel.send("That's you dumb dumb!")
                    else:
                        await message.channel.send(member.name + " is the owner, he wouldn't break his own rules so he is immune!")
                else:
                    await message.channel.send("Bruh, I'm a bot. If you have a problem with me, take it up with the owner.")
            else:
                await message.channel.send(member.name + " doesn't exist bro.")
        else:
            await message.channel.send("You don't have permission to do that.")

    if message.content.startswith('Z clearwarns'):
        modRole = discord.utils.get(message.author.guild.roles, name="Moderator")
        if modRole in message.author.roles:
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
                await message.channel.send((str(member) + "isn't a member exist bro."))
                return

            members[str(member)] = 0
            await message.channel.send(("Cleared " + member.name + "'s warns."))

            with open(warnDataFilename, "wb") as file:
                pickle.dump(warnUnpickledData, file)
        else:
            await message.channel.send("You don't have permission to do that.")

    if message.content.startswith('Z clearallwarns'):
        modRole = discord.utils.get(message.author.guild.roles, name="Moderator")
        if modRole in message.author.roles:
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
            
            await message.channel.send("Everyone is now free of their warns.")

            with open(warnDataFilename, "wb") as file:
                pickle.dump(warnUnpickledData, file)
        else:
            await message.channel.send("You don't have permission to do that.")

@client.event
async def on_reaction_add(reaction, user):
    pollMsg = pollUnpickledData[str(reaction.message.guild)][str(reaction.message.id)]
    pollUpRole = discord.utils.get(reaction.message.guild.roles, name=pollMsg.pollUpRole)
    pollDownRole = discord.utils.get(reaction.message.guild.roles, name=pollMsg.pollDownRole)
    if reaction.message.id == pollMsg.msgID:
        if reaction.emoji == '👍':
            await assignRole(pollUpRole, user)
        if reaction.emoji == '👎':
            await assignRole(pollDownRole, user)

@client.event
async def on_reaction_remove(reaction, user):
    pollMsg = pollUnpickledData[str(reaction.message.guild)][str(reaction.message.id)]
    pollUpRole = discord.utils.get(reaction.message.guild.roles, name=pollMsg.pollUpRole)
    pollDownRole = discord.utils.get(reaction.message.guild.roles, name=pollMsg.pollDownRole)
    if reaction.message.id == pollMsg.msgID:
        if reaction.emoji == '👍':
            await removeRole(pollUpRole, user)
        if reaction.emoji == '👎':
            await removeRole(pollDownRole, user)
    # if reaction.emoji == '👍':
    #     await user.remove_roles(discord.utils.get(user.guild.roles, name='Puppy lover'), reason=None, atomic=False)
    # if reaction.emoji == '👎':
    #     await user.remove_roles(discord.utils.get(user.guild.roles, name='Cat lover'), reason=None, atomic=False)

async def assignRole(role, user):
    await user.add_roles(role, reason=None, atomic=False)
async def removeRole(role, user):
    await user.remove_roles(role, reason=None, atomic=False)

client.run(key)
