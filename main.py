import os

import discord

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
  ch1 = client.get_channel(1087087110290419884)
  f = open('rules.txt')
  await ch1.send(f.read())


TOKEN = os.environ['TOKEN']

client.run(TOKEN)
