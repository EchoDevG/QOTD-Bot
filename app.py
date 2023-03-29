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



# https://stackoverflow.com/questions/63769685/discord-py-how-to-send-a-message-everyday-at-a-specific-time

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

chat_logs = {}
client = commands.Bot(command_prefix=".", intents=intents)
load_dotenv()

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await client.loop.create_task(background_task())
    


openai.api_key = os.environ.get("OPENAI_KEY")
PERSPECTIVE_API_KEY = os.environ.get("PERSPECTIVE_KEY")




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


@client.command(description="Add questions to the bot")
async def add(ctx, arg):
    print(f"question added: {arg}")
    f = open("/home/container/potentialQuestions.txt", "a")

    saveMessage = str(ctx.message.author) + "#" + arg
    print("question saved to potentialQuestions.txt: " + saveMessage)

    f.write(f"{saveMessage}\n")
    f.close()
    await ctx.send(f"Question added: {arg}")


# if a message is reacted to a bunch, add it to a quotes
@client.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == "⭐":
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions, emoji=payload.emoji.name)

        logfile = open("/home/container/quotesMessages.txt", "r")
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

            logfile = open("/home/container/quotesMessages.txt", "a")
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


@client.command()
async def joke(ctx):

    location = "/home/container/badJokes.txt"
    with open(location) as f:
        lineCount = sum(1 for _ in f)

    lineNum = random.randint(0, lineCount)

    with open(location) as fp:
        for i, line in enumerate(fp):
            if i == lineNum:
                outputMessage = line
            elif i > lineCount:
                break

    await ctx.send(ctx.author.mention + " " + outputMessage)


@client.command()
async def force(ctx):
    print("forcing QOTD")
    if ctx.author.id == 715621217754808340:

        location = "/home/container/questions.txt"

        with open(location) as f:
            lineCount = sum(1 for _ in f)
            lineNum = random.randint(0, lineCount)

        with open(location) as fp:
            for i, line in enumerate(fp):
                if i == lineNum:
                    outputMessage = line
                elif i > lineCount:
                    break
        lineNum = str(lineNum)
        print(outputMessage)

        embedToSend = discord.Embed(title=outputMessage, color=0xFF5733)
        embedToSend.set_author(name="Question Of The Day")
        embedToSend.set_footer(text=("This was question number " + lineNum))
        await ctx.send(embed=embedToSend)
    else:
        print(f"{ctx.author} tried to force QOTD")
        await ctx.send("you do not have access to that command")


# music bot, courtesy of ChatGPT (shhhh)

voice = None
song_queue = []


async def play_music(ctx):
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
    song_queue.pop(0)
    voice.play(source, after=lambda e: client.loop.create_task(play_music(ctx)))


@client.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("You're not connected to a voice channel")
        return

    global voice
    if voice is not None:
        await voice.move_to(ctx.author.voice.channel)
        return

    voice = await ctx.author.voice.channel.connect()


@client.command()
async def leave(ctx):
    global voice
    await ctx.voice_client.disconnect()
    voice = None


@client.command()
async def play(ctx, *, url):
    global voice
    global song_queue
    song_queue.append(url)

    if voice is None:
        await ctx.invoke(join)

    if not voice.is_playing():
        await play_music(ctx)


@client.command()
async def skip(ctx):
    global voice
    if voice.is_playing():
        voice.stop()


@client.command()
async def queue(ctx):
    global song_queue
    if not song_queue:
        await ctx.send("There are no songs in the queue.")
        return

    queue = ""
    for i, song in enumerate(song_queue):
        queue += f"{i+1}. {song}\n"

    await ctx.send(f"```Queue:\n{queue}```")


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
        
    f = open("/home/container/chat_logs.txt", "a")

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
        
    f = open("/home/container/chat_logs.txt", "a")

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

    with open("/home/container/locations.txt", "r") as fr:
            # reading line by line
            lines = fr.readlines()
    
    message = ""
    
    for line in lines:
        message+=f'{line}\n'
    await ctx.send(message)

    
    
    
    
    
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
    
    
            
client.run(os.environ.get("BOT_TOKEN"))