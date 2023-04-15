from keepAlive import keep_alive

import os
from replit import db

import requests
from bs4 import BeautifulSoup
from functions import *
import discord
from discord.ext import commands
from discord import Webhook
from discord.embeds import Embed

import schedule

import asyncio

bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())



@bot.event
async def on_ready():
  print("ready")
  ID = os.environ["SERVER_ID"]
  guild = bot.get_guild(int(ID))
  
  webhook = discord.utils.get(await guild.webhooks(), id=db["webhook"])
  
  async def updateNews():
    while True:
      await updateNewsChannel(webhook)
      await asyncio.sleep(300)
    
  bot.loop.create_task(updateNews())

@bot.event
async def on_message(message):

  if message.author == bot.user:
    return
  if isinstance(message.author, discord.User):
    return

#User commands
  
  if message.content.startswith("$moderate"): 
    link = "https://docs.google.com/forms/d/e/1FAIpQLSc1gdhWAYWiCxoPXgK9-k-HydFy7iIqif0-a_yvi95H1HCBrQ/viewform?usp=sf_link"
    msg = "Thank you for your interest in moderation! Below is a link to a Moderator application form. \n" + link
    await message.channel.send(msg)
    logChannel = discord.utils.get(message.guild.text_channels, name="server-logs")
    serverOwner = discord.utils.get(message.guild.members, name="Jack_Sloaner")
    await logChannel.send("`{}` has used $moderate! Look out for new form submission! {}".format(message.author, serverOwner.mention))

  if message.content.startswith('$suggest'):
    author = message.author
    msg = "`{}`: {}".format(author, message.content[8:])
    suggestionChannel = discord.utils.get(message.guild.channels, name = 'suggestions')
    await suggestionChannel.send(msg)
    await message.channel.send("**Your suggestion has been sent to a moderator channel. Thank you for your input!**")
    logChannel = discord.utils.get(message.guild.text_channels, name="server-logs")
    serverOwner = discord.utils.get(message.guild.members, name="Jack_Sloaner")
    await logChannel.send("`{}` has used $suggest! Take a peek at #suggestions! {}".format(author, serverOwner.mention))

  
  if (not discord.utils.get(message.author.roles, name="Moderator")) and (
      not message.author.guild_permissions.administrator):
    return


#Moderator commands

  if message.content.startswith(
      '$roleMenu') and message.channel.name == "roles":
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
  payloadInfo = await getPayloadInfo(bot.get_guild(payload.guild_id), payload,
                                     "roles")
  if not payloadInfo:
    return
  reactionList = db["reactions"]
  for x in reactionList:
    reactedMessage = payloadInfo["message"]
    message = await payloadInfo["channel"].fetch_message(x[3])
    reactionEmoji = str(payload.emoji)
    if x[1] == reactionEmoji and message == reactedMessage:
      await payloadInfo["user"].add_roles(
        discord.utils.get(message.guild.roles, name=x[0]))


TOKEN = os.environ['TOKEN']


@bot.event
async def on_raw_reaction_remove(payload):
  payloadInfo = await getPayloadInfo(bot.get_guild(payload.guild_id), payload,
                                     "roles")
  if not payloadInfo:
    return

  reactionList = db["reactions"]

  for x in reactionList:
    message = await payloadInfo["channel"].fetch_message(x[3])
    reactionEmoji = str(payload.emoji)
    reactedMessage = payloadInfo["message"]

    if x[1] == reactionEmoji and message == reactedMessage:
      await payloadInfo["user"].remove_roles(
        discord.utils.get(message.guild.roles, name=x[0]))


@bot.event
async def on_raw_message_delete(payload):
  payloadInfo = await getPayloadInfo(bot.get_guild(payload.guild_id), payload,
                                     "roles")
  if not payloadInfo:
    return
  
  reactionList = db["reactions"]
  i = 0
  indexList = []
  for x in reactionList:
    if payload.message_id == x[3]:
      indexList.append(i)
    i += 1
  indexList.reverse()
  for i in indexList:
    db["reactions"].pop(i)

keep_alive()
bot.run(TOKEN)
