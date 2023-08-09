import pymongo
import disnake
from disnake.ext import commands
from pymongo import MongoClient
from config import *
from mod import *
import time
import re

test_guild = [1084577336340512889]

emoji_money_id = 1091827829500555286


class Page(commands.Cog, name="page"):
    def __init__(self, bot):
        self.bot = bot

        self.cluster = self.bot.cluster
        self.lroles: pymongo.collection.Collection = self.cluster.infinity.L_roles
        self.lshop: pymongo.collection.Collection = self.cluster.infinity.L_roles_shop
        self.profile: pymongo.collection.Collection = self.cluster.infinity.profile
        self.l_buys_roles: pymongo.collection.Collection = self.cluster.infinity.buys_roles
        self.g_count: pymongo.collection.Collection = self.cluster.infinity.guilds
        self.lovess: pymongo.collection.Collection = self.cluster.infinity.loves
        self.l_room: pymongo.collection.Collection = self.cluster.infinity.L_rooms

    @commands.slash_command(
        name='leaderboard',
        dm_permission=False,
        description=f'Просмотр серверного топа по категориям',
        color=0x2b2d31,
        options=[
            disnake.Option(
                name='тип',
                description=f'Выберите топ, который хотите посмотреть',
                required=True,
                type=disnake.OptionType.integer,
                choices=[
                    disnake.OptionChoice(
                        name='голосовой онлайн',
                        value=1
                    ),
                    disnake.OptionChoice(
                        name='баланс',
                        value=2
                    ),
                    disnake.OptionChoice(
                        name='онлайн лаврум',
                        value=3
                    ),
                    disnake.OptionChoice(
                        name='онлайн личных комнат',
                        value=4
                    ),
                ]
            )
        ]
    )
    async def leaderboard(self, ctx: disnake.ApplicationCommandInteraction, тип: int):
        types: int = тип
        if types == 1:
            find = self.profile.find({"guild_id": ctx.guild.id, "voice": {"$gt": 0}}).sort([("voice", -1)])
            find = group_list(list(find)[:30], 10)
            count = len(find)
            if count == 0:
                await ctx.send(embed=disnake.Embed(color=0x2b2d31, description=f'{ctx.author.mention}, данный топ **пуст**!')),
                return
            embed = disnake.Embed(
                title=f'Топ по онлайну — {ctx.guild.name}',
                description='',
                color=0x2b2d31
            )
            embeds = []
            for page, group in enumerate(find):
                for index, user in enumerate(group):
                    place = page * 10 + index + 1
                    member = ctx.guild.get_member(user['member_id'])
                    online = user['voice']
                    minutes = int(online % 60)
                    hour = int(online // 60)
                    if hour < 1:
                        hour = 0
                    if minutes < 1 or minutes >= 60:
                        minutes = 0
                    if member:
                        embed.description += f'**{place})** Пользователь: {member.mention}\n**·** Онлайн: `{hour}ч, {minutes}м` \n'
                    else:
                        self.profile.delete_one(user)
                embed.set_footer(text=f'Страница {page + 1}/{count}')
                embeds.append(embed.copy())
                embed.description = ''
            if len(embeds) > 1:
                btns = Pages_Standart(embeds=embeds, time_end=180)
                await ctx.send(embed=embeds[0], view=btns)
            else:
                await ctx.send(embed=embeds[0])
        elif types == 2:
            finds = self.profile.find({"guild_id": ctx.guild.id, "balance": {"$gt": 0}}).sort([("balance", -1)])
            find = group_list(list(finds)[:30], 10)
            count = len(find)
            if count == 0:
                await ctx.send(embed=disnake.Embed(color=0x2b2d31, description=f'{ctx.author.mention}, данный топ **пуст**!'))
                return
            embed = disnake.Embed(
                title=f'Топ по деньгам — {ctx.guild.name}',
                description='',
                color=0x2b2d31
            )
            embeds = []
            for page, group in enumerate(find):
                for index, user in enumerate(group):
                    place = page * 10 + index + 1
                    member = ctx.guild.get_member(user['member_id'])
                    if member:
                        embed.description += f'{place}) Баланс: {int(user["balance"])} {self.bot.get_emoji(emoji_money_id)}\n**·** Пользователь: {member.mention} \n'
                    else:
                        embed.description += f'{place}) Баланс: {int(user["balance"])} {self.bot.get_emoji(emoji_money_id)}\n**·** Пользователь: <@{user["member_id"]}> \n'
                embed.set_footer(text=f'Страница {page + 1}/{count}')
                embeds.append(embed.copy())
                embed.description = ''
            if len(embeds) > 1:
                btns = Pages_Standart(embeds=embeds, time_end=180)
                await ctx.send(embed=embeds[0], view=btns)
            else:
                await ctx.send(embed=embeds[0])
        elif types == 3:
            finds = self.lovess.find({"guild_id": ctx.guild.id, "voice": {"$gt": 0}}).sort([("voice", -1)])
            find = group_list(list(finds)[:30], 10)
            count = len(find)
            if count == 0:
                await ctx.send(embed=disnake.Embed(color=0x2b2d31, description=f'{ctx.author.mention}, данный топ **пуст**!'))
                return
            embed = disnake.Embed(
                title=f'Топ по онлайну лаврум — {ctx.guild.name}',
                description='',
                color=0x2b2d31
            )
            embeds = []
            for page, group in enumerate(find):
                for index, user in enumerate(group):
                    place = page * 10 + index + 1
                    man = ctx.guild.get_member(user["man"])
                    girl = ctx.guild.get_member(user["girl"])
                    if man and girl:
                        embed.description += f'{place}) Провели: {user["voice"]//60} ч, {user["voice"]%60} м\n {man.mention} и {girl.mention}'
                    else:
                        embed.description += f'{place}) Провели: {user["voice"]//60} ч, {user["voice"]%60} м\n <@{user["man"]}> и <@{user["girl"]}>'
                embed.set_footer(text=f'Страница {page + 1}/{count}')
                embeds.append(embed.copy())
                embed.description = ''
            if len(embeds) > 1:
                btns = Pages_Standart(embeds=embeds, time_end=180)
                await ctx.send(embed=embeds[0], view=btns)
            else:
                await ctx.send(embed=embeds[0])
        elif types == 4:
            finds = self.l_room.find({"guild_id": ctx.guild.id, "voice": {"$gt": 0}}).sort([("voice", -1)])
            find = group_list(list(finds)[:30], 10)
            count = len(find)
            if count == 0:
                await ctx.send(embed=disnake.Embed(color=0x2b2d31, description=f'{ctx.author.mention}, данный топ **пуст**!'))
                return
            embed = disnake.Embed(
                title=f'Топ по онлайну личных комнат — {ctx.guild.name}',
                description='',
                color=0x2b2d31
            )
            embeds = []
            for page, group in enumerate(find):
                for index, user in enumerate(group):
                    place = page * 10 + index + 1
                    channel: disnake.VoiceChannel = ctx.guild.get_channel(user['channel'])
                    if channel:
                        embed.description += f'{place}) Провели: {user["voice"]//60} ч, {user["voice"]%60} м\n {channel.mention}'
                    else:
                        place -= 1
                        continue
                embed.set_footer(text=f'Страница {page + 1}/{count}')
                embeds.append(embed.copy())
                embed.description = ''
            if len(embeds) > 1:
                btns = Pages_Standart(embeds=embeds, time_end=180)
                await ctx.send(embed=embeds[0], view=btns)
            else:
                await ctx.send(embed=embeds[0])

    @commands.slash_command(
        name='shop',
        description=f'Открыть магазин личных ролей',
    )
    async def shop(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        emoji = self.bot.get_emoji(emoji_money_id)
        finds = list(self.lshop.find({"guild_id": ctx.guild.id}))
        if not finds:
            emb = disnake.Embed(
                title='Магазин личных ролей',
                description=f'Магазин в данный момент **пуст**!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=emb, ephemeral=True)
            return
        find = group_list(finds, 5)
        embed = disnake.Embed(
            title=f'Магазин личных ролей',
            description='',
            color=0x2b2d31
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embeds = []
        for page, group in enumerate(find):
            for index, r in enumerate(group):
                place = page * 5 + index + 1
                role = ctx.guild.get_role(r['_id'])
                member = ctx.guild.get_member(r["role_owner"])
                if role and member:
                    embed.description += f'**{place})** {role.mention}\n**·** **Продавец:** {member.mention}\n**·** **Стоимость:** `{r["price"]}`{emoji}\n**·** **Куплена раз:** `{r["buy_raz"]}`\n\n'
                else:
                    place -= 1
                    self.lshop.delete_one(r)
            embeds.append(embed.copy())
            embed.description = ''
        await Shop_Button(ctx, embeds, self.bot, 120, finds, self.profile, len(finds), self.lshop, self.l_buys_roles)



def setup(bot):
    bot.add_cog(Page(bot))
    print('Ког: "Страницы" загрузился!')
