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

  if message.content.startswith('$roleMenu') and message.channel.name == "roles":
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
    if logChannel:
      await logChannel.send("`{}` has cleared the `#{}` channel".format(
        Author, curChannel))

@bot.event
async def on_raw_reaction_add(payload):
  guild = bot.get_guild(payload.guild_id)
  user = discord.utils.get(guild.members, id=payload.user_id)
  channels = guild.channels
  roleChannel = discord.utils.get(channels, name="roles")
  
  channel = discord.utils.get(channels, id = payload.channel_id)
  if channel != roleChannel:
    return
  reactionList = db["reactions"]
       
  for x in reactionList:
    reactedMessage = await channel.fetch_message(payload.message_id)
    message = await channel.fetch_message(x[3])
    reactionEmoji = str(payload.emoji)
    if x[1] == reactionEmoji and message == reactedMessage:
      await user.add_roles(discord.utils.get(message.guild.roles, name=x[0]))

TOKEN = os.environ['TOKEN']

@bot.event
async def on_raw_reaction_remove(payload):
  guild = bot.get_guild(payload.guild_id)
  user = discord.utils.get(guild.members, id=payload.user_id)
  channels = guild.channels
  channel = discord.utils.get(channels, id=payload.channel_id)
  roleChannel = discord.utils.get(channels, name="roles")
  
  
  if channel != roleChannel:
    return
  reactionList = db["reactions"]
  
  for x in reactionList:
    message = await channel.fetch_message(x[3])
    reactionEmoji = str(payload.emoji)
    reactedMessage = await channel.fetch_message(payload.message_id)
    
    if x[1] == reactionEmoji and message == reactedMessage:
      await user.remove_roles(discord.utils.get(message.guild.roles, name=x[0]))
      
bot.run(TOKEN)
