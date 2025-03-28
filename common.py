import discord
from discord.ext import commands
import os
import pickle

prefixes = 'z ', 'Z '
client = commands.Bot(command_prefix=prefixes)
client.remove_command('help')
embedColour = 0x6495ED
def embedFooters():
    return ["Potato Gang is good, Pineapple Gang is evil",
        "Check out the creator's server at: https://discord.gg/9nP75tN",
        "Add ZBot to your server at: zacoons.com/code/zbot",
        "Made by Zacoons, feel free to join his server: https://discord.gg/9nP75tN",
        "Watching over {serverCount} servers for free".format(serverCount=str(len(client.guilds)))]
completedReaction = '✅'
errorReaction = '❌'

def tryLoadSavedDict(filename):
    if os.path.isfile(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)
    else:
        return dict()

def tryParseInt(input):
    try:
        return True, int(input)
    except ValueError:
        return False, input


#Command errors
badSelfActionError = "That's you dum dum"
nonExistentCommandError = "That's not a command, lol"
badMemberPermsError = "You don't have the perms to use that command :/"
badBotPermsError = "I don't have the perms to do that :/"
badArgsError = "You haven't provided the required amount of arguments, try looking at the help menu with `z help`"
nullItemError = "Lol nice try, you don't have that item"
notEnoughItemsError = "Smh, you don't have that many"
def nonExistentItemError(itemName):
    return "What the heck is a **{item}**".format(item=itemName)