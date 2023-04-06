import discord
from discord.ext import commands
from datetime import time, datetime, timedelta
import asyncio
import random
import os
import requests

class weather_cog(commands.Cog):
    
    
    def __init__(self, client):
        self.client = client
    

# weather reports

    @commands.command()
    async def weather(self, ctx, arg=352792):
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

    @commands.command()
    async def weathercode(self, ctx):

        with open("/home/container/text/locations.txt", "r") as fr:
                # reading line by line
                lines = fr.readlines()

        message = ""

        for line in lines:
            message+=f'{line}\n'
        await ctx.send(message)



async def setup(client):
    await client.add_cog(weather_cog(client))
    