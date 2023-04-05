import discord
from discord.ext import commands
from datetime import time, datetime, timedelta
import asyncio
import random
import os

class chat_cog(commands.Cog):
    
    
    def __init__(self, client):
        self.client = client
    





async def setup(client):
    await client.add_cog(chat_cog(client))
    