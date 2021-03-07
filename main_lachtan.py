import asyncpraw
import json
import time
import random
import os
import asyncio
import discord
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from discord.ext import tasks
from random import randint
from threading import Timer
from main import *
all_messages = []
ready_list = []
playing_users = []

####/Intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = True
intents.members = True
from discord import Member
####\Intents
client = commands.Bot(intents=intents, command_prefix='!')

PRAYERS = 'Otče náš, ktorý si na nebesiach, posväť sa meno tvoje, príď kráľovstvo tvoje, buď vôľa tvoja ako v nebi, tak i na zemi. Chlieb náš každodenný daj nám dnes a odpusť nám naše viny, ako i my odpúšťame svojim vinníkom, a neuveď nás do pokušenia, ale zbav nás zlého.\nAmen.\n:church::cross::church:'

ready_users_list = {}

session_dict = {}

MINIMAL_NUMBER = 1
MAXIMAL_NUMBER = 11
MAXIMAL_LEN_GAME = 30


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
    if str(message.channel) != "bot-commands":
      await message.message.delete()
      await send_report_message(message)
      return
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
    session_dict[f'{game}_game'] = game
    session_dict[f'{game}_max_players'] = number
    session_dict[f'{game}_ready_players'] = 0
    session_dict[f'{game}_ready_players'] += 1
    await get_message(message, message.author, game)
    


@client.command(help="Adds user to choosen session")
async def ready(message, session_to):
    if str(message.channel) != "bot-commands":
      await message.message.delete()
      await send_report_message(message)
      return
    if session_to != session_dict[f'{session_to}_game']:
        return
    if message.author.id in ready_list:
      return
    all_messages.append(message.message)
    session_dict[f'{session_to}_ready_players'] += 1
    await get_message(message, message.author,
                      session_dict[f'{session_to}_game'])


@client.command(help="Removes user from the choosen session")
async def unready(message, session_in_unready):
    if str(message.channel) != "bot-commands":
      await message.message.delete()
      await send_report_message(message)
      return
    if session_in_unready != session_dict[f'{session_in_unready}_game']:
        return
    await session_unready(message, session_in_unready, message.author)


@client.command(help="Sends funny picture")
async def russia(message):
    if str(message.channel) != "bot-commands":
      await message.message.delete()
      await send_report_message(message)
      return
    await command_russia(message)


@client.command(help="Sends random video of best csgo plays")
async def cheater(message):
    if str(message.channel) != "bot-commands":
      await message.message.delete()
      await send_report_message(message)
      return
    await command_cheater(message)


@client.command(help="If u forget to pray, `!pochvalen` command is for you")
async def pochvalen(message):
    if str(message.channel) != "bot-commands":
      await message.message.delete()
      await send_report_message(message)
      return
    await command_pochvalen(message)

@client.command(help="spacex")
async def spacex(message):
  embed=discord.Embed(title="r/SpaceX", url="https://www.reddit.com/r/spacex/comments/lypki5/decommissioned_starship_snx_test_tanks_and/", description='**Sn11 launch estimated at 4pm**',color=0x000000)
  embed.set_image(url="https://www.nasaspaceflight.com/wp-content/uploads/2021/02/NSF-2021-02-07-23-06-16-827.jpg")
  await message.channel.send(embed=embed)


async def first_session_message(message, first_name: str, started_session: str):
    """Sends starting session message"""
    await game_presence(started_session)
    ready_users_list[f"{started_session}_ready_list"] = []
    ready_users_list[f"{started_session}_ready_list"].append(first_name.mention)
    max_players = f"{session_dict[f'{started_session}_max_players']}"
    first_session_ms = await message.channel.send(
        f'1. **| {first_name} |** started session: **{started_session}**\n**{max_players}** players are able to join'
    )
    all_messages.append(first_session_ms)
    ready_list.append(message.author.id)


async def session_ready(message, player_name: str, session):
    """Sends ready information message"""
    ready_user_message = f"{session_dict[f'{session}_ready_players']}"
    rdy_msg = await message.channel.send(
        f"**{ready_user_message}. {player_name}** is ready in **{session}** session"
    )
    await ready_information(message, session, player_name)
    all_messages.append(rdy_msg)
    ready_list.append(message.author.id)


async def ending_of_session(message, ending_name: str, ended_session: str):
    """Sends last ready information message, execute timer to assign fucker and delete all things that was in before session"""
    ready_list.append(message.author.id)
    full_players = f"{session_dict[f'{ended_session}_max_players']}"
    await message.channel.send(
        f'**{full_players}. | {ending_name} |** Everyone is ready in **{ended_session}** session! \nEnjoy gaming!'
    )
    session_dict.pop(f'{ended_session}_ready_players')
    session_dict.pop(f'{ended_session}_game')
    session_dict.pop(f'{ended_session}_max_players')
    if session_dict == {}:
        for single_message in all_messages:
            await single_message.delete()
    await assing_fucker_role(message)  #5 minutes break
    await default_presence()
    all_messages.clear()
    ready_list.clear()


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
    all_messages.append(message.message)
    all_messages.append(unready_information_mes)


async def ready_information(message, session, player_name):
    """Simple function to send ready list after some user being ready"""
    ready_users_list[f"{session}_ready_list"].append(player_name.mention)
    after_ready_list_members = f"{ready_users_list[f'{session}_ready_list']}"
    ready_list_ms = await message.channel.send(
        f"**{session} ready list:** {after_ready_list_members}"
    )
    all_messages.append(ready_list_ms)


async def unready_information(message, session, player_name):
    """Simple function to send ready list after some user being unready"""
    ready_users_list[f"{session}_ready_list"].remove(player_name)
    after_unready_list_members = f"{ready_users_list[f'{session}_ready_list']}"
    ready_list_ms = await message.channel.send(
        f"**{session} ready list:** {after_unready_list_members}"
    )
    all_messages.append(ready_list_ms)


async def timer_assign_fucker(choose_timer: int):
    print("doing stuff")
    await asyncio.sleep(choose_timer)


async def assing_fucker_role(message):
    """After 5minutes it compare playing users with ready users and according to result, 
  add role to ready player but not playing"""
    await timer_assign_fucker(300) #default time is 300
    role = message.guild.get_role(
        812862836710834207)  #test_role= 812860101672828938, default_role=812862836710834207
    suka_list = []
    checker = []
    missing_players = []
    print("Timer ended")
    for i in ready_list:
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
          type=discord.ActivityType.playing, name='Waiting in lobby'))


async def game_presence(game):
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing, name=f'In {game} lobby'))



async def send_report_message(message):
  report_channel = client.get_channel(777200768842858506) #test channel: 817104867671408660, default channel: 777200768842858506
  await report_channel.send(f'{message.author.mention} tried to send "** {message.content} **" in **{message.channel}** channel\nStop! Thats not channel for commands!')


###REDDIT###
reddit = asyncpraw.Reddit(
                    client_id="lSzeNaBj-R2kSw",
                    client_secret = "_MWFtFngy7JEglhZhRh7HL1Dzo_BJQ",
                    username = "CerveneTlacitko",
                    password = "vY5D4]ZWqb'>Hrt*YcFs",
                    user_agent = "pythonpraw"
                    )   
async def spacex_reddit():
  channel = client.get_channel(818166852064247818)#testid 814640180283441163
  subreddit = await reddit.subreddit("spacex")
  async for submission in subreddit.stream.submissions(skip_existing=True):
    await spacex_post_message(channel, submission.subreddit, submission.title, submission.url)


# async def facts_reddit():
#   channel = client.get_channel(818248378923745291)#testid 814640180283441163
#   subreddit = await reddit.subreddit("facts")
#   async for submission in subreddit.stream.submissions(skip_existing=False):
#     await spacex_post_message(channel, submission.subreddit, submission.title, submission.url)


async def spacex_post_message(reddit_channel, subreddit_name, post_title, post_url):
    embed=discord.Embed(title=f"r/{subreddit_name}", url=f"{post_url}", description=f"{post_title}", color=0x000000)
    embed.set_image(url=f"{post_url}")
    await reddit_channel.send(embed=embed)     
###REDDIT###


@client.event
async def on_message(message):
  if (message.author == client.user):
    return
  if str(message.channel) != 'bot-commands' and message.content[0] == '!':
    await message.delete()
    await send_report_message(message)
  
  await client.process_commands(message)


@client.event
async def on_member_update(before, curr):
    """Adds member to playing users list when he changed activity"""
    games = ["counter-strike: global offensive", "payday 2"] #while test mode on, add "test"
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
    embed=discord.Embed(title=f"**Hey {member.name}, welcome to Milošovy hrátky server!**", color=0x009dff)
    embed.set_author(name="by chalankolachtanovity")
    embed.add_field(name=":red_circle:Rules:", value="1. Dont write commands in general chat:bangbang:", inline=True)
    embed.add_field(name=":red_circle:Bot Lachtan", value="**Bot Lachtan** is our unique bot with unique functions! Feel free to use him!", inline=False)
    embed.set_footer(text="enjoy!")
    await client.get_channel(783670260200767488).send(content=member.mention, embed=embed)
    #test id is 812777032613888132
    #default id is 783670260200767488


@client.event
async def on_ready():
  # await facts_reddit()
  await spacex_reddit()
  

keep_alive()
client.run(os.getenv('TOKEN'))