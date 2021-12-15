import asyncpraw
import sqlite3
import random
import asyncio
import discord
import pytesseract as tess
import os
import requests
import PIL
import io
import toml
from discord import Spotify
import json
from steam_stats import download_stats_for_player
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from stats_compare import get_before_stat, get_last_stat
from main import *
import datetime
from PIL import Image, ImageFont, ImageDraw 


# all_messages = []
ready_list = []
html_ready_list = []
playing_users = []
final_users_list = []
session_names_ids = []

# Intents
intents = discord.Intents().all()
# Intents

bot = commands.Bot(intents=intents, command_prefix='!', help_command=None)

PRAYERS = 'Otče náš, ktorý si na nebesiach, posväť sa meno tvoje, príď kráľovstvo tvoje, buď vôľa tvoja ako v nebi, tak i na zemi. Chlieb náš každodenný daj nám dnes a odpusť nám naše viny, ako i my odpúšťame svojim vinníkom, a neuveď nás do pokušenia, ale zbav nás zlého.\nAmen.\n:church::cross::church:'

BONUS_WEAPONS = [('total_kills_knife', 'Knife'), ('total_kills_ak47', 'AK-47'), ('total_kills_m4a1', 'M4A4'), ('total_kills_awp', 'AWP'), ('total_kills_p90', 'P90'), ('total_kills_glock', 'Glock'), ('total_kills_deagle', 'Deagle'), ('total_kills_negev', 'Negev'), ('total_kills_xm1014', 'XM-1014'), ('total_hits_mag7', 'MAG-7')]

STATS_FOR_STAT_COMMAND = [('session', 'Session'), ('datetime', 'Datetime'), ('total_kills', 'Kills'), ('total_deaths', 'Deaths'), ('total_kills_headshot', 'HS kills'), ('total_damage_done', 'Demage'), ('total_kills_knife', 'Knife kills'), ('total_kills_ak47', 'AK-47 kills'), ('total_kills_m4a1', 'M4A4 kills'), ('total_kills_awp', 'AWP kills'), ('total_planted_bombs', 'Planted bombs'), ('total_defused_bombs', 'Defused bombs')]

html_dict = {}

session_dict = {}

POSITIVE = ["yes", "Yes", "yea", "y", "sure", "ye", "Ye", "Y"]
MINIMAL_NUMBER = 1
MAXIMAL_NUMBER = 11
MAXIMAL_LEN_GAME = 30
SESSION_ROLE = 881505468667797554 #TEST-881509999623409724, ORIG-881505468667797554
GAMING_ROLE = 825875949413072957 #TEST-881509999623409725, ORIG-825875949413072957
GAMING_CATEGORY = 825872608091832332 #TEST-881522734776078366, ORIG-825872608091832332
SPACEX_ROLE = 853289230784004096
NERD_ROLE = 853289397616640030


@bot.command(help='All commands')
async def help(ctx, args=None):
    help_mes = ['Calling 911...', 'Any problem?', 'Some problem here?', 'No worries, i gotch ya']
    help_embed = discord.Embed(title=random.choice(help_mes), description='List of supported commands:')
    command_names_list = [x.name for x in bot.commands]

    if not args:
        for i,x in enumerate(bot.commands):
            help_embed.add_field(
                name=f"`!{x.name}` {x.signature}",
                value=f"> {x.help}",
                inline=True
            )

    # If the argument is a command, get the help text from that command:
    elif args in command_names_list:
        help_embed.add_field(
            name=args,
            value=bot.get_command(args).help
        )

    # If someone is just trolling:
    else:
        help_embed.add_field(
            name="Nope.",
            value="Don't think I got that command"
        )

    await ctx.send(embed=help_embed)


@bot.command()
async def userinfo(ctx, *, member: discord.Member=None):
  """Displays information on a user"""
  if member == None:
      member = ctx.message.author
  embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
  embed.set_author(name=f"User Info - {member}")
  embed.set_thumbnail(url=member.avatar_url)
  await ctx.send(embed=embed)


@bot.command(help="Creates session", aliases=['s', 'ss'])
async def startsession(message, name: str, max_players: int):
    if str(message.channel) != 'bot-commands':
        await message.channel.send(f'')
        return
    if max_players <= MINIMAL_NUMBER:
        await message.channel.send('Error: Minimum players in the session is **2**!')
        return
    if max_players >= MAXIMAL_NUMBER:
        await message.channel.send(
            'Error: Maximum players in the session is **10**!')
        return
    if len(name) >= MAXIMAL_LEN_GAME:
        await message.channel.send('Error: Maximum lenght of game is **30**!')
        return
    if f'{name}_game' in session_dict:
        return

    await set_vars_to_dict(message, name, max_players)
    await get_message(message, name)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    if payload.guild_id is None:
        return

    flat_a = flatten(session_names_ids)

    if payload.message_id not in flat_a:
        return

    for session_name, session_id in session_names_ids:
        if payload.message_id == session_id:
            session = session_name

    user = bot.get_user(payload.user_id)
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(session_dict[f'{session}_first_ms_id'])
    session_owner = session_dict[f'{session}_started_by_id']
    max_p = session_dict[f'{session}_max_players']
    current_p = session_dict[f'{session}_ready_players']

    if max_p == current_p:
        return

    if str(payload.emoji) == '❌':
        await session_unready(payload, session)
        await message.remove_reaction('❌', user)
    if str(payload.emoji) == '✅':
        if payload.user_id in session_dict[f'{session}_ready_list'] and payload.member.name != "CerveneTlacitko":
            return
        session_dict[f'{session}_ready_players'] += 1
        await get_message(payload, session)

    if str(payload.emoji) == '📊':
        if payload.user_id != session_owner:
            await message.remove_reaction('📊', user)
            return
        session_dict[f'{session}_statistics'] = True
    if str(payload.emoji) == '🔊':
        if payload.user_id != session_owner:
            await message.remove_reaction('🔊', user)
            return
        session_dict[f'{session}_create_vc'] = True
    if str(payload.emoji) == '🎮':
        if payload.user_id != session_owner:
            await message.remove_reaction('🎮', user)
            return
        session_dict[f'{session}_gaming_session'] = True
    if str(payload.emoji) == '<:ouremoji:851164594320048208>':
        session_dict[f'{session}_soviet_session'] = True


@bot.command(help='Ends session', aliases=['e', 'end'])
async def endsession(ctx, session):
    if str(ctx.channel) != 'bot-commands':
        return
    try:
        session_dict[f'{session}_game']
    except KeyError:
        await ctx.send(f'There is no session called **"{session}"**', delete_after=5)
        await ctx.message.delete()
        return
    if ctx.author.id not in session_dict[f'{session}_ready_list']:
        embed = discord.Embed(
            title='Missing permissions!', 
            description='You must be in this session to end it!', 
            color=0xff1414
        )
        await ctx.message.delete()
        await ctx.send(embed=embed, delete_after=10)
        return

    await session_end(ctx, session)


@bot.command(aliases=['m'])
async def move(ctx, session):
    await move_to_session_vc(ctx, session)


@bot.command(help='Adds one more space to session', aliases=["joinsession"])
async def join_to(message, session: str):
    if session != session_dict[f'{session}_voice_channel']:
        return
    await ask_to_join(message, session)


@bot.command(help='Voice channel join')
async def bot_join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@bot.command(help='Voice channel disconnect')
async def leave(ctx):
    await ctx.voice_client.disconnect()


# @bot.command(help="Sends funny picture")
# async def russia(message):
#     await command_russia(message)


@bot.command(help="Sends random video of best csgo plays")
async def cheater(message):
    await command_cheater(message)


@bot.command(help="Pray, pray and pray!")
async def pochvalen(message):
    await command_pochvalen(message)


@bot.command(help='Detailed info about the project', aliases=['project'])
async def info(ctx):
    toml_open = toml.load(open('pyproject.toml'))['tool']['poetry']
    project_name = toml_open['name']
    project_version = toml_open['version']
    project_description = toml_open['description']
    project_authors = ', '.join(toml_open['authors'])
    embed = discord.Embed(title='Info about the project', url='https://github.com/chalankolachtanovity/Bot_ready/blob/master/README.md')
    embed.add_field(name='Name:', value=toml_open['name'])
    embed.add_field(name='Version:', value=toml_open['version'])
    embed.add_field(name='Description:', value=toml_open['description'])
    embed.add_field(name='Authors:', value=', '.join(toml_open['authors']))
    await ctx.send(embed=embed)


@bot.command(help='Share your music')
async def spotify(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
        pass
    if user.activities:
        for activity in user.activities:
            if isinstance(activity, Spotify):
                embed = discord.Embed(
                    title=f"{user.name}'s Spotify",
                    description="Listening to {}".format(activity.title),
                    color=0xC902FF)
                embed.description = f"Link: \nhttps://open.spotify.com/track/{activity.track_id}"
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Artist", value=activity.artist)
                embed.add_field(name="Album", value=activity.album)
                embed.set_footer(text="Song started at {}".format(activity.created_at.strftime("%H:%M")))
            await ctx.send(embed=embed)


@bot.command(help='See your last session stats')
async def stats(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    name = get_username(user.name)

    embed = discord.Embed(title=f'Last session stats for **{name}**')
    for sql_name, nice_name in STATS_FOR_STAT_COMMAND:
        embed.add_field(name=f'> {nice_name}', value=f'> {get_stat(sql_name, name)}')
    await ctx.send(embed=embed)


async def create_vc_channel(guild, game: str, number: int):
    banned_role = discord.utils.get(guild.roles, name="@everyone")

    overwrites = {
        banned_role: discord.PermissionOverwrite(connect=False),
    }
    for user_id in session_dict[f'{game}_ready_list']:
        user = await bot.fetch_user(user_id)
        overwrites[user] = discord.PermissionOverwrite(connect=True)

    new_voice_channel = await guild.create_voice_channel(name=f"{game} session", category=bot.get_channel(GAMING_CATEGORY), user_limit=number+1, overwrites=overwrites)
    session_dict[f'{game}_voice_channel'] = new_voice_channel
    if session_dict[f'{game}_soviet_session'] is True:
        await soviet_songs(new_voice_channel)


@bot.command(help='!createpass `<name>` `<surrname>` `<birth_date>` `<birth_place>` `<gender> - "be what you want to be"`')
async def createpass(ctx, name, surrname, birth_date, birth_place, gender):
    LIMIT = 70
    user = ctx.author

    if len(name+surrname+birth_date+birth_place+gender) > LIMIT:
        await ctx.send('Too many letters')
        return

    if os.path.isfile(f"russian_passes/{user.name}_pass.jpg"):
        embed = discord.Embed(title='You already have your passport!', description='Type `!pass` to see your pass')
        await ctx.send(embed=embed, delete_after=10)
        return

    if os.path.isfile(f"russian_passes/{user.name}_pass.jpg") == False:
        img_data = requests.get(user.avatar_url).content
        with open(f'avatars/{user.name}.jpg', 'wb') as handler:
            handler.write(img_data)

    if os.path.isfile(f"avatars/{user.name}_resized.jpg") == False:
        resize_image(user)

    format_pass(ctx, user, name, surrname, birth_date, birth_place, gender)


@bot.command(aliases=['pass'])
async def viewpass(ctx, *, member: discord.Member=None):
    if member == None:
        member = ctx.author

    if os.path.isfile(f"russian_passes/{member.name}_pass.jpg"):
        embed = discord.Embed(title='Pass:', description=f'User: `{member.name}`')
        f = discord.File(f"russian_passes/{member.name}_pass.jpg")
        await ctx.send(embed=embed, file=f)
    else:
        embed = discord.Embed(title='Pass not found', description=f'There is no pass for `{member}`')
        await ctx.send(embed=embed, delete_after=10)
        return


async def resize_image(user):
    avatar_image = Image.open(f'avatars/{user.name}.jpg')
    if avatar_image.mode != 'RGB':
        img = avatar_image.convert('RGB')
    foo = img.resize((410,510),Image.ANTIALIAS)
    foo.save(f"avatars/{user.name}_resized.jpg",quality=95)
    os.remove(f"avatars/{user.name}.jpg")

async def format_pass(ctx, user, name, surrname, birth_date, birth_place, gender):
    date_today = datetime.datetime.today().strftime('%d.%m.')
    pass_image = Image.open("russian_passes/pass.jpg")
    avatar_image = Image.open(f'avatars/{user.name}_resized.jpg')
    big_font = ImageFont.truetype("Roboto-Bold.ttf", 60)
    small_font = ImageFont.truetype("Roboto-Bold.ttf", 50)

    name_surrname = f"{name}\n{surrname}"
    birth_date_place = f'{birth_date}                 {birth_place}\n{gender}\n{date_today}'

    image_editable = ImageDraw.Draw(pass_image)
    image_editable.text((530,1200), name_surrname, (0, 0, 0), font=big_font, spacing=50, aling="right")
    image_editable.text((530,1480), birth_date_place, (0, 0, 0), font=small_font, spacing=25, aling="right")

    Image.Image.paste(pass_image, avatar_image, (50, 1210))

    pass_image.save(f"russian_passes/{user.name}_pass.jpg", quality=95)
    f = discord.File(f"russian_passes/{user.name}_pass.jpg")
    embed = discord.Embed(title='Your pass is ready', description='Congratulations, you can now use `!russia` command.')
    await ctx.send(embed=embed, file=f)


async def soviet_songs(channel):
    paths_to_anthem = ['mp3/soviet_anthem.mp3', 'mp3/Konarmejskij-marsh.mp3', 'mp3/Nash-paravos.mp3', 'mp3/Varshavjanka.mp3']
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio(random.choice(paths_to_anthem)), after=lambda e: print('done', e))
    await asyncio.sleep(120)
    await vc.disconnect()
    await channel.edit(user_limit=channel.user_limit-1)


async def set_vars_to_dict(message, game: str, number: int):
    html_dict["session"] = game
    html_dict["max_players"] = number
    session_dict[f"{game}_ready_list_mentions"] = []
    session_dict[f'{game}_started_by_id'] = message.author.id
    session_dict[f'{game}_playing_users'] = []
    session_dict[f'{game}_ready_list'] = []
    session_dict[f'{game}_ready_list'].append(message.author.id)
    session_dict[f'{game}_game'] = game
    session_dict[f'{game}_max_players'] = number
    session_dict[f'{game}_ready_players'] = 0
    session_dict[f'{game}_ready_players'] += 1
    # booleans
    session_dict[f'{game}_statistics'] = False
    session_dict[f'{game}_create_vc'] = False
    session_dict[f'{game}_gaming_session'] = False
    session_dict[f'{game}_soviet_session'] = False


async def get_message(message, session):
    """Sends message according to ready players"""
    READY_PLAYERS = session_dict[f'{session}_ready_players']
    MAX_PLAYERS = session_dict[f'{session}_max_players']
    if READY_PLAYERS == 1:
        await first_session_message(message, session)
    if READY_PLAYERS >= 2 and READY_PLAYERS != MAX_PLAYERS:
        await session_ready(message, session)
    if READY_PLAYERS == MAX_PLAYERS:
        await ending_of_session(message, session)


async def first_session_message(message, started_session: str):
    """Sends starting session message"""

    await in_lobby_presence(started_session)

    max_players = session_dict[f'{started_session}_max_players']

    embed = discord.Embed(
        title=f"**{started_session}** session - lobby", 
        description=f"""
        Started by **{message.author}**
        Session: **{started_session}**
        Players able to join: **{max_players}**
        Players joined: {message.author.mention}
        """,
        color=0x1f8b4c
    )
    embed.set_footer(text=f"Join with emoji reaction below ↓")
    first_session_ms = await message.channel.send(embed=embed)
    session_dict[f'{started_session}_first_ms_id'] = first_session_ms.id

    emojis = ['❌', '✅', '📊', '🔊', '🎮', '<:ouremoji:851164594320048208>']
    for emoji in emojis:
        await first_session_ms.add_reaction(emoji)

    session_names_ids.append((started_session, first_session_ms.id))
    session_dict[f"{started_session}_ready_list_mentions"].append(message.author.mention)
    ready_list.append(message.author.id)
    html_ready_list.append(message.author.name)


async def session_ready(payload, session):
    """Sends ready information message"""
    if session != session_dict[f'{session}_game']:
        return
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    channel = await bot.fetch_channel(payload.channel_id)
    started_by = await bot.fetch_user(session_dict[f'{session}_started_by_id'])

    session_dict[f'{session}_ready_list'].append(member.id)
    session_dict[f"{session}_ready_list_mentions"].append(member.mention)
    member_mentions = ', '.join(session_dict[f'{session}_ready_list_mentions'])

    msg = await channel.fetch_message(session_dict[f'{session}_first_ms_id'])

    embed = discord.Embed(
        title=f"**{session}** session - lobby", 
        description=f"""
        Started by **{started_by}**
        Session: **{session}**
        Players able to join: **{session_dict[f'{session}_max_players']}**
        Players joined: {member_mentions}
        """,
        color=0x1f8b4c
    )
    embed.set_footer(text=f"Join with emoji reaction below ↓")
    await msg.edit(embed=embed)

    ready_list.append(member.id)
    html_ready_list.append(member.name)


async def ending_of_session(payload, ended_session: str):
    """Sends last ready information message, execute timer to assign fucker and delete all things that was in before session"""

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    channel = await bot.fetch_channel(payload.channel_id)
    msg = await channel.fetch_message(session_dict[f'{ended_session}_first_ms_id'])

    session_dict[f'{ended_session}_ready_list'].append(member.id)
    session_dict[f"{ended_session}_ready_list_mentions"].append(member.mention)
    after_ready_list_members = ', '.join(session_dict[f'{ended_session}_ready_list_mentions'])
    all_p = session_dict[f'{ended_session}_max_players']

    embed = discord.Embed(
        title=f'{ended_session} session - Full', 
        description=f"""
        Status: **Ongoing**
        Players: **{all_p}**/**{all_p}**
        Players list: {after_ready_list_members}
        """,
        color=0x9E0000#0x9b59b6
        )
    embed.set_footer(text="Enjoy this session! Don't forget to launch CS:GO!")

    if session_dict[f'{ended_session}_gaming_session'] is True:
        for member_id in session_dict[f'{ended_session}_ready_list']:
            await guild.get_member(member_id).add_roles(guild.get_role(GAMING_ROLE))
        embed.set_thumbnail(url="https://www.dictionary.com/e/wp-content/uploads/2018/07/CS-GO3.jpg")

    if session_dict[f'{ended_session}_soviet_session'] is True:
        embed.set_thumbnail(url="https://i.pinimg.com/originals/f4/67/a2/f467a22305243ef1eee7373ca8e0f0b9.png")

    await msg.edit(embed=embed)
    await session_presence(ended_session)

    if session_dict[f'{ended_session}_statistics'] is True:
        for name in html_ready_list:
            check_list(name)
        get_before_stat(final_users_list)

        session_dict[f'{ended_session}_bonus_weapon'] = [random.choice(BONUS_WEAPONS)]
        for env, nice in session_dict[f'{ended_session}_bonus_weapon']:
            embed = discord.Embed(title=f'Bonus weapon for {ended_session} session is {nice}  🎁', description='The player with most kills on this weapon will win this session')
        await channel.send(embed=embed)

    if session_dict[f'{ended_session}_create_vc'] is True:
        number = session_dict[f'{ended_session}_max_players']
        await create_vc_channel(guild, ended_session, number)

    for member_id in session_dict[f'{ended_session}_ready_list']:
        await guild.get_member(member_id).add_roles(guild.get_role(SESSION_ROLE))

    html_dict.clear()
    ready_list.clear()
    html_ready_list.clear()


def check_list(user):
    if user == 'CerveneTlacitko':
        final_users_list.append(('t_kmaso', 'Kmasko', KMASKO_DICT['personaname'], 673099696629350416))
    if user == 'teetou':
        final_users_list.append(('t_teetou', 'Teetou', TEETOU_DICT['personaname'], 765908540878487572))
    if user == 'Bonsai':
        final_users_list.append(('t_aligator', 'Aligator', ALIGATOR_DICT['personaname'], 489114476222742528))
    if user == 'milan čonka':
        final_users_list.append(('t_stano', 'Stano', STANO_DICT['personaname'], 489117343964725260))
    if user == 'Tajmoti':
        final_users_list.append(('t_tajmoti', 'Tajmoti', TAJMOTI_DICT['personaname'], 140197100062244864))
    if user == 'andrzej':
        final_users_list.append(('t_dron', 'Dron', DRON_DICT['personaname'], 491236539716730890))
    if user == 'Kulivox':
        final_users_list.append(('t_kulivox', 'Kulivox', KULIVOX_DICT['personaname'], 265552128335020032))


def get_username(username):
    usernames = [('CerveneTlacitko', 'Kmasko'), ('teetou', 'Teetou'), ('Bonsai', 'Aligator'), ('milan čonka', 'Stano'), ('Tajmoti', 'Tajmoti'), ('andrzej', 'Dron'), ('Kulivox', 'Kulivox')]
    for d_name, sql_name in usernames:
        if d_name == username:
            return sql_name


async def session_end(ctx, session):
    possible_q = ['really?', '100% sure?', 'for real?', 'are you sure?']
    emojis = ['✅', '❌']

    choosen_q = random.choice(possible_q)
    dscrpt = f"Session: {session}"

    embed = discord.Embed(title=f"**{ctx.author.name}**, {choosen_q}", description=dscrpt)
    embed.set_footer(text='Add reaction below ↓')
    confirming_message = await ctx.send(embed=embed)
    for emoji in emojis:
        await confirming_message.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.author

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

    except asyncio.TimeoutError:
        await ctx.message.delete()
        await confirming_message.delete()
        return

    else:
        if str(reaction.emoji) == '✅':
            await confirming_message.delete()
            await ctx.message.delete()
            await end_function(ctx, session)
        else:
            await ctx.message.delete()
            await confirming_message.delete()


async def end_function(ctx, vc_name):
    existing_channel = discord.utils.get(ctx.guild.channels, name=f"{vc_name} session")
    general_channel = discord.utils.get(ctx.guild.channels, name="General")
    msg = await ctx.fetch_message(session_dict[f'{vc_name}_first_ms_id'])

    if session_dict[f'{vc_name}_create_vc'] is True:
        for member in ctx.author.voice.channel.members:
            await member.move_to(general_channel)
            if existing_channel is None:
                await ctx.send(f'No channel named "{vc_name}" was found')
                return

    embed = discord.Embed(
        title=f'{vc_name} session - Ended', 
        description=f"""
        Status: **Ended**
        Session: **{vc_name}**
        Check <#842840247980261486> for session statistics!
        """,
    )
    await msg.edit(embed=embed)

    for member in session_dict[f'{vc_name}_ready_list']:
        user = bot.get_user(member)
        await ctx.guild.get_member(user.id).remove_roles(ctx.guild.get_role(GAMING_ROLE))
        await ctx.guild.get_member(user.id).remove_roles(ctx.guild.get_role(SESSION_ROLE))

    if existing_channel is not None:
        await existing_channel.delete()
    if session_dict[f'{vc_name}_statistics'] is True:
        get_last_stat(final_users_list, vc_name)
        await asyncio.sleep(5)
    if session_dict[f'{vc_name}_statistics'] is True:
        await create_stats_table(vc_name)
    ms_id = session_dict[f'{vc_name}_first_ms_id']
    session_names_ids.remove((vc_name, ms_id))
    await pop_items_in_dict(vc_name)
    await default_presence()
    final_users_list.clear()


async def pop_items_in_dict(session):
    keys_to_pop = [f'{session}_started_by_id', f'{session}_playing_users', f'{session}_ready_list', f'{session}_game', f'{session}_max_players', f'{session}_ready_players', f'{session}_statistics', f'{session}_create_vc', f'{session}_gaming_session', f'{session}_voice_channel', f'{session}_first_ms_id', f'{session}_soviet_session', f'{session}_bonus_weapon', f'{session}_ready_list_mentions']
    for key in keys_to_pop:
        session_dict.pop(key, None)


async def move_to_session_vc(ctx, vc_name):
    channel = discord.utils.get(ctx.guild.channels, name=f'{vc_name} session')
    for member in ctx.author.voice.channel.members:
        await member.move_to(channel)


async def move_to(channel_id, message):
    channel = bot.get_channel(channel_id)
    await message.author.move_to(channel)


async def ask_to_join(message, session: str):
    channel = session_dict[f'{session}_voice_channel']
    embed = discord.Embed(title=f"{message.author.name}, you can join", description=f'Session: {session}')
    await message.channel.send(embed=embed)
    user = await bot.fetch_user(message.author.id)
    overwrites = {
        user: discord.PermissionOverwrite(connect=True)
    }
    await channel.edit(user_limit=channel.user_limit+1, overwrites=overwrites)

    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(SESSION_ROLE))
    if session_dict[f'{session}_gaming_session'] is True:
        await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))


async def create_stats_table(session):
    channel = await bot.fetch_channel(881509999807971359) #842840247980261486
    embed = discord.Embed(title='Statistics for **{}** session'.format(get_stat('session', 'Kmasko')))
    for_best_stat = {}
    b_w = session_dict[f'{session}_bonus_weapon']
    for env, nice in b_w:
        bonus_weapon = nice
        bonus_weapon_env = env
    for env, nice, steam, user_id in final_users_list:
        bonus_stat = get_stat(bonus_weapon_env, (nice))
        for_best_stat[user_id] = bonus_stat
        embed.add_field(
            name=f'**{steam}**', 
            value='> Kills: {}\n> Deaths: {}\n> {} kills: **{}**'.format(get_stat('total_kills', (nice)), get_stat('total_deaths', (nice)), bonus_weapon, bonus_stat), inline=True
        )
        embed.set_footer(text=get_stat('datetime', 'Kmasko'))

    all_values = for_best_stat.items()
    max_value = max(for_best_stat.values())
    user_id = max(all_values, key = lambda x:x[1])
    user = bot.get_user(user_id[0])

    embed.add_field(
        name=f'**Session winner**  🎉', 
        value=f'> {user.mention} is the winner with **{max_value}** **{bonus_weapon}** kills', 
        inline=False
    )
    await channel.send(embed=embed)


def get_stat(stat, name):
    conn = sqlite3.connect("file::memory:?cache=shared")
    c = conn.cursor()
    c.execute(f"""SELECT {stat} FROM stats WHERE name='{name}' ORDER BY datetime desc LIMIT 1""")
    z = c.fetchall()
    conn.commit()
    conn.close()
    for x in z[0]:
        return x


async def session_unready(payload, session: str):
    if session != session_dict[f'{session}_game']:
        return
    if payload.user_id not in session_dict[f'{session}_ready_list']:
        return
    if session_dict[f'{session}_ready_players'] == 1:
        return
    if payload.user_id in playing_users:
        playing_users.remove(payload.user_id)
    session_dict[f'{session}_ready_players'] -= 1

    mentions = session_dict[f'{session}_ready_list_mentions']
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    channel = await bot.fetch_channel(payload.channel_id)
    msg = await channel.fetch_message(session_dict[f'{session}_first_ms_id'])
    started_by = await bot.fetch_user(session_dict[f'{session}_started_by_id'])

    if member.mention in mentions:
        session_dict[f'{session}_ready_list_mentions'].remove(member.mention)
    session_dict[f'{session}_ready_list'].remove(payload.user_id)
    ready_list.remove(payload.user_id)
    html_ready_list.remove(member.name)

    player_mentions = ', '.join(session_dict[f'{session}_ready_list_mentions'])

    embed = discord.Embed(
        title=f"**{session}** session - lobby", 
        description=f"""
        Started by **{started_by}**
        Session: **{session}**
        Players able to join: **{session_dict[f'{session}_max_players']}**
        Players joined: {player_mentions}
        """,
        color=0x1f8b4c
    )
    embed.set_footer(text=f"Join with emoji reaction below ↓")
    await msg.edit(embed=embed)


async def timer_assign_fucker(choose_timer: int):
    await asyncio.sleep(choose_timer)


# async def assing_fucker_role(message, game):
#     """After 5minutes it compare playing users with ready users and according to result,
#   add role to ready player but not playing"""
#     await timer_assign_fucker(120)
#     role = message.guild.get_role(812862836710834207)
#     suka_list = []
#     checker = []
#     missing_players = []
#     print("Timer ended")
#     for i in session_dict[f'{game}_ready_list']:
#         if i in playing_users:
#             checker.append(True)
#         else:
#             checker.append(i)
#     if checker.count(True) != len(checker):
#         missing_players.append(checker)
#         for f_player in missing_players[0]:
#             user = bot.get_user(f_player)
#             await message.guild.get_member(user.id).add_roles(role)
#             suka_list.append(user.mention)
#         embed = discord.Embed(title='Wall of shame!', description=f'Shame on you {suka_list[0]}!')
#         embed.set_footer(text="Get rid of this role by launching CS:GO under 2 minutes!")
#         await message.channel.send(embed=embed)

#     else:
#         print("equal")

#     x = [value for value in session_dict[f'{game}_ready_list'] if value in playing_users]
#     x_list = []
#     x_list.append(x)
#     for u_player in x_list[0]:
#         unban_user = bot.get_user(u_player)
#         await message.guild.get_member(unban_user.id).remove_roles(role)


async def command_russia(message):
    bot_answer = ['Here you are', 'Enjoy', 'Cyka', 'Suka Blyat', 'Suka', '<3', '...', '☭', ':flag_ru:', 'Cyka blyat']
    images = await get_dir_files('rsimgs/')
    random_image = random.choice(images)
    one_img = random_image
    f = discord.File(f"rsimgs/{one_img}")
    e = discord.Embed(title=random.choice(bot_answer), color=0xde2b2b)
    e.set_image(url=f"attachment://{one_img}")
    e.set_footer(text=f" • Requested by {message.author.name} ☭")
    await message.channel.send(file=f, embed=e)


async def get_dir_files(dirname: str) -> list:
    files = []
    for file in listdir(dirname):
        full_path = join(file)
        files.append(full_path)
    return files


async def command_cheater(message):
    videos = await get_dir_videos('vid/')
    random_video = random.choice(videos)
    await message.channel.send(file=discord.File(random_video))


async def get_dir_videos(dirname: str) -> list:
    videos = []
    for file in listdir(dirname):
        full_path = join(dirname, file)
        if isfile(full_path):
            videos.append(full_path)
    return videos


def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)


async def command_pochvalen(message):
    """Replies 'aj naveky, amen' to the player saying pochvalen."""
    myEmbed = discord.Embed(title="Aj naveky, Amen.",
                            description=PRAYERS,
                            color=0xff0000)
    myEmbed.set_footer(text="Pozdravujem všetkých poliakov!")
    await message.channel.send(embed=myEmbed)


async def default_presence():
    soviet_songs = ['[If Tomorrow War Comes] music: Pokrass brothers', '[The Sacred War] music: A. Alexandrov', '[Invincible and legendary] music: A. Alexandrov', '[Dark girl] music: A. Novikov', '[We the Red Soldiers]', '[White Army, Black Baron] music: Samuil Pokrass', '[Song about Shchors] music: M. Blanter', '[Red flag]', '[Katyusha] music: M. Blanter', '[Blue headkerchief] music: E. Peterburgsky']
    # await bot.change_presence(activity=discord.Activity(
    #     type=discord.ActivityType.listening, name=random.choice(soviet_songs)))
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name='Spaceflights'))


async def in_lobby_presence(game):
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing, name=f'In {game} lobby'))


async def session_presence(session):
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=f'{session} session'))

async def send_report_message(message):
    report_channel = bot.get_channel(777200768842858506)
    await report_channel.send(f'{message.author.mention} tried to send "** {message.content} **" in **{message.channel}** channel\nYou can\'t do that')


# REDDIT


@bot.command()
async def russia(ctx, subred="ANormalDayInRussia"):
    if os.path.isfile(f"russian_passes/{ctx.author.name}_pass.jpg") == False:
        embed = discord.Embed(title="You don't have passport!", description="Type `!createpass` to create your own passport.")
        await ctx.send(embed=embed)
        return

    msg = await ctx.send('Загрузка... ')

    reddit = asyncpraw.Reddit(
                    client_id=os.getenv('client_id'),
                    client_secret=os.getenv('client_secret'),
                    username=os.getenv('username'),
                    password=os.getenv('password'),
                    user_agent="pythonpraw"
                    )

    subreddit = await reddit.subreddit(subred)
    all_subs = []
    top = subreddit.top(limit=100) # bot will choose between the top 250 memes

    async for submission in top:
        all_subs.append(submission)

    random_sub = random.choice(all_subs)

    name = random_sub.title
    url = random_sub.url
    extension = random_sub.url[len(random_sub.url) - 3 :].lower()

    embed = discord.Embed(title=f'__{name}__', colour=discord.Colour.random(), timestamp=ctx.message.created_at, url=url)

    if "jpg" in extension or "png" in extension or "gif" in extension:
        embed.set_image(url=url)
    else:
        embed.add_field(name="This post contains a video", value='Click on the title to view it')

    embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar_url)
    embed.set_footer(text=f'r/{subred}')
    await msg.delete()
    await ctx.send(embed=embed)
    return


# REDDIT
async def read_image(message):
    await message.channel.send("Processing...")
    print(message.attachments[0].url)
    os.environ["TESSDATA_PREFIX"] = "/home/runner/.apt/usr/share/tesseract-ocr/4.00/tessdata/"
    tess.pytesseract.tesseract_cmd = r'tesseract'

    response = requests.get(message.attachments[0].url)
    image_bytes = io.BytesIO(response.content)
    img = PIL.Image.open(image_bytes)

    text = tess.image_to_string(img)
    print(text)
    await message.channel.send(f"Picture text:\n {text}")
    print("done")


@bot.event
async def on_message(message):
    if (message.author == bot.user):
        return

    # if str(message.channel) == 'pytess' and message.attachments[0].url is not None:
    #      await read_image(message)

    # if str(message.channel) != 'bot-commands' and message.content[0] == '!':
    #     if message.author.name != 'CerveneTlacitko':
    #         await message.delete()
    #         await send_report_message(message)
    #         return

    # if str(message.channel) == 'bot-commands' and message.content[0] != '!':
    #     if message.author.name != 'CerveneTlacitko':
    #         if message.content not in POSITIVE:
    #             await message.delete()
    #             await send_report_message(message)
    #             return
    await bot.process_commands(message)


@bot.event
async def on_member_update(before, curr):
    """Adds member to playing users list when he changed activity"""
    games = ["counter-strike: global offensive", "payday 2", "test"]

    if curr.activity and curr.activity.name.lower() in games:
        if curr.id not in playing_users:
            playing_users.append(curr.id)

    if before.activity and before.activity.name.lower() in games and curr.activities not in games:
        if curr.id in playing_users:
            playing_users.remove(curr.id)


@bot.event
async def on_member_join(member):
    embed = discord.Embed(title=f"**Hey {member.name}, welcome to Milošovy hrátky server!**", color=0x009dff)
    embed.set_author(name="by chalankolachtanovity")
    embed.add_field(name=":red_circle:Rules:", value="We don't have any rules, everything is moderated by bot **Lachtan**.\nType **!help**", inline=True)
    embed.set_thumbnail(url="https://m.smedata.sk/api-media/media/image/sme/6/30/3065226/3065226_600x400.jpeg?rev=3")
    embed.add_field(name=":red_circle:Bot Lachtan", value="Bot **Lachtan** is our unique bot with unique functions! Feel free to use him!", inline=False)
    embed.set_footer(text="enjoy!")
    await bot.get_channel(783670260200767488).send(content=member.mention, embed=embed)


# @bot.event
# async def on_voice_state_update(member, before, current):
#     if str(member) == 'Lachtan#1982':
#         return
#     if current.channel is None:
#         return
#     if int(current.channel.category_id) == 825872608091832332:
#         return
#     vc = await current.channel.connect()
#     vc.play(discord.FFmpegPCMAudio("mp3/rickrollaf.mp3"), after=lambda e: print('done', e))
#     await asyncio.sleep(random.randint(2,7))
#     await vc.disconnect()


@bot.command(help='Rickroll your mates')
async def play(ctx):
    voicechannel = discord.utils.get(ctx.guild.channels, name='General') # ctx.author.voice.channel
    vc = await voicechannel.connect()
    vc.play(discord.FFmpegPCMAudio("mp3/rickrollaf.mp3"), after=lambda e: print('rickrolled', e))


@bot.event
async def on_command_error(ctx, error):
    answers = ['Huh?', 'You are trying impossible', '"Human being"', 'I just sometimes ask, why.', 'No way', 'Again?', 'Just...', 'XD', 'Wtf dude.', '2+2?', 'No comment']
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title=random.choice(answers), description='Check spelling', color=0xff1414)
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=random.choice(answers), description=f'Missing a required argument `<{error.param.name}>`.  Do `!help <commandname>`', color=0xff1414)
        await ctx.send(embed=embed)
    raise error


@bot.event
async def on_ready():
    print("Discord -> connected")
    await default_presence()
    # await spacex_reddit()
    # await bot.process_commands

    
keep_alive()
bot.run(os.getenv('TOKEN'))
