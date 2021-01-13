import os
import discord
from keep_alive import keep_alive

client = discord.Client()
ready = 0


@client.event
async def on_message(message):
    if (message.author == client.user):
        return
                
    if message.content == '!ready':
        global ready_list
        global ready
    
        if message.author not in ready_list:
            ready += 1
            ready_list.add(message.author)

        
        
            totalMembers = 5                                             
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
                ready = 0
                ready_list.clear()


    if message.content == "!unready" and message.author in ready_list: 
        ready -= 1
        ready_list.remove(message.author)
        await message.channel.send(f'Lachtan |{message.author}| is unready')
    




keep_alive()
client.run(os.getenv('TOKEN'))