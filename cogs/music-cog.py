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



class music_cog(commands.Cog):
    
    
    def __init__(self, client):
        self.client = client


    # music bot, courtesy of ChatGPT (shhhh)

    voice = None
    song_queue = []


    async def play_music(self, ctx, client):
        if not song_queue:
            global voice
            await voice.disconnect()
            voice = None
            return

        video_url = song_queue[0]
        video = pytube.YouTube(video_url)
        audio_stream = video.streams.filter(only_audio=True).first()
        source = await discord.FFmpegOpusAudio.from_probe(
            audio_stream.url,
            **{
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            },
        )
        self.song_queue.pop(0)
        voice.play(source, after=lambda e: client.loop.create_task(self.play_music(ctx)))


    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You're not connected to a voice channel")
            return

        global voice
        if voice is not None:
            await voice.move_to(ctx.author.voice.channel)
            return

        self.voice = await ctx.author.voice.channel.connect()


    @commands.command()
    async def leave(self, ctx):
        global voice
        await ctx.voice_client.disconnect()
        voice = None


    @commands.command()
    async def play(self, ctx, *, url):
        global voice
        global song_queue
        self.song_queue.append(url)

        if voice is None:
            await ctx.invoke(join)

        if not voice.is_playing():
            await self.play_music(ctx)


    @commands.command()
    async def skip(self, ctx):
        global voice
        if voice.is_playing():
            self.voice.stop()


    @commands.command()
    async def queue(self, ctx):
        global song_queue
        if not song_queue:
            await ctx.send("There are no songs in the queue.")
            return

        queue = ""
        for i, song in enumerate(self.song_queue):
            self.queue += f"{i+1}. {song}\n"

        await ctx.send(f"```Queue:\n{self.queue}```")




async def setup(client):
    await client.add_cog(music_cog(client))
    