from keepAlive import keep_alive

import os
from replit import db

import requests
from bs4 import BeautifulSoup
from functions import *
import discord
from discord.ext import commands
from discord import app_commands
from discord import Webhook
from discord.embeds import Embed
import typing
from typing import Optional

import schedule

import asyncio

TOKEN = os.environ['TOKEN']
ID = os.environ["SERVER_ID"]
bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())

@bot.event
async def on_ready():
  print("ready")
  guild = bot.get_guild(int(ID))
  try:
    synced = await bot.tree.sync() 
    print("Synced {} command(s)".format(len(synced)))
  except Exception as e:
    print(e)

  UofTNews = discord.utils.get(await guild.webhooks(), id=db["webhook"][0])
  techMemeNews = discord.utils.get(await guild.webhooks(), id=db["webhook"][1])

  async def updateTMNews():
    while True:
      await updateNewsChannel(techMemeNews)
      await asyncio.sleep(240)
  
  bot.loop.create_task(updateTMNews())
  
  async def updateUTNews():
    while True:
      await updateNewsChannel(UofTNews)
      await asyncio.sleep(240)
  
  bot.loop.create_task(updateUTNews())


@bot.event
async def on_message(message):
  if str(message.channel.id) == os.environ["INTRO_ID"]:
    if str(message.author.id) != os.environ["BOAT_ID"]:
      await asyncio.sleep(2)
      await message.delete()

  if message.author == bot.user:
    return
  if isinstance(message.author, discord.User):
    return

#User commands
  if message.content.startswith('$suggest'):
    author = message.author
    print(db["blackList"])
    if author.id in db["blackList"]:
      await message.reply('**Unfortunately you are blackListed from $suggest**')
      return
    msg = "`{}`: {}".format(author, message.content[8:])
    suggestionChannel = discord.utils.get(message.guild.channels,
                                          name='suggestions')
    await suggestionChannel.send(msg)
    await message.reply(
      "**Your suggestion has been sent to a moderator channel. Thank you for your input!**"
    )
    logChannel = discord.utils.get(message.guild.text_channels,
                                   name="server-logs")
    serverOwner = discord.utils.get(message.guild.members, name="Jack_Sloaner")
    await logChannel.send(
      "`{}` has used $suggest! Take a peek at #suggestions! {}".format(
        author, serverOwner.mention))

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
    logChannel = disco4rd.utils.get(message.guild.text_channels,
                                   name="server-logs")
    if logChannel:
      await logChannel.send("`{}` has cleared the `#{}` channel".format(
        Author, curChannel))
      
  if message.content.startswith('$blackList'):
    args = message.content.strip(" ").split(" ")
    args = args[1:]
    print(args)
    for userDiscrim in args:
      user = discord.utils.get(message.guild.members, discriminator=userDiscrim)
      if user:
        if user.id not in db["blackList"]:
          db["blackList"].append(user.id)
  

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

@bot.event
async def on_member_join(member):
  db["introduced"][member.id] = False

@bot.tree.command(name="moderate", description="Interested in moderation?")
async def moderate(ctx: discord.Interaction):
    link = "https://docs.google.com/forms/d/e/1FAIpQLSc1gdhWAYWiCxoPXgK9-k-HydFy7iIqif0-a_yvi95H1HCBrQ/viewform?usp=sf_link"
    msg = "**Thank you for your interest in moderation! Below is a link to a Moderator application form.** \n" + link
    await ctx.response.send_message(msg, ephemeral=True)
    logChannel = discord.utils.get(ctx.guild.text_channels,
                                   name="server-logs")
    serverOwner = discord.utils.get(ctx.guild.members, name="Jack_Sloaner")
    await logChannel.send(
      "`{}` has used $moderate! Look out for new form submission! {}".format(
        ctx.user, serverOwner.mention))
    

@bot.tree.command(name="introduce", description="Introduce yourself")
@app_commands.choices(year = [
  app_commands.Choice(name = "1st", value="1st"),
  app_commands.Choice(name = "2nd", value="2nd"),
  app_commands.Choice(name = "3rd", value="3rd"),
  app_commands.Choice(name = "4th", value="4th"),
])
@app_commands.choices(school = [
  app_commands.Choice(name = "Graduated", value = "Graduated"),
  app_commands.Choice(name = "Highschool", value = "Highschool"),
  app_commands.Choice(name = "UofT", value="University of Toronto"),
  app_commands.Choice(name = "TMU", value="Toronto Metropolitan University"),
  app_commands.Choice(name = "UBC", value="University of British Columbia"),
  app_commands.Choice(name = "UWaterLoo", value="University of Waterloo"),
  app_commands.Choice(name = "OttawaU", value="University of Ottawa"),
  app_commands.Choice(name = "Carleton", value="Carleton University"),
  app_commands.Choice(name = "QueensU", value="Queen's University"),
  app_commands.Choice(name = "McGill", value="McGill University"),
  app_commands.Choice(name = "YorkU", value="York University"),
  app_commands.Choice(name = "Western", value="Western University"),
  app_commands.Choice(name = "UGuelph", value="University of Guelph"),
  app_commands.Choice(name = "Simon Fraser", value="Simon Fraser University"),
  app_commands.Choice(name = "UCalgary", value="University of Calgary"),
  app_commands.Choice(name = "UAlberta", value="University of Alberta"),
    app_commands.Choice(name = "US University", value="US University"),
  app_commands.Choice(name = "Other (University)", value="Other (University)"),
  app_commands.Choice(name = "Conestoga", value="Conestoga College"),
  app_commands.Choice(name = "Centennial", value="Centennial College"),
  app_commands.Choice(name = "Humber", value="Humber College"),
  app_commands.Choice(name = "Seneca", value="Seneca College"),
  app_commands.Choice(name = "George Brown", value="George Brown College"),
  app_commands.Choice(name = "Other (College)", value="Other (College)"),
  app_commands.Choice(name = "N/A", value="N/A"),
])
@app_commands.describe(name = "Your First Name", program = "Your Program", school = "Your school", year = "Your year of study", interests = "What are your areas of interest?", message = "Write whatever you want about yourself, or anything else!")
async def introduce(ctx: discord.Interaction, name: str, school: app_commands.Choice[str], program: str, year: app_commands.Choice[str], interests: str, message: typing.Optional[str]):
  member = ctx.user
  if db["introduced"][str(member.id)]:
    await ctx.response.send_message("You've already introduced yourself!", ephemeral=True)
    return
  embed = createIntroEmbed(member, name, school, program, year, interests, message)
  await ctx.response.send_message(ctx.user.mention,embed=embed)
  db["introduced"][str(member.id)] = True

keep_alive()
bot.run(TOKEN)