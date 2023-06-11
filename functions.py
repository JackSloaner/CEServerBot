import sys
import discord
from discord.embeds import Embed
from bs4 import BeautifulSoup
import requests

from datetime import datetime
import pytz
import os
from discord.ext import commands
from replit import db


# $roleMenu functions
async def getPayloadInfo(guild, payload, channelName):
  if isinstance(payload, discord.RawReactionActionEvent):
    user = discord.utils.get(guild.members, id=payload.user_id)
  else:
    user = 0
  channels = guild.channels
  channel = discord.utils.get(channels, id=payload.channel_id)
  message = 0
  if isinstance(payload, discord.RawReactionActionEvent):
    async for x in channel.history(limit=200):
      if x.id == payload.message_id:
        message = x
  soughtChannel = discord.utils.get(channels, name=channelName)
  payloadInfo = {"channel": channel}
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


# Webhook functions


def createUTEmbed(link, title, image, label):
  link = "https://www.utoronto.ca" + link
  image = "https://www.utoronto.ca" + image
  response = requests.get(link)
  soup = BeautifulSoup(response.content, 'html.parser')
  firstParagraph = soup.find_all('div', {'class': 'field--name-body'})[1].find('p').get_text().strip()
  embed = Embed(title=title,
                url=link,
                description=firstParagraph + "..",
                colour=0x0563f8)
  embed.set_author(name="University of Toronto News")
  embed.set_image(url=image)
  timezone = pytz.timezone('America/Toronto')
  now = datetime.now(timezone)
  hour = now.strftime("%I").strip("0")
  date_time = now.strftime("%m/%d/%Y • {}:%M %p".format(hour))
  embed.set_footer(text=date_time)

  return embed


def createTMEmbed(link, author):
  embed = Embed(title=link.get_text(), url=link["href"], colour=0x8cbeb6)
  embed.set_author(name=author.get_text(), url=author["href"])
  embed.add_field(name="TechMeme news", value="")
  timezone = pytz.timezone('America/Toronto')
  now = datetime.now(timezone)
  hour = now.strftime("%I").strip("0")
  date_time = now.strftime("%m/%d/%Y • {}:%M %p".format(hour))
  embed.set_footer(text=date_time)

  return embed


async def updateNewsChannel(webhook):
  searchInfo = {}
  if webhook.id == db["webhook"][0]:
    await updateUTChannel(webhook)
  if webhook.id == db["webhook"][1]:
    await updateTMChannel(webhook)


async def updateUTChannel(webhook):
  response = requests.get("https://www.utoronto.ca/news/searchnews")
  soup = BeautifulSoup(response.content, 'html.parser')

  allDivs = soup.find('div', {'class': 'view-content'}).find_all('div')
  count = 0
  i = 0
  latestStories = []

  for x in range(len(allDivs))[2:]:
    if i == 0:
      story = allDivs[x + 2].find('a')
      if not story:
        i += 1
        continue
      label = story["aria-label"]
      imageLink = allDivs[x].find('img')
      if imageLink:
        imageLink = imageLink["src"]
      else:
        imageLink = 'https://www.utoronto.ca/sites/all/themes/uoft_stark/img/UofT_Centered.svg'

      storyItem = (story["href"], story.get_text(), imageLink, label)
      latestStories.append(storyItem)
    if i == 5:
      i = 0
    else:
      i += 1
  if len(latestStories) > 6:
    latestStories = latestStories[:6]
  latestStories.reverse()
  popCount = 0
  for storyNum in range(len(latestStories)):
    story = latestStories[storyNum]
    link = story[0]
    title = story[1]
    image = story[2]
    label = story[3]
    linkID = hash(link)

    if linkID not in db["UTstories"]:
      print(linkID)
      print(db["UTstories"])
      embed = createUTEmbed(link, title, image, label)
      await webhook.send(embed=embed)
      popCount += 1
      db["UTstories"].append(linkID)
      print("New Story: {}".format(title))
  for x in range(popCount):
    print("Here\n")
    db["UTstories"].pop(0)


async def updateTMChannel(webhook):
  response = requests.get("https://techmeme.com/river")
  soup = BeautifulSoup(response.content, 'html.parser')

  latestStories = soup.find_all('table')[1].find_all('a')
  latestAuthors = soup.find_all('table')[1].find_all('a')
  i = 1
  count = len(latestStories) - 1
  enumStories = range(len(latestStories))
  for index in enumStories:
    if i == 1:
      i = i - 1
      latestAuthors.pop(count)
    else:
      latestStories.pop(count)
      i = 1
    count = count - 1

  if len(latestStories) > 6:
    latestStories = latestStories[:6]
    latestAuthors = latestAuthors[:6]
  latestStories.reverse()
  latestAuthors.reverse()
  for x in range(len(latestStories)):
    link = latestStories[x]
    author = latestAuthors[x]
    linkID = hash(link["href"])
    if linkID not in db["TMstories"]:
      embed = createTMEmbed(link, author)
      await webhook.send(embed=embed)
      db["TMstories"].pop(0)
      db["TMstories"].append(linkID)
      print("new story")


# Slash Command functions


def createIntroEmbed(member, name, school, program, year, interests, message):
  embed = discord.Embed(title="Hey, I'm {}!".format(name),
                        description="{}".format(member),
                        color=0x0563f8)
  embed.set_thumbnail(url=member.display_avatar.url)
  embed.add_field(name="School:", value=school.value)
  embed.add_field(name="Program:", value=program)
  embed.add_field(name="Year:", value=year.value, inline=True)
  embed.add_field(name="Interests:", value=interests, inline=True)
  if message:
    embed.add_field(name="Message:", value=message, inline=True)
  timezone = pytz.timezone('America/Toronto')
  now = datetime.now(timezone)
  hour = now.strftime("%I").strip("0")
  date_time = now.strftime("%m/%d/%Y • {}:%M %p".format(hour))
  embed.set_footer(text=date_time)
  return embed
