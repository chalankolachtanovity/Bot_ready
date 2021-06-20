import discord
import json
import random
import os
import asyncio

os.chdir('/home/runner/Bot-Lachtan-2')

DOGE = '<:doge:856173922865512468>'

earth_first_field = """
🟦🟦🟦🟦🟦🟦🟦
🟦🟦🟦🟦🟦🟦🟦
🟦🟦🟦🟦🟦🟦🟦
🟦🟦🟦🟦🟦🟦🟦
🟦🟦🟦<:SN15:855791206546407424>🟦🟦🟦
<:yellow:855786772725235752><:yellow:855786772725235752><:yellow:855786772725235752><:yellow:855786772725235752><:yellow:855786772725235752><:yellow:855786772725235752><:yellow:855786772725235752>
"""


async def spacex_launch_to_mars(ctx, rocket_name):
    with open('spacex.json', 'r') as f:
        datas = json.load(f)

    rockets = datas[f'{ctx.author.id}_acc']['rockets']

    if rockets == []:
        embed = discord.Embed(title='Missing rocket', description='You have zero rockets in your inventory!')
        await ctx.send(embed=embed, delete_after=5)
        return

    if rocket_name in rockets:
        if datas[f'{ctx.author.id}_acc']['launches'] == 0:
            embed = discord.Embed(title='SpaceX launch', description=f'{earth_first_field}\nLaunches: 0\nProgress: 0')
            message = await ctx.send(embed=embed)
            datas[f'{ctx.author.id}_acc']['message_id'] = message.id

            embed = discord.Embed(title='Checks', description=' - TFR Activated\n - Pad Closeouts\n - Village cleared\n - Road closed\n - Pad cleared\n - Final checkouts\n - Recondenser\n - Tank Farm Activity\n - Methane vent\n - Engine chill\n - Launch imminent\n - Launch')
            message = await ctx.send(embed=embed)
            datas[f'{ctx.author.id}_acc']['checks_message_id'] = message.id

        for rocket in rockets:
            if rocket == rocket_name: 
                await spacex_launch_animation(ctx, datas, rocket)
                break
    else:
        embed = discord.Embed(title='Check spelling', description=f'You don\'t have any rocket called **{rocket_name}**')
        await ctx.send(embed=embed, delete_after=5)
        return

    with open('spacex.json', 'w') as f:
        json.dump(datas, f)


async def spacex_launch_from_earth_frames(g, launch, rocket, rotate_to_land, landing, end):
    frames = [
    f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{launch}🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
    f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
    f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
    f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
    f'🟦🟦🟦{rotate_to_land}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
    f'🟦🟦🟦{landing}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
    f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{landing}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}', 
    f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{landing}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
    f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rotate_to_land}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
    f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{end}🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
    ]
    return frames


async def spacex_launch_to_mars_frames(success_explosion, g, launch, rocket, landing, explosion):
    b = ':blue_square:'
    m = '<:mars:856130070565486592>'
    m_a = '<:marsair:856130036272988191>'
    if success_explosion == 0:
        frames = [
        f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{launch}🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛{rocket}⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        f'⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛{rocket}⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        f'⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛{rocket}⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        f'⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛{rocket}⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        f'⬛⬛⬛{rocket}⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        f'{m_a}{m_a}{m_a}{landing}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m}{m}{m}{m}{m}{m}{m}',
        f'{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{landing}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m}{m}{m}{m}{m}{m}{m}',
        f'{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{landing}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m}{m}{m}{m}{m}{m}{m}',
        f'{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{landing}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m}{m}{m}{m}{m}{m}{m}',
        f'{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}{m_a}\n{m_a}{m_a}{m_a}{rocket}{m_a}{m_a}{m_a}\n{m}{m}{m}{m}{m}{m}{m}',
        ]
    elif success_explosion == 1:
        frames = [
        f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{launch}🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'🟦🟦🟦{rocket}🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦🟦🟦\n{g}{g}{g}{g}{g}{g}{g}',
        f'⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛{rocket}⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        f'⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛{rocket}⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        f'⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛{rocket}⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        f'⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛{explosion}⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        f'⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛⬛⬛\n{b}{b}{b}{b}{b}{b}{b}',
        ]
    return frames


async def checks(message):
    checks = [' - TFR Activated\n', '- Pad Closeouts\n', '- Village cleared\n', '- Road closed\n', '- Pad cleared\n', '- Final checkouts\n', '- Recondenser\n', '- Tank Farm Activity\n', '- Methane vent\n', '- Engine chill\n', '- Launch imminent\n', '- Launch']
        
    
    fail_success = random.choice([0,1,2])
    sleep_time = random.choice([1,2])
    if fail_success == 2:
        random_len = random.randint(5,12)
        for i in range(random_len):
            await asyncio.sleep(sleep_time)
            string = ''
            for idx, value in enumerate(checks):
                if idx <= i:
                    check_cross = '✅'
                    if i == int(random_len-1):
                        check_cross = '❌'
                    string+=(f'{check_cross} {value}')
                else:
                    string+=(f'{value}')

            embed = discord.Embed(title='Checks', description=string)
            await message.edit(embed=embed)
        string = ''
        for item in checks:
            string+=(f'❌ {item}')
        embed = discord.Embed(title='Launch scrubbed ❌', description=string)
        await message.edit(embed=embed)
        raise

    else:
        for i in range(len(checks)):
            await asyncio.sleep(sleep_time)
            string = ''
            for idx, value in enumerate(checks):
                if idx <= i:
                    string+=(f'✅ {value}')
                else:
                    string+=(f'{value}')

            embed = discord.Embed(title='Checks', description=string)
            await message.edit(embed=embed)
    return message


async def spacex_launch_animation(ctx, datas, rocket_name):
    experience = datas[f'{ctx.author.id}_acc']['experience']
    launches = datas[f'{ctx.author.id}_acc']['launches']
    rockets = ', '.join(datas[f'{ctx.author.id}_acc']['rockets'])
    embed_checks = discord.Embed(title='Checks', description=' - TFR Activated\n - Pad Closeouts\n - Village cleared\n - Road closed\n - Pad cleared\n - Final checkouts\n - Recondenser\n - Tank Farm Activity\n - Methane vent\n - Engine chill\n - Launch imminent\n - Launch')
    main_message = await ctx.fetch_message(datas[f'{ctx.author.id}_acc']['message_id'])
    embed = discord.Embed(title=f'{rocket_name} launch', description=f'{earth_first_field}\nLaunches: {launches}\nProgress: {experience}\nCurrent rockets: **{rockets}**')
    await main_message.edit(embed=embed)
    checks_message = await ctx.fetch_message(datas[f'{ctx.author.id}_acc']['checks_message_id'])
    ground = '<:sand:856129037414694914>'
    launch = '<:sn15launch:855793869967065088>'
    landing_rotate = '<:sn15rotate:856128617465118720>'
    rocket = '<:sn15fly:856128617880485919>'
    rocket_at_pad = '<:sn15pad:856128617666838548>'
    explosion = '<:explosion:855824840610545704>'
    landing = '<:sn15horizontal:856128617917710346>'

    mars = 0

    try:
        message = await checks(checks_message)
    except:
        embed = discord.Embed(title=f'{rocket_name} flight scrubbed', description=f'{earth_first_field}\nLaunches: {launches}\nProgress: {experience}\nCurrent rockets: **{rockets}**')
        await main_message.edit(embed=embed)
        return

    if experience <= 10:
        explosion_frames = await spacex_launch_from_earth_frames(ground, launch, rocket, landing_rotate, landing, explosion)
        success_frames = await spacex_launch_from_earth_frames(ground, launch, rocket, landing_rotate, landing, rocket_at_pad)

    elif experience >= 10:
        mars = 1
        explosion_frames = await spacex_launch_to_mars_frames(1, ground, launch, rocket, landing, explosion)
        success_frames = await spacex_launch_to_mars_frames(0, ground, launch, rocket, landing, explosion)

    time = 10
    while True:
        try:
            await asyncio.sleep(1)
            time -= 1
            embed = discord.Embed(title='Launch', description=f"`Countdown: {time} seconds`")
            await checks_message.edit(embed=embed)
            if time <= 0:
                embed = discord.Embed(title='Launch', description='Upcoming states:\n - **Landing**\n - **Vechile safing**')
                await checks_message.edit(embed=embed)
                explode_success = random.randint(0,3)
                if explode_success == 2:
                    for frame in explosion_frames:
                        await asyncio.sleep(1)
                        embed = discord.Embed(title=f'{rocket_name} launch', description=f'{frame}\nLaunches: {launches}\nProgress: {experience}')
                        await main_message.edit(embed=embed)

                    embed = discord.Embed(title='Landed ❌', description='Vechile state: **Exploded**')
                    await checks_message.edit(embed=embed)

                    datas[f'{ctx.author.id}_acc']['rockets'].remove(rocket_name)
                    datas[f'{ctx.author.id}_acc']['experience'] -= 2
                    datas[f'{ctx.author.id}_acc']['launches'] += 1
                    datas[f'{ctx.author.id}_acc']['dogecoins'] -= 20
                    experience = datas[f'{ctx.author.id}_acc']['experience']
                    launches = datas[f'{ctx.author.id}_acc']['launches']
                    rockets = ', '.join(datas[f'{ctx.author.id}_acc']['rockets'])
                    await asyncio.sleep(2)
                    embed = discord.Embed(title='SpaceX facility / after launch / failed', description=f'{earth_first_field}\nLaunches: {launches}\nProgress: {experience}\nCurrent rockets: **{rockets}**')
                    await main_message.edit(embed=embed)

                    await asyncio.sleep(5)
                    embed = discord.Embed(title='SpaceX facility / repairing', description=f'{earth_first_field}\nLaunches: {launches}\nProgress: {experience}\nCurrent rockets: **{rockets}**')
                    await main_message.edit(embed=embed)
                    await asyncio.sleep(5)
                    embed = discord.Embed(title='SpaceX facility / ready to launch', description=f'{earth_first_field}\nLaunches: {launches}\nProgress: {experience}\nCurrent rockets: **{rockets}**')
                    await main_message.edit(embed=embed)

                    await checks_message.edit(embed=embed_checks)

                    if datas[f'{ctx.author.id}_acc']['dogecoins'] <= 0:
                        embed = discord.Embed(title='You lost!', description=f'Don\'t worry, you still have 20 {DOGE} for another try')
                        datas[f'{ctx.author.id}_acc']['dogecoins'] += 20
                        await message.delete()
                        await message.edit(embed=embed)
                        datas[f'{ctx.author.id}_acc']['experience'] = 0
                        datas[f'{ctx.author.id}_acc']['launches'] = 0

                else:
                    for frame in success_frames:
                        await asyncio.sleep(1)
                        embed = discord.Embed(title=f'{rocket_name} launch', description=f'{frame}\nLaunches: {launches}\nProgress: {experience}')
                        await main_message.edit(embed=embed)

                    embed = discord.Embed(title='Landed ✅', description='Vechile state: **Safing**')
                    await checks_message.edit(embed=embed)

                    datas[f'{ctx.author.id}_acc']['dogecoins'] += 20
                    datas[f'{ctx.author.id}_acc']['experience'] += 2
                    datas[f'{ctx.author.id}_acc']['launches'] += 1
                    experience = datas[f'{ctx.author.id}_acc']['experience']
                    launches = datas[f'{ctx.author.id}_acc']['launches']
                    if mars != 1:
                        await asyncio.sleep(2)
                        embed = discord.Embed(title='SpaceX facility / after launch / success', description=f'{earth_first_field}\nLaunches: {launches}\nProgress: {experience}\nCurrent rockets: **{rockets}**')
                        await main_message.edit(embed=embed)

                        embed = discord.Embed(title='Landed ✅', description='Vechile state: **Safe**')
                        await checks_message.edit(embed=embed)

                        await asyncio.sleep(5)
                        embed = discord.Embed(title='SpaceX facility / maintence', description=f'{earth_first_field}\nLaunches: {launches}\nProgress: {experience}\nCurrent rockets: **{rockets}**')
                        await main_message.edit(embed=embed)
                        await asyncio.sleep(5)
                        embed = discord.Embed(title='SpaceX facility / ready to launch', description=f'{earth_first_field}\nLaunches: {launches}\nProgress: {experience}\nCurrent rockets: **{rockets}**')
                        await main_message.edit(embed=embed)
                    else:
                        await asyncio.sleep(2)
                        embed = discord.Embed(title='You have succesfully landed on mars!', description=f'Total launches: {launches}\nProgress: {experience}')
                        await main_message.edit(embed=embed)
                        datas[f'{ctx.author.id}_acc']['experience'] = 0
                        datas[f'{ctx.author.id}_acc']['launches'] = 0
                    
                    await checks_message.edit(embed=embed_checks)

                break
        except:
            break


async def spacex_private_launch(ctx):
    with open('spacex.json', 'r') as f:
        datas = json.load(f)
        
    if not f'{ctx.author.id}' in datas:
        datas[f'{ctx.author.id}'] = {}
        datas[f'{ctx.author.id}']['experience'] = 0
        datas[f'{ctx.author.id}']['level'] = 1
        datas[f'{ctx.author.id}']['money'] = 0
    with open('spacex.json', 'w') as f:
        json.dump(datas, f)


AVIABLE_ROCKETS = {
  'FalconHeavy':120,
  'SN15':100,
  'Falcon9':20,
  'SuperHeavy':150
}


async def rockets_shop(ctx):
    embed = discord.Embed(title='SpaceX shop')
    for rocket, price in AVIABLE_ROCKETS.items():
        embed.add_field(name=rocket, value=f'{price} {DOGE}')
    await ctx.send(embed=embed, delete_after=5)


async def buy_rocket(ctx, rocket):
    with open('spacex.json', 'r') as f:
        datas = json.load(f)

    for rocket_name, price in AVIABLE_ROCKETS.items():
        if rocket_name == rocket:
            if datas[f'{ctx.author.id}_acc']['dogecoins'] < price:
              embed = discord.Embed(title='Not enough money', description=f'You don\'t have enough money to buy **{rocket_name}**')
              await ctx.send(embed=embed, delete_after=5)
              return
            datas[f'{ctx.author.id}_acc']['dogecoins'] -= price
            wallet = datas[f'{ctx.author.id}_acc']['dogecoins']
            datas[f'{ctx.author.id}_acc']['rockets'].append(rocket_name)
            rockets = ', '.join(datas[f'{ctx.author.id}_acc']['rockets'])
            embed = discord.Embed(title='Thanks!', description=f'You have successfully bought a SpaceX rocket!\nRocket: **{rocket_name}**\nPrice: **{price}** {DOGE}\nCurrent wallet: **{wallet}** {DOGE}\nYour rockets: **{rockets}**')
            await ctx.send(embed=embed, delete_after=5)
            break
    else:
        embed = discord.Embed(title='Check spelling!', description=f'There is no rocket called **{rocket}**')
        await ctx.send(embed=embed, delete_after=5)

    with open('spacex.json', 'w') as f:
        json.dump(datas, f)


async def user_wallet(ctx):
    with open('spacex.json', 'r') as f:
        datas = json.load(f)
        
    wallet = datas[f'{ctx.author.id}_acc']['dogecoins']
    rockets = ', '.join(datas[f'{ctx.author.id}_acc']['rockets'])
    embed = discord.Embed(title='Your dogecoin wallet', description=f'You have **{wallet}** {DOGE}\nYour rockets: **{rockets}**')
    await ctx.send(embed=embed, delete_after=5)


async def create_user_acc(ctx):
    if ctx.author.bot == False:
        with open('spacex.json', 'r') as f:
            datas = json.load(f)

        await update_data(datas, ctx)

        with open('spacex.json', 'w') as f:
            json.dump(datas, f)


async def update_data(datas, ctx):
    if not f'{ctx.author.id}_acc' in datas:
        datas[f'{ctx.author.id}_acc'] = {}
        datas[f'{ctx.author.id}_acc']['experience'] = 0
        datas[f'{ctx.author.id}_acc']['launches'] = 0
        datas[f'{ctx.author.id}_acc']['dogecoins'] = 40
        datas[f'{ctx.author.id}_acc']['rockets'] = []