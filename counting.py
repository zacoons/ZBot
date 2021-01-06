import discord
from discord.ext import commands
import pickle
from common import tryLoadSavedDict, client, embedColour, embedFooters, completedReaction, errorReaction, tryParseInt
import typing
import asyncio

class CountingData():
    def __init__(self, channel, previousAuthor, number):
        self.channel = channel
        self.previousAuthor = previousAuthor
        self.number = number

dataFilename = "countingData.pickle"
global unpickledData


#Commands
@client.command()
@commands.has_permissions(kick_members=True)
async def setcountingchannel(message, channel:typing.Optional[discord.TextChannel]):
    if channel == None:
        channel = message.channel
    
    data = loadData(message.guild)
    data.channel = str(channel.id)
    saveData()

    await message.message.add_reaction(completedReaction)


#Events
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    data = loadData(message.guild)
    
    if str(message.channel.id) == data.channel:
        isInt, number = tryParseInt(message.content)
        if isInt:
            if str(message.author.id) == data.previousAuthor:
                await message.delete()
                msg = await message.channel.send("One at a time boi")
                asyncio.sleep(3)
                await msg.delete()
                return

            if number == data.number + 1:
                data.number += 1
                data.previousAuthor = str(message.author.id)
                if number == 50:
                    await message.channel.send("Keep, going! You're on fire ;)")
                    await message.add_reaction('🔥')
                elif number == 21:
                    await message.channel.send("What's 9 plus 10")
                    await message.add_reaction('😏')
                elif number == 69 or number == 420:
                    await message.channel.send("Hehe")
                    await message.add_reaction('😏')
                elif number == 100:
                    await message.channel.send("Wow you guys reached **100**, nicely done B)")
                    await message.add_reaction('🎉')
                elif number == 250:
                    await message.channel.send("Damn you guys are amazing! Keep it up")
                    await message.add_reaction('🎊')
                elif number == 500:
                    await message.channel.send(":sparkles: Holy moly you guys are incredible! You deserve a gold star :sparkles:")
                    await message.add_reaction('🌟')
                elif number == 1000:
                    await message.channel.send("H- How did you guys even get here")
                    await message.add_reaction('🏆')
                else:
                    await message.add_reaction(completedReaction)
            else:
                await message.channel.send("Wrong number, now it's back to **0** ;-;")
                await message.add_reaction(errorReaction)
                data.previousAuthor = None
                data.number = 0
        saveData()

    await client.process_commands(message)


#Functions
def saveData():
    with open(dataFilename, "wb") as file:
        pickle.dump(unpickledData, file)

def loadData(guild):
    if not str(guild.id) in unpickledData:
        unpickledData[str(guild.id)] = CountingData(None, None, 1)

    return unpickledData[str(guild.id)]


unpickledData = tryLoadSavedDict(dataFilename)