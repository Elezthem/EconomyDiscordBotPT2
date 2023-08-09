import pymongo
import disnake
from disnake.ext import commands
from pymongo import MongoClient
from config import *
import time
import re
from mod import *
from disnake import ButtonStyle
import requests
from PIL import Image
import os

test_guild = [1084577336340512889]
emoji_money_id = 1091827829500555286


class lroles(commands.Cog, name="lroles"):
    def __init__(self, bot):
        self.bot = bot

        self.cluster = self.bot.cluster
        self.lroles: pymongo.collection.Collection = self.cluster.infinity.L_roles
        self.lshop: pymongo.collection.Collection = self.cluster.infinity.L_roles_shop
        self.profile: pymongo.collection.Collection = self.cluster.infinity.profile
        self.g_count: pymongo.collection.Collection = self.cluster.infinity.guilds
        self.l_buys_roles: pymongo.collection.Collection = self.cluster.infinity.buys_roles

    async def ballance(self, member_id, guild_id):
        acc = self.profile.find_one({"member_id": member_id, "guild_id": guild_id})
        if acc and "balance" in acc.keys():
            return acc['balance']
        else:
            return 0

    async def get_member(self, member1, guild: disnake.Guild):
        if type(member1) != int:
            id_mem = member1 \
                .replace("<", "") \
                .replace("@", "") \
                .replace("!", "") \
                .replace(">", "")
        else:
            id_mem = member1
        member = guild.get_member(id_mem)
        return member

    @commands.slash_command(
        name='role'
    )
    async def roles(self, ctx):
        pass

    @roles.sub_command(
        name='create',
        description=f'Создать личную роль',
        options=[
            disnake.Option(
                name='name',
                description='Укажите название роли',
                required=True,
                type=disnake.OptionType.string
            ),
            disnake.Option(
                name='color',
                description='Укажите цвет роли (в hex формате)',
                required=True,
                type=disnake.OptionType.string
            )
        ],
    )
    async def create_role(self, ctx: disnake.ApplicationCommandInteraction, name: str, color: str):
        money = await self.ballance(ctx.author.id, ctx.guild.id)
        emoji = self.bot.get_emoji(emoji_money_id)
        if self.lroles.count_documents({"owner_id": ctx.author.id, "guild_id": ctx.guild.id}) == 3:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, вы **достигли** лимита по владению личными ролями!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            emb.set_footer(
                text='На сервере действует ограничение 3 личных роли на пользователя!')
            await ctx.send(embed=emb, ephemeral=True)
            return
        elif money < 5000:  # цена создания роли
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, ваш баланс **меньше** `5000` {emoji}!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=emb, ephemeral=True)
            return
        await ctx.response.defer()
        emb = disnake.Embed(
            title='Создание личной роли',
            description=f'{ctx.author.mention}, вы **уверены** что хотите создать роль с названием: `{name}` и цветом: `{color}` ?',
            color=0x2b2d31
        )
        emb.set_thumbnail(url=ctx.author.avatar.url)
        emb.set_footer(text='Стоимость роли составляет 5000 монет')
        row = disnake.ui.ActionRow()
        row.add_button(style=ButtonStyle.green,
                       label='Да', emoji='✔', custom_id='role_create_1')
        row.add_button(style=ButtonStyle.red, label='Нет',
                       emoji='❌', custom_id='role_create_2')
        msg = await ctx.edit_original_message(embed=emb, components=[row])
        try:
            inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=120, check=lambda i: i.author.id == ctx.author.id and i.message.id == msg.id)
        except asyncio.TimeoutError:
            await ctx.edit_original_message(components=[])
            return
        if inter.component.custom_id == 'role_create_1':
            color = color \
                .replace("#", "")
            try:
                color = int(f"{color}", 16)
            except ValueError:
                await inter.response.edit_message(f'Цвет должен состоять из **6** **букв(английских) или цифр**',
                                                  components=[])
                return
            role = await ctx.guild.create_role(name=name, colour=disnake.Colour(color))
            rol_i = role.id
            times1 = int(time.time())
            timess = int(times1 + 60*60*24*30)
            rol = {
                "owner_id": ctx.author.id,
                "r_id": rol_i,
                "count": self.lroles.count_documents({"owner_id": ctx.author.id, "guild_id": ctx.guild.id}) + 1,
                "role_time": timess,
                "rol_name": name,
                "role_create_time": int(time.time()),
                "guild_id": ctx.guild.id
            }
            self.lroles.insert_one(rol)
            self.profile.update_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id}, {"$inc": {"balance": -10000}},
                                  True)
            await ctx.author.add_roles(role)
            emb = disnake.Embed(
                title='Создание личной роли',
                description=f'{ctx.author.mention}, вы **успешно** создали роль {role.mention}!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            emb.set_footer(
                text='Для управления ролью используйте команду: /role manage')
            await inter.response.edit_message(embed=emb, components=[])
        elif inter.component.custom_id == 'role_create_2':
            emb = disnake.Embed(
                title='Отказ',
                description=f'{ctx.author.mention}, вы **отменили** создание личной роли!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await inter.response.edit_message(embed=emb)

    @roles.sub_command(
        name='info',
        description=f'Посмотреть информацию о личной роли',
        options=[
            disnake.Option(
                name='role',
                description='Укажите роль',
                type=disnake.OptionType.role,
                required=True
            )
        ]
    )
    async def role_info(self, ctx: disnake.ApplicationCommandInteraction, role):
        finds = self.lroles.find_one({"r_id": role.id})
        if not finds:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, данная роль **не является личной!**',
                color=0x2b2d31
                
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=emb, ephemeral=True)
        else:
            finds_shop = self.lshop.find_one({"_id": role.id})
            if finds_shop:
                buys = 'Да'
                buys_raz = finds_shop['buy_raz']
            else:
                buys = 'Нет'
                buys_raz = 0
            emb = disnake.Embed(
                title=f'Информация о Роли - {role}',
                description=f'**· Роль:** {role.mention}\n'
                            f'**· Владелец:** {ctx.guild.get_member(finds["owner_id"]).mention}\n'
                            f'**· Носителей:** `{len(role.members)}`\n'
                            f'**· Продаётся:** `{buys}`\n'
                            f'**· Продана раз:** `{buys_raz}`\n'
                            f'**· ID:** `{role.id}`\n'
                            f'**· Цвет роли:** `{role.color}`\n\n'
                            f'**· Действует до:** <t:{finds["role_time"]}>\n',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=emb)

    @roles.sub_command(
        name='manage',
        description=f'Управление личной ролью',
        options=[],
        guild_ids=test_guild
    )
    async def role_menu(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        finds1 = list(self.lroles.find({"owner_id": ctx.author.id, "guild_id": ctx.guild.id}))
        finds = group_list(finds1)
        if not finds1:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, у вас **нет** личной роли!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            emb.set_footer(
                text=f'Для помощи в её создании - нажмите кнопку ниже!')
            row = disnake.ui.ActionRow()
            row.add_button(style=ButtonStyle.gray,
                           label='Информация', emoji='📄', custom_id='create_help1')
            msg = await ctx.edit_original_message(embed=emb, components=[row])
            try:
                inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=120, check=lambda i: i.author.id == ctx.author.id and i.message.id == msg.id)
            except asyncio.TimeoutError:
                await ctx.edit_original_message(components=[])
                return
            if inter.component.custom_id == 'create_help1':
                emb = disnake.Embed(
                    title='Помощь по созданию личной роли',
                    description=f'Для создания личной роли требуется **5000 {self.bot.get_emoji(emoji_money_id)}**!\n'
                                f'Команда для создания роли `/role create`\n'
                                f'Для её работы требуется указать название и цвет роли!\n'
                                f'Код цвета надо указывать в hex - формате.\n'
                                f'`/role create *имя* *цвет* ` - пример создания роли.\n'
                                f'Сайт hex-цветов: https://htmlcolorcodes.com',
                    color=0x2b2d31

                )
                emb.set_footer(
                    text=f'По всем ошибкам бота обращаться к "Neptun#1001"')
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await inter.response.edit_message(embed=emb, components=[])
        else:
            ball = await self.ballance(ctx.author.id, ctx.guild.id)
            emoji = self.bot.get_emoji(emoji_money_id)
            emb2 = disnake.Embed(
                title='Личные Роли',
                description=f'{ctx.author.mention}, **выберите** роль ниже!',
                color=0x2b2d31
            )
            emb2.set_thumbnail(url=ctx.author.avatar.url)
            optioons = []
            names = []
            for page, group in enumerate(finds):
                for index, r in enumerate(group):
                    times = ((r['role_time'] - int(time.time())) // 60) // 60
                    days = int(times // 24)
                    time_end: str = f'{days} д, {int(times % 24)} ч'
                    names.append({"name": r['rol_name']})
                    optioons.append(disnake.SelectOption(
                        label=r['rol_name'], value=f"select_l_role_{r['count']}",
                        description=f"До конца действия роли осталось: {time_end}"))
            row = disnake.ui.ActionRow()
            row.add_select(options=optioons,
                           placeholder="Выберите роль!",
                           min_values=1,
                           max_values=1,
                           custom_id='select_to_role')
            msg = await ctx.edit_original_message(embed=emb2, components=[row])
            try:
                inter: disnake.MessageInteraction = await self.bot.wait_for("dropdown", timeout=60, check=lambda i: i.author.id == ctx.author.id and i.message.id == msg.id)
            except asyncio.TimeoutError:
                await ctx.edit_original_message(components=[])
                return
            if inter.component.custom_id == "select_to_role":
                if inter.values[0] == 'select_l_role_1':
                    abc = names[0]
                    num1 = self.lroles.find_one({"rol_name": abc['name']})
                elif inter.values[0] == 'select_l_role_2':
                    abc = names[1]
                    num1 = self.lroles.find_one({"rol_name": abc['name']})
                elif inter.values[0] == 'select_l_role_3':
                    abc = names[2]
                    num1 = self.lroles.find_one({"rol_name": abc['name']})
                else:
                    return
                rol_id = num1['r_id']
                rol_time = num1['role_time']
                r_s = self.lshop.find_one({"_id": rol_id})
                role = ctx.guild.get_role(rol_id)
                emb = disnake.Embed(
                    title='Личная Роль',
                    description=f'{ctx.author.mention}, **выберите** что хотите **сделать** с вашей личной ролью {role.mention}\n'
                                f'\nВаша роль действует до <t:{int(rol_time)}>',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                row1 = disnake.ui.ActionRow()
                row1.add_button(style=ButtonStyle.gray,
                                label='Переименовать', emoji='🖊', custom_id='role_manage_1')
                row1.add_button(style=ButtonStyle.gray,
                                label='Изменить цвет', emoji='🎨', custom_id='role_manage_2')
                row1.add_button(style=ButtonStyle.gray,
                                label='Выдать роль', emoji='➕', custom_id='role_manage_3')
                row1.add_button(style=ButtonStyle.gray,
                                label='Снять роль', emoji='➖', custom_id='role_manage_4')
                row1.add_button(style=ButtonStyle.gray,
                                label='Продлить', emoji='💠', custom_id='role_manage_5')
                row2 = disnake.ui.ActionRow()
                row2.add_button(style=ButtonStyle.gray, label='Изменить иконку',
                                emoji='🖼', custom_id='role_manage_12')
                if r_s:
                    row2.add_button(style=ButtonStyle.gray, label='Выставить на Продажу',
                                    emoji='🛒', custom_id='role_manage_6', disabled=True)
                    row2.add_button(style=ButtonStyle.gray, label='Снять с Продажи', emoji='❌',
                                    custom_id='role_manage_7')
                else:
                    row2.add_button(style=ButtonStyle.gray, label='Выставить на Продажу',
                                    emoji='🛒', custom_id='role_manage_6')
                    row2.add_button(style=ButtonStyle.gray, label='Снять с Продажи', emoji='❌',
                                    custom_id='role_manage_7',
                                    disabled=True)
                row2.add_button(style=ButtonStyle.gray,
                                label='Удалить роль', emoji='🗑', custom_id='role_manage_8')
                row2.add_button(style=ButtonStyle.gray,
                                label='Отмена', emoji='🚫', custom_id='role_manage_9')
                await inter.response.edit_message(embed=emb, components=[row1, row2])
                try:
                    def check_a(i: disnake.MessageInteraction):
                        if i.author.id == ctx.author.id and i.message.id == msg.id:
                            return True
                        return False

                    inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=120,
                                                                                check=lambda i: check_a(i))
                except asyncio.TimeoutError:
                    await ctx.edit_original_message(components=[])
                    return
                if inter.component.custom_id == 'role_manage_1':
                    emb = disnake.Embed(
                        title='Изменение названия',
                        description=f'{ctx.author.mention}, введите **новое** название вашей **роли**',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    emb.set_footer(text=f'Для этого у вас есть 60 секунд.')
                    await inter.response.edit_message(embed=emb, components=[])
                    try:
                        name = await self.bot.wait_for("message", check=lambda i: i.author == ctx.author, timeout=60)
                    except asyncio.TimeoutError:
                        emb = disnake.Embed(
                            title='Изменение названия роли',
                            description=f'{ctx.author.mention}, время **вышло**!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                        return
                    await name.delete()
                    nname = name.content
                    await role.edit(name=nname)
                    self.lroles.update_one({"_id": ctx.author.id}, {"$set": {"rol_name": nname}})
                    emb = disnake.Embed(
                        title='Изменение названия роли',
                        description=f'{ctx.author.mention}, вы **изменили** название роли на `"{nname}"` у роли {role.mention}',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    await inter.edit_original_message(embed=emb, components=[])
                    self.lroles.update_one({'r_id': role.id}, {"$set": {"rol_name": nname}})
                elif inter.component.custom_id == 'role_manage_2':
                    emb = disnake.Embed(
                        title='Изменение цвета роли',
                        description=f'{ctx.author.mention}, введите **новый** цвет для вашей **роли**',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    emb.set_footer(text=f'Для этого у вас есть 60 секунд.')
                    await inter.response.edit_message(embed=emb, components=[])
                    try:
                        col = await self.bot.wait_for("message", check=lambda i: i.author == ctx.author, timeout=60)
                    except asyncio.TimeoutError:
                        emb = disnake.Embed(
                            title='Изменение цвета роли',
                            description=f'{ctx.author.mention}, время **вышло**!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                        return
                    await col.delete()
                    coll = col.content
                    color = int(f"{coll}", 16)
                    await role.edit(colour=disnake.Colour(color))
                    emb = disnake.Embed(
                        title='Изменение цвета роли',
                        description=f'{ctx.author.mention}, вы **изменили** цвет вашей роли на `"{coll}"` у роли {role.mention}',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    await inter.edit_original_message(embed=emb, components=[])
                elif inter.component.custom_id == 'role_manage_3':
                    emb = disnake.Embed(
                        title='Выдача личной роли',
                        description=f'{ctx.author.mention}, укажите **id пользователя** или его **упоминание**. ',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    emb.set_footer(text='Для этого у вас есть 60 секунд.')
                    await inter.response.edit_message(embed=emb, components=[])
                    try:
                        res = await self.bot.wait_for("message", check=lambda i: i.author == ctx.author, timeout=60)
                    except asyncio.TimeoutError:
                        emb = disnake.Embed(
                            title='Выдача личной роли',
                            description=f'{ctx.author.mention}, время **вышло**!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                        return
                    await res.delete()
                    member = await self.get_member(member1=res.content, guild=inter.guild)
                    await member.add_roles(role)
                    emb = disnake.Embed(
                        title='Выдача личной роли',
                        description=f'{ctx.author.mention}, вы **выдали** роль {role.mention} пользователю {member.mention}',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    await inter.edit_original_message(embed=emb, components=[])
                elif inter.component.custom_id == 'role_manage_4':
                    emb = disnake.Embed(
                        title='Снятие личной роли',
                        description=f'{ctx.author.mention}, укажите **id пользователя** или его **упоминание**.',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    emb.set_footer(text='Для этого у вас есть 60 секунд.')
                    await inter.response.edit_message(embed=emb, components=[])
                    try:
                        res = await self.bot.wait_for("message", check=lambda i: i.author == ctx.author, timeout=60)
                    except asyncio.TimeoutError:
                        emb = disnake.Embed(
                            title='Снятие личной роли',
                            description=f'{ctx.author.mention}, время **вышло**!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                        return
                    await res.delete()
                    member = await self.get_member(member1=res.content, guild=inter.guild)
                    polzovatel = self.l_buys_roles.find({"_id": member.id})
                    if polzovatel:
                        emb = disnake.Embed(
                            title='Ошибка',
                            description=f'{ctx.author.mention}, вы **не можете** снять роль с пользователя купившему её в магазине!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                    else:
                        await member.remove_roles(role)
                        emb = disnake.Embed(
                            title='Снятие Личной Роли',
                            description=f'{ctx.author.mention}, вы **сняли** роль {role.mention} с пользователя {member.mention}',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                elif inter.component.custom_id == 'role_manage_5':
                    emb = disnake.Embed(
                        title='Продление Роли',
                        description=f'{ctx.author.mention}, вы уверены что хотите продлить роль {role.mention} на **30** дней за **3000** {emoji}',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    row = disnake.ui.ActionRow()
                    row.add_button(style=ButtonStyle.green,
                                   label='Да', emoji='✔', custom_id='role_create_10')
                    row.add_button(style=ButtonStyle.red,
                                   label='Нет', emoji='❌', custom_id='role_create_11')
                    await inter.response.edit_message(embed=emb, components=[row])
                    try:
                        def check_a(i: disnake.MessageInteraction):
                            if i.author.id == ctx.author.id and i.message.id == msg.id:
                                return True
                            return False

                        inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=120,
                                                                                    check=lambda i: check_a(i))
                    except asyncio.TimeoutError:
                        await ctx.edit_original_message(components=[])
                        return
                    if inter.component.custom_id == 'role_create_10':
                        ball = self.profile.find_one({"member_id": ctx.author.id, "guild_id": inter.guild.id})['balance']
                        if ball < 3000:
                            emb = disnake.Embed(
                                title=f'Продление Роли',
                                description=f'{ctx.author.mention}, ваш баланс **меньше** `3000` {emoji}',
                                color=0x2b2d31
                            )
                            emb.set_thumbnail(url=ctx.author.avatar.url)
                            await inter.response.edit_message(embed=emb, components=[])
                        else:
                            self.lroles.update_one({"r_id": role.id}, {"$inc": {"role_time": 60*60*24*30}})
                            self.profile.update_one({"_id": ctx.author.id}, {"$inc": {"balance": -3000}})
                            emb = disnake.Embed(
                                title=f'Продление Роли',
                                description=f'{ctx.author.mention}, вы **продлили** вашу роль {role.mention} на **30 дней** за **3000** {emoji}',
                                color=0x2b2d31
                            )
                            emb.set_thumbnail(url=ctx.author.avatar.url)
                            await inter.response.edit_message(embed=emb, components=[])
                    elif inter.component.custom_id == 'role_create_11':
                        emb = disnake.Embed(
                            title='Продление Роли',
                            description=f'{ctx.author.mention}, вы **отменили** продление вашей роли {role.mention}'),
                        color=0x2b2d31
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.response.edit_message(embed=emb, components=[])
                elif inter.component.custom_id == 'role_manage_6':
                    emb = disnake.Embed(
                        title='Продажа роли',
                        description=f'{ctx.author.mention}, введите **цену** для вашей **роли**\n'
                                    f'`цена должна быть целым числом`',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    emb.set_footer(text=f'Для этого у вас есть 60 секунд.')
                    await inter.response.edit_message(embed=emb, components=[])
                    try:
                        name = await self.bot.wait_for("message", check=lambda i: i.author == ctx.author, timeout=60)
                    except asyncio.TimeoutError:
                        emb = disnake.Embed(
                            title='Продажа роли',
                            description=f'{ctx.author.mention}, время **вышло**!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                        return
                    await name.delete()
                    try:
                        price = int(name.content)
                    except ValueError:
                        await inter.edit_original_message(f'{ctx.author.mention}, это **не число**!')
                        return
                    if price > 999999:
                        emb = disnake.Embed(
                            title='Продажа роли',
                            description=f'{ctx.author.mention}, цена роли не может быть более **999999** монет! \n'
                                        f'`Вы указали цену {price} монет!` ',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                    elif price < 100:
                        emb = disnake.Embed(
                            title='Продажа роли',
                            description=f'{ctx.author.mention}, цена роли не может быть меньше **100** монет! \n'
                                        f'`Вы указали цену {price} монет!` ',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                    else:
                        self.lshop.insert_one(
                            {"_id": role.id, "price": price, "role_owner": ctx.author.id, "buy_raz": 0,
                             "guild_id": ctx.guild.id})
                        emb = disnake.Embed(
                            title='Продажа роли',
                            description=f'{ctx.author.mention}, вы **выставили** вашу роль {role.mention} в магазин за `{price}` {self.bot.get_emoji(emoji_money_id)}!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                elif inter.component.custom_id == 'role_manage_7':
                    self.lshop.delete_one(r_s)
                    emb = disnake.Embed(
                        title='Снятие Роли с Продажи',
                        description=f'{ctx.author.mention}, вы **сняли** вашу роль {role.mention} с продажи в магазине!',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    await inter.response.edit_message(embed=emb, components=[])
                elif inter.component.custom_id == 'role_manage_8':
                    emb = disnake.Embed(
                        title='Удаление роли',
                        description=f'{ctx.author.mention}, вы уверены что хотите **удалить** роль с сервера **навсегда**?',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    row = disnake.ui.ActionRow()
                    row.add_button(style=ButtonStyle.green,
                                   label='Да', emoji='✔', custom_id='role_create_13')
                    row.add_button(style=ButtonStyle.red,
                                   label='Нет', emoji='❌', custom_id='role_create_14')
                    await inter.response.edit_message(embed=emb, components=[row])
                    try:
                        def check_a(i: disnake.MessageInteraction):
                            if i.author.id == ctx.author.id and i.message.id == msg.id:
                                return True
                            return False

                        inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=120,
                                                                                    check=lambda i: check_a(i))
                    except asyncio.TimeoutError:
                        await ctx.edit_original_message(components=[])
                        return
                    if inter.component.custom_id == 'role_create_13':
                        await role.delete()
                        self.lroles.delete_one(num1)
                        if r_s:
                            self.lshop.delete_one(r_s)
                        emb = disnake.Embed(
                            title='Удаление роли',
                            description=f'{ctx.author.mention}, вы **удалили** свою роль с сервера!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.response.edit_message(embed=emb, components=[])
                    elif inter.component.custom_id == 'role_create_14':
                        emb = disnake.Embed(
                            title='Удаление роли',
                            description=f'{ctx.author.mention}, вы **отменили** удаление роли с сервера!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.response.edit_message(embed=emb, components=[])
                elif inter.component.custom_id == 'role_manage_9':
                    emb = disnake.Embed(
                        title='Меню личной роли',
                        description=f'{ctx.author.mention}, вы **закрыли** меню личной роли!',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    await inter.response.edit_message(embed=emb, components=[])
                elif inter.component.custom_id == 'role_manage_12':
                    emb = disnake.Embed(
                        title='Изменение иконки роли',
                        description=f'{ctx.author.mention}, **отправьте** в чат вашу картинку для роли\n',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    emb.set_footer(text='Для отмены введите: cancel | Для сброса: reset')
                    await inter.response.edit_message(embed=emb, components=[])
                    try:
                        name: disnake.Message = await self.bot.wait_for("message",
                                                                        check=lambda i: i.author == ctx.author,
                                                                        timeout=60)
                    except asyncio.TimeoutError:
                        emb = disnake.Embed(
                            title='Изменение Иконки Роли',
                            description=f'{ctx.author.mention}, время **вышло**!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                        return
                    await name.delete()
                    if len(name.content) != 0:
                        if name.content == "cancel":
                            emb = disnake.Embed(
                                title='Изменение Иконки Роли',
                                description=f'{ctx.author.mention}, вы **отменили** изменение иконки роли!',
                                color=0x2b2d31
                            )
                            await inter.edit_original_message(embed=emb, components=[])
                            return
                        elif name.content == 'reset':
                            await role.edit(icon=None)
                            emb = disnake.Embed(
                                title='Изменение Иконки Роли',
                                description=f'{ctx.author.mention}, вы **сбросили** иконку роли!',
                                color=0x2b2d31
                            )
                            await inter.edit_original_message(embed=emb, components=[])
                            return
                    if len(name.attachments) > 0:
                        img = Image.open(requests.get(name.attachments[0].url, stream=True).raw)
                        img.save(f'src/icons_role/{name.author.id}.png')
                        with open(f'src/icons_role/{name.author.id}.png', "rb") as image:
                            f = image.read()
                            b = bytearray(f)
                    else:
                        emb = disnake.Embed(
                            title='Ошибка',
                            description=f'{ctx.author.mention}, **проверьте** вашу иконку и повторите попытку!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                        return
                    try:
                        await role.edit(icon=b)
                        os.remove(f'src/icons_role/{name.author.id}.png')
                    except (disnake.NotFound, disnake.Forbidden, disnake.HTTPException, disnake.InvalidArgument):
                        emb = disnake.Embed(
                            title='Ошибка',
                            description=f'{ctx.author.mention}, **проверьте** вашу иконку и повторите попытку!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=ctx.author.avatar.url)
                        await inter.edit_original_message(embed=emb, components=[])
                        return
                    emb = disnake.Embed(
                        title='Изменение Иконки Роли',
                        description=f'{ctx.author.mention}, вы **успешно** изменили иконку для роли {role.mention}',
                        color=0x2b2d31
                    )
                    await inter.edit_original_message(embed=emb, components=[])


def setup(bot):
    bot.add_cog(lroles(bot))
    print('Ког: "Личные Роли" загрузился!')
