import discord
from discord.ext import commands
import random
import asyncio
import sqlite3

session_dict = {}
session_names_ids = []
ready_list = []
playing_users = []
final_users_list = []

MINIMAL_PLAYERS = 1
MAXIMAL_PLAYERS = 10
MAXIMAL_LEN_GAME = 30
SESSION_ROLE = 881509999623409724 #TEST-881509999623409724, ORIG-881505468667797554
GAMING_ROLE = 881509999623409725 #TEST-881509999623409725, ORIG-825875949413072957
GAMING_CATEGORY = 881522734776078366 #TEST-881522734776078366, ORIG-825872608091832332
BONUS_WEAPONS = [('total_kills_knife', 'Knife'), ('total_kills_ak47', 'AK-47'), ('total_kills_m4a1', 'M4A4'), ('total_kills_awp', 'AWP'), ('total_kills_p90', 'P90'), ('total_kills_glock', 'Glock'), ('total_kills_deagle', 'Deagle'), ('total_kills_negev', 'Negev'), ('total_kills_xm1014', 'XM-1014'), ('total_hits_mag7', 'MAG-7')]
STATS_FOR_STAT_COMMAND = [('session', 'Session'), ('datetime', 'Datetime'), ('total_kills', 'Kills'), ('total_deaths', 'Deaths'), ('total_kills_headshot', 'HS kills'), ('total_damage_done', 'Demage'), ('total_kills_knife', 'Knife kills'), ('total_kills_ak47', 'AK-47 kills'), ('total_kills_m4a1', 'M4A4 kills'), ('total_kills_awp', 'AWP kills'), ('total_planted_bombs', 'Planted bombs'), ('total_defused_bombs', 'Defused bombs')]


class Session(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def get_stat(self, stat, name):
        conn = sqlite3.connect("file::memory:?cache=shared")
        c = conn.cursor()
        c.execute(f"""SELECT {stat} FROM stats WHERE name='{name}' ORDER BY datetime desc LIMIT 1""")
        z = c.fetchall()
        conn.commit()
        conn.close()
        for x in z[0]:
            return x


    def get_username(self, username):
        usernames = [('CerveneTlacitko', 'Kmasko'), ('teetou', 'Teetou'), ('Bonsai', 'Aligator'), ('milan čonka', 'Stano'), ('Tajmoti', 'Tajmoti'), ('andrzej', 'Dron'), ('Kulivox', 'Kulivox')]
        for d_name, sql_name in usernames:
            if d_name == username:
                return sql_name


    async def create_stats_table(self, session):
        channel = await self.bot.fetch_channel(881509999807971359) #842840247980261486
        embed = discord.Embed(title='Statistics for **{}** session'.format(self.get_stat('session', 'Kmasko')))
        for_best_stat = {}
        b_w = session_dict[f'{session}_bonus_weapon']
        for env, nice in b_w:
            bonus_weapon = nice
            bonus_weapon_env = env
        for env, nice, steam, user_id in final_users_list:
            bonus_stat = self.get_stat(bonus_weapon_env, (nice))
            for_best_stat[user_id] = bonus_stat
            embed.add_field(
                name=f'**{steam}**', 
                value='> Kills: {}\n> Deaths: {}\n> {} kills: **{}**'.format(self.get_stat('total_kills', (nice)), self.get_stat('total_deaths', (nice)), bonus_weapon, bonus_stat), inline=True
            )
            embed.set_footer(text=self.get_stat('datetime', 'Kmasko'))

        all_values = for_best_stat.items()
        max_value = max(for_best_stat.values())
        user_id = max(all_values, key = lambda x:x[1])
        user = self.bot.get_user(user_id[0])

        embed.add_field(
            name=f'**Session winner**  ??', 
            value=f'> {user.mention} is the winner with **{max_value}** **{bonus_weapon}** kills', 
            inline=False
        )
        await channel.send(embed=embed)


    async def soviet_songs(self, channel):
        paths_to_anthem = ['mp3/soviet_anthem.mp3', 'mp3/Konarmejskij-marsh.mp3', 'mp3/Nash-paravos.mp3', 'mp3/Varshavjanka.mp3']
        await channel.edit(user_limit=channel.user_limit+1)
        vc = await channel.connect()
        vc.play(discord.FFmpegPCMAudio(random.choice(paths_to_anthem)), after=lambda e: print('done', e))
        await asyncio.sleep(120)
        await vc.disconnect()
        await channel.edit(user_limit=channel.user_limit-1)


    async def create_vc_channel(self, guild, game: str, number: int):
        banned_role = discord.utils.get(guild.roles, name="@everyone")

        overwrites = {
            banned_role: discord.PermissionOverwrite(connect=False),
        }
        for user_id in session_dict[f'{game}_ready_list']:
            user = await self.bot.fetch_user(user_id)
            overwrites[user] = discord.PermissionOverwrite(connect=True)

        new_voice_channel = await guild.create_voice_channel(name=f"{game} session", category=self.bot.get_channel(GAMING_CATEGORY), user_limit=number, overwrites=overwrites)
        session_dict[f'{game}_voice_channel'] = new_voice_channel
        if session_dict[f'{game}_soviet_session'] is True:
            await self.soviet_songs(new_voice_channel)


    async def session_conditions(self, ctx, name, max_players):
        if max_players <= MINIMAL_PLAYERS or max_players >= MAXIMAL_PLAYERS:
            embed = discord.Embed(
                title='Error: maximum players',
                description=f'''
                    Minimal players: **{MINIMAL_PLAYERS}**
                    Maximal players: **{MAXIMAL_PLAYERS}**
                    Your value: **{max_players}**
                '''
            )
            await ctx.send(embed=embed, delete_after=10)
            raise

        if len(name) >= MAXIMAL_LEN_GAME:
            embed = discord.Embed(
                title='Error: maximum name lenght',
                description=f'Maximum letters in name: **{MAXIMAL_LEN_GAME}**'
            )
            await ctx.send(embed=embed, delete_after=10)
            raise

        if f'{name}_game' in session_dict.keys():
            embed = discord.Embed(
                title=f'Error: **{name}** session already exists',
                description='You need to create new session'
            )
            await ctx.send(embed=embed, delete_after=10)
            raise


    async def set_vars_to_dict(self, ctx, game: str, number: int):
        session_dict[f"{game}_ready_list_mentions"] = []
        session_dict[f'{game}_started_by_id'] = ctx.author.id
        session_dict[f'{game}_playing_users'] = []
        session_dict[f'{game}_ready_list'] = []
        session_dict[f'{game}_list_names'] = []
        session_dict[f'{game}_game'] = game
        session_dict[f'{game}_max_players'] = number
        session_dict[f'{game}_ready_players'] = 1
        # booleans
        session_dict[f'{game}_statistics'] = False
        session_dict[f'{game}_create_vc'] = False
        session_dict[f'{game}_gaming_session'] = False
        session_dict[f'{game}_soviet_session'] = False


    async def create_session_embed(self, session):
        started_by = await self.bot.fetch_user(session_dict[f'{session}_started_by_id'])
        max_players = session_dict[f'{session}_max_players']
        member_mentions = ', '.join(session_dict[f'{session}_ready_list_mentions'])
        current_players = session_dict[f'{session}_ready_players']

        if current_players != max_players:
            embed = discord.Embed(
                title=f"**{session}** session - lobby", 
                description=f"""
                Started by **{started_by}**
                Session: **{session}**
                Players able to join: **{max_players}**
                Players joined: {member_mentions}
                """,
                color=discord.Colour.random()
            )
            embed.set_footer(text=f"Join with emoji reaction below ↓")
        
        else: 
            embed = discord.Embed(
                title=f'{session} session - Full', 
                description=f"""
                Status: **Ongoing**
                Players: **{max_players}**/**{max_players}**
                Players list: {member_mentions}
                """,
                color=0x9E0000

                )
            embed.set_footer(text="Enjoy this session!")

        return embed


    async def get_message(self, ctx, session, user):
        """Sends message according to ready players"""
        READY_PLAYERS = session_dict[f'{session}_ready_players']
        MAX_PLAYERS = session_dict[f'{session}_max_players']

        session_dict[f"{session}_ready_list_mentions"].append(user.mention)
        session_dict[f'{session}_list_names'].append(user.name)
        session_dict[f'{session}_ready_list'].append(user.id)

        if READY_PLAYERS == 1:
            await self.first_session_message(ctx, session)
        if READY_PLAYERS >= 2 and READY_PLAYERS != MAX_PLAYERS:
            await self.session_ready(ctx, session)
        if READY_PLAYERS == MAX_PLAYERS:
            await self.ending_of_session(ctx, session)


    async def first_session_message(self, ctx, session: str):
        """Sends starting session message"""

        embed = await self.create_session_embed(session)
        
        first_session_ms = await ctx.send(embed=embed)
        session_dict[f'{session}_first_ms_id'] = first_session_ms.id

        session_names_ids.append((session, first_session_ms.id))

        emojis = ['❌', '✅', '📊', '🔊', '🎮', '<:ouremoji:851164594320048208>']
        for emoji in emojis:
            await first_session_ms.add_reaction(emoji)

        await self.in_lobby_presence(session)


    async def session_ready(self, payload, session):
        """Sends ready information message"""
        if session != session_dict[f'{session}_game']:
            return
        channel = await self.bot.fetch_channel(payload.channel_id)
        msg = await channel.fetch_message(session_dict[f'{session}_first_ms_id'])

        embed = await self.create_session_embed(session)

        await msg.edit(embed=embed)


    async def session_parameters_check(self, session, guild, embed, channel, msg):
        if session_dict[f'{session}_gaming_session'] is True:
            for member_id in session_dict[f'{session}_ready_list']:
                await guild.get_member(member_id).add_roles(guild.get_role(GAMING_ROLE))
            embed.set_thumbnail(url="https://www.dictionary.com/e/wp-content/uploads/2018/07/CS-GO3.jpg")

        if session_dict[f'{session}_soviet_session'] is True:
            embed.set_thumbnail(url="https://i.pinimg.com/originals/f4/67/a2/f467a22305243ef1eee7373ca8e0f0b9.png")

        await msg.edit(embed=embed)

        if session_dict[f'{session}_statistics'] is True:
            for name in session_dict[f'{session}_list_names']:
                self.check_list(name)
            self.get_before_stat(final_users_list)

            session_dict[f'{session}_bonus_weapon'] = [random.choice(BONUS_WEAPONS)]
            for env, nice in session_dict[f'{session}_bonus_weapon']:
                embed = discord.Embed(title=f'Bonus weapon for {session} session is {nice}  🎁', description='The player with most kills on this weapon will win this session')
            await channel.send(embed=embed)

        if session_dict[f'{session}_create_vc'] is True:
            number = session_dict[f'{session}_max_players']
            await self.create_vc_channel(guild, session, number)


    async def ending_of_session(self, payload, session: str):
        """Sends last ready information message, execute timer to assign fucker and delete all things that was in before session"""

        guild = self.bot.get_guild(payload.guild_id)
        channel = await self.bot.fetch_channel(payload.channel_id)
        msg = await channel.fetch_message(session_dict[f'{session}_first_ms_id'])

        embed = await self.create_session_embed(session)

        await self.session_parameters_check(session, guild, embed, channel, msg)

        await msg.edit(embed=embed)
        await self.session_presence(session)
        for member_id in session_dict[f'{session}_ready_list']:
            await guild.get_member(member_id).add_roles(guild.get_role(SESSION_ROLE))


    async def session_interaction(self, payload, session):
        user = self.bot.get_user(payload.user_id)
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(session_dict[f'{session}_first_ms_id'])
        session_owner = session_dict[f'{session}_started_by_id']
        max_p = session_dict[f'{session}_max_players']
        current_p = session_dict[f'{session}_ready_players']

        if max_p == current_p:
            return

        if str(payload.emoji) == '❌':
            await self.session_unready(self, payload, session)
            await message.remove_reaction('❌', user)
        if str(payload.emoji) == '✅':
            if payload.user_id in session_dict[f'{session}_ready_list'] and payload.member.name != "CerveneTlacitko":
                return
            session_dict[f'{session}_ready_players'] += 1
            await self.get_message(payload, session, user)

        if str(payload.emoji) == '📊':
            if payload.user_id != session_owner:
                await message.remove_reaction('📊', user)
                return
            session_dict[f'{session}_statistics'] = True
        if str(payload.emoji) == '🔊':
            if payload.user_id != session_owner:
                await message.remove_reaction('🔊', user)
                return
            session_dict[f'{session}_create_vc'] = True
        if str(payload.emoji) == '🎮':
            if payload.user_id != session_owner:
                await message.remove_reaction('🎮', user)
                return
            session_dict[f'{session}_gaming_session'] = True
        if str(payload.emoji) == '<:ouremoji:851164594320048208>':
            session_dict[f'{session}_soviet_session'] = True


    async def session_end(self, ctx, session):
        possible_q = ['really?', '100% sure?', 'for real?', 'are you sure?']
        emojis = ['✅', '❌']

        choosen_q = random.choice(possible_q)
        dscrpt = f"Session: {session}"

        embed = discord.Embed(title=f"**{ctx.author.name}**, {choosen_q}", description=dscrpt)
        embed.set_footer(text='Add reaction below ↓')
        confirming_message = await ctx.send(embed=embed)
        for emoji in emojis:
            await confirming_message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

        except asyncio.TimeoutError:
            await ctx.message.delete()
            await confirming_message.delete()
            return

        else:
            if str(reaction.emoji) == '✅':
                await confirming_message.delete()
                await ctx.message.delete()
                await self.end_function(ctx, session)
            else:
                await ctx.message.delete()
                await confirming_message.delete()


    async def end_function(self, ctx, vc_name):
        existing_channel = discord.utils.get(ctx.guild.channels, name=f"{vc_name} session")
        general_channel = discord.utils.get(ctx.guild.channels, name="General")
        msg = await ctx.fetch_message(session_dict[f'{vc_name}_first_ms_id'])
        if session_dict[f'{vc_name}_create_vc'] is True:
            try:
                for member in ctx.author.voice.channel.members:
                    await member.move_to(general_channel)
            except:
                pass

            if existing_channel is None:
                await ctx.send(f'No channel named "{vc_name}" was found')
                return

        embed = discord.Embed(
            title=f'{vc_name} session - Ended', 
            description=f"""
            Status: **Ended**
            Session: **{vc_name}**
            Check <#842840247980261486> for session statistics!
            """,
        )
        await msg.edit(embed=embed)

        for member in session_dict[f'{vc_name}_ready_list']:
            user = self.bot.get_user(member)
            await ctx.guild.get_member(user.id).remove_roles(ctx.guild.get_role(GAMING_ROLE))
            await ctx.guild.get_member(user.id).remove_roles(ctx.guild.get_role(SESSION_ROLE))

        if existing_channel is not None:
            await existing_channel.delete()
        if session_dict[f'{vc_name}_statistics'] is True:
            self.get_last_stat(final_users_list, vc_name)
            await asyncio.sleep(5)
        if session_dict[f'{vc_name}_statistics'] is True:
            await self.create_stats_table(vc_name)
        ms_id = session_dict[f'{vc_name}_first_ms_id']
        session_names_ids.remove((vc_name, ms_id))
        await self.pop_items_in_dict(vc_name)
        await self.default_presence()
        final_users_list.clear()


    async def pop_items_in_dict(self, session):
        keys_to_pop = [f'{session}_started_by_id', f'{session}_playing_users', f'{session}_ready_list', f'{session}_game', f'{session}_max_players', f'{session}_ready_players', f'{session}_statistics', f'{session}_create_vc', f'{session}_gaming_session', f'{session}_voice_channel', f'{session}_first_ms_id', f'{session}_soviet_session', f'{session}_bonus_weapon', f'{session}_ready_list_mentions']
        for key in keys_to_pop:
            session_dict.pop(key, None)


    async def move_to_session_vc(ctx, vc_name):
        channel = discord.utils.get(ctx.guild.channels, name=f'{vc_name} session')
        for member in ctx.author.voice.channel.members:
            await member.move_to(channel)


    async def ask_to_join(self, message, session: str):
        channel = session_dict[f'{session}_voice_channel']
        embed = discord.Embed(title=f"{message.author.name}, you can join", description=f'Session: {session}')
        await message.channel.send(embed=embed)
        user = await self.bot.fetch_user(message.author.id)
        overwrites = {
            user: discord.PermissionOverwrite(connect=True)
        }
        await channel.edit(user_limit=channel.user_limit+1, overwrites=overwrites)

        await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(SESSION_ROLE))
        if session_dict[f'{session}_gaming_session'] is True:
            await message.guild.get_member(message.author.id).add_roles(message.guild.get_role(GAMING_ROLE))


    async def session_unready(self, payload, session: str):
        if session != session_dict[f'{session}_game']:
            return
        if payload.user_id not in session_dict[f'{session}_ready_list']:
            return
        if session_dict[f'{session}_ready_players'] == 1:
            return
        if payload.user_id in playing_users:
            playing_users.remove(payload.user_id)
        session_dict[f'{session}_ready_players'] -= 1

        mentions = session_dict[f'{session}_ready_list_mentions']
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        channel = await self.bot.fetch_channel(payload.channel_id)
        msg = await channel.fetch_message(session_dict[f'{session}_first_ms_id'])
        started_by = await self.bot.fetch_user(session_dict[f'{session}_started_by_id'])

        if member.mention in mentions:
            session_dict[f'{session}_ready_list_mentions'].remove(member.mention)
        session_dict[f'{session}_ready_list'].remove(payload.user_id)
        ready_list.remove(payload.user_id)

        player_mentions = ', '.join(session_dict[f'{session}_ready_list_mentions'])

        embed = discord.Embed(
            title=f"**{session}** session - lobby", 
            description=f"""
            Started by **{started_by}**
            Session: **{session}**
            Players able to join: **{session_dict[f'{session}_max_players']}**
            Players joined: {player_mentions}
            """,
            color=0x1f8b4c
        )
        embed.set_footer(text=f"Join with emoji reaction below ↓")
        await msg.edit(embed=embed)


    def flatten(self, l, ltypes=(list, tuple)):
        ltype = type(l)
        l = list(l)
        i = 0
        while i < len(l):
            while isinstance(l[i], ltypes):
                if not l[i]:
                    l.pop(i)
                    i -= 1
                    break
                else:
                    l[i:i + 1] = l[i]
            i += 1
        return ltype(l)


    async def default_presence(self):
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name='Spaceflights'))


    async def in_lobby_presence(self, game):
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing, name=f'In {game} lobby'))


    async def session_presence(self, session):
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f'{session} session'))


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        if payload.guild_id is None:
            return

        flat_a = self.flatten(session_names_ids)

        if payload.message_id not in flat_a:
            return

        for session_name, session_id in session_names_ids:
            if payload.message_id == session_id:
                session = session_name

        await self.session_interaction(payload, session)

    @commands.command(help="Creates session", aliases=['s', 'ss'])
    async def startsession(self, ctx, name: str, max_players: int):
        try:
            await self.session_conditions(ctx, name, max_players)
        except:
            await ctx.message.delete()
            return
        await self.set_vars_to_dict(ctx, name, max_players)
        await self.get_message(ctx, name, ctx.author)


    @commands.command(help='Ends session', aliases=['e', 'end'])
    async def endsession(self, ctx, session):
        if str(ctx.channel) != 'bot-commands':
            return
        try:
            session_dict[f'{session}_game']
        except KeyError:
            await ctx.send(f'There is no session called **"{session}"**', delete_after=5)
            await ctx.message.delete()
            return
        if ctx.author.id not in session_dict[f'{session}_ready_list']:
            embed = discord.Embed(
                title='Missing permissions!', 
                description='You must be in this session to end it!', 
                color=0xff1414
            )
            await ctx.message.delete()
            await ctx.send(embed=embed, delete_after=10)
            return

        await self.session_end(ctx, session)


    @commands.command(help='Adds one more space to session', aliases=["joinsession"])
    async def join_to(self, message, session: str):
        if session != session_dict[f'{session}_voice_channel']:
            return
        await self.ask_to_join(self, message, session)


    @commands.command(help='See your last session stats')
    async def stats(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        name = self.get_username(user.name)

        embed = discord.Embed(title=f'Last session stats for **{name}**')
        for sql_name, nice_name in STATS_FOR_STAT_COMMAND:
            embed.add_field(name=f'> {nice_name}', value=f'> {self.get_stat(sql_name, name)}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Session(bot))