import sys
import discord
import os
from discord.ext import commands
from replit import db

async def getPayloadInfo(guild, payload, channelName):
  if isinstance(payload, discord.RawReactionActionEvent
):  
    user = discord.utils.get(guild.members, id=payload.user_id)
  else:
    user = 0
  channels = guild.channels
  channel = discord.utils.get(channels, id=payload.channel_id)
  message = 0
  if isinstance(payload, discord.RawReactionActionEvent
):
    async for x in channel.history(limit=200):
      if x.id == payload.message_id:
        message = x
  soughtChannel = discord.utils.get(channels, name=channelName)
  payloadInfo = {"channel":channel}
  if user:
    payloadInfo["user"] = user
  if message:
    payloadInfo["message"] = message
  
  if channel == soughtChannel:
    return payloadInfo
  return 0


def nextConfig(lastConfig):
  reverse = lastConfig.copy()
  reverse.reverse()
  loopIndex = 1
  while reverse[loopIndex] == 1:
    loopIndex += 1
  while reverse[loopIndex] == 0:
    loopIndex += 1
  realIndex = len(lastConfig) - loopIndex - 1
  newConfig = lastConfig[0:realIndex]
  newConfig.append(0)
  ones = lastConfig.count(1) - newConfig.count(1)
  for x in range(ones):
    newConfig.append(1)
  rest = len(lastConfig) - len(newConfig)
  for x in range(rest):
    newConfig.append(0)

  return newConfig


def lastOne(config):
  latest = 0
  i = 0
  for x in config:
    if x == 1:
      latest = i
    i += 1
  return latest


def findConfigs(startConfig, final):
  if startConfig == final:
    return [startConfig.copy()]
  cfList = []
  while startConfig != final:
    cfList.append(startConfig.copy())
    lastPos = lastOne(startConfig)
    while startConfig[-1] == 0:
      startConfig[lastPos] = 0
      startConfig[lastPos + 1] = 1
      lastPos += 1
      cfList.append(startConfig.copy())
    if startConfig != final:
      startConfig = nextConfig(startConfig)
      if startConfig == final:
        cfList.append(startConfig)
      
  return cfList

def getAllNumberConfigs(length):
  ones = 0
  totalConfigs = []
  for starts in range(length + 1):
    config = []
    final = []
    for x in range(ones):
      config.append(1)
    for x in range(length - ones):
      config.append(0)
      final.append(0)
    for x in range(ones):
      final.append(1)
    set1 = findConfigs(config, final)
    totalConfigs.extend(set1)
    ones += 1
  return totalConfigs

def dashOrSpace(num):
  if num: 
    return "-"
  return " "
  
def getAllConfigs(string):
  curDash = string.find("-")
  dashPos = []
  escape = -1
  while curDash != escape:
    dashPos.append(curDash)
    curDash = dashPos[-1] + string[(dashPos[-1] + 1):].find("-") + 1
    escape = dashPos[-1]
  numberConfigs = getAllNumberConfigs(len(dashPos))
  stringConfigs = []
  for numConfig in numberConfigs:
    if not dashPos:
        config = string
        break
    config = string[0:dashPos[0]]
    i = 0
    for dash in dashPos:
      config += dashOrSpace(numConfig[i])
      if i != len(dashPos) - 1:
        config += string[(dashPos[i] + 1):dashPos[i + 1]]
      else:
        config += string[(dashPos[i] + 1):]
      i += 1
    stringConfigs.append(config)
  return stringConfigs

async def roleMenu(message):
  args = message.content.split(" ")
  for x in args:
    x.strip(" ")
  menuType = args[1]
  args = args[2:]
  msg = '**Role menu: {}**\n ‎\n'.format(menuType)
  roleList = message.guild.roles
  usedRoles = []
  for roleName in args:
    role = discord.utils.get(roleList, name=roleName)
    if not role:
      allConfigs = getAllConfigs(roleName)
      for config in allConfigs:
        role = discord.utils.get(roleList, name=(config))
        if role:
          break
    if role:
      usedRoles.append([roleName, role])

  emojis = {}
  with open("emojis.txt") as f:
    rawFile = f.read()
    rawPairs = rawFile.split("\n")
    for pair in rawPairs:
      emojiPair = pair.strip(" ").split("|")
      emojis[emojiPair[0]] = emojiPair[1]
  reactions = []
  for role in usedRoles:
    if role[0] in emojis:
      curEmoji = emojis[role[0]]
    else:
      curEmoji = ' ‎ '
    msg += '{}: `{}`\n ‎ \n'.format(curEmoji, role[1].name)
    reactions.append([role[1].name, curEmoji, role[1].id])
  botMessage = await message.channel.send(msg)
  for x in reactions:
    x.append(botMessage.id)
    db["reactions"].append(x)
  await message.delete()

