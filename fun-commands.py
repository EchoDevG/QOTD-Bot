import discord
from discord.ext import commands
from datetime import time, datetime, timedelta
import asyncio
import random
import os

class fun_commands(commands.Cog):
    
    
    def __init__(self, client):
        self.client = client
        
        
        
    @client.command()
    async def lengthen(ctx, arg):
    
        words = arg.split()
    
        new_word = []
    
        for word in words:
        
            url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/synonyms"
            headers = {
	        "X-RapidAPI-Key": os.environ.get("WORDSAPI_TOKEN"),
	        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
            }
    
            response = requests.request("GET", url, headers=headers)
        
            length = len(word)
            temp_word = word
        
            try:
            
                for item in response.json()["synonyms"]:
                    if len(item) >= length:
                        length = len(item)
                        temp_word = item
                
                new_word.append(temp_word)
            except:
                new_word.append(temp_word)
        
        new_word_string = ""
        for word in new_word:
            new_word_string += f'{word} '
        
        await ctx.send(ctx.author.mention + f' {new_word_string}')
    
    
    
    
    
    @client.command()
    async def hello(ctx):
        print(f"hello command from @{ctx.message.author}")
        await ctx.send(f"hello {ctx.author.mention}!")


    @client.command()
    async def ping(ctx):
        print(f"ping command from @{ctx.message.author}")
        await ctx.send(f"My ping is** {round(client.latency*1000)} Ms**")


    @client.command()
    async def leakechosipaddress(ctx):
        print(f"carters command from @{ctx.message.author}")
        await ctx.send("Echos IP address is 207.97.227.239")
  
    
    
    
    
    





async def setup(client):
    await client.add_cog(fun_commands(client))
    