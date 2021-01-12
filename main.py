import os
import discord
from keep_alive import keep_alive

client = discord.Client()
ready = 0


@client.event
async def on_message(message):
    if (message.author == client.user):
        return

    totalMembers = 5                
    if message.content == '!ready':
        global ready
        ready += 1
                                                    #1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ ✔️ ✅ 🎮 ✨    
        if (ready == 1):      
            await message.channel.send(f'1️⃣ First lachtan is ready ✅✨ ``` {message.author} ```')

        elif (ready == 2):
            await message.channel.send(f'2️⃣ Second lachtan is ready ✅✨ ``` {message.author} ```')

        elif (ready == 3):
            await message.channel.send(f'3️⃣ Third lachtan is ready ✅✨ ``` {message.author} ```')

        elif (ready == 4):
            await message.channel.send(f'4️⃣ Fourth lachtan is ready, last one remains ✅✨ ``` {message.author} ```')
    
        elif (ready == totalMembers):
            await message.channel.send(f'5️⃣ |`{message.author}`| Every lachtan is ready, prepare for extreme praying! ⛪ 🎮 ⛪ ')
            ready -= 5

    if message.content == '!all':
      await message.channel.send('Enjoy gaming!🎮 And remember!, more prayers, better game!🙏🙏🙏 \n```!ready was restored```')
      ready = 0
    




keep_alive()
client.run(os.getenv('TOKEN'))