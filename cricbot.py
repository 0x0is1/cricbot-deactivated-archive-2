import requests
import json
from discord.ext import commands
import discord
import os
from datetime import datetime
from dateutil import tz
k = 0

msg_id = 0

def start_time(starting_timestamp):
    utc = datetime.fromtimestamp(int(starting_timestamp))
    time = str(utc.astimezone(tz.gettz('Asia/Kolkata')))[5:16]
    return time

def venue(json_data):
    venue_name = json_data['venue']['name']
    venue_location = json_data['venue']['location']
    return venue_name + ', ' + venue_location

def series_name(json_data):
    return json_data['series_name']

def match_id(json_data):
    return json_data['header']['match_desc']

def livescore(json_data, team_type):
    name = json_data[team_type]['name']
    score = json_data[team_type]['innings'][0]['score']
    wickets = json_data[team_type]['innings'][0]['wkts']
    overs = json_data[team_type]['innings'][0]['overs']
    return str(name + ' ' + score + '/' + wickets + ' (' + overs + ')')

def heading(json_data):
    team1 = json_data['team1']['name']
    team2 = json_data['team2']['name']
    return team1 + ' vs ' + team2

def match_desc(json_data):
    return json_data['header']['match_desc']

def running_status(json_data):
    return json_data['header']['status']

def s():
    f = requests.get(
        'http://mapps.cricbuzz.com/cbzios/match/livematches').content
    json_data = json.loads(f.decode('utf-8'))
    return json_data['matches']


def m(i):
    m_id = s()[i]['match_id']
    f = requests.get('http://mapps.cricbuzz.com/cbzios/match/' +
                     m_id + '/mini-commentary').content
    raw_f = json.loads(f.decode('utf-8'))
    g = requests.get('http://mapps.cricbuzz.com/cbzios/match/' + m_id).content
    raw_g = json.loads(g.decode('utf-8'))
    return raw_f, raw_g

def schedule_embed(j):
    embed = discord.Embed(title='Match schedule',color=0x03f8fc)
    raw_name = s()
    for i in range(0, j):
        try:
            embed.add_field(name=str(i) + '. ' +
                            raw_name[i]['series_name'] + ',' + start_time(raw_name[i]['header']['start_time']), value=raw_name[i]['team1']['name'] + ' vs ' + raw_name[i]['team2']['name'], inline=False)
        except Exception as e:
            embed.add_field(name=str(i), value=e, inline=False)
    return embed

def help_embed(cmd):
    def s_help():
        embed = discord.Embed(title="CricBot", color=0x03f8fc)
        embed.add_field(name="Description:", value="I am a discord bot made to see cricket livescores on discord server. I am under development. you are using my Beta version", inline=False)
        embed.add_field(name="Commands:", value="*score: Get you score of available match \n *schedule: Get you list and index of match in the list", inline=False)
        embed.add_field(
            name="Help commands:", value="Get help for specific command: *help score, *help schedule", inline=False)
        embed.add_field(
            name="Invite: ", value="You can invite me to your server by clicking on this link: https://discord.com/api/oauth2/authorize?client_id=757685102183448709&permissions=26688&scope=bot")
        return embed

    def score_help():
        embed = discord.Embed(title="CricBot", color=0x03f8fc)
        embed.add_field(
            name="Description:", value="This command is used for view score with supplied item number. You can get item number from *schedule command.", inline=False)
        embed.add_field(
            name="Example:", value="if match item number is 3, type *score 3, if 0, type *score 0", inline=False)
        embed.add_field(
            name="Invite: ", value="You can invite me to your server by clicking on this link: https://discord.com/api/oauth2/authorize?client_id=757685102183448709&permissions=26688&scope=bot")
        return embed

    def schedule_help():
        embed = discord.Embed(title="CricBot", color=0x03f8fc)
        embed.add_field(
            name="Description:", value="This command is used for view upcoming and live matches list.", inline=False)
        embed.add_field(
            name="Example:", value="if you want top 5 matches details, type *schedule 5", inline=False)
        embed.add_field(
            name="Invite: ", value="You can invite me to your server by clicking on this link: https://discord.com/api/oauth2/authorize?client_id=757685102183448709&permissions=26688&scope=bot")
        return embed

    commands = {'help': s_help(), 'score': score_help(), 'schedule': schedule_help()}    
    try:
        return commands[cmd]
    except:
        pass

def score_embed(i):
    state = s()[i]['header']['state_title']
    timestamp = s()[i]['header']['start_time']
    embed = discord.Embed(title=heading(m(int(i))[1]) + ', ' + match_desc(m(int(i))[0]), color=0x03f8fc)
    embed.add_field(name="Series name", value=series_name(
        m(int(i))[0]), inline=False)
    embed.add_field(name="Venue", value=venue(m(int(i))[0]), inline=False)
    embed.add_field(name="Start time", value=start_time(
        timestamp), inline=False)
    if state == 'Preview':
        embed.add_field(name="State: ", value="To be start", inline=False)
    else:
        try:
            embed.add_field(name="Score", value=livescore(
                m(int(i))[0], 'bat_team') + '\n' + livescore(m(int(i))[0], 'bow_team'), inline=False)
        except:
            try:
                embed.add_field(name="Score", value=livescore(
                    m(int(i))[0], 'bat_team'), inline=False)
            except:
                embed.add_field(name='State: ', value=state, inline=False)

    embed.add_field(name="Status", value=running_status(
        m(int(i))[0]), inline=False)
    return embed

bot = commands.Bot(command_prefix='*')
bot.remove_command('help')

@bot.event
async def on_ready():
    print('bot is running.')

@bot.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    if user.bot:
        pass
    else:
        if msg_id == 0:
            pass
        else:
            message = await channel.fetch_message(msg_id)
            try:
                await message.remove_reaction('🔄', user)
            except:
                pass
            await message.edit(embed=score_embed(k))

@bot.command()
async def score(ctx,i=0):
    message = await ctx.send(embed=score_embed(i))
    global msg_id
    msg_id = message.id
    await message.add_reaction('🔄')
    global k
    k = i

@bot.command()
async def schedule(ctx, j=5):
    await ctx.send(embed=schedule_embed(j))

@bot.command()
async def help(ctx, item='help'):
    embed = help_embed(item)
    try:
        await ctx.send(embed=embed)
    except:
        pass

auth_token = os.environ.get('DISCORD_BOT_TOKEN')
bot.run(auth_token)
