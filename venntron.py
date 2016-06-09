# coding=utf8

import asyncio
import dataset
import discord
import feedparser
import functools
import importlib
import operator
import os
import random
import re
import sys
import time
import urllib.parse
from collections import defaultdict
from datetime import datetime
from discord.ext import commands
from glob import glob
from pymarkovchain import MarkovChain
from random import randint
from time import time

client = commands.Bot(command_prefix='.', description='fuck')

#mc = MarkovChain()
currentDirectory = sys.path[0] + "\\"
#try:
#    with open(currentDirectory + "logpruned.txt", 'r',  encoding="utf8") as log:
#        thelog = log.read()
#    mc.generateDatabase(thelog)
#except Exception as e:
#    print("Issue with markov database: {0}".format(e))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('--------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    global duckActive
    global duckShowTime
    authorID = str(message.author.id)
    if message.content.startswith('.bang'):
        if duckActive == True:
            duckActive = False
            timeToKill = "{:.3f}".format(time() - duckShowTime)
            currentKills = add_kills(authorID)
            if currentKills > 1:
                duckPlural = "ducks"
            else:
                duckPlural = "duck"
            await client.send_message(message.channel, message.author.mention + " you shot a duck in " + timeToKill + " seconds! You have killed " + str(currentKills) + " " + duckPlural + " in the /r/worldbuilding server!")
        else:
            await client.send_message(message.channel, "There is no duck! What are you shooting at?")
        client.send_message(message.channel, "got it")
        return
    if message.content.startswith('.bef'):
        if duckActive == True:
            duckActive = False
            timeToKill = "{:.3f}".format(time() - duckShowTime)
            currentKills = add_friends(authorID)
            if currentKills > 1:
                duckPlural = "ducks"
            else:
                duckPlural = "duck"
            await client.send_message(message.channel, message.author.mention + " you befriended a duck in " + timeToKill + " seconds! You made friends with " + str(currentKills) + " " + duckPlural + " in the /r/worldbuilding server!")
        else:
            await client.send_message(message.channel, "You tried befriending a non-existent duck, that's fucking creepy.")
        return
    with open(currentDirectory + "logpruned.txt", "a", encoding="utf8") as myfile:
        myfile.write(message.content + '. ')
    thenumber = randint(1,120)
    if thenumber < 1:
        print("Markov time!")
        await client.send_message(message.channel, mc.generateString())

#this is the shit that's gonna fuck

def add_kills(authorID):
    db = dataset.connect('sqlite:///duckhunt.db')
    table = db['users']
    user = table.find_one(username = authorID)
    if user != None:
        new_points = user['total_kills'] + 1
        data = dict(id = user['id'], total_kills = new_points)
        table.update(data, ['id'])
        user = table.find_one(username = authorID)
        return user['total_kills']
    else:
        table.insert(dict(username = authorID, total_kills = 1, total_friends = 0))
        return 1

def add_friends(authorID):
    db = dataset.connect('sqlite:///duckhunt.db')
    table = db['users']
    user = table.find_one(username = authorID)
    if user != None:
        new_points = user['total_friends'] + 1
        data = dict(id = user['id'], total_friends = new_points)
        table.update(data, ['id'])
        user = table.find_one(username = authorID)
        return user['total_friends']
    else:
        table.insert(dict(username = authorID, total_kills = 0, total_friends = 1))
        return 1




#here's the duck hunt SHIT
duck_tail = "・゜゜・。。・゜゜"
duck = ["\\\_o< ", "\\\\\_O< ", "\\\_0< "]
duck_noise = ["QUACK!", "FLAP FLAP!", "quack!"]
channel_ids = ["135181651708739584"]
duckChannel = ""
channel = ""



async def duck_hunt():
    await client.wait_until_ready()
    global duckActive
    global duckShowTime
    duckActive = False
    while not client.is_closed:
        await asyncio.sleep(randint(600,2400))
        duckActive = True
        duckChannel = random.choice(channel_ids)
        channel = discord.Object(id=duckChannel)
        counter = 0
        await client.send_message(channel, duck_tail + random.choice(duck) + random.choice(duck_noise))
        print("Duck is now active!")
        duckShowTime = time()
        while duckActive == True:
            await asyncio.sleep(10)

async def sub_tracker():
    await client.wait_until_ready()
    latestTitle = ""
    while not client.is_closed:
        feed = feedparser.parse('https://www.reddit.com/r/worldbuilding+deepworldbuilding/new/.rss')
        if latestTitle != feed["items"][0]["title"]:
            latestLink = feed["items"][0]["link"]
            if "DeepWorldbuilding" in latestLink:
                latestSub = "/r/deepworldbuilding"
            else:
                latestSub = "/r/worldbuilding"
            latestLink = latestLink.split("/comments/",1)[1]
            latestLink = "https://redd.it/" + latestLink[:6]
            latestTitle = feed["items"][0]["title"]
            latestAuthor = feed["items"][0]["author"]
            await client.send_message(discord.Object(id='135181651708739584'), '(' + latestLink + ') "' + latestTitle + '" by ' + latestAuthor + ' in ' + latestSub)
        await asyncio.sleep(5)


loop = asyncio.get_event_loop()

#and here we are initializing the client
try:
    loop.create_task(duck_hunt())
    loop.create_task(sub_tracker())
    loop.run_until_complete(client.login(''))
    loop.run_until_complete(client.connect())
except Exception:
    loop.run_until_complete(client.close())
finally:
    loop.close()
