import discord, requests
import json
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


def running_status(i,json_data):
    return json_data[i]['header']['status']


def livematches_list():
    f = requests.get(
        'http://mapps.cricbuzz.com/cbzios/match/livematches').content
    json_data = json.loads(f.decode('utf-8'))
    return json_data['matches']



def score_data_provider(i):
    m_id = livematches_list()[i]['match_id']
    f = requests.get('http://mapps.cricbuzz.com/cbzios/match/' +
                     m_id + '/mini-commentary').content
    raw_f = json.loads(f.decode('utf-8'))
    g = requests.get('http://mapps.cricbuzz.com/cbzios/match/' + m_id).content
    raw_g = json.loads(g.decode('utf-8'))
    return raw_f, raw_g


def schedule_embed(j):
    embed = discord.Embed(title='Match schedule', color=0x03f8fc)
    raw_name = livematches_list()
    for i in range(0, j):
        try:
            embed.add_field(name=str(i) + '. ' +
                            raw_name[i]['series_name'] + ',' + start_time(raw_name[i]['header']['start_time']), value=raw_name[i]['team1']['name'] + ' vs ' + raw_name[i]['team2']['name'], inline=False)
        except Exception as e:
            embed.add_field(name=str(i), value=e, inline=False)
    return embed


def help_embed(cmd):
    source_code = 'You can get source code from here: https://github.com/0x0is1/cricbot'

    def s_help():
        embed = discord.Embed(title="CricBot", color=0x03f8fc)
        embed.add_field(
            name="Description:", value="I am a discord bot made to see cricket livescores on discord server. I am under development. you are using my Beta version", inline=False)
        embed.add_field(
            name="Commands:", value="*score: Get you score of available match \n *schedule: Get you list and index of match in the list", inline=False)
        embed.add_field(
            name="Help commands:", value="Get help for specific command: *help score, *help schedule", inline=False)
        embed.add_field(
            name="Invite: ", value="You can invite me to your server by clicking on this link: https://discord.com/api/oauth2/authorize?client_id=757685102183448709&permissions=26688&scope=bot")
        embed.add_field(name="Source: ", value=source_code)
        return embed

    def score_help():
        embed = discord.Embed(title="CricBot", color=0x03f8fc)
        embed.add_field(
            name="Description:", value="This command is used for view score with supplied item number. You can get item number from *schedule command.", inline=False)
        embed.add_field(
            name="Example:", value="if match item number is 3, type *score 3, if 0, type *score 0", inline=False)
        embed.add_field(
            name="Invite: ", value="You can invite me to your server by clicking on this link: https://discord.com/api/oauth2/authorize?client_id=757685102183448709&permissions=26688&scope=bot")
        embed.add_field(name="Source: ", value=source_code)
        return embed

    def schedule_help():
        embed = discord.Embed(title="CricBot", color=0x03f8fc)
        embed.add_field(
            name="Description:", value="This command is used for view upcoming and live matches list.", inline=False)
        embed.add_field(
            name="Example:", value="if you want top 5 matches details, type *schedule 5", inline=False)
        embed.add_field(
            name="Invite: ", value="You can invite me to your server by clicking on this link: https://discord.com/api/oauth2/authorize?client_id=757685102183448709&permissions=26688&scope=bot")
        embed.add_field(name="Source: ", value=source_code)

        return embed

    commands = {'help': s_help(), 'score': score_help(),
                'schedule': schedule_help()}
    try:
        return commands[cmd]
    except:
        pass


def score_embed(i):
    state = livematches_list()[i]['header']['state_title']
    timestamp = livematches_list()[i]['header']['start_time']
    embed = discord.Embed(title=heading(
        score_data_provider(int(i))[1]) + ', ' + match_desc(score_data_provider(int(i))[0]), color=0x03f8fc)
    embed.add_field(name="Series name", value=series_name(
        score_data_provider(int(i))[0]), inline=False)
    embed.add_field(name="Venue", value=venue(score_data_provider(int(i))[0]), inline=False)
    embed.add_field(name="Start time", value=start_time(
        timestamp), inline=False)
    if state == 'Preview':
        embed.add_field(name="State: ", value="To be start", inline=False)
    else:
        try:
            embed.add_field(name="Score", value=livescore(score_data_provider(int(i))[0], 'bat_team') + '\n' + livescore(score_data_provider(int(i))[0], 'bow_team'), inline=False)
        except:
            try:
                embed.add_field(name="Score", value=livescore(score_data_provider(int(i))[0], 'bat_team'), inline=False)
            except:
                embed.add_field(name='State: ', value=state, inline=False)

    embed.add_field(name="Status", value=running_status(int(i),livematches_list()), inline=False)
    return embed
