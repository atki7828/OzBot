#!/usr/bin/python3

from bs4 import BeautifulSoup as bs
import asyncio
import sqlite3
import json
import html
import youtubesearchpython as yts
import time
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
#GUILD = (' ').join(sys.argv[1:])

bot = commands.Bot(command_prefix='!')

emojis = []

def score():
    table = 'triviascore'
    conn = sqlite3.connect("botDB.db")
    cursor = conn.cursor()
    rows = cursor.execute('SELECT * FROM ' + table).fetchall()
    return rows

def win(author):
    table = 'triviascore'
    conn = sqlite3.connect("botDB.db")
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS ' + table + '(id INTEGER, user TEXT, score INTEGER)')
    print(type(author.id))
    row = cursor.execute('SELECT * FROM ' + table + ' where id = ?',(author.id,)).fetchall()
    if(len(row) < 1):
        cursor.execute('INSERT INTO ' + table + ' VALUES (?,?,?)',(author.id,author.name,1))
        conn.commit()
        conn.close()
        return
    cursor.execute('UPDATE ' + table + ' SET score = score + 1 WHERE id = ?',(author.id,))
    conn.commit()
    conn.close()

def get_emojis():
    unicode_file = './.emojis3'
    emojis = []
    with open(unicode_file,'r') as f:
        for line in f:
            code = line.strip()
            code = code.encode('utf-8').decode('unicode-escape')
            emojis.append(code)
    return emojis

def rand_emoji():
    return emojis[random.randint(0,len(emojis))]

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
def rand_img(sr,t='day'):
    limit = 100
    count = 0
    url = 'http://www.reddit.com/r/{subreddit}/top.json?t={timeRange}&limit=100'.format(subreddit=sr,timeRange=t);
    print('url: ' + url)
    r = requests.get(url,headers={'User-Agent':'bot 0.1'})
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

@bot.command(name='yt')
async def yt(ctx,*args):
    query = (" ").join(args)
    search = yts.SearchVideos(query,mode='json')
    #print(search.result())
    result = json.loads(search.result())['search_result'][0]
    await ctx.send('youtube results:\n' + result['link'])

# this reacts to a message with 10 random emojis.
@bot.command(name='emoji')
async def emoji(ctx):
    msg = await ctx.send('hi')
    for i in range(10):
        e = emojis[random.randint(0,len(emojis))]
        print(e)
        #await ctx.send(c)
        try:
            await msg.add_reaction(e)
        except:
            continue

@bot.command(name='8ball')
async def eightball(ctx,*args):
    answers = [
            'As I see it, yes.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Concentrate and ask again.',
            'Don’t count on it.',
            'It is certain.',
            'It is decidedly so.',
            'Most likely.',
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Outlook good.',
            'Reply hazy, try again.',
            'Signs point to yes.',
            'Very doubtful.',
            'Without a doubt.',
            'Yes.',
            'Yes – definitely.',
            ' You may rely on it.'
            ]
    res = answers[random.randint(0,len(answers))]
    await ctx.send(res)

@bot.command(name='trivia')
async def trivia(ctx,*args):
    if(len(args) > 0 and args[0] == 'score'):
        print('score')
        rows = score()
        await ctx.send(rows)
        print(rows)
        return
    url = 'https://opentdb.com/api.php?amount=1&difficulty=easy'
    res = requests.get(url,headers={'User-Agent':'OzBot 0.1'})
    data = res.json()['results'][0]
    question = html.unescape(data['question'])
    category = data['category']
    difficulty = data['difficulty']
    answers = []
    correct_answer = html.unescape(data['correct_answer'])
    incorrect_answers = data['incorrect_answers']
    incorrect_answers = [html.unescape(i) for i in incorrect_answers]
    answers.append(correct_answer)
    answers.extend(incorrect_answers)
    random.shuffle(answers)

    answers_dict = {chr(ord('A')+i) : answers[i] for i in range(len(answers))}

    #question_msg = '[ category: ' + category + ' ]\n'
    question_msg = question + '\n'
    question_msg += ('\n').join(a + '\t' + answers_dict[a] for a in answers_dict)

    await ctx.send(question_msg)

    answered = []

    def check(m):
        print(m.content)
        if(m.author.bot):
            return False
        correct = answers_dict[m.content] == correct_answer 
        if(correct and m.author not in answered):
            return True
        if(not correct):
            if(m.author not in answered):
                answered.append(m.author)
            return False
        return False

    try:
        correct = False
        msg = await bot.wait_for('message',check=check,timeout=10.0)
        await ctx.send(correct_answer + ' is right.\n' + str(msg.author.name) + ' wins!')
        win(msg.author)
        '''
        while(not correct):
            msg = await bot.wait_for('message',timeout=10.0)
            if(not msg.author.bot):
                correct = answers_dict[msg.content] == correct_answer
                if(correct and msg.author not in answered):
                    await ctx.send(correct_answer + ' is right.\n' + str(msg.author) + ' wins!')
                else:
                    if(msg.author not in answered):
                        await ctx.send('wrong')
                        answered.append(msg.author)
                    correct = False
        '''
    except asyncio.TimeoutError:
        await ctx.send('time\'s up;  the correct answer is ' + correct_answer)

@bot.command(name='mood')
async def wait(ctx):
    e = emojis[random.randint(0,len(emojis))]
    await ctx.send(e)
    
@bot.command(name='wait')
async def wait(ctx,*args):
    for i in range(int(args[0])):
        await ctx.send(i+1)
        time.sleep(1)

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

@bot.command(name='CAT')
async def bigcat(ctx):
    f = download_file(rand_img('bigcats','month'),'bigcats')
    if(f == 'NONE'):
        await ctx.send('no images found....')
        return
    print(f)
    await ctx.send('CAT.')
    await ctx.send(file=discord.File(f))

@bot.command(name='steam')
async def steam(ctx,*args):
    base_url = 'https://store.steampowered.com/search/'
    search = requests.get(base_url,params={'term':args})
    soup = bs(search.content,'html.parser')
    results = soup.find("div",{"id":"search_resultsRows"})
    link = results.find("a")["href"]
    await ctx.send(link)


emojis = get_emojis()

bot.run(TOKEN)
