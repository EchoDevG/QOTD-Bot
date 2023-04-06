import discord
from discord.ext import commands
from datetime import time, datetime, timedelta
import asyncio
import random
import os

class Cog_Name(commands.Cog):
    
    
    def __init__(self, client):
        self.client = client
    


    # if a message is reacted to a bunch, add it to a quotes
    @commands.event
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name == "⭐":
            channel = self.client.get_channel(payload.channel_id)
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
                send_channel=self.client.get_channel(1077397181302059068)
                # await send_channel.send(str(reaction.count))
                msg = await self.client.get_channel(payload.channel_id).fetch_message(
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


            
            



async def setup(client):
    await client.add_cog(Cog_Name(client))



