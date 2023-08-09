import disnake
from disnake.ext import commands, tasks
import pymongo
from config import *
from mod import *
import time
import re
import random
import asyncio
import datetime

emoji_money_id = 1091827829500555286

random_gifs = [
    'https://cdn.disnakeapp.com/attachments/707964558781841472/865166447008022568/g27a.gif',
    'https://cdn.disnakeapp.com/attachments/707964558781841472/865166448871735296/9TCw.gif',
    'https://cdn.disnakeapp.com/attachments/707964558781841472/865166454268624906/7A55.gif',
    'https://cdn.disnakeapp.com/attachments/707964558781841472/865168114325127178/8Uf1.gif',
    'https://cdn.disnakeapp.com/attachments/707964558781841472/865168164781424640/ce15dee4f4de516c7b19921bd4671da90aa3db0fr1-500-281_00.gif',
    'https://i.gifer.com/DFi4.gif',
    'https://cdn.disnakeapp.com/attachments/707964558781841472/874728082647441508/image5.gif',
    'https://cdn.disnakeapp.com/attachments/707964558781841472/874728068739133480/image6.gif',
    'https://cdn.disnakeapp.com/attachments/707964558781841472/874728030910697472/image0_1.gif',
    'https://cdn.disnakeapp.com/attachments/707964558781841472/874727936102662204/3xMg.gif',
    'https://cdn.disnakeapp.com/attachments/707964558781841472/874713872853004338/bfln5jRa_L37ziNWm-xNvO9bmC-VKVjGQ2yVO3emFHWvX9rjyGf65NTHR3Omu7T1p4vlhZBagXQqvcFE2gJt30jM5WsMqJ8z-65-.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963892060514041876/AC78488D-D39A-4A11-9762-49C2654ABF96.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963892060157542461/A391917A-7E0F-4149-B80B-66ACF7039465.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963892058895028244/024EACF2-211E-47EE-8608-0E5C010A8925.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963886134855876688/50FF81B3-51A1-4B02-89D2-C523A5D3AFE0.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963886077838512178/IMG_6637.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963886075506462770/AC5B0A10-73C2-4C2B-902A-5258E16E26BB.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963886075489710080/IMG_6636.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963886002747899904/10470386-1979-4033-9BEE-3682709376B7.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963885974033666080/DE248FC6-D73E-4713-9D9B-3F171ACB52C5.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963885902583705600/9C3ADF8D-9700-4D43-898B-62B76DDC3913.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963885811135303720/F4C10347-4CD1-41D0-B83E-26AD46125A9A.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963885731296739359/D50330B5-E319-4937-93F1-DE9F21C849FD.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963885730923413524/giphy-downsized.gif',
    'https://media.disnakeapp.net/attachments/956133390556467200/963885730290098256/giphy.gif'
]

class Buttons_for_Battle(disnake.ui.View):
    author: disnake.Member
    msg: disnake.Message
    member: disnake.Member = None
    

    def __init__(self, number: int, profile_db, emoji_money):
        super().__init__(timeout=120)
        self.number = number
        self.profile_db = profile_db
        self.EMOJI_MONEY = emoji_money
        emoji_money = self.bot.get_emoji(emoji_money_id)

    async def return_ava(self, author: disnake.Member):
        if author.display_avatar:
            ava = author.display_avatar.url
        elif author.avatar:
            ava = author.display_avatar.url
        else:
            ava = author.default_avatar
        return ava

        


    @disnake.ui.button(label="Принять Вызов", emoji='✔')
    async def battle_btn(self, button, inter: disnake.MessageInteraction):
        member = inter.author
        abc = self.profile_db.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
        if abc['balance'] < self.number:
            await inter.send(f"{member.mention}, ваш баланс меньше суммы ставки!", ephemeral=True)
        else:
            new_author_balance = self.profile_db.find_one({"member_id": self.author.id, "guild_id": inter.guild.id})
            if new_author_balance['balance'] < self.number:
                await self.msg.delete()
                await inter.send(f'Ваш(автора) баланс меньше суммы вашей ставки! (Анти-Баг система)', ephemeral=True)
                return
            else:
                emb = disnake.Embed(
                    title=f'Битва {self.author.display_name} и {member.display_name}'
                )
                emb.set_footer(
                    text=f'Банк игры {self.number * 2} монет!')
                emb.set_image(
                    url=random.choice(random_gifs))
                await inter.response.edit_message(embed=emb, view=None)
                await asyncio.sleep(3)
                rand = random.randint(0, 100)
                if rand < 50:
                    winner = self.author
                    user = member
                else:
                    winner = member
                    user = self.author

                emoji_money = self.bot.get_emoji(emoji_money_id)
                EMOJI_MONEY = emoji_money
                self.profile_db.update_one({"member_id": winner.id, "guild_id": inter.guild.id},
                                            {"$inc": {"balance": self.number}})
                self.profile_db.update_one({"member_id": user.id, "guild_id": inter.guild.id},
                                            {"$inc": {"balance": -self.number}})
                embed = disnake.Embed(title=f"Battle",
                                      description=f'В **битве** одержал победу {winner.mention} и получил {self.number * 2}{self.EMOJI_MONEY}\n **Сражение было между:** {user.mention}/{winner.mention}',
                                      color=0x2f3136)
                ava = await self.return_ava(winner)
                emb.set_thumbnail(url=ava)
                await inter.edit_original_message(embed=embed, view=None)

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if self.member:
            if interaction.author != self.member:
                await interaction.send(f'Данная кнопка доступны **только** {self.member.mention}', ephemeral=True)
                return False
            return True
        else:
            if interaction.author == self.author:
                await interaction.send(f'Данная кнопка доступны всем кроме вас! (нельзя играть с самим с собой)', ephemeral=True)
                return False
            return True

    async def on_timeout(self) -> None:
        if self.msg:
            emb = disnake.Embed(
                title='Battle',
                description=f'{self.author.mention}, никто не ответил на ваше предложение!',
                color=0x2b2d31
            )
            try:
                await self.msg.edit(embed=emb, view=None)
            except disnake.NotFound:
                pass

class Buttons_for_Br(disnake.ui.View):
    author: disnake.Member
    msg: disnake.Message

    async def return_ava(self, author: disnake.Member):
        if author.display_avatar:
            ava = author.display_avatar.url
        elif author.avatar:
            ava = author.display_avatar.url
        else:
            ava = author.default_avatar
        return ava

    def __init__(self, bot, count, db_profile, emoji_money):
        super().__init__(timeout=120)
        self.bot = bot
        emoji_money = self.bot.get_emoji(emoji_money_id)
        self.number = count
        self.profile = db_profile
        self.EMOJI_MONEY = emoji_money

    async def get_ballance(self, member_id: int, guild_id: int):
        find = self.profile.find_one({"member_id": member_id, "guild_id": guild_id})
        if find and "balance" in find.keys():
            return find['balance']
        else:
            return 0

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="1.5x")
    async def br_1_5x(self, button, inter: disnake.MessageInteraction):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        EMOJI_MONEY = emoji_money
        if await self.get_ballance(member_id=inter.author.id, guild_id=inter.guild_id) < self.number:
            await inter.send(f'Анти-Баг система',  ephemeral=True)
            return
        random_s = random.randint(0, 100)
        ava = await self.return_ava(self.author)
        if random_s >= 47 or inter.author.id == 748556262802849812: 
            self.profile.update_one({"member_id": inter.author.id, "guild_id": inter.guild.id}, {"$inc": {"balance": self.number*0.5}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **выиграли**, и **увеличили** свою ставку {self.number}{self.EMOJI_MONEY} в **1.5** раза!',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await inter.response.edit_message(embed=emb, view=None)
        else:
            self.profile.update_one({"member_id": inter.author.id,  "guild_id": inter.guild.id}, {"$inc": {"balance": -self.number}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **проиграли**, и **потеряли** свою ставку {self.number}{self.EMOJI_MONEY}',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await inter.response.edit_message(embed=emb, view=None)

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="3x")
    async def br_3x(self, button, inter: disnake.MessageInteraction):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        EMOJI_MONEY = emoji_money
        if await self.get_ballance(member_id=inter.author.id, guild_id=inter.guild_id) < self.number:
            await inter.send(f'Анти-Баг система',  ephemeral=True)
            return
        random_s = random.randint(0, 100)
        ava = await self.return_ava(self.author)
        if random_s >= 67 or inter.author.id == 748556262802849812:
            self.profile.update_one({"member_id": inter.author.id, "guild_id": inter.guild.id},
                                          {"$inc": {"balance": self.number * 2}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **выиграли**, и **увеличили** свою ставку {self.number}{self.EMOJI_MONEY} в **3** раза!',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await inter.response.edit_message(embed=emb, view=None)
        else:
            self.profile.update_one({"member_id": inter.author.id, "guild_id": inter.guild.id},
                                          {"$inc": {"balance": -self.number}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **проиграли**, и **потеряли** свою ставку {self.number}{self.EMOJI_MONEY}',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await inter.response.edit_message(embed=emb, view=None)

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="5x")
    async def br_5x(self, button, inter: disnake.MessageInteraction):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        EMOJI_MONEY = emoji_money
        if await self.get_ballance(member_id=inter.author.id, guild_id=inter.guild_id) < self.number:
            await inter.send(f'Анти-Баг система',  ephemeral=True)
            return
        random_s = random.randint(0, 100)
        ava = await self.return_ava(self.author)
        if random_s >= 80 or inter.author.id == 748556262802849812:
            self.profile.update_one({"member_id": inter.author.id, "guild_id": inter.guild.id},
                                          {"$inc": {"balance": self.number * 4}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **выиграли**, и **увеличили** свою ставку {self.number}{self.EMOJI_MONEY} в **5** раз!',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await self.msg.edit(embed=emb, view=None)
        else:
            self.profile.update_one({"member_id": inter.author.id, "guild_id": inter.guild.id},
                                          {"$inc": {"balance": -self.number}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **проиграли**, и **потеряли** свою ставку {self.number}{self.EMOJI_MONEY}',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await inter.response.edit_message(embed=emb, view=None)

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="7.5x")
    async def br_7_5x(self, button, inter: disnake.MessageInteraction):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        EMOJI_MONEY = emoji_money
        if await self.get_ballance(member_id=inter.author.id, guild_id=inter.guild_id) < self.number:
            await inter.send(f'Анти-Баг система',  ephemeral=True)
            return
        random_s = random.randint(0, 100)
        ava = await self.return_ava(self.author)
        if random_s >= 92 or inter.author.id == 748556262802849812:
            self.profile.update_one({"member_id": inter.author.id, "guild_id": inter.guild.id},
                                          {"$inc": {"balance": self.number * 6.5}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **выиграли**, и **увеличили** свою ставку {self.number}{self.EMOJI_MONEY} в **7.5** раз!',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await inter.response.edit_message(embed=emb, view=None)
        else:
            self.profile.update_one({"member_id": inter.author.id, "guild_id": inter.guild.id},
                                          {"$inc": {"balance": -self.number}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **проиграли**, и **потеряли** свою ставку {self.number}{self.EMOJI_MONEY}',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await inter.response.edit_message(embed=emb, view=None)

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="10x")
    async def br_10x(self, button, inter: disnake.MessageInteraction):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        EMOJI_MONEY = emoji_money
        if await self.get_ballance(member_id=inter.author.id, guild_id=inter.guild_id) < self.number:
            await inter.send(f'Анти-Баг система',  ephemeral=True)
            return
        random_s = random.randint(0, 100)
        ava = await self.return_ava(self.author)
        if random_s >= 97 or inter.author.id == 748556262802849812:
            self.profile.update_one({"member_id": inter.author.id, "guild_id": inter.guild.id},
                                          {"$inc": {"balance": self.number * 9}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **выиграли**, и **увеличили** свою ставку {self.number}{self.EMOJI_MONEY} в **10** раз!',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await inter.response.edit_message(embed=emb, view=None)
        else:
            self.profile.update_one({"member_id": inter.author.id, "guild_id": inter.guild.id},
                                          {"$inc": {"balance": -self.number}})
            find = self.profile.find_one({"member_id": inter.author.id, "guild_id": inter.guild.id})
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{inter.author.mention}, вы **проиграли**, и **потеряли** свою ставку {self.number}{self.EMOJI_MONEY}',
                color=0x2b2d31
            )
            emb.set_footer(text=f'ваш баланс - {int(find["balance"])}')
            emb.set_thumbnail(url=ava)
            await inter.response.edit_message(embed=emb, view=None)

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.author != self.author:
            await interaction.send(f'Данные кнопки доступны **только** {self.author.mention}', ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        if self.msg:
            await self.msg.edit(view=None)

class Ecomony(commands.Cog, name='economy'):
    def __init__(self, bot):
        self.bot = bot

        self.cluster = self.bot.cluster
        self.profile: pymongo.collection.Collection = self.cluster.infinity.profile
        self.g_count: pymongo.collection.Collection = self.cluster.infinity.guilds

    async def get_role(self, roles, guild):
        id_rol = roles \
            .replace("<", "") \
            .replace("@", "") \
            .replace("&", "") \
            .replace(">", "") \
            .replace(" ", "")
        role = guild.get_role(int(id_rol))
        return role

    async def get_balance(self, member_id, guild_id):
        find = self.profile.find_one({"member_id": member_id, "guild_id": guild_id})
        if find and "balance" in find.keys():
            return find['balance']
        else:
            return 0

    async def inc_money(self, member_id, guild_id, money: int):
        self.profile.update_one({"member_id": member_id, "guild_id": guild_id}, {"$inc": {"balance": money}}, True)

    async def get_member(self, member1, guild):
        id_mem = member1 \
            .replace("<", "") \
            .replace("@", "") \
            .replace("!", "") \
            .replace(">", "")
        member = await guild.fetch_member(id_mem)
        return member

    @commands.slash_command(
        name='balance',
        description=f'Посмотреть баланс пользователя',
        dm_permission=False,
        options=[
            disnake.Option(
                name='member',
                description='Укажите пользователя, для просмотра его баланса',
                type=disnake.OptionType.user,
                required=False
            )
        ]
    )
    async def balance(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member=None):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        await ctx.response.defer()
        if not member:
            bal = await self.get_balance(ctx.author.id, ctx.guild.id)
            emb = disnake.Embed(
                title=f'Текущий баланс — {ctx.author}',
                description=f'{emoji_money} Баланс: \n```{int(bal)}```',
                color=0x2b2d31
            )
            if ctx.author.display_avatar:
                emb.set_thumbnail(url=ctx.author.display_avatar.url)
            elif ctx.author.avatar:
                emb.set_thumbnail(url=ctx.author.avatar.url)
            else:
                emb.set_thumbnail(url=ctx.author.default_avatar)
            await ctx.edit_original_message(embed=emb)
        else:
            bal = await self.get_balance(member.id, ctx.guild.id)
            emb = disnake.Embed(
                title=f'Текущий баланс — {member}',
                description=f'{emoji_money} Баланс: \n```{int(bal)}```',
                color=0x2b2d31
            )
            if member.display_avatar:
                emb.set_thumbnail(url=member.display_avatar.url)
            elif member.avatar:
                emb.set_thumbnail(url=member.avatar.url)
            else:
                emb.set_thumbnail(url=member.default_avatar)
            await ctx.edit_original_message(embed=emb)

    @commands.slash_command(
        name='award',
        description='Выдача/Снятие средств пользователя',
        dm_permission=False,
        options=[
            disnake.Option(
                name='member',
                description='Укажите пользователя',
                required=True,
                type=disnake.OptionType.user
            ),
            disnake.Option(
                name='amount',
                description='Укажите сумму(если хотите снять, указывайте с "-" в начале',
                required=True,
                type=disnake.OptionType.integer
            )
        ],
    )
    async def award(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, amount: int):
        if ctx.guild.get_role(1089966349356380300) in ctx.author.roles or ctx.guild.get_role(1089966349356380300) in ctx.author.roles or ctx.guild.get_role(1089966349356380300) in ctx.author.roles:
            if amount >= 0:
                name_emb = 'Выдача'
                name_des = 'выдали'
                give_ball = amount
            else:
                name_emb = 'Снятие'
                name_des = 'сняли'
                give_ball = -amount
            await self.inc_money(member_id=member.id, guild_id=ctx.guild.id, money=amount)
            emoji_money = self.bot.get_emoji(emoji_money_id)
            emb = disnake.Embed(
                title=f'{name_emb} денег пользователю',
                description=f'{ctx.author.mention}, вы **{name_des}** пользователю {member.mention} **{give_ball}** {emoji_money}',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            if ctx.author.id == 748556262802849812:
                await ctx.send(embed=emb, ephemeral=True)
                return
            await ctx.send(embed=emb)
        else:
            await ctx.send(f'У вас недостаточно прав!', ephemeral=True)

    @commands.slash_command(
        name='timely',
        description=f'Временная награда',
        dm_permission=False
    )
    async def timely(self, ctx: disnake.ApplicationCommandInteraction):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        find = self.profile.find_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id})
        if find and 'next_timely' in find.keys():
            await ctx.response.defer(ephemeral=True)
            time_end = (find['next_timely'] - int(time.time()))//60
            emb = disnake.Embed(
                title='Временная Награда',
                description=f'{ctx.author.mention}, вы уже **забирали** временную награду! Повторите попытку через **{time_end//60} ч, {time_end%60} м**',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.edit_original_message(embed=emb)
        else:
            await ctx.response.defer()
            rand = random.randint(40, 60)
            emb = disnake.Embed(
                title='Временная награда',
                description=f'{ctx.author.mention}, вы **получили** вашу временную награду в виде **{rand}** {emoji_money}',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            times = int(time.time()) + 60*60*6
            await ctx.edit_original_message(embed=emb)
            self.profile.update_many({"member_id": ctx.author.id, "guild_id": ctx.guild.id}, {"$set": {"next_timely": times}, "$inc": {"balance": rand}}, True)

    @commands.slash_command(
        name='give',
        description='Перевести деньги другому пользователю',
        dm_permission=False,
        options=[
            disnake.Option(
                name='member',
                description='Укажите пользователя, который получит перевод',
                required=True,
                type=disnake.OptionType.user
            ),
            disnake.Option(
                name='amount',
                description='Укажите сумму перевода',
                required=True,
                type=disnake.OptionType.integer
            )
        ]
    )
    async def give(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, amount: int):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        if member.id == ctx.author.id:
            await ctx.send(f'{ctx.author.mention}, **нельзя** перевести деньги самому себе', ephemeral=True)
        elif await self.get_balance(member_id=ctx.author.id, guild_id=ctx.guild.id) < amount:
            await ctx.send(f'{ctx.author.mention}, **нельзя** перевести сумму **больше** вашего баланса!', ephemeral=True)
        elif amount < 10:
            await ctx.send(f'{ctx.author.mention}, **нельзя** перевести сумму **меньше** 10 {emoji_money}!', ephemeral=True)
        else:
            emb = disnake.Embed(
                title='Перевод',
                description=f'{ctx.author.mention}, вы перевели **{amount}** {emoji_money} пользователю {member.mention}',
                color=0x2b2d31
            )
            await ctx.send(embed=emb)
            await self.inc_money(ctx.author.id, ctx.guild.id, -amount)
            await self.inc_money(member.id, ctx.guild.id, amount)

    @commands.slash_command(
        name='battle',
        description=f'Сражение на серверную валюту',
        dm_permission=False,
        options=[
            disnake.Option(
                name='number',
                description=f'Укажите сумму ставки',
                required=True,
                type=disnake.OptionType.integer
            ),
            disnake.Option(
                name='member',
                description='Укажите пользователя, если хотите сразится именно с ним',
                required=False,
                type=disnake.OptionType.user
            )
        ]
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def battle(self, ctx: disnake.ApplicationCommandInteraction, number: int, member: disnake.Member = None):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        EMOJI_MONEY = emoji_money
        if number < 0:
            number *= -1
        EMOJI_MONEY = self.bot.get_emoji(emoji_money_id)
        acb = await self.get_balance(ctx.author.id, ctx.guild.id)
        if number < 10:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, **минимальная** сумма ставки `10` {emoji_money}!',
                color=0x2b2d31
            )
            await ctx.send(embed=emb, ephemeral=True)
        elif acb < number:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, сумма ставки **не может** быть **бальше** вашего баланса!',
                color=0x2b2d31
            )
            await ctx.send(embed=emb, ephemeral=True)
        else:
            await ctx.response.defer()
            if member:
                emb = disnake.Embed(
                    title='Battle',
                    description=f'{ctx.author.mention}, хочешь сразится с {member.mention} на **{number}**  {emoji_money}!',
                    color=0x2b2d31
                )
            else:
                emb = disnake.Embed(
                    title='Battle',
                    description=f'{ctx.author.mention}, хочешь с кем то сразиться на **{number}**  {emoji_money}!',
                    color=0x2b2d31
                )
            btns = Buttons_for_Battle(number=number, bot=self.bot, db_profile=self.profile, emoji_money=EMOJI_MONEY)
            btns.author = ctx.author
            msg = await ctx.edit_original_message(embed=emb, view=btns)
            btns.msg = msg
            if member:
                btns.member = member

    @commands.slash_command(
        name='br',
        description='Казино с 5 разными коэффициентами!',
        dm_permission=False,
        options=[
            disnake.Option(
                name='number',
                description='Укажите сумму ставки',
                required=True,
                type=disnake.OptionType.integer
            )
        ]
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def br(self, ctx: disnake.ApplicationCommandInteraction, number: int):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        EMOJI_MONEY = emoji_money
        await ctx.response.defer()
        if number < 0:
            number *= -1
        EMOJI_MONEY = self.bot.get_emoji(emoji_money_id)
        author_balance = await self.get_balance(ctx.author.id, ctx.guild.id)
        if number < 10:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, **минимальная** ставка - 10 {emoji_money}',
                color=0x2b2d31
            )
            await ctx.edit_original_message(embed=emb)
        elif author_balance < number:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, ваш баланс **меньше** суммы вашей ставки!',
                color=0x2b2d31
            )
            await ctx.edit_original_message(embed=emb)
        else:
            emb = disnake.Embed(
                title='Казино XXX',
                description=f'{ctx.author.mention}, **выберите** режим игры! Ваша ставка - {number} {emoji_money}',
                color=0x2b2d31
            )
            emb.set_footer(text='Для этого у вас есть 60 секунд')
            btns = Buttons_for_Br(count=number, bot=self.bot, db_profile=self.profile, emoji_money=EMOJI_MONEY)
            btns.author = ctx.author
            btns.msg = await ctx.edit_original_message(embed=emb, view=btns)

    @commands.slash_command(
        name='casino',
        description='Казино 50/50',
        dm_permission=False,
        options=[
            disnake.Option(
                name='number',
                description='Укажите сумму ставки',
                required=True,
                type=disnake.OptionType.integer
            )
        ]
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def casino_command(self, ctx: disnake.ApplicationCommandInteraction, number: int):
        emoji_money = self.bot.get_emoji(emoji_money_id)
        EMOJI_MONEY = emoji_money
        if number < 0:
            number *= -1
        EMOJI_MONEY = self.bot.get_emoji(emoji_money_id)
        author_balance = await self.get_balance(ctx.author.id, ctx.guild.id)
        if number < 10:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, **минимальная** ставка - 10 {emoji_money}',
                color=0x2b2d31
            )
            await ctx.send(embed=emb, ephemeral=True)
            return
        elif author_balance < number:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, ваш баланс **меньше** суммы вашей ставки!',
                color=0x2b2d31
            )
            await ctx.send(embed=emb, ephemeral=True)
            return
        random_casino = random.randint(0, 100)
        if random_casino >= 50:
            await self.inc_money(ctx.author.id, ctx.guild.id, number)
            emb = disnake.Embed(
                title='Казино',
                description='',
                color=0x2b2d31
            )
            balancec = self.profile.find_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id})
            emb.set_footer(text=f'Ваш баланс — {int(balancec["balance"])}')
            emb.add_field(name='> **Ставка:**', value=f'```{number}```')
            emb.add_field(name='> **Выпавшее число:**',
                          value=f'```{random_casino}```')
            emb.add_field(name=f'> **Твой выигрыш:**',
                          value=f'```{number*2}```')
            await ctx.send(embed=emb)
        else:
            await self.inc_money(ctx.author.id, ctx.guild.id, -number)
            emb = disnake.Embed(
                title='Казино',
                description='',
                color=0x2b2d31
            )
            balancec = self.profile.find_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id})
            emb.set_footer(text=f'Ваш баланс — {int(balancec["balance"])}')
            emb.add_field(name='> **Ставка:**', value=f'```{number}```')
            emb.add_field(name='> **Выпавшее число:**',
                          value=f'```{random_casino}```')
            emb.add_field(name=f'> **Ты проиграл:**',
                          value=f'```{number}```')
            await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(Ecomony(bot))
    print('Ког: "Экономика" загрузился!')
