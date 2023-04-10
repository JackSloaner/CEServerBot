import os
from replit import db

from functions import *
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())

@bot.event
async def on_ready():
  print("ready")


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if (not discord.utils.get(message.author.roles, name="Moderator")) and (
      not message.author.guild_permissions.administrator):
    return


#Moderator commands

  if message.content.startswith('$roleMenu'):
    await roleMenu(message)

  if message.content.startswith('$clearChannel'): 
    Author = message.author
    curChannel = message.channel
    msgs = []
    async for message in curChannel.history(limit=200):
      msgs.append(message)
    await curChannel.delete_messages(msgs)
    logChannel = discord.utils.get(message.guild.text_channels,
                                 name="server-logs")
    await logChannel.send("`{}` has cleared the `#{}` channel".format(
    Author, curChannel))

TOKEN = os.environ['TOKEN']

bot.run(TOKEN)
