import discord
from discord.ext import commands
from common import client, errorReaction, completedReaction

#Commands
@client.command(aliases=["join"])
async def play(message):
    channel = message.message.author.voice.channel
    voiceClient = discord.utils.get(client.voice_clients, guild=message.guild)

    if channel == None:
        await message.channel.send("You're not currently in a voice channel")
        await message.message.add_reaction(errorReaction)
        return
    
    if voiceClient and voiceClient.is_connected():
        await voiceClient.move_to(channel)
    else:
        await channel.connect()

    await message.message.add_reaction(completedReaction)

    search = message.message.content[6:]
    if search == "":
        return

@client.command(aliases=["leave", "disconnect"])
async def stop(message):
    voiceClient = discord.utils.get(client.voice_clients, guild=message.guild)

    if voiceClient == None:
        await message.channel.send("I'm not currently in a voice channel")
        await message.message.add_reaction(errorReaction)
        return

    await voiceClient.disconnect()
    # channel.disconnect()

    await message.message.add_reaction(completedReaction)