import requests
import json
from discord.ext import commands
import discord
import os
from datetime import datetime
from dateutil import tz


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


bot = commands.Bot(command_prefix='*')


@bot.event
async def on_ready():
    print('bot is running.')


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


@bot.command()
async def score(ctx, i=0):
    state = s()[i]['header']['state_title']
    timestamp = s()[i]['header']['start_time']
    embed = discord.Embed(title=heading(m(int(i))[1]) + ', ' + match_desc(m(int(i))[0]),
                          color=0x03f8fc, timestamp=ctx.message.created_at)
    embed.add_field(name="Series name", value=series_name(
        m(int(i))[0]), inline=False)
    embed.add_field(name="Venue", value=venue(m(int(i))[0]), inline=False)
    embed.add_field(name="Start time", value=start_time(timestamp), inline=False)
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
    await ctx.send(embed=embed)


@bot.command()
async def schedule(ctx, j=5):
    embed = discord.Embed(title='Match schedule',
                          color=0x03f8fc, timestamp=ctx.message.created_at)
    raw_name = s()
    for i in range(0, j):
        try:
            embed.add_field(name=str(i) + '. ' +
                            raw_name[i]['series_name'] + ',' + start_time(raw_name[i]['header']['start_time']), value=raw_name[i]['team1']['name'] + ' vs ' + raw_name[i]['team2']['name'], inline=False)
        except Exception as e:
            embed.add_field(name=str(i), value=e, inline=False)
    await ctx.send(embed=embed)

auth_token = os.environ.get('DISCORD_BOT_TOKEN')
bot.run(auth_token)
