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
  if (not discord.utils.get(message.author.roles, name="Moderator")) and (not message.author.guild_permissions.administrator):
    return
  curChannel = message.channel

#Moderator commands
  
  if message.content.startswith('$roleMenu'):
    await roleMenu(message)

TOKEN = os.environ['TOKEN']

bot.run(TOKEN)
