from discord.ext import commands
from cricbot_lib import *
import os

k = {}

msg_id = {}


bot = commands.Bot(command_prefix='*')
bot.remove_command('help')

@bot.event
async def on_ready():
    print('bot is running.')


@bot.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    channel_id = channel.id
    if not user.bot:
        if channel_id in msg_id:
            message = await channel.fetch_message(msg_id[channel_id])
            try:
                await message.remove_reaction('🔄', user)
            except:
                pass
            await message.edit(embed=score_embed(k[channel_id]))
        else:
            pass
    else:
        pass


@bot.command()
async def score(ctx, i=0):
    message = await ctx.send(embed=score_embed(i))
    channel_id = ctx.message.channel.id
    global msg_id
    msg_id[channel_id] = message.id
    await message.add_reaction('🔄')
    global k
    k[channel_id] = i


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
