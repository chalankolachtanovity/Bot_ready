from os import listdir
from os.path import isfile, join
import random
import os
import discord
from keep_alive import keep_alive
ready_list = []
client = discord.Client()
ready = 0


PRAYERS = 'Otče náš, ktorý si na nebesiach, posväť sa meno tvoje, príď kráľovstvo tvoje, buď vôľa tvoja ako v nebi, tak i na zemi. Chlieb náš každodenný daj nám dnes a odpusť nám naše viny, ako i my odpúšťame svojim vinníkom, a neuveď nás do pokušenia, ale zbav nás zlého.\nAmen.\n:church::cross::church:   '

READY_PLAYER_THRESHOLD = 5

async def command_pochvalen(message):
    """Replies 'aj naveky, amen' to the player saying pochvalen."""
    myEmbed = discord.Embed(title="Aj naveky, Amen.", description=PRAYERS, color=0xff0000)
    myEmbed.set_footer(text="Pozdravujem všetkých poliakov!")
    await message.channel.send(embed=myEmbed)

async def get_message_for_nth_player(pos: int, player_name: str) -> str:
  """Creates a message inofrming which player has just become ready."""
  if pos == 1:     
      return f'1️⃣ First lachtan is ready ✅✨ ``` {player_name} ```'
  elif pos == 2:
      return f'2️⃣ Second lachtan is ready ✅✨ ``` {player_name} ```'
  elif pos == 3:
      return f'3️⃣ Third lachtan is ready ✅✨ ``` {player_name} ```'
  elif pos == 4:
      return f'4️⃣ Fourth lachtan is ready, last one remains ✅✨ ``` {player_name} ```'
  elif pos == READY_PLAYER_THRESHOLD:
      return f'5️⃣ |`{player_name}`| Every lachtan is ready, prepare for extreme praying! ⛪ 🎮 ⛪ '


async def command_ready(message):
    """If a player is not already ready, adds him to the
    ready list and prints a friendly informative message about his ready state.
    If READY_PLAYER_THRESHOLD are now ready, clears the ready list and
    wishes all players a good game."""
    global ready_list

    if message.author not in ready_list:
        ready_list.append(message.author)
        ready_count = len(ready_list)
        player_message = await get_message_for_nth_player(ready_count, message.author)
        await message.channel.send(player_message)
        if ready_count == READY_PLAYER_THRESHOLD:
          ready_list.clear()

async def command_unready(message):
    if message.author not in ready_list:
      return
    ready_list.remove(message.author)
    await message.channel.send(f'Lachtan **|{message.author}|** is unready \nPlayers ready: {ready}')

async def command_russia(message): 
    images = await get_dir_files('rsimgs/')
    random_image = random.choice(images)
    await message.channel.send(file=discord.File(random_image))

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Polish Anthem'))

@client.event
async def on_message(message):
    if (message.author == client.user):
        return
    if message.content in ['Pochvalen', 'Pochválen', 'pochvalen', 'pochválen']:
        await command_pochvalen(message)
    if message.content == '!ready':
        await command_ready(message)
    if message.content == "!unready":
        await command_unready(message)
    if message.content == '!russia':
        await command_russia(message)
    if message.content == "!cheater":
        await command_cheater(message)

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

keep_alive()
client.run(os.getenv('TOKEN'))