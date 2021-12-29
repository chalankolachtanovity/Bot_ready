import discord
from discord.ext import commands
import random
import sqlite3


PRAYERS = 'Otče náš, ktorý si na nebesiach, posväť sa meno tvoje, príď kráľovstvo tvoje, buď vôľa tvoja ako v nebi, tak i na zemi. Chlieb náš každodenný daj nám dnes a odpusť nám naše viny, ako i my odpúšťame svojim vinníkom, a neuveď nás do pokušenia, ale zbav nás zlého.\nAmen.\n:church::cross::church:'


class Entertainment(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    async def command_pochvalen(self, message):
        """Replies 'aj naveky, amen' to the player saying pochvalen."""
        myEmbed = discord.Embed(title="Aj naveky, Amen.",
                                description=PRAYERS,
                                color=0xff0000)
        myEmbed.set_footer(text="Pozdravujem všetkých poliakov!")
        await message.channel.send(embed=myEmbed)


    async def command_cheater(self, message):
        videos = ['https://imgur.com/a/hVu7qGU', 'https://imgur.com/29LOtBD', 'https://imgur.com/dKa8ZGW']
        random_video = random.choice(videos)
        await message.channel.send(random_video)


    @commands.command(help="Sends random video of best csgo plays")
    async def cheater(self, message):
        await self.command_cheater(message)


    @commands.command(help="Pray, pray and pray!")
    async def pochvalen(self, message):
        await self.command_pochvalen(message)


    @commands.command(help='Share your music')
    async def spotify(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
            pass
        if user.activities:
            for activity in user.activities:
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


def setup(bot):
    bot.add_cog(Entertainment(bot))