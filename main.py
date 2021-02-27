import json
from discord.ext import commands
from os import listdir
from os.path import isfile, join
import random
import os
import asyncio
import discord
from keep_alive import keep_alive
from discord.ext import tasks
all_messages = []
ready_list = []
playing_users = []
from random import randint

####
intents = discord.Intents.default()
intents.typing = False
intents.presences = True
intents.members = True
from discord import Member
####
client = commands.Bot(intents=intents, command_prefix='!')

from threading import Timer
import time

ready = 0

PRAYERS = 'Otče náš, ktorý si na nebesiach, posväť sa meno tvoje, príď kráľovstvo tvoje, buď vôľa tvoja ako v nebi, tak i na zemi. Chlieb náš každodenný daj nám dnes a odpusť nám naše viny, ako i my odpúšťame svojim vinníkom, a neuveď nás do pokušenia, ale zbav nás zlého.\nAmen.\n:church::cross::church:   '

READY_PLAYER_THRESHOLD = 5

async def command_pochvalen(message):
    """Replies 'aj naveky, amen' to the player saying pochvalen."""
    myEmbed = discord.Embed(title="Aj naveky, Amen.",
                            description=PRAYERS,
                            color=0xff0000)
    myEmbed.set_footer(text="Pozdravujem všetkých poliakov!")
    await message.channel.send(embed=myEmbed)


SESSION_DICT = {
  "session_ready_players":0
}

async def first_session_message(message, first_p_name: str, started_session: str):
  list_of_users.append(message.author.mention)
  first_ms = await message.channel.send(f'| **{first_p_name}** | started session: **{started_session}** \n{SESSION_DICT["player_number"]} players are able to join ')
  ready_list.append(message.author.id)
  all_messages.append(first_ms)


async def session_ready(message, ready_player_name: str, ready_session):
    ready_list.append(message.author.id)
    if message.author.id not in ready_list:
      rdy_msgs = await message.channel.send(f'{SESSION_DICT["session_ready_players"]}. {ready_player_name} is ready in {ready_session} session')
      all_messages.append(rdy_msgs)
      await ready_information(message)

async def all_session_ready(message, last_p_name:str, before_session:str):
    ready_list.append(message.author.id)
    await message.channel.send(f'| **{last_p_name}** | Everyone is ready in {before_session} session! \nEnjoy gaming!')
    SESSION_DICT["session_ready_players"] = 0
    SESSION_DICT.pop("game")
    SESSION_DICT.pop("player_number")
    for single_message in all_messages:
      await single_message.delete()

    await timer_to_start_csgo(message)
    all_messages.clear()
    ready_list.clear()
    list_of_users.clear()


async def all_session_messages(message, player_name, session):
  if SESSION_DICT['session_ready_players'] == 1:
    await first_session_message(message, player_name, session)
  
  if SESSION_DICT['session_ready_players'] >= 2 and SESSION_DICT['session_ready_players'] != SESSION_DICT['player_number']:
    print('ready doing')
    await session_ready(message, player_name, session)
  
  if SESSION_DICT['session_ready_players'] == SESSION_DICT['player_number']:
      await all_session_ready(message, player_name, session)


@client.command()
async def startsession(message, game: str, number: int):
    if number <= 1:
      return
    if number >= 11:
      await message.channel.send('Maximum players in session is **10**!')
      return
    if len(game) >= 30:
      await message.channel.send('Maximum lenght of game is **30**!')
      return
    all_messages.append(message.message)
    SESSION_DICT['game'] = game
    SESSION_DICT['player_number'] = number
    SESSION_DICT['session_ready_players'] += 1
    await all_session_messages(message, message.author, game)


@client.command()
async def ready(message, ready_session):
    if ready_session != SESSION_DICT['game']:
      return 
    if message.author.id in ready_list:
      return
    all_messages.append(message.message)
    SESSION_DICT['session_ready_players'] += 1
    if SESSION_DICT['session_ready_players'] == 0:
      return
    await all_session_messages(message, message.author, SESSION_DICT['game'])
    

async def session_unready(message):
    if message.author.id not in ready_list:
        return
    if message.author.id in playing_users:
      playing_users.remove(message.author.id)
    SESSION_DICT['session_ready_players'] -= 1
    ready_list.remove(message.author.id)
    unready_information_mes = await message.channel.send(
        f'Lachtan **| {message.author} |** is unready\nPlayers ready: {SESSION_DICT["session_ready_players"]}')
    all_messages.append(message.message)
    all_messages.append(unready_information_mes)
    await unready_information(message)


@client.command()
async def unready(message, unready_session):
  if unready_session != SESSION_DICT['game']:
      return 
  await session_unready(message)


@client.command()
async def russia(message):
  await command_russia(message)

@client.command()
async def cheater(message):
  await command_cheater(message)

@client.command(aliases=['Pochvalen', 'Pochválen', 'pochválen'])
async def pochvalen(message):
  await command_pochvalen(message)

@client.command()
async def all(message):
  await all()


list_of_users = []

async def ready_information(message):
    list_of_users.append(message.author.mention)
    new_list_users = (', '.join(list_of_users))
    ready_users_mes = await message.channel.send(f"**Ready list:** {new_list_users}")
    all_messages.append(ready_users_mes)


async def unready_information(message):
    list_of_users.remove(message.author.mention)
    new_list_users = (', '.join(list_of_users))
    ready_users_mes = await message.channel.send(f"**Ready list:** {new_list_users}")
    all_messages.append(ready_users_mes)


async def timer_assign_fucker(choose_timer: int):
    print("doing stuff")
    await asyncio.sleep(choose_timer)



async def timer_to_start_csgo(message):
  await timer_assign_fucker(10)
  role = message.guild.get_role(812860101672828938)
  print("Timer ended")
  suka_list = []
  checker = []
  missing_players = []
  for i in ready_list:
      if i in playing_users:
          checker.append(True)
      else:
          checker.append(i)
  if checker.count(True) != len(checker):
    print(f'ready list = {ready_list}')
    print(f'playing users = {playing_users}')
    print(f'missing players: {checker}')
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



@client.event
async def on_member_update(before, curr):  
    games = ["counter-strike: global offensive", "test"]

    if curr.activity and curr.activity.name.lower() in games:
      if curr.name not in playing_users:
        playing_users.append(curr.id)

    if before.activity and before.activity.name.lower() in games and curr.activities not in games:
      if curr.name in playing_users:
        playing_users.remove(curr.id)



async def command_ready(message):
    """If a player is not already ready, adds him to the
    ready list and prints a friendly informative message about his ready state.
    If READY_PLAYER_THRESHOLD are now ready, clears the ready list and
    wishes all players a good game."""
    global ready_list

    # if message.author.name not in ready_list:
    ready_list.append(message.author.id)
    ready_count = len(ready_list)
    all_messages.append(message)
    
    await ready_information(message)
  
    if ready_count == READY_PLAYER_THRESHOLD:
        for idk in all_messages:
          await idk.delete()

        all_messages.clear()

        await timer_to_start_csgo(message)
        ready_list.clear()
        list_of_users.clear()
        

async def command_russia(message):
    images = await get_dir_files('rsimgs/')
    random_image = random.choice(images)
    await message.channel.send(file=discord.File(random_image))


@client.event
async def on_ready():
    print("Ready")


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name='Separ'))


async def delete_message_after_unready(message, nnumber):
    await message.channel.purge(limit=200, check=lambda x: str(nnumber) in x.content)
    print(nnumber)


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


@client.event
async def ban_timoty(message):
  banned_channels = ['welcome', 'commands-info']
  if str(message.channel) in banned_channels and message.author.name == "Tajmoti" or message.author.name == "daddyndo1":
    await message.delete()


keep_alive()
client.run(os.getenv('TOKEN'))

