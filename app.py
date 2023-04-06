# app.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import time, datetime, timedelta
import asyncio
import random
import linecache
import sys
import os
from os.path import join
from discord.utils import get
import pytube
import requests
import re
import openai
import json
from googleapiclient import discovery
from discord.ext.commands import cooldown, BucketType
from dotenv import load_dotenv
from os.path import join, dirname
from cogs.QOTD_cog import QOTD



# https://stackoverflow.com/questions/63769685/discord-py-how-to-send-a-message-everyday-at-a-specific-time

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True




client = commands.Bot(command_prefix=".", intents=intents)
load_dotenv()





@client.event
async def on_ready():
    await client.load_extension("cogs.QOTD_cog")
    print("QOTD cog loaded")
    await client.load_extension("cogs.fun-commands")
    print("Fun commands cog loaded")
    await client.load_extension("cogs.chat-cog")
    print("Chat cog loaded")
    await client.load_extension("cogs.music-cog")
    print("Music cog loaded")
    await client.load_extension("cogs.weather-cog")
    print("Weather cog loaded")
    await client.load_extension("cogs.poll-cog")
    print("Poll cog loaded")
    print(f"We have logged in as {client.user}")
    QOTD(client).setup(client)
    

            
client.run(os.environ.get("BOT_TOKEN"))