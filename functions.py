import sys
import discord
import os
from discord.ext import commands
from replit import db



async def roleMenu(message):
  args = message.content.strip().split(" ")
  menuType = args[1]
  args = args[2:]
  msg = '**Role menu: {}**\n ‎\n'.format(menuType)
  roleList = message.guild.roles
  usedRoles = []
  for roleName in args:
    role = discord.utils.get(roleList, name=roleName)
    #Add check for all dash/space configurations
    if role:
      usedRoles.append([roleName, role])

  emojis = {}
  with open("emojis.txt") as f:
    rawFile = f.read()
    rawPairs = rawFile.split("\n")
    for pair in rawPairs:
      emojiPair = pair.strip(" ").split("|")
      emojis[emojiPair[0]] = emojiPair[1]
  for role in usedRoles:
    if role[0] in emojis:
      curEmoji = emojis[role[0]]
    else:
      curEmoji = ' ‎ '
    msg += '{}: `{}`\n ‎ \n'.format(curEmoji, role[1].name)
  botMessage = await message.channel.send(msg)
  await message.delete()

