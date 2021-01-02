import discord
from discord.ext import commands
import asyncio
from common import tryLoadSavedDict, client, completedReaction, badSelfActionError, embedFooters, embedColour
import pickle
import typing
import random

dataFilename = "warnData.pickle"
unpickledData = tryLoadSavedDict(dataFilename)

#Commands
@client.command()
@commands.has_permissions(kick_members=True)
async def warn(message, member:discord.Member):
    if member != None:
        if member.id != message.author.id:
            await warnMember(member, message)
        else:
            await message.channel.send(badSelfActionError)
    else:
        await "{member} isn't a member bro".format(member=member)

@client.command()
async def warns(message, member:typing.Optional[discord.Member]):
    if member == None:
        member = message.author 
    memberData = loadMemberData(message.guild, member)

    embedVar = discord.Embed(title="{member}'s Warns".format(member=member.display_name), description="", color=embedColour)
    embedVar.set_footer(text=random.choice(embedFooters()), icon_url=discord.utils.get(message.guild.members, name="ZBot").avatar_url)
    embedVar.set_thumbnail(url=member.avatar_url)  
    embedVar.add_field(name=member.display_name, value=memberData, inline=False)

    await message.channel.send(embed=embedVar)

@client.command()
@commands.has_permissions(kick_members=True)
async def pardon(message, member:discord.Member):
    members = loadData(message.guild)

    if str(member.id) not in members:
        return

    members[str(member.id)] = 0
    await message.message.add_reaction(completedReaction)

    saveData(members)

@client.command()
@commands.has_permissions(kick_members=True)
async def pardonall(message):
    members = loadData(message.guild)

    for member in members:
        if members[member] == None:
            return
        members[member] = 0
    
    await message.message.add_reaction(completedReaction)

    saveData(members)

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
    if str(guild) in unpickledData:
        return unpickledData[str(guild)]
    else:
        unpickledData[str(guild)] = dict()
        return unpickledData[str(guild)]
def loadMemberData(guild, member):
    data = loadData(guild)
    memberid = str(member.id)
    if not memberid in data:
        data[memberid] = 0
    return data[memberid]
def saveData(data):
    with open(dataFilename, "wb") as file:
        pickle.dump(data, file)

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
    if member != None:
        if member.id != client.user.id:
            if member.id != message.guild.owner_id and member.id:
                members = loadData(message.guild)
                if not str(member.id) in members:
                    members[str(member.id)] = 0
                
                if str(member.id) in members:
                    members[str(member.id)] += 1
                else:
                    members[str(member.id)] = 1

                if members[str(member.id)] >= 3 and member.id != message.guild.owner_id:
                    try:
                        await member.send("Too many warns and you were kicked from the server! If you wish to rejoin maybe reread the rules")
                    except:
                        pass
                    members[str(member.id)] = 0
                    await member.kick(reason=None)
                else:
                    await message.channel.send("{member} you have been warned! **{warns}/3**".format(member=member.mention, warns=str(members[str(member.id)])))
                
                saveData(members)
            else:
                await message.channel.send("{member} is the owner, he wouldn't break his own rules so he is immune".format(member=member.mention))
        else:
            await message.channel.send("Bruh, I'm a bot. If you have a problem with me, take it up with the owner")
    else:
        await message.channel.send("**{member}** doesn't exist bro".format(member=member.mention))