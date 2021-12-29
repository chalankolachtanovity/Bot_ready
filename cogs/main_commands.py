import discord
from discord.ext import commands
import random
import toml

class Main(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(help='All commands')
    async def help(self, ctx, args=None):
        help_mes = ['Calling 911...', 'Any problem?', 'Some problem here?', 'No worries, i gotch ya']
        help_embed = discord.Embed(title=random.choice(help_mes), description='List of supported commands:')
        command_names_list = [x.name for x in self.bot.commands]

        if not args:
            for i,x in enumerate(self.bot.commands):
                help_embed.add_field(
                    name=f"`!{x.name}` {x.signature}",
                    value=f"> {x.help}",
                    inline=True
                )

        # If the argument is a command, get the help text from that command:
        elif args in command_names_list:
            help_embed.add_field(
                name=args,
                value=self.bot.get_command(args).help
            )

        # If someone is just trolling:
        else:
            help_embed.add_field(
                name="Nope.",
                value="Don't think I got that command"
            )

        await ctx.send(embed=help_embed)


    @commands.command()
    async def userinfo(self, ctx, *, member: discord.Member=None):
        """Displays information on a user"""
        if member == None:
            member = ctx.message.author
        embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
        embed.set_author(name=f"User Info - {member}")
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)


    @commands.command(help='Detailed info about the project', aliases=['project'])
    async def info(self, ctx):
        toml_open = toml.load(open('pyproject.toml'))['tool']['poetry']
        embed = discord.Embed(title='Info about the project', url='https://github.com/chalankolachtanovity/Bot_ready/blob/master/README.md')
        embed.add_field(name='Name:', value=toml_open['name'])
        embed.add_field(name='Version:', value=toml_open['version'])
        embed.add_field(name='Description:', value=toml_open['description'])
        embed.add_field(name='Authors:', value=', '.join(toml_open['authors']))
        await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title=f"**Hey {member.name}, welcome to Milošovy hrátky server!**", color=0x009dff)
        embed.set_author(name="by chalankolachtanovity")
        embed.add_field(name=":red_circle:Rules:", value="We don't have any rules, everything is moderated by bot **Lachtan**.\nType **!help**", inline=True)
        embed.set_thumbnail(url="https://m.smedata.sk/api-media/media/image/sme/6/30/3065226/3065226_600x400.jpeg?rev=3")
        embed.add_field(name=":red_circle:Bot Lachtan", value="Bot **Lachtan** is our unique bot with unique functions! Feel free to use him!", inline=False)
        embed.set_footer(text="enjoy!")
        await self.bot.get_channel(783670260200767488).send(content=member.mention, embed=embed)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        answers = ['Huh?', 'You are trying impossible', '"Human being"', 'I just sometimes ask, why.', 'No way', 'Again?', 'Just...', 'XD', 'Wtf dude.', '2+2?', 'No comment']
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(title=random.choice(answers), description='Check spelling', color=0xff1414)
            await ctx.send(embed=embed)
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title=random.choice(answers), description=f'Missing a required argument `<{error.param.name}>`.  Do `!help <commandname>`', color=0xff1414)
            await ctx.send(embed=embed)
        raise error


    @commands.Cog.listener()
    async def on_ready(self):
        print("Discord -> connected")
        await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, 
                    name='Spaceflights')
            )


def setup(bot):
    bot.add_cog(Main(bot))