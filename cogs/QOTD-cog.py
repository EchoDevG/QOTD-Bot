import discord
from discord.ext import commands
from datetime import time, datetime, timedelta
import asyncio
import random
import os

class QOTD(commands.Cog):
    
    
    def __init__(self, client):
        self.client = client
    
    
    
    
    WHEN = time(2, 30, 0)
    channels = []
    
    
    
    async def on_ready():
        print(f"QOTD Cog loaded")
    
    
    
    async def called_once_a_day(self):  # Fired every day
        await self.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
        channels = []
        #channels.append(888352659562721291)  # computer science
        channels.append(1079795482580230225)  # echos testing server
        #channels.append(1080189433686536272)  # no bitches?
        
        chat_logs={}
        group_chat_logs={}
    
        lookfor = "questions.txt"

        for root, dirs, files in os.walk("/"):
            if lookfor in files:
                # found one!
                path = os.path.join(root, lookfor)
                location = path  # this is the path you required
                break
            outputMessage = "@echo something went wrong"

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

        try:
            if os.stat("/home/container/questionQueue.txt").st_size > 0:
                print("Looking in question queue")
                outputMessage = await check_queue()

                user = outputMessage[: (outputMessage.find("#") + 5)]
                messageContent = outputMessage[(outputMessage.find("#") + 6) :]
                print(user)
                print(messageContent)
                outputMessage = messageContent

                embedToSend = discord.Embed(title=outputMessage, color=0xB336FC)
                embedToSend.set_author(name="Question Of The Day")
                embedToSend.set_footer(
                text=("This was a queued question, asked by: @" + user)
                )
                print("Queued QOTD constructed")
            else:
                print("no items in question queue")
                embedToSend = discord.Embed(title=outputMessage, color=0xB336FC)
                embedToSend.set_author(name="Question Of The Day")
                embedToSend.set_footer(text=("This was question number " + lineNum))
                print("Random QOTD constructed")
        except OSError:
            print("No queue file")
            embedToSend = discord.Embed(title=outputMessage, color=0xB336FC)
            embedToSend.set_author(name="Question Of The Day")
            embedToSend.set_footer(text=("This was question number " + lineNum))

        for channel_id in channels:
            try:
                channel = self.get_channel(channel_id)
                print(channel.id)
                await channel.send(embed=embedToSend)
                print("QOTD sent to channel: " + channel.name)
            except:
                print("channel not found")


    async def check_queue():
        question = ""
        try:
            with open("/home/container/questionQueue.txt", "r") as fr:
                # reading line by line
                lines = fr.readlines()
                # pointer for position
                ptr = 0
                # opening in writing mode

                with open("/home/container/questionQueue.txt", "w") as fw:
                    for line in lines:
                        # we want to remove 5th line
                        if ptr != 0:
                            fw.write(line)
                        else:
                            question = line
                        ptr += 1
            print("Deleted")
            return question
        except:
            print("Oops! something error")


    async def background_task():
        now = datetime.utcnow()
        if (
            now.time() > WHEN
        ):  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
            tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
            await asyncio.sleep(
               seconds
            )  # Sleep until tomorrow and then the loop will start
        while True:
            now = (
            datetime.utcnow()
            )  # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
            target_time = datetime.combine(now.date(), WHEN)  # 6:00 PM today (In UTC)
            seconds_until_target = (target_time - now).total_seconds()
            await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
            await called_once_a_day()  # Call the helper function that sends the message
            tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
            await asyncio.sleep(
                seconds
            )  # Sleep until tomorrow and then the loop will start a new iteration




    @commands.command()
    async def force(self, ctx):
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
            
            
            
        def setup(self):
            self.bot.loop.create_task(self.background_task(self))




async def setup(client):
    await client.add_cog(QOTD(client))
    