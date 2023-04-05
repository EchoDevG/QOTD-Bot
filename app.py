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




chat_logs = {}
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
    print(f"We have logged in as {client.user}")
    QOTD(client).setup(client)
    







openai.api_key = os.environ.get("OPENAI_KEY")
PERSPECTIVE_API_KEY = os.environ.get("PERSPECTIVE_KEY")






# if a message is reacted to a bunch, add it to a quotes
@client.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == "⭐":
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions, emoji=payload.emoji.name)

        logfile = open("/home/container/text/quotesMessages.txt", "r")
        loglist = logfile.readlines()
        logfile.close()
        found = False
        for line in loglist:
            if str(payload.message_id) in line:
                found = True

        if reaction and reaction.count >= 2 and not found:
            send_channel=client.get_channel(1077397181302059068)
            # await send_channel.send(str(reaction.count))
            msg = await client.get_channel(payload.channel_id).fetch_message(
                payload.message_id
            )
            author = msg.author

            logfile = open("/home/container/text/quotesMessages.txt", "a")
            logfile.write(str(payload.message_id) + "\n")

            if len(msg.content)<1024:
                message_to_send = f'{msg.content}\n\n{msg.jump_url}'
            else:
                message_to_send = msg.jump_url
            
            embedToSend = discord.Embed(title="", color=0xFF5733)
            embedToSend.set_author(name=author.display_name)
            embedToSend.add_field(name="", value=f"**{message_to_send}**")
            embedToSend.set_thumbnail(url=str(author.avatar))

            if len(msg.attachments) > 0:
                embedToSend.set_image(url=reaction.message.attachments[0].url)

            embedToSend.set_footer(text="quoted by popular request")
            print(f"message quoted: {msg.content}")
            await send_channel.send(embed=embedToSend)






# chatbot

    
group_chat_logs=[]
    
@client.command()
#@commands.cooldown(1, 60, commands.BucketType.user)
async def groupchat(ctx, arg):
        
        
    try:
        group_chat_logs.append({"role": "user", "content": arg})
    except:
        group_chat_logs = [
            {"role": "system", "content": "Hi! I am a friendly individual"},
            {"role": "user", "content": "You are Toxy, a happy AI made by a person named Echo. Answer concisely. Be friendly with everyone."},
            {"role": "system", "content": "I am here to help!"},
            {"role": "user", "content": arg}
        ]
        
    #print(str(chat_logs[ctx.author]))
       
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=group_chat_logs,
        temperature = 0.7
    )
    
    output = response.choices[0]['message']['content']
    print(output)

    toxic = False

    perspective_client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=PERSPECTIVE_API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False
    )

    analyze_request = {
        "comment": {"text": output},
        "requestedAttributes": {"TOXICITY": {}},
    }

    response = perspective_client.comments().analyze(body=analyze_request).execute()
        #print(json.dumps(response, indent=2))
    
    toxicity = (response["attributeScores"]["TOXICITY"]["summaryScore"]["value"])

    if toxicity > 0.65:
        toxic = True
    else:
        toxic = False
        
    f = open("/home/container/logs/chat_logs.txt", "a")

    saveMessage = str(ctx.message.author) + " --- " + arg + " --- " + output
    print("message saved to chat_logs.txt")
    
    f.write(f"{saveMessage}\n")
    f.close()
    
    
    if not toxic:
        await ctx.send(ctx.author.mention + "\n" + output)
        print("sent to discord")
        group_chat_logs.append({"role": "system", "content": output})
    else:
        await ctx.send(
            ctx.author.mention
            + " Sorry, the bot is being toxic. Please try a different prompt"
        )

        
        
@client.command()
#@commands.cooldown(1, 60, commands.BucketType.user)
async def chat(ctx, arg):
        
        
    try:
        chat_logs[ctx.author].append({"role": "user", "content": arg})
    except:
        chat_logs[ctx.author] = [
            {"role": "system", "content": "Hi! I am a friendly individual"},
            {"role": "user", "content": "You are Toxy, a happy AI made by a person named Echo. Answer concisely. Be friendly with everyone."},
            {"role": "system", "content": "I am here to help!"},
            {"role": "user", "content": arg}
        ]
        
    #print(str(chat_logs[ctx.author]))
       
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_logs[ctx.author],
        temperature = 0.7
    )
    
    output = response.choices[0]['message']['content']
    print(output)

    toxic = False

    perspective_client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=PERSPECTIVE_API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False
    )

    analyze_request = {
        "comment": {"text": output},
        "requestedAttributes": {"TOXICITY": {}},
    }

    response = perspective_client.comments().analyze(body=analyze_request).execute()
        #print(json.dumps(response, indent=2))
    
    toxicity = (response["attributeScores"]["TOXICITY"]["summaryScore"]["value"])

    if toxicity > 0.65:
        toxic = True
    else:
        toxic = False
        
    f = open("/home/container/logs/chat_logs.txt", "a")

    saveMessage = str(ctx.message.author) + " --- " + arg + " --- " + output
    print("message saved to chat_logs.txt")
    
    f.write(f"{saveMessage}\n")
    f.close()
    
    
    if not toxic:
        await ctx.send(ctx.author.mention + "\n" + output)
        print("sent to discord")
        chat_logs[ctx.author].append({"role": "system", "content": output})
    else:
        await ctx.send(
            ctx.author.mention
            + " Sorry, the bot is being toxic. Please try a different prompt"
        )

        
# polling

@client.command()
async def poll(ctx, question, *options: str):
    if len(options) <= 1:
        await ctx.send('You need more than one option to make a poll!')
        return
    if len(options) > 10:
        await ctx.send('You cannot make a poll for more than 10 things!')
        return

    if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
        reactions = ['✅', '❌']
    else:
        reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

    description = []
    for x, option in enumerate(options):
        description += '\n {} {}'.format(reactions[x], option)
    embed = discord.Embed(title=question, description=''.join(description))
    react_message = await ctx.send(embed=embed)
    for reaction in reactions[:len(options)]:
        await react_message.add_reaction(reaction)
    embed.set_footer(text='Poll ID: {}'.format(react_message.id))
    await react_message.edit(embed=embed)
    
    
@client.command()
async def tally(ctx, id=None):
    poll_message = await ctx.channel.fetch_message(id)
    embed = poll_message.embeds[0]
    unformatted_options = [x.strip() for x in embed.description.split('\n')]
    print(f'unformatted{unformatted_options}')
    opt_dict = {x[:2]: x[3:] for x in unformatted_options} if unformatted_options[0][0] == '1' \
        else {x[:1]: x[2:] for x in unformatted_options}
    # check if we're using numbers for the poll, or x/checkmark, parse accordingly
    voters = [client.user.id]  # add the bot's ID to the list of voters to exclude it's votes

    tally = {x: 0 for x in opt_dict.keys()}
    for reaction in poll_message.reactions:
        if reaction.emoji in opt_dict.keys():
            reactors = [message async for message in reaction.users(limit=100)]
            for reactor in reactors:
                if reactor.id not in voters:
                    tally[reaction.emoji] += 1
                    voters.append(reactor.id)
    output = f"Results of the poll for '{embed.title}':\n" + '\n'.join(['{}: {}'.format(opt_dict[key], tally[key]) for key in tally.keys()])
    await ctx.send(output)


    
    
# weather reports

@client.command()
async def weather(ctx, arg=352792):
    response = requests.get(f'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/{arg}/?res=3hourly&key={os.environ.get("MET_OFFICE_KEY")}')
    print(response.status_code)
    
    
    temperature = []
    feels_like = []
    precipitation = []
    wind = []
    time = []
    
    for i in range(len(response.json()["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"])):
        temperature.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["T"])
        feels_like.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["F"])
        precipitation.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["Pp"])
        wind.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["S"])
        time.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["$"])

        
    
    message = "Today: \n"
    
    for x in range(len(temperature)):
         message += (f'{int(int(time[x]) / 60)}:00 :\nTemperature:{temperature[x]}°C -- Feels like {feels_like[x]}°C -- Rain chance {precipitation[x]}% -- Wind speed {wind[x]}mph \n\n')
        
        
        
    temperature = []
    feels_like = []
    precipitation = []
    wind = []
    time = []
        
        
        
    for i in range(len(response.json()["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"])):
        temperature.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"][i]["T"])
        feels_like.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"][i]["F"])
        precipitation.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"][i]["Pp"])
        wind.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"][i]["S"])
        time.append(response.json()["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"][i]["$"])
        
        
    
    embedToSend = discord.Embed(title="Weather Report", color=0x00B63D)
    embedToSend.add_field(name="", value=message)
    embedToSend.set_footer(text=("Powered by Met Office DataPoint"))
    
    await ctx.send(embed=embedToSend)
    
    message = "Tomorrow:\n"
    
        
    for x in range(len(temperature)):
        message += (f'{int(int(time[x]) / 60)}:00 :\nTemperature:{temperature[x]}°C -- Feels like {feels_like[x]}°C -- Rain chance {precipitation[x]}% -- Wind speed {wind[x]}mph \n\n')
        
    print(str(len(message)))
        
    embedToSend = discord.Embed(title="Weather Report", color=0x00B63D)
    embedToSend.add_field(name="", value=message)
    embedToSend.set_footer(text=("Powered by Met Office DataPoint"))
            
            
    await ctx.send(embed=embedToSend)
    
@client.command()
async def weathercode(ctx):

    with open("/home/container/text/locations.txt", "r") as fr:
            # reading line by line
            lines = fr.readlines()
    
    message = ""
    
    for line in lines:
        message+=f'{line}\n'
    await ctx.send(message)

    
    
    
    
    

    
    
            
client.run(os.environ.get("BOT_TOKEN"))