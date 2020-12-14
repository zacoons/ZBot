import discord
from discord.ext import commands
import os
import pickle

prefixes = 'z ', 'Z '
client = commands.Bot(command_prefix=prefixes)
client.remove_command('help')
embedColour = 0x6495ED
embedFooters = ["Potato Gang is good, Pineapple Gang is evil",
    "Check out the creator's discord at: https://discord.gg/9nP75tN",
    "Add ZBot to your server at: zacoons.com/code/zbot",
    "Made by Zacoons, feel free to join the help server: https://discord.gg/9nP75tN",
    "Watching over "+str(len(client.guilds))+" servers for free"]

def TryLoadSavedDict(filename):
    if os.path.isfile(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)
    else:
        return dict()