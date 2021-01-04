import discord
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
                await giveOneAtATimeError(message.channel)
                return

            if number == data.number + 1:
                data.number += 1
                data.previousAuthor = str(message.author.id)
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

async def giveOneAtATimeError(channel):
    errorMsg = await channel.send("One at a time boi, wait for the next person to go")
    await asyncio.sleep(5)
    await errorMsg.delete()

unpickledData = tryLoadSavedDict(dataFilename)