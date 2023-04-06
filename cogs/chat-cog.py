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

class chat_cog(commands.Cog):
    
    
    def __init__(self, client):
        self.client = client  
        load_dotenv()
        
        
    # chatbot

    
    chat_logs = {}
    group_chat_logs=[]
    openai.api_key = os.environ.get("OPENAI_KEY")
    PERSPECTIVE_API_KEY = os.environ.get("PERSPECTIVE_KEY")

    @commands.command()
    #@commands.cooldown(1, 60, commands.BucketType.user)
    async def groupchat(self, ctx, arg):


        try:

            self.group_chat_logs.append({"role": "user", "content": arg})
        except:
            self.group_chat_logs = [
                {"role": "system", "content": "Hi! I am a friendly individual"},
                {"role": "user", "content": "You are Toxy, a happy AI made by a person named Echo. Answer concisely. Be friendly with everyone."},
                {"role": "system", "content": "I am here to help!"},
                {"role": "user", "content": arg}
            ]

        #print(str(chat_logs[ctx.author]))
        try:   
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.group_chat_logs,
                temperature = 0.7
            )
        except:
            self.group_chat_logs = [
                {"role": "system", "content": "Hi! I am a friendly individual"},
                {"role": "user", "content": "You are Toxy, a happy AI made by a person named Echo. Answer concisely. Be friendly with everyone."},
                {"role": "system", "content": "I am here to help!"},
                {"role": "user", "content": arg}
            ]
            await ctx.send("too many tokens. try again.")
            return


        output = response.choices[0]['message']['content']
        print(output)

        toxic = False

        perspective_client = discovery.build(
            "commentanalyzer",
            "v1alpha1",
            developerKey=self.PERSPECTIVE_API_KEY,
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
            self.group_chat_logs.append({"role": "system", "content": output})
        else:
            await ctx.send(
                ctx.author.mention
                + " Sorry, the bot is being toxic. Please try a different prompt"
            )



    @commands.command()
    #@commands.cooldown(1, 60, commands.BucketType.user)
    async def chat(self, ctx, arg):


        try:
            self.chat_logs[ctx.author].append({"role": "user", "content": arg})
        except:
            self.chat_logs[ctx.author] = [
                {"role": "system", "content": "Hi! I am a friendly individual"},
                {"role": "user", "content": "You are Toxy, a happy AI made by a person named Echo. Answer concisely. Be friendly with everyone."},
                {"role": "system", "content": "I am here to help!"},
                {"role": "user", "content": arg}
            ]

        #print(str(chat_logs[ctx.author]))
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.chat_logs[ctx.author],
                temperature = 0.7
            )
        except:
            self.chat_logs[ctx.author] = [
                {"role": "system", "content": "Hi! I am a friendly individual"},
                {"role": "user", "content": "You are Toxy, a happy AI made by a person named Echo. Answer concisely. Be friendly with everyone."},
                {"role": "system", "content": "I am here to help!"},
                {"role": "user", "content": arg}
            ]
            await ctx.send("too many tokens. try again")
            return

        output = response.choices[0]['message']['content']
        print(output)

        toxic = False

        perspective_client = discovery.build(
            "commentanalyzer",
            "v1alpha1",
            developerKey=self.PERSPECTIVE_API_KEY,
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
            self.chat_logs[ctx.author].append({"role": "system", "content": output})
        else:
            await ctx.send(
                ctx.author.mention
                + " Sorry, the bot is being toxic. Please try a different prompt"
            )




async def setup(client):
    await client.add_cog(chat_cog(client))
    