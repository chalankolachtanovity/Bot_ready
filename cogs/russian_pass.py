import discord
from discord.ext import commands
import os
import requests
from PIL import Image, ImageFont, ImageDraw 
import datetime
import random
import asyncpraw


reddit = asyncpraw.Reddit(
                client_id=os.getenv('client_id'),
                client_secret=os.getenv('client_secret'),
                username=os.getenv('username'),
                password=os.getenv('password'),
                user_agent="pythonpraw"
                )


class Russian_pass(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    async def resize_image(self, user):
        avatar_image = Image.open(f'avatars/{user.name}.jpg')
        if avatar_image.mode != 'RGB':
            img = avatar_image.convert('RGB')
        else:
            img = avatar_image
        foo = img.resize((410,510),Image.ANTIALIAS)
        foo.save(f"avatars/{user.name}_resized.jpg",quality=95)
        os.remove(f"avatars/{user.name}.jpg")

    async def format_pass(self, ctx, user, name, surrname, birth_date, birth_place, gender):
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


    @commands.command(help='!createpass `<name>` `<surrname>` `<birth_date>` `<birth_place>` `<gender> - "be what you want to be"`')
    async def createpass(self, ctx, name, surrname, birth_date, birth_place, gender):
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
            await self.resize_image(user)

        await self.format_pass(ctx, user, name, surrname, birth_date, birth_place, gender)


    @commands.command(aliases=['pass'])
    async def viewpass(self, ctx, *, member: discord.Member=None):
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


    @commands.command()
    async def russia(self, ctx, subred="ANormalDayInRussia"):
        if os.path.isfile(f"russian_passes/{ctx.author.name}_pass.jpg") == False:
            embed = discord.Embed(title="You don't have passport!", description="Type `!createpass` to create your own passport.")
            await ctx.send(embed=embed)
            return

        msg = await ctx.send('Загрузка... ')

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


def setup(bot):
    bot.add_cog(Russian_pass(bot))