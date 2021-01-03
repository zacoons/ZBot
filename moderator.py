import discord
from discord.ext import commands
import asyncio
from common import tryLoadSavedDict, client, completedReaction, badSelfActionError, embedFooters, embedColour, errorReaction
import pickle
import typing
import random

dataFilename = "warnData.pickle"

class WarnData:
    def __init__(self, reason, warner):
        self.reason = reason
        self.warner = warner

#Commands
@client.command()
@commands.has_permissions(kick_members=True)
async def warn(message, member:discord.Member):
    if member != None:
        if member.id != message.author.id:
            reason = message.message.content[30:]
            await warnMember(member, message, reason)
        else:
            await message.channel.send(badSelfActionError)
    else:
        await "{member} isn't a member bro".format(member=member)

@client.command()
async def warns(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author 
    data = loadData(message.guild)

    embedVar = discord.Embed(title="{member}'s Warns".format(member=member.display_name), description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters()), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)

    if str(member.id) not in data or len(data[str(member.id)]) == 0:
        await message.channel.send("He doesn't have any warns")
        message.message.add_reaction(errorReaction)
        return

    for warnNumber in data[str(member.id)]:
        if data[str(member.id)][warnNumber].warner != None:
            warner = await message.guild.fetch_member(data[str(member.id)][warnNumber].warner)
        reason = data[str(member.id)][warnNumber].reason
        if reason == "":
            reason = "None"
        embedVar.add_field(name="Reason: {reason}".format(reason=reason), value="Warned by: {warner}".format(warner=warner.display_name), inline=False)

    await message.channel.send(embed=embedVar)

@client.command()
@commands.has_permissions(kick_members=True)
async def pardon(message, member:discord.Member):
    members = loadData(message.guild)

    if str(member.id) not in members:
        await message.channel.send("He hasn't been warned yet")
        return

    members[str(member.id)].clear()
    await message.message.add_reaction(completedReaction)

    saveData()

@client.command()
@commands.has_permissions(kick_members=True)
async def pardonall(message):
    members = loadData(message.guild)

    for member in members:
        members[str(member.id)].clear()
    
    await message.message.add_reaction(completedReaction)

    saveData()

@client.command()
@commands.has_permissions(kick_members=True)
async def mute(message, member:discord.Member, time:typing.Optional[int]):
    if member == client.user:
        await message.channel.send("Why are you trying to mute me")
        return
    if member == message.author:
        await message.channel.send(badSelfActionError)
        return
    
    if time == None or time == 0:
        await message.channel.send("{member} was muted indefinitely".format(member=member.mention))
    else:
        await message.channel.send("{member} was muted for **{time}** seconds".format(member=member.mention, time=str(time)))

    await muteMember(member, time, message.channel)

    await message.message.add_reaction(completedReaction)

@client.command()
@commands.has_permissions(kick_members=True)
async def unmute(message, member:discord.Member):
    mutedRole = discord.utils.get(message.guild.roles, name="Muted")

    if not mutedRole in member.roles:
        await message.channel.send("He's not muted tho")
        return
    
    await member.remove_roles(mutedRole)

    await message.channel.send("{member} was unmuted".format(member=member.mention))
    await message.message.add_reaction(completedReaction)


#Functions
def loadData(guild):
    if str(guild.id) not in unpickledData:
        unpickledData[str(guild.id)] = dict()
    return unpickledData[str(guild.id)]
def saveData():
    with open(dataFilename, "wb") as file:
        pickle.dump(unpickledData, file)

async def muteMember(member, muteTime, channel):
    mutedRole = discord.utils.get(channel.guild.roles, name="Muted")

    if mutedRole == None:
        mutedRole = await channel.guild.create_role(name="Muted")

        for channel in channel.guild.channels:
            perms = channel.overwrites_for(mutedRole)
            perms.view_channel = False
            perms.send_messages = False
            await channel.set_permissions(mutedRole, overwrite=perms)

    await member.add_roles(mutedRole, reason=None)

    if muteTime != None or muteTime == 0:
        await asyncio.sleep(muteTime)
        await member.remove_roles(mutedRole)

async def warnMember(member, message, reason):
    if member == None:
        await message.channel.send("**{member}** doesn't exist bro".format(member=member.mention))
        await message.message.add_reaction(errorReaction)
        return
    
    if member.id == client.user.id:
        await message.channel.send("Bruh, I'm a bot. If you have a problem with me, take it up with my creator: Zacoons#2407")
        await message.message.add_reaction(errorReaction)
        return

    if member.id == message.guild.owner_id:
        await message.channel.send("{member} is the owner, he wouldn't break his own rules so he is immune".format(member=member.mention))
        await message.message.add_reaction(errorReaction)
        return
    
    if member.id == message.author.id:
        await message.channel.send(badSelfActionError)
        message.message.add_reaction(errorReaction)
        return

    members = loadData(message.guild)
    if str(member.id) not in members:
        members[str(member.id)] = dict()
    memberWarns = members[str(member.id)]

    memberWarns[str(len(memberWarns) + 1)] = WarnData(reason, str(message.author.id))

    if len(memberWarns) >= 3 and member.id != message.guild.owner_id:
        try:
            await member.send("Too many warns and you were kicked from the server! If you wish to rejoin maybe read the rules this time")
        except:
            pass
        memberWarns.clear()
        await member.kick(reason="3/3 warns")
    else:
        await message.channel.send("{member} you have been warned! **{warns}/3** {reason}".format(member=member.mention, warns=str(len(memberWarns)), reason=reason))
    
    saveData()

unpickledData = tryLoadSavedDict(dataFilename)