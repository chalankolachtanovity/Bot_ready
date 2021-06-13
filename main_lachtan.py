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
from discord import Spotify
from steam_stats import download_stats_for_player
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from stats_compare import *
from main import *
all_messages = []
ready_list = []
html_ready_list = []
playing_users = []
final_users_list = []

# Intents
intents = discord.Intents().all()
# Intents

bot = commands.Bot(intents=intents, command_prefix='!', help_command=None)

PRAYERS = 'Otče náš, ktorý si na nebesiach, posväť sa meno tvoje, príď kráľovstvo tvoje, buď vôľa tvoja ako v nebi, tak i na zemi. Chlieb náš každodenný daj nám dnes a odpusť nám naše viny, ako i my odpúšťame svojim vinníkom, a neuveď nás do pokušenia, ale zbav nás zlého.\nAmen.\n:church::cross::church:'

html_dict = {}

kills_dict = {}

list_for_i_message = {}

session_dict = {}

POSITIVE = ["yes", "Yes", "yea", "y", "sure", "ye", "Ye", "Y"]
MINIMAL_NUMBER = 1
MAXIMAL_NUMBER = 11
MAXIMAL_LEN_GAME = 30
GAMING_ROLE = 825875949413072957
GAMING_CATEGORY = 825872608091832332
SPACEX_ROLE = 853289230784004096
NERD_ROLE = 853289397616640030


@bot.command()
async def help(ctx, args=None):
    help_mes = ['Calling 911...']
    help_embed = discord.Embed(title="911, whats your emergency?")
    command_names_list = [x.name for x in bot.commands]

    if not args:
        help_embed.add_field(
            name="List of supported commands:",
            value="\n> !".join(x.name for i,x in enumerate(bot.commands)),
            inline=False
        )
        help_embed.add_field(
            name="Details",
            value="Type `!help <command name>` for more details about each command.",
            inline=False
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


# @bot.command()
# async def event(ctx):
#     # if ctx.author.id != 673099696629350416:
#     #     return
#     await ctx.message.delete()
#     # emojis = ['<:facts:853333168177414145>', '<:spaceX:853325340466479112>']
#     embed = discord.Embed(title="Wassup everyone!", description="I'm sure you know I, <@783750741700509766>, am active. I've noticed that you may be interrupted by messages I send every day in #facts and #spacex. Therefore, I will leave it on you whether you want or not receive news from these two topics.", color=0xffffff)
#     embed.add_field(name="Easy entry, Easier exit!", value="React with emojis below this message. You can remove your subscription at any time by removing your reaction.\n\n• <:facts:853333168177414145> **for facts subscription**\n• <:spaceX:853325340466479112> **for SpaceX subscription**")
#     embed.set_footer(text='Click ⬇️ ! / Unclick ⬇️ !')
#     # mes = await ctx.send(content="@everyone", embed=embed)
#     # for emoji in emojis:
#     #     await mes.add_reaction(emoji)
#     ms = await ctx.channel.fetch_message(853339565426868234)
#     await ms.edit(embed=embed)
    



@bot.command(help="Creates custom session with max players.", aliases=['s', 'ss'])
async def startsession(message, name: str, max_players: int):
    if str(message.channel) != 'bot-commands':
        await message.channel.send('Check god damn channel! Ne-ver-mind, i will do it for you, ')
        return
    """Create keys, values in dict and sends message according to user preferences"""
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
    all_messages.append(message.message)
    await set_vars_to_dict(message, name, max_players)
    await get_message(message, name)
    # await move_to(session_dict[f'{name}_voice_channel'].id, message)


@bot.command()
async def get_server_icon_url(ctx):
    icon_url = ctx.guild.icon_url
    await ctx.send(f"The icon url is: {icon_url}")


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    if payload.guild_id is None:
        return

    user = bot.get_user(payload.user_id)
    channel = await bot.fetch_channel(payload.channel_id)

    if session_dict != {}:
      session = html_dict["session"]
      message = await channel.fetch_message(session_dict[f'{session}_first_ms_id'])
      session_owner = session_dict[f'{session}_started_by_id']

      if payload.message_id != session_dict[f'{session}_first_ms_id']:
          return

      if str(payload.emoji) == '❌':
          await session_unready(payload, session)
          await message.remove_reaction('❌', user)
      if str(payload.emoji) == '✅':
          if payload.user_id in ready_list and payload.member.name != "CerveneTlacitko":
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

    if str(payload.emoji) == '<:facts:853333168177414145>':
        if payload.channel_id == 853324149523218432:
            await channel.guild.get_member(user.id).add_roles(channel.guild.get_role(NERD_ROLE))
            embed = discord.Embed(title='Facts subscription!', description='Wassup nerd, I have some spicy Facts for you!', color=0x4aeb1e)
            embed.set_footer(text='Enjoy!')
            await user.send(embed=embed)

    if str(payload.emoji) == '<:spaceX:853325340466479112>':
        if payload.channel_id == 853324149523218432:
            await channel.guild.get_member(user.id).add_roles(channel.guild.get_role(SPACEX_ROLE))
            embed = discord.Embed(title='SpaceX subscription!', description='You are now following the news about SpaceX!', color=0x4aeb1e)
            embed.set_footer(text='Enjoy!')
            await user.send(embed=embed)


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return
    if payload.guild_id is None:
        return

    user = bot.get_user(payload.user_id)
    channel = await bot.fetch_channel(payload.channel_id)

    if str(payload.emoji) == '<:facts:853333168177414145>':
        if payload.channel_id == 853324149523218432:
            await channel.guild.get_member(user.id).remove_roles(channel.guild.get_role(NERD_ROLE))
            embed = discord.Embed(title='Unfollowed, Facts', description='I hope you learned something new!', color=0xf40101)
            await user.send(embed=embed)

    if str(payload.emoji) == '<:spaceX:853325340466479112>':
        if payload.channel_id == 853324149523218432:
            await channel.guild.get_member(user.id).remove_roles(channel.guild.get_role(SPACEX_ROLE))
            embed = discord.Embed(title='Unfollowed, SpaceX', description='I hope you enjoyed SpaceX news!', color=0xf40101)
            await user.send(embed=embed)


# @bot.command(help="Adds user to choosen session", aliases=['r'])
# async def ready(message, session_to):
#     if session_to != session_dict[f'{session_to}_game']:
#         await message.channel.send(f'Session "{session_to}" was not found')
#         return
#     if message.author.id in ready_list and message.author.name != "CerveneTlacitko":
#         await message.channel.send(f'You are already in "{session_to}"" session')
#         return
#     all_messages.append(message.message)
#     session_dict[f'{session_to}_ready_players'] += 1
#     await get_message(message, session_to)
    # await move_to(session_dict[f'{session_to}_voice_channel'].id, message)


# @bot.command(help="Removes user from the choosen session")
# async def unready(message, session_in_unready):
#     if session_in_unready != session_dict[f'{session_in_unready}_game']:
#         await message.channel.send(f'Session "{session_in_unready}" was not found')
#         return
#     await session_unready(message, session_in_unready)


@bot.command(help='delete a channel with the specified name', aliases=['e', 'end'])
async def endsession(ctx, session):
    await session_end(ctx, session)


async def session_end(ctx, session):
    possible_q = ['really?', '100% sure?', 'for real?', 'are you sure?']
    default_txt = await bot.fetch_channel(777200768842858506)

    choosen_q = random.choice(possible_q)
    channel = ctx.channel
    dscrpt = f"Session: {session}"

    embed = discord.Embed(title=f"**{ctx.author.name}**, {choosen_q}", description=dscrpt)
    embed.set_footer(text='Reply to this message!')
    await default_txt.send(embed=embed)

    try:
        message = await bot.wait_for("message", check=lambda m: m.channel == channel, timeout=30.0)

    except asyncio.TimeoutError:
        return

    else:
        if message.content in POSITIVE:
            embed2 = discord.Embed(title='I hope you enjoyed this session', description=f'Session: **{session}**\nStatus: **ended**\nCheck <#842840247980261486> for session statistics!')
            await message.channel.send(embed=embed2)
            await end_function(ctx, session)
        else:
            return


@bot.command(aliases=['m'])
async def move(ctx, session):
    await move_to_session_vc(ctx, session)


@bot.command(aliases=["joinsession"])
async def join_to(message, session: str):
    if session != session_dict[f'{session}_voice_channel']:
        return
    await ask_to_join(message, session)


@bot.command(help='Voice channel bot join')
async def bot_join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@bot.command()
async def test(message, session: str):
    get_last_stat(PLAYERS, session)


@bot.command(help='Voice channel bot leave')
async def leavee(ctx):
    await ctx.voice_client.disconnect()


@bot.command(help="Sends funny picture")
async def russia(message):
    await command_russia(message)


@bot.command(help="Sends random video of best csgo plays")
async def cheater(message):
    await command_cheater(message)


@bot.command(help="If u forget to pray, `!pochvalen` command is for you")
async def pochvalen(message):
    await command_pochvalen(message)


@bot.command()
async def table(message):
    await create_stats_table()


@bot.command()
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


async def create_vc_channel(guild, game: str, number: int):
    allowed_role = discord.utils.get(guild.roles, name="gaming")
    banned_role = discord.utils.get(guild.roles, name="MUNI")
    banned_role_1 = discord.utils.get(guild.roles, name="lachtan")
    overwrites = {
        allowed_role: discord.PermissionOverwrite(connect=True),
        banned_role: discord.PermissionOverwrite(connect=False),
        banned_role_1: discord.PermissionOverwrite(connect=False),

    }
    new_voice_channel = await guild.create_voice_channel(name=f"{game} session", category=bot.get_channel(GAMING_CATEGORY), user_limit=number+1, overwrites=overwrites)
    session_dict[f'{game}_voice_channel'] = new_voice_channel
    if session_dict[f'{game}_soviet_session'] is True:
        await russian_anthem(new_voice_channel)


async def russian_anthem(channel):
    paths_to_anthem = ['mp3/soviet_anthem_0.mp3', 'mp3/soviet_anthem_1.mp3']
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio(random.choice(paths_to_anthem)), after=lambda e: print('done', e))
    await asyncio.sleep(195)
    await vc.disconnect()


async def set_vars_to_dict(message, game: str, number: int):
    list_for_i_message[f"{game}_ready_list"] = []
    html_dict["session"] = game
    html_dict["max_players"] = number
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
    welcome_to_session = ['This is', 'Say hi to', 'Wanna join?', "I'ts gonna be fun with ", '"Here comes the"', 'Something is waiting for you to join -', "Very tempting, isn't it?", "Now, you can't stop it", 'you, are, addicted...']

    if session_dict[f'{started_session}_gaming_session'] is True:
        await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))
        await game_presence(started_session)

    max_players = session_dict[f'{started_session}_max_players']

    embed = discord.Embed(title=f"**{random.choice(welcome_to_session)} {started_session} session**", description=f"Started by **{message.author}**\nSession: **{started_session}**\nPlayers able to join: **{max_players}**")
    embed.set_footer(text=f"Join with emoji reaction below ↓")
    first_session_ms = await message.channel.send(embed=embed)
    session_dict[f'{started_session}_first_ms_id'] = first_session_ms.id
    emojis = ['❌', '✅', '📊', '🔊', '🎮', '<:ouremoji:851164594320048208>']
    for emoji in emojis:
        await first_session_ms.add_reaction(emoji)

    list_for_i_message[f"{started_session}_ready_list"].append(message.author.mention)
    ready_list.append(message.author.id)
    html_ready_list.append(message.author.name)


async def session_ready(payload, session):
    """Sends ready information message"""
    if session != session_dict[f'{session}_game']:
        return
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    session_dict[f'{session}_ready_players'] += 1
    # await move_to(session_dict[f'{session_to}_voice_channel'].id, message)

    session_dict[f'{session}_ready_list'].append(member.id)
    list_for_i_message[f"{session}_ready_list"].append(member.mention)

    if session_dict[f'{session}_gaming_session'] is True:
        await guild.get_member(member.id).add_roles(guild.get_role(GAMING_ROLE))

    ready_list.append(member.id)
    html_ready_list.append(member.name)

@bot.command()
async def ooo(ctx):
  await ctx.channel.send('⏱️')
  await ctx.message.add_reaction('⏱️')
  # add timer option -> on_reaction_event... assign_fucker_role
  # test -> it worked...


async def ending_of_session(payload, ended_session: str):
    """Sends last ready information message, execute timer to assign fucker and delete all things that was in before session"""
    ending_messages = ["Let's go!", 'Full of upcoming fun!', 'Players - registred.', 'All ready', 'Prepare for battle', "Players, don't pee your pants", "Let's save the world", "Let's blow up the world"]

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    channel = await bot.fetch_channel(payload.channel_id)

    session_dict[f'{ended_session}_ready_list'].append(member.id)
    list_for_i_message[f"{ended_session}_ready_list"].append(member.mention)

    after_ready_list_members = ', '.join(list_for_i_message[f'{ended_session}_ready_list'])
    all_p = session_dict[f'{ended_session}_max_players']
    embed = discord.Embed(title=f'**{ended_session}** session. {random.choice(ending_messages)}', description=f'Players: **{all_p}**/**{all_p}**\nPlayers list: {after_ready_list_members}')
    embed.set_footer(text="Enjoy this session! Don't forget to launch CS:GO!")
    await channel.send(embed=embed)

    if session_dict[f'{ended_session}_create_vc'] is True:
        number = session_dict[f'{ended_session}_max_players']
        await create_vc_channel(guild, ended_session, number)

    if session_dict[f'{ended_session}_statistics'] is True:
        for name in html_ready_list:
            check_list(name)
        get_before_stat(final_users_list)

    for single_message in all_messages:
        await single_message.delete()

    if session_dict[f'{ended_session}_gaming_session'] is True:
        for member_id in session_dict[f'{ended_session}_ready_list']:
            await guild.get_member(member_id).add_roles(guild.get_role(GAMING_ROLE))
    await default_presence()

    html_dict.pop("session")
    html_dict.pop("max_players")
    all_messages.clear()
    ready_list.clear()
    html_ready_list.clear()


def check_list(user):
    if user == 'CerveneTlacitko':
        final_users_list.append(('t_kmaso', 'Kmasko', KMASKO_DICT['personaname']))
    if user == 'teetou':
        final_users_list.append(('t_teetou', 'Teetou', TEETOU_DICT['personaname']))
    if user == 'Bonsai':
        final_users_list.append(('t_aligator', 'Aligator', ALIGATOR_DICT['personaname']))
    if user == 'milan čonka':
        final_users_list.append(('t_stano', 'Stano', STANO_DICT['personaname']))
    if user == 'Tajmoti':
        final_users_list.append(('t_tajmoti', 'Tajmoti', TAJMOTI_DICT['personaname']))
    if user == 'andrzej':
        final_users_list.append(('t_dron', 'Dron', DRON_DICT['personaname']))


async def end_function(ctx, vc_name):
    existing_channel = discord.utils.get(ctx.guild.channels, name=f"{vc_name} session")
    general_channel = discord.utils.get(ctx.guild.channels, name="General")
    if existing_channel is None:
        await ctx.send(f'No channel named "{vc_name}" was found')
        return
    for member in session_dict[f'{vc_name}_ready_list']:
        user = bot.get_user(member)
        await ctx.guild.get_member(user.id).remove_roles(ctx.guild.get_role(GAMING_ROLE))

    for member in ctx.author.voice.channel.members:
        await member.move_to(general_channel)

    if existing_channel is not None:
        await existing_channel.delete()
    if session_dict[f'{vc_name}_statistics'] is True:
        get_last_stat(final_users_list, vc_name)
    await asyncio.sleep(5)
    if session_dict[f'{vc_name}_statistics'] is True:
        await create_stats_table()
    await pop_items_in_dict(vc_name)
    final_users_list.clear()


async def pop_items_in_dict(session):
    keys_to_pop = [f'{session}_started_by_id', f'{session}_playing_users', f'{session}_ready_list', f'{session}_game', f'{session}_max_players', f'{session}_ready_players', f'{session}_statistics', f'{session}_create_vc', f'{session}_gaming_session', f'{session}_voice_channel', f'{session}_first_ms_id', f'{session}_soviet_session']
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
    await channel.edit(user_limit=channel.user_limit + 1)
    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))


async def create_stats_table():
    channel = await bot.fetch_channel(842840247980261486)
    myEmbed = discord.Embed(title='Statistics for **{}** session'.format(get_stat('session', 'Kmasko')))
    for env, nice, steam in final_users_list:
        myEmbed.add_field(name=f'**{steam}**', value='> Kills: {}\n> Deaths: {}'.format(get_stat('total_kills', (nice)), get_stat('total_deaths', (nice))), inline=True)
        myEmbed.set_footer(text=get_stat('datetime', 'Kmasko'))
    await channel.send(embed=myEmbed)


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
    if payload.user_id not in ready_list:
        return
    if session_dict[f'{session}_ready_players'] == 1:
        return
    if payload.user_id in playing_users:
        playing_users.remove(payload.user_id)
    session_dict[f'{session}_ready_players'] -= 1

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    ready_list.remove(payload.user_id)
    html_ready_list.remove(member.name)


async def timer_assign_fucker(choose_timer: int):
    await asyncio.sleep(choose_timer)


async def assing_fucker_role(message, game):
    """After 5minutes it compare playing users with ready users and according to result,
  add role to ready player but not playing"""
    await timer_assign_fucker(120)
    role = message.guild.get_role(812862836710834207)
    suka_list = []
    checker = []
    missing_players = []
    print("Timer ended")
    for i in session_dict[f'{game}_ready_list']:
        if i in playing_users:
            checker.append(True)
        else:
            checker.append(i)
    if checker.count(True) != len(checker):
        missing_players.append(checker)
        for f_player in missing_players[0]:
            user = bot.get_user(f_player)
            await message.guild.get_member(user.id).add_roles(role)
            suka_list.append(user.mention)
        embed = discord.Embed(title='Wall of shame!', description=f'Shame on you {suka_list[0]}!')
        embed.set_footer(text="Get rid of this role by launching CS:GO under 2 minutes!")
        await message.channel.send(embed=embed)

    else:
        print("equal")

    x = [value for value in ready_list if value in playing_users]
    x_list = []
    x_list.append(x)
    for u_player in x_list[0]:
        unban_user = bot.get_user(u_player)
        await message.guild.get_member(unban_user.id).remove_roles(role)


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


async def command_pochvalen(message):
    """Replies 'aj naveky, amen' to the player saying pochvalen."""
    myEmbed = discord.Embed(title="Aj naveky, Amen.",
                            description=PRAYERS,
                            color=0xff0000)
    myEmbed.set_footer(text="Pozdravujem všetkých poliakov!")
    await message.channel.send(embed=myEmbed)


async def default_presence():
    soviet_songs = ['[If Tomorrow War Comes] music: Pokrass brothers', '[The Sacred War] music: A. Alexandrov', '[Invincible and legendary] music: A. Alexandrov', '[Dark girl] music: A. Novikov', '[We the Red Soldiers]', '[White Army, Black Baron] music: Samuil Pokrass', '[Song about Shchors] music: M. Blanter', '[Red flag]', '[Katyusha] music: M. Blanter', '[Blue headkerchief] music: E. Peterburgsky']
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name=random.choice(soviet_songs)))


async def game_presence(game):
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing, name=f'In {game} lobby'))


async def send_report_message(message):
    report_channel = bot.get_channel(777200768842858506)
    await report_channel.send(f'{message.author.mention} tried to send "** {message.content} **" in **{message.channel}** channel\nStop! Thats not channel for that stuff!')


# REDDIT
reddit = asyncpraw.Reddit(
                    client_id=os.getenv('client_id'),
                    client_secret=os.getenv('client_secret'),
                    username=os.getenv('username'),
                    password=os.getenv('password'),
                    user_agent="pythonpraw"
                    )


async def spacex_reddit():
    spacex_channel = bot.get_channel(818166852064247818)
    facts_channel = bot.get_channel(819169067747246120)
    spacex_subreddit = await reddit.subreddit("spacex")
    facts_subreddit = await reddit.subreddit("facts")
    async for spacex_submission in spacex_subreddit.stream.submissions(skip_existing=True):
        extension = spacex_submission.url[len(spacex_submission.url) - 3 :].lower()
        if "jpg" not in extension and "png" not in extension:
            await reddit_message_img(spacex_channel, spacex_submission.subreddit,
            spacex_submission.title, '<3', 'https://i.imgur.com/hzrRwO3.png', 1
            )
        else:
            await reddit_message_img(spacex_channel, spacex_submission.subreddit, spacex_submission.title, '',spacex_submission.url, 1
            )

        async for facts_submission in facts_subreddit.stream.submissions(skip_existing=True):
            if len(facts_submission.selftext) + len(facts_submission.title) > 255:
                await reddit_message_img(facts_channel, facts_submission.subreddit,
                facts_submission.title, 'To see more -> link', facts_submission.url, 0
                )
            else:
                await reddit_message_img(facts_channel, facts_submission.subreddit,
                facts_submission.title, facts_submission.selftext, facts_submission.url, 0
                )


async def reddit_message_img(reddit_channel, subreddit_name, post_title, post_description, post_link, i):
    embed = discord.Embed(title=f"r/{subreddit_name}", url=f"{post_link}", color=0x0)
    if len(post_description) + len(post_title) < 255:
        embed.add_field(name=f"{post_title}", value=f"{post_description}")
    if i == 1:
        embed.set_image(url=f"{post_link}")
    await reddit_channel.send(embed=embed)
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

    # if str(message.channel) == 'test' and message.attachments[0].url is not None:
    #     await read_image(message)

    if str(message.channel) != 'bot-commands' and message.content[0] == '!':
        if message.author.name != 'CerveneTlacitko':
            await message.delete()
            await send_report_message(message)
            return

    if str(message.channel) == 'bot-commands' and message.content[0] != '!':
        if message.content not in POSITIVE:
            await message.delete()
            await send_report_message(message)
            return
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


@bot.command()
async def playy(ctx):
    voicechannel = discord.utils.get(ctx.guild.channels, name='General') # ctx.author.voice.channel
    vc = await voicechannel.connect()
    vc.play(discord.FFmpegPCMAudio("rickrollaf.mp3"), after=lambda e: print('done', e))


@bot.event
async def on_command_error(ctx, error):
    answers = ['Huh?', 'You are trying impossible', '"Human being"', 'I just sometimes ask, why.', 'No way', 'Again?', 'Just...', 'XD', 'Wtf dude.', '2+2?', 'No comment']
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title=random.choice(answers), description='Check spelling', color=0xff1414)
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=random.choice(answers), description=f'Missing a required argument `<{error.param.name}>`.  Do !help', color=0xff1414)
        await ctx.send(embed=embed)
    raise error


@bot.event
async def on_ready():
    print("Discord -> connected")
    await default_presence()
    await spacex_reddit()
    await bot.process_commands

keep_alive()
bot.run(os.getenv('TOKEN'))
