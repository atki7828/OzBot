#!/usr/bin/python3

import os
import shutil
import discord
from discord.ext import commands
import random
import requests
import sys
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
print(TOKEN)
#GUILD = (' ').join(sys.argv[1:])

bot = commands.Bot(command_prefix='!')

def is_image(url):
    ext = url.split('/')[-1].split('.')[-1]
    if "jpg" in ext:
        return True
    if "jpeg" in ext:
        return True
    if "png" in ext:
        return True
    if "gif" in ext:
        return True
    return False


# scrape subreddit for image files from past 24 hours, 
# return random
def rand_img(sr):
    limit = 100
    count = 0
    url = 'http://www.reddit.com/r/{subreddit}/top.json?t=day&limit=100'.format(subreddit=sr);
    print('url: ' + url)
    r = requests.get(url,headers={'User-Agent':'bot 0.1'})
    #r = requests.get('http://www.reddit.com/r/{subreddit}.json?limit=100'.format(subreddit=sr))
    rand = random.randint(0,r.json()['data']['dist']-1)
    posts = r.json()['data']['children']
    pic = posts[rand]
    while(not is_image(pic['data']['url']) or pic['data']['over_18'] == True):
        count += 1
        if(count > limit):
            return 'NONE'
        rand = random.randint(0,r.json()['data']['dist']-1)
        pic = posts[rand]
    #print(pic['data'])
    return pic['data']['url']

# download found image
def download_file(url,folder):
    if(url == 'NONE'):
        return url
    directory = os.path.join('.',folder)
    if not os.path.exists(directory):
        os.makedirs(directory)
    local_name = url.split('/')[-1]
    path = os.path.join(directory,local_name)
    with requests.get(url,stream=True) as r:
        with open(path,'wb') as f:
            shutil.copyfileobj(r.raw,f)
    return path

@bot.command(name='speak')
async def quote(ctx):
    await ctx.send('hello world!')

@bot.command(name='cat')
async def cat(ctx):
    f = download_file(rand_img('cats'),'cats')
    if(f == 'NONE'):
        await ctx.send('no images found....')
        return
    print(f)
    await ctx.send('cat.')
    await ctx.send(file=discord.File(f))

'''
client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(f'{client.user} is connected to the following guild:')
    print(f'{guild.name}(id: {guild.id})')
    print('vox channels:')
    for channel in guild.voice_channels:
        print(channel)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    out = str(message.author) + ' said ' + message.content + '!'
    await message.channel.send(out)

client.run(TOKEN)
'''
bot.run(TOKEN)

