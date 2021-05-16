import asyncpraw
import sqlite3
import json
import time
import random
import os
import asyncio
import discord
import pytesseract as tess
import os
from PIL import Image
import requests
import PIL
import io
from discord import Spotify
from steam_stats import download_stats_for_player
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from stats_compare import *
from discord.ext import tasks
from random import randint
from threading import Timer
from main import *
all_messages = []
ready_list = []
html_ready_list = []
playing_users = []
final_users_list = []

####/Intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = True
intents.members = True
from discord import Member
####\Intents
client = commands.Bot(intents=intents, command_prefix='!')

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
#812860090620837889 TEST |#825875949413072957
GAMING_CATEGORY = 825872608091832332
#776876130929999905 TEST |#825872608091832332


class MyHelp(commands.MinimalHelpCommand):
    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), color=0x009dff)
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
    
    def get_command_signature(self, command):
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Help', description="Use `!help [command]` for more info on a command.", color=0x0062ff)
        for cog, commands in mapping.items():
           filtered = await self.filter_commands(commands, sort=True)
           command_signatures = [self.get_command_signature(c) for c in filtered]
           if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Commands Category")
                embed.add_field(name=cog_name, value="\n\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

            
    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=error)
        channel = self.get_destination()
        await channel.send(embed=embed)


client.help_command = MyHelp()

@client.command(help="Creates custom session with max players.")
async def startsession(message, game: str, number: int):
    """Create keys, values in dict and sends message according to user preferences"""
    if number <= MINIMAL_NUMBER:
        await message.channel.send('Error: Minimum players in the session is **2**!')
        return
    if number >= MAXIMAL_NUMBER:
        await message.channel.send(
            'Error: Maximum players in the session is **10**!')
        return
    if len(game) >= MAXIMAL_LEN_GAME:
        await message.channel.send('Error: Maximum lenght of game is **30**!')
        return
    if f'{game}_game' in session_dict:
        return
    all_messages.append(message.message)
    await create_vc_channel(message, game, number)
    await set_vars_to_dict(message, game, number)
    await get_message(message, game)
    # await move_to(session_dict[f'{game}_voice_channel'].id, message)

@client.command(help="Adds user to choosen session")
async def ready(message, session_to):
    if session_to != session_dict[f'{session_to}_game']:
        await message.channel.send(f'Session "{session_to}" was not found')
        return
    if message.author.id in ready_list and message.author.name != "CerveneTlacitko":
      await message.channel.send(f'You are already in "{session_to}"" session')
      return
    all_messages.append(message.message)
    session_dict[f'{session_to}_ready_players'] += 1
    await get_message(message, session_to)
    # await move_to(session_dict[f'{session_to}_voice_channel'].id, message)


@client.command(help="Removes user from the choosen session")
async def unready(message, session_in_unready):
    if session_in_unready != session_dict[f'{session_in_unready}_game']:
        await message.channel.send(f'Session "{session_in_unready}" was not found')
        return
    await session_unready(message, session_in_unready)


@client.command(help='delete a channel with the specified name')
async def end(ctx, channel_name):
    possible_q = ['really?', '100% sure?', 'for real?', 'are you sure?']
    embed = discord.Embed(title=f"**{ctx.author.name}**, {random.choice(possible_q)}", description='This cannot be undone.')
    await ctx.channel.send(embed=embed)
    
    try:
      message = await client.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30.0)
    
    except asyncio.TimeoutError:
        return
    else:
      if message.content in POSITIVE:
        embed2 = discord.Embed(title='I hope you enjoyed this session', description=f'Session: **{channel_name}**\nStatus: **ended**\nCheck #stats for session statistics!')
        await message.channel.send(embed=embed2)
        await end_function(ctx, channel_name)
      else:
        return


@client.command(aliases=["join"])
async def join_to(message, session: str):
    if session != session_dict[f'{session}_voice_channel']:
      return
    await ask_to_join(message, session)


@client.command(help='Voice channel bot join')
async def bot_join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@client.command()
async def test(message, session: str):
  get_last_stat(PLAYERS, session)


@client.command(help='Voice channel bot leave')
async def leave(ctx):
    await ctx.voice_client.disconnect()


@client.command(help="Sends funny picture")
async def russia(message):
    await command_russia(message)


@client.command(help="Sends random video of best csgo plays")
async def cheater(message):
    await command_cheater(message)


@client.command(help="If u forget to pray, `!pochvalen` command is for you")
async def pochvalen(message):
    await command_pochvalen(message)


@client.command()
async def table(message):
    await create_stats_table()


@client.command()
async def spotify(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author
        pass
    if user.activities:
        for activity in user.activities:
            if isinstance(activity, Spotify):
                embed = discord.Embed(
                    title = f"{user.name}'s Spotify",
                    description = "Listening to {}".format(activity.title),
                    color = 0xC902FF)
                embed.description = f"Link: \nhttps://open.spotify.com/track/{activity.track_id}"
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Artist", value=activity.artist)
                embed.add_field(name="Album", value=activity.album)
                embed.set_footer(text="Song started at {}".format(activity.created_at.strftime("%H:%M")))
                await ctx.send(embed=embed)


async def create_vc_channel(message, game: str, number: int):
    allowed_role = discord.utils.get(message.guild.roles, name="gaming")
    banned_role = discord.utils.get(message.guild.roles, name="MUNI")
    banned_role_1 = discord.utils.get(message.guild.roles, name="lachtan")
    overwrites = {
      allowed_role: discord.PermissionOverwrite(connect = True),
      banned_role: discord.PermissionOverwrite(connect = False),
      banned_role_1: discord.PermissionOverwrite(connect = False),

    }
    new_voice_channel = await message.guild.create_voice_channel(name = f"{game} session", category = client.get_channel(GAMING_CATEGORY), user_limit = number, overwrites=overwrites)
    session_dict[f'{game}_voice_channel'] = new_voice_channel


async def set_vars_to_dict(message, game: str, number: int):
    list_for_i_message[f"{game}_ready_list"] = []
    html_dict["session"] = game
    html_dict["max_players"] = number
    session_dict[f'{game}_ready_list'] = []
    session_dict[f'{game}_ready_list'].append(message.author.id)
    session_dict[f'{game}_game'] = game
    session_dict[f'{game}_max_players'] = number
    session_dict[f'{game}_ready_players'] = 0
    session_dict[f'{game}_ready_players'] += 1


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
    welcome_to_session = ['This is', 'Say hi to', 'Wanna join?', "I'ts gonna be fun with ", '"Here comes the"', 'Something is waiting for you', "Very tempting, isn't it?", "Now, you can't stop it", 'you, are, addicted...']

    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))
    await game_presence(started_session)

    list_for_i_message[f"{started_session}_ready_list"].append(message.author.mention)
    max_players = session_dict[f'{started_session}_max_players']

    embed = discord.Embed(title=f"**{random.choice(welcome_to_session)} {started_session} session**", description=f"**1.** {message.author}\nSession: **{started_session}**\nPlayers able to join: **{max_players}**")
    embed.set_footer(text=f"Join with > !ready {started_session}")
    first_session_ms = await message.channel.send(embed=embed)

    all_messages.append(first_session_ms)
    ready_list.append(message.author.id)
    html_ready_list.append(message.author.name)


async def session_ready(message, session):
    """Sends ready information message"""
    session_dict[f'{session}_ready_list'].append(message.author.id)
    list_for_i_message[f"{session}_ready_list"].append(message.author.mention)

    ready_user_message = session_dict[f'{session}_ready_players']
    after_ready_list_members = ', '.join(list_for_i_message[f'{session}_ready_list'])
    max_players = session_dict[f'{session}_max_players']

    embed = discord.Embed(title=f"**{ready_user_message}. {message.author}**", description=f"Session: **{session}**\nJoined players: **{ready_user_message}**/**{max_players}**\nReady list: {after_ready_list_members}")
    embed.set_footer(text=f"Join with > !ready {session}")
    rdy_msg = await message.channel.send(embed=embed)

    all_messages.append(rdy_msg)
    ready_list.append(message.author.id)
    html_ready_list.append(message.author.name)

    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))


async def ending_of_session(message, ended_session: str):
    """Sends last ready information message, execute timer to assign fucker and delete all things that was in before session"""
    ending_messages = ["Let's go!", 'Full of upcoming fun!', 'Players - registred.', 'All ready', 'Prepare for battle', "Players, don't pee your pants", "Let's save the world", "Let's blow up the world"]

    ready_list.append(message.author.id)
    html_ready_list.append(message.author.name)
    session_dict[f'{ended_session}_ready_list'].append(message.author.id)
    list_for_i_message[f"{ended_session}_ready_list"].append(message.author.mention)

    after_ready_list_members = ', '.join(list_for_i_message[f'{ended_session}_ready_list'])
    all_p = session_dict[f'{ended_session}_max_players']
    embed = discord.Embed(title=f'**{ended_session}** session. {random.choice(ending_messages)}', description=f'Players: **{all_p}**/**{all_p}**\nPlayers list: {after_ready_list_members}')
    embed.set_footer(text="Enjoy this session! Don't forget to launch CS:GO!")
    await message.channel.send(embed=embed)

    for name in html_ready_list:
      check_list(name)
    get_before_stat(final_users_list)

    for single_message in all_messages:
        await single_message.delete()

    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))
    await assing_fucker_role(message, ended_session) #2 minutes break
    await default_presence()

    session_dict[f'{ended_session}_ready_list'].pop
    session_dict.pop(f'{ended_session}_ready_players')
    session_dict.pop(f'{ended_session}_game')
    session_dict.pop(f'{ended_session}_max_players')
    html_dict.pop("session")
    html_dict.pop("max_players")
    all_messages.clear()
    ready_list.clear()
    html_ready_list.clear()


def check_list(user):
    if user == 'CerveneTlacitko':
      final_users_list.append(('t_kmaso','Kmasko'))
    if user == 'teetou':
      final_users_list.append(('t_teetou','Teetou'))
    if user == 'Bonsai':
      final_users_list.append(('t_aligator','Aligator'))
    if user == 'milan čonka':
      final_users_list.append(('t_stano','Stano'))
    if user == 'Tajmoti':
      final_users_list.append(('t_tajmoti','Tajmoti'))


async def end_function(ctx, vc_name):
  existing_channel = discord.utils.get(ctx.guild.channels, name=f"{vc_name} session")
  general_channel = discord.utils.get(ctx.guild.channels, name="General")
  if existing_channel is None:
    await ctx.send(f'No channel named "{vc_name}" was found')
    return
  for members in session_dict[f'{vc_name}_ready_list']:
    user = client.get_user(members)
    await ctx.guild.get_member(user.id).remove_roles(ctx.guild.get_role(GAMING_ROLE))

  for member in ctx.author.voice.channel.members:
    await member.move_to(general_channel)

  if existing_channel is not None:
    await existing_channel.delete()
    session_dict.pop(f"{vc_name}_voice_channel")

  get_last_stat(final_users_list, vc_name)
  await asyncio.sleep(5)
  await create_stats_table()
  final_users_list.clear()


async def move_to(channel_id, message):
  channel = client.get_channel(channel_id)
  await message.author.move_to(channel)


async def ask_to_join(message, session: str):
    channel = session_dict[f'{session}_voice_channel']
    embed = discord.Embed(title=f"{message.author.name}, you can join", description=f'Session: {session}')
    await message.channel.send(embed=embed)
    await channel.edit(user_limit=channel.user_limit+1)
    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))


async def create_stats_table():
    channel = await client.fetch_channel(842840247980261486)
    myEmbed = discord.Embed(title='Statistics for **{}** session'.format(get_stat('session', 'Kmasko')))
    for env, nice in final_users_list:
      myEmbed.add_field(name=f'**{nice}**', value='> Kills: {}\n> Deaths: {}'.format(get_stat('total_kills', (nice)), get_stat('total_deaths', (nice))),inline=True)
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


async def session_unready(message, session: str):
    if message.author.id not in ready_list:
        return
    if session_dict[f'{session}_ready_players'] == 1:
      return
    if message.author.id in playing_users:
        playing_users.remove(message.author.id)
    session_dict[f'{session}_ready_players'] -= 1

    list_for_i_message[f"{session}_ready_list"].remove(message.author.mention)
    after_unready_list_members = ', '.join(list_for_i_message[f'{session}_ready_list'])

    embed = discord.Embed(title=f"**{message.author}** is unready", description=f"session: {session}\nready list: {after_unready_list_members}")
    unready_information_mes = await message.channel.send(embed=embed)

    ready_list.remove(message.author.id)
    html_ready_list.remove(message.author.name)
    all_messages.append(message.message)
    all_messages.append(unready_information_mes)


async def timer_assign_fucker(choose_timer: int):
    await asyncio.sleep(choose_timer)


async def assing_fucker_role(message, game):
    """After 5minutes it compare playing users with ready users and according to result, 
  add role to ready player but not playing"""
    await timer_assign_fucker(120) #default time is 120
    role = message.guild.get_role(
        812862836710834207)  #test_role= 812860101672828938, default_role=812862836710834207
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
            user = client.get_user(f_player)
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
        unban_user = client.get_user(u_player)
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
    await client.change_presence(activity=discord.Activity(
          type=discord.ActivityType.listening, name='Rolling in the Deep'))


async def game_presence(game):
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing, name=f'In {game} lobby'))



async def send_report_message(message):
  report_channel = client.get_channel(777200768842858506) #test channel: 817104867671408660, default channel: 777200768842858506
  await report_channel.send(f'{message.author.mention} tried to send "** {message.content} **" in **{message.channel}** channel\nStop! Thats not channel for that stuff!')


###REDDIT###
reddit = asyncpraw.Reddit(
                    client_id=os.getenv('client_id'),
                    client_secret =os.getenv('client_secret'),
                    username = os.getenv('username'),
                    password = os.getenv('password'),
                    user_agent = "pythonpraw"
                    )   
async def spacex_reddit():
  spacex_channel = client.get_channel(818166852064247818)#testid 818166852064247818
  facts_channel = client.get_channel(819169067747246120)
  spacex_subreddit = await reddit.subreddit("spacex")
  facts_subreddit = await reddit.subreddit("facts")
  async for spacex_submission in spacex_subreddit.stream.submissions(skip_existing=True):
    extension = spacex_submission.url[len(spacex_submission.url) - 3 :].lower()
    if "jpg" not in extension and "png" not in extension:
      numbr = 1
      await reddit_message_img(spacex_channel, spacex_submission.subreddit,
      spacex_submission.title, spacex_submission.url, numbr
      )
    else:
      nmbr = 2
      await reddit_message_img(spacex_channel, spacex_submission.subreddit, spacex_submission.title,
       spacex_submission.url, nmbr)

    async for facts_submission in facts_subreddit.stream.submissions(skip_existing=True):
      number = 3
      await reddit_message_img(facts_channel, facts_submission.subreddit,
      facts_submission.title, facts_submission.author, number
      )
  

async def reddit_message_img(reddit_channel, subreddit_name, post_title, post_link, pos):
    if pos == 3:
      embed=discord.Embed(title=f"r/{subreddit_name}", description=f"{post_title}", color=0x0)
      await reddit_channel.send(embed=embed)
    if pos !=3:
      if pos == 1:
        embed=discord.Embed(title=f"r/{subreddit_name}", url=f"{post_link}", description=f"{post_title}", color=0x0)
        await reddit_channel.send(embed=embed)
      if pos == 2:
        embed=discord.Embed(title=f"r/{subreddit_name}", url=f"{post_link}", description=f"{post_title}", color=0x0)
        embed.set_image(url=f"{post_link}")
        await reddit_channel.send(embed=embed)
###REDDIT###

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


@client.event
async def on_message(message):
  if (message.author == client.user):
    return

  if str(message.channel) == 'test' and message.attachments[0].url != None:
    await read_image(message)

  if str(message.channel) != 'bot-commands' and message.content[0] == '!':
    if message.author.name != 'CerveneTlacitko':
      await message.delete()
      await send_report_message(message)
      return
  
  if str(message.channel) == 'general' and message.content[0] == '!':
    if message.content not in POSITIVE:
      await message.delete()
      await send_report_message(message)
      return
  await client.process_commands(message)


@client.event
async def on_member_update(before, curr):
    """Adds member to playing users list when he changed activity"""
    games = ["counter-strike: global offensive", "payday 2", "test"]
    if curr.activity and curr.activity.name.lower() in games:
        if curr.id not in playing_users:
            playing_users.append(curr.id)

    if before.activity and before.activity.name.lower() in games and curr.activities not in games:
        if curr.id in playing_users:
            playing_users.remove(curr.id)

@client.event
async def ban_timoty(message):
    banned_channels = ['welcome', 'commands-info']
    if str(message.channel) in banned_channels and message.author.name == "Tajmoti" or message.author.name == "daddyndo1":
        await message.delete()


@client.event
async def on_member_join(member):
    embed = discord.Embed(title=f"**Hey {member.name}, welcome to Milošovy hrátky server!**", color=0x009dff)
    embed.set_author(name="by chalankolachtanovity")
    embed.add_field(name=":red_circle:Rules:", value="We don't have any rules, everything is moderated by bot **Lachtan**.\nType **!help**", inline=True)
    embed.set_thumbnail(url="https://m.smedata.sk/api-media/media/image/sme/6/30/3065226/3065226_600x400.jpeg?rev=3")
    embed.add_field(name=":red_circle:Bot Lachtan", value="Bot **Lachtan** is our unique bot with unique functions! Feel free to use him!", inline=False)
    embed.set_footer(text="enjoy!")
    await client.get_channel(783670260200767488).send(content=member.mention, embed=embed)
    #test id is 812777032613888132
    #default id is 783670260200767488

@client.event
async def on_command_error(ctx, error):
    print(error)
    answers = ['Huh?', 'You are trying impossible', '"Human being"', 'I just sometimes ask, why.', 'No way', 'Again?', 'Just...', 'XD', 'Wtf dude.', '2+2?', 'No comment']
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title=random.choice(answers), description='Check spelling')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=random.choice(answers), description='Missing a required argument.  Do !help')
        await ctx.send(embed=embed)

@client.event
async def on_ready():
  print("Discord -> connected")
  await default_presence()
  await spacex_reddit()
  await client.process_commands

keep_alive()
client.run(os.getenv('TOKEN'))

