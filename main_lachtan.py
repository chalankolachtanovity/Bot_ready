import asyncpraw
import json
import time
import random
import os
import asyncio
import discord
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
    html_dict["session"] = game 
    html_dict["max_players"] = number
    session_dict[f'{game}_ready_list'] = []
    session_dict[f'{game}_ready_list'].append(message.author.id)
    session_dict[f'{game}_game'] = game
    session_dict[f'{game}_max_players'] = number
    session_dict[f'{game}_ready_players'] = 0
    session_dict[f'{game}_ready_players'] += 1
    await get_message(message, message.author, game)
    await move_to(session_dict[f'{game}_voice_channel'].id, message)
    

async def create_vc_channel(message, game, number):
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


@client.command(aliases=["ask_join"])
async def join(message, session_to):
    await message.channel.send(f"**{message.author.name}**, you are able to join this session.")
    await ask_to_join(session_to, message)
      

async def ask_to_join(session, message):
    channel = session_dict[f'{session}_voice_channel']
    await channel.edit(user_limit=channel.user_limit+1)
    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))



@client.command(help='delete a channel with the specified name')
async def end(ctx, channel_name):
    await ctx.channel.send(f"**{ctx.author.name}** are you sure? (y/n)")
    
    try:
      message = await client.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30.0)
    
    except asyncio.TimeoutError:
        return
    else:
      if message.content in POSITIVE:
        await message.channel.send(f'The {channel_name} session ends...')
        await end_function(ctx, channel_name)
      else:
        return

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

  get_last_stat(final_users_list, vc_name)
  final_users_list.clear()

@client.command(help='Voice channel bot join')
async def bot_join(ctx):
    channel = ctx.author.voice.channel
    user = client.get_user(783750741700509766)
    await channel.connect()

@client.command()
async def test(message, session: str):
  get_last_stat(PLAYERS, session)

@client.command(help='Voice channel bot leave')
async def leave(ctx):
    await ctx.voice_client.disconnect()
    

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
    await get_message(message, message.author,
                      session_dict[f'{session_to}_game'])
    await move_to(session_dict[f'{session_to}_voice_channel'].id, message)


async def channel_check(message):
    if str(message.channel) != 'bot-commands' and message.content[0] == '!':
      await message.delete()
      await send_report_message(message)

@client.command(help="Removes user from the choosen session")
async def unready(message, session_in_unready):
    if session_in_unready != session_dict[f'{session_in_unready}_game']:
        await message.channel.send(f'Session "{session_to}" was not found')
        return
    await session_unready(message, session_in_unready, message.author)


@client.command(help="Sends funny picture")
async def russia(message):
    await command_russia(message)


@client.command(help="Sends random video of best csgo plays")
async def cheater(message):
    await command_cheater(message)


@client.command(help="If u forget to pray, `!pochvalen` command is for you")
async def pochvalen(message):
    await command_pochvalen(message)

async def first_session_message(message, first_name: str, started_session: str):
    """Sends starting session message"""
    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))
    await game_presence(started_session)
    list_for_i_message[f"{started_session}_ready_list"] = []
    list_for_i_message[f"{started_session}_ready_list"].append(first_name.mention)
    max_players = f"{session_dict[f'{started_session}_max_players']}"
    first_session_ms = await message.channel.send(
        f'**1. | {first_name.mention} |** started session: **{started_session}**\n**{max_players}** players are able to join'
    )
    all_messages.append(first_session_ms)
    ready_list.append(message.author.id)
    html_ready_list.append(message.author.name)


async def session_ready(message, player_name: str, session):
    """Sends ready information message"""
    session_dict[f'{session}_ready_list'].append(message.author.id)
    ready_user_message = f"{session_dict[f'{session}_ready_players']}"
    rdy_msg = await message.channel.send(
        f"**{ready_user_message}. {player_name.mention}** is ready in **{session}** session"
    )
    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))
    await ready_information(message, session, player_name)
    all_messages.append(rdy_msg)
    ready_list.append(message.author.id)
    html_ready_list.append(message.author.name)
  
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

async def ending_of_session(message, ending_name: str, ended_session: str):
    """Sends last ready information message, execute timer to assign fucker and delete all things that was in before session"""
    await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))
    ready_list.append(message.author.id)
    session_dict[f'{ended_session}_ready_list'].append(message.author.id)
    html_ready_list.append(message.author.name)
    for name in html_ready_list:
      check_list(name)
    get_before_stat(final_users_list)
    full_players = f"{session_dict[f'{ended_session}_max_players']}"
    await message.channel.send(
        f'**{full_players}. | {ending_name.mention} |** Everyone is ready in **{ended_session}** session! \nEnjoy gaming!'
    )
    session_dict.pop(f'{ended_session}_ready_players')
    session_dict.pop(f'{ended_session}_game')
    session_dict.pop(f'{ended_session}_max_players')
    session_dict.pop(f"{ended_session}_voice_channel")
    html_dict.pop("session")
    html_dict.pop("max_players")
    if session_dict == {}:
        for single_message in all_messages:
            await single_message.delete()
    await assing_fucker_role(message, ended_session) #5 minutes break
    session_dict[f'{ended_session}_ready_list'].pop  
    await default_presence()
    all_messages.clear()
    ready_list.clear()
    html_ready_list.clear()


async def get_message(message, player_name, session):
    """Sends message according to ready players"""
    if session_dict[f'{session}_ready_players'] == 1:
        await first_session_message(message, player_name, session)

    if session_dict[f'{session}_ready_players'] >= 2 and session_dict[f'{session}_ready_players'] != session_dict[f'{session}_max_players']:
        await session_ready(message, player_name, session)

    if session_dict[f'{session}_ready_players'] == session_dict[f'{session}_max_players']:
        await ending_of_session(message, player_name, session)


async def session_unready(message, session_in_unready, player_to_unready):
    if message.author.id not in ready_list:
        return
    if session_dict[f'{session_in_unready}_ready_players'] == 1:
      return
    if message.author.id in playing_users:
        playing_users.remove(message.author.id)
    session_dict[f'{session_in_unready}_ready_players'] -= 1

    players_ready = f"{session_dict[f'{session_in_unready}_ready_players']}"
    unready_information_mes = await message.channel.send(
        f'Lachtan **| {message.author} |** is unready\nPlayers ready: {players_ready}'
    )
    await unready_information(message, session_in_unready, player_to_unready.mention)
    ready_list.remove(message.author.id)
    html_ready_list.remove(message.author.name)
    all_messages.append(message.message)
    all_messages.append(unready_information_mes)


async def ready_information(message, session, player_name):
    """Simple function to send ready list after some user being ready"""
    list_for_i_message[f"{session}_ready_list"].append(player_name.mention)
    after_ready_list_members = f"{list_for_i_message[f'{session}_ready_list']}"
    ready_list_ms = await message.channel.send(
        f"**{session} ready list:** {after_ready_list_members}"
    )
    all_messages.append(ready_list_ms)


async def unready_information(message, session, player_name):
    """Simple function to send ready list after some user being unready"""
    list_for_i_message[f"{session}_ready_list"].remove(player_name)
    after_unready_list_members = f"{list_for_i_message[f'{session}_ready_list']}"
    ready_list_ms = await message.channel.send(
        f"**{session} ready list:** {after_unready_list_members}"
    )
    all_messages.append(ready_list_ms)


async def move_to(channel_id, message):
  channel = client.get_channel(channel_id) 
  await message.author.move_to(channel)


async def timer_assign_fucker(choose_timer: int):
    await asyncio.sleep(choose_timer)


async def assing_fucker_role(message, game):
    """After 5minutes it compare playing users with ready users and according to result, 
  add role to ready player but not playing"""
    await timer_assign_fucker(120) #default time is 
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
        await message.channel.send(f'| **{suka_list}** | enjoy your new role.')

    else:
        print("equal")

    x = [value for value in ready_list if value in playing_users]
    x_list = []
    x_list.append(x)
    for u_player in x_list[0]:
        unban_user = client.get_user(u_player)
        await message.guild.get_member(unban_user.id).remove_roles(role)


async def command_russia(message):
    images = await get_dir_files('rsimgs/')
    random_image = random.choice(images)
    await message.channel.send(file=discord.File(random_image))


async def get_dir_files(dirname: str) -> list:
    files = []
    for file in listdir(dirname):
        full_path = join(dirname, file)
        if isfile(full_path):
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
          type=discord.ActivityType.listening, name='SpaceX news'))


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


@client.event
async def on_message(message):
  if (message.author == client.user):
    return
  # await message.channel.send(message.attachments[0].url) this is cool
  if str(message.channel) != 'bot-commands' and message.content[0] == '!':
    await message.delete()
    await send_report_message(message)
  
  if str(message.channel) != 'general' and message.content[0] != '!':
    if message.content not in POSITIVE:
      await message.delete()
      await send_report_message(message)
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

@client.command()
async def spotify(ctx, invite_user, user: discord.Member = None):
    invited_user = await client.fetch_user(invite_user)
    if user == None:
        user = ctx.author
        pass
    if int(invite_user) == ctx.author.id:
      await ctx.channel.send("You cant invite yourself.")
      return
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
                await ctx.send(content=f"{invited_user.mention}, {user} invited you to listen this song!", embed=embed)

@client.event
async def ban_timoty(message):
    banned_channels = ['welcome', 'commands-info']
    if str(message.channel) in banned_channels and message.author.name == "Tajmoti" or message.author.name == "daddyndo1":
        await message.delete()


@client.event
async def on_member_join(member):
    embed=discord.Embed(title=f"**Hey {member.name}, welcome to Milošovy hrátky server!**", color=0x009dff)
    embed.set_author(name="by chalankolachtanovity")
    embed.add_field(name=":red_circle:Rules:", value="We don't have any rules, everything is moderated by bot **Lachtan**.\nType **!help**", inline=True)
    embed.set_thumbnail(url="https://m.smedata.sk/api-media/media/image/sme/6/30/3065226/3065226_600x400.jpeg?rev=3")
    embed.add_field(name=":red_circle:Bot Lachtan", value="Bot **Lachtan** is our unique bot with unique functions! Feel free to use him!", inline=False)
    embed.set_footer(text="enjoy!")
    await client.get_channel(783670260200767488).send(content=member.mention, embed=embed)
    #test id is 812777032613888132
    #default id is 783670260200767488

@client.event
async def on_ready():
  await default_presence()
  await spacex_reddit()
  

keep_alive()
client.run(os.getenv('TOKEN')) 