import time

import disnake
import pymongo.collection
from disnake.ext import commands, tasks
from config import *
from mod import *
import asyncio

test_guild = [1084577336340512889]


class Drop_Room(disnake.ui.View):
    def __init__(self, opt, msg, user, names, db, bot):
        super().__init__(timeout=60)
        self.add_item(select_menu_room_create(options=opt, user=user, names=names, db=db, bot=bot))
        self.msg: disnake.ApplicationCommandInteraction = msg
        self.user = user

    async def on_timeout(self) -> None:
        self.clear_items()
        emb = disnake.Embed(
            title='Меню личных комнат',
            description=f'{self.user.mention}, Время **закончилось** на **Выбор комнты** / **т.д**',
            color=0x2b2d31
        )
        emb.set_thumbnail(url=self.user.avatar.url)
        await self.msg.edit_original_message(embed=emb, view=None)


class select_menu_room_create(disnake.ui.Select):
    def __init__(self, options, names, user, db, bot):
        super().__init__(
            placeholder="Выберите комнату",
            min_values=1,
            max_values=1,
            options=options
        )
        self.names = names
        self.user = user
        self.db = db
        self.bot = bot

    async def callback(self, interaction: disnake.MessageInteraction):
        if self.user.id != interaction.user.id:
            await interaction.send(f'{interaction.user.mention}, это меню **не принадлежит** вам!')
            return
        val = self.values[0]
        if val == 'select_l_room_1':
            abc = self.names[0]
        elif val == 'select_l_room_2':
            abc = self.names[1]
        elif val == 'select_l_room_3':
            abc = self.names[2]
        elif val == 'select_l_room_4':
            abc = self.names[3]
        elif val == 'select_l_room_5':
            abc = self.names[4]
        elif val == 'select_l_room_6':
            abc = self.names[5]
        elif val == 'select_l_room_7':
            abc = self.names[6]
        elif val == 'select_l_room_8':
            abc = self.names[7]
        elif val == 'select_l_room_9':
            abc = self.names[8]
        elif val == 'select_l_room_10':
            abc = self.names[9]
        else:
            abc = self.names[0]
        num1 = self.db.find_one(
            {"room_name": abc['name'], "guild_id": interaction.guild.id, "manage_id": interaction.author.id})
        channel = self.bot.get_channel(num1['channel'])
        emb = disnake.Embed(
            title='Личная комната',
            description=f'{interaction.author.mention}, **выберите** что хотите **сделать** личной комнатой <#{channel.id}>\n',
            color=0x2b2d31
        )
        emb.set_thumbnail(url=interaction.author.avatar.url)
        row1 = disnake.ui.ActionRow()
        row1.add_button(style=disnake.ButtonStyle.gray,
                        label='Пригласить в комнату ролью', emoji='🎭', custom_id='l_rooms_1')
        row1.add_button(style=disnake.ButtonStyle.gray,
                        label='Пригласить в комнату без роли', emoji='➕', custom_id='l_rooms_2')
        row1.add_button(style=disnake.ButtonStyle.gray,
                        label='Выгнать из комнаты', emoji='➖', custom_id='l_rooms_3')
        row1.add_button(style=disnake.ButtonStyle.gray,
                        label='Открыть комнату для Всех', emoji='🔓', custom_id='l_rooms_4')
        row1.add_button(style=disnake.ButtonStyle.gray,
                        label='Закрыть комнату для Всех', emoji='🔒', custom_id='l_rooms_5')
        row2 = disnake.ui.ActionRow()
        row2.add_button(style=disnake.ButtonStyle.gray,
                        label='Права на Мут и Мув', emoji='💠', custom_id='l_rooms_6')
        row2.add_button(style=disnake.ButtonStyle.gray,
                        label='Переименовать комнату', emoji='🖊', custom_id='l_rooms_9')
        row2.add_button(style=disnake.ButtonStyle.gray,
                        label='Сменить цвет роли', emoji='🎨', custom_id='l_rooms_10')
        row3 = disnake.ui.ActionRow()
        row3.add_button(style=disnake.ButtonStyle.gray,
                        label='Спрятать комнату от Всех', custom_id='l_rooms_11')
        row3.add_button(style=disnake.ButtonStyle.gray,
                        label='Показать комнату Всем', custom_id='l_rooms_12')
        await interaction.response.edit_message(embed=emb, components=[row1, row2])
        try:
            def check_a(i: disnake.MessageInteraction):
                if i.author.id == interaction.author.id and i.message.id == interaction.message.id:
                    return True
                return False
            inter: disnake.MessageInteraction = await self.bot.wait_for(
                "button_click",
                check=lambda i: check_a(i),
                timeout=60
            )
        except asyncio.TimeoutError:
            try:
                await interaction.edit_original_message(components=[])
            except (disnake.HTTPException, disnake.Forbidden, disnake.NotFound):
                return
            return
        author: disnake.Member = inter.author
        msg: disnake.Message = inter.message
        if inter.component.custom_id == "l_rooms_1":
            emb = disnake.Embed(
                title='Приглашение Участника в Комнату с ролью',
                description=f'{author.mention}, **упомяните** пользователя.',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)
            emb.set_footer(text=f'Для этого у вас есть 60 секунд.')
            await msg.edit(embed=emb, components=[])
            try:
                res = await self.bot.wait_for("message", check=lambda i: i.author == author, timeout=60)
                await res.delete()
                id_mem = res.content \
                    .replace("<", "") \
                    .replace("@", "") \
                    .replace("!", "") \
                    .replace(">", "")
                member = await inter.guild.fetch_member(id_mem)
                if member:
                    role = inter.guild.get_role(num1['role'])
                    if role in member.roles:
                        emb = disnake.Embed(
                            title='Приглашение Участника в Комнату с Ролью',
                            description=f'{author.mention}, у пользователя {member.mention} **уже есть** роль комнаты <#{channel.id}>',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=author.avatar.url)
                        await msg.edit(embed=emb, components=[], delete_after=60)
                    else:
                        emb = disnake.Embed(
                            title='Приглашение Участника в Комнату с Ролью',
                            description=f'{author.mention}, вы **пригласили** пользователя {member.mention} в комнату <#{channel.id}>',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=author.avatar.url)
                        await msg.edit(embed=emb, components=[])
                        await member.add_roles(role)
                        await channel.set_permissions(member, connect=True, view_channel=True)
                else:
                    emb = disnake.Embed(
                        title='Ошибка!',
                        description=f'{author.mention}, я **не могу** найти данного пользователя! Попробуйте ещё раз.',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=author.avatar.url)
                    await msg.edit(embed=emb, components=[])
            except asyncio.TimeoutError:
                emb = disnake.Embed(
                    title='Приглашение Участника в Комнату с Ролью',
                    description=f'{author.mention}, время **вышло**!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=author.avatar.url)
                await msg.edit(embed=emb, components=[], delete_after=45)
        elif inter.component.custom_id == 'l_rooms_2':
            emb = disnake.Embed(
                title='Приглашение Участника в Комнату без Роли',
                description=f'{author.mention}, **упомяните** пользователя.',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)
            emb.set_footer(text=f'Для этого у вас есть 60 секунд.')
            await msg.edit(embed=emb, components=[])
            try:
                res = await self.bot.wait_for("message", check=lambda i: i.author == author, timeout=60)
                await res.delete()
                id_mem = res.content \
                    .replace("<", "") \
                    .replace("@", "") \
                    .replace("!", "") \
                    .replace(">", "")
                member = await inter.guild.fetch_member(id_mem)
                if member:
                    emb = disnake.Embed(
                        title='Приглашение Участника в Комнату без Роли',
                        description=f'{author.mention}, вы **пригласили** пользователя {member.mention} в комнату <#{channel.id}>',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=author.avatar.url)
                    await msg.edit(embed=emb, components=[], delete_after=60)
                    await channel.set_permissions(member, connect=True, view_channel=True)
                else:
                    emb = disnake.Embed(
                        title='Ошибка!',
                        description=f'{author.mention}, я **не могу** найти данного пользователя! Попробуйте ещё раз.',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=author.avatar.url)
                    await msg.edit(embed=emb, components=[])
            except asyncio.TimeoutError:
                emb = disnake.Embed(
                    title='Приглашение Участника в Комнату без Роли',
                    description=f'{author.mention}, время **вышло**!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=author.avatar.url)
                await msg.edit(embed=emb, components=[], delete_after=45)
        elif inter.component.custom_id == 'l_rooms_3':
            emb = disnake.Embed(
                title='Кик Пользователя из Комнаты',
                description=f'{author.mention}, **упомяните** пользователя.',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)
            emb.set_footer(text=f'Для этого у вас есть 60 секунд.')
            await msg.edit(embed=emb, components=[])
            try:
                res = await self.bot.wait_for("message", check=lambda i: i.author == author, timeout=60)
                await res.delete()
                id_mem = res.content \
                    .replace("<", "") \
                    .replace("@", "") \
                    .replace("!", "") \
                    .replace(">", "")
                member = await inter.guild.fetch_member(id_mem)
                if member:
                    role = inter.guild.get_role(num1['role'])
                    emb = disnake.Embed(
                        title='Кик Пользователя из Комнаты',
                        description=f'{author.mention}, вы **выгнали** пользователя {member.mention} из комнаты <#{channel.id}>',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=author.avatar.url)
                    await msg.edit(embed=emb, components=[], delete_after=60)
                    await channel.set_permissions(member, connect=False, view_channel=False)
                    try:
                        await member.remove_roles(role)
                    except disnake.Forbidden or disnake.HTTPException:
                        pass
                else:
                    emb = disnake.Embed(
                        title='Ошибка!',
                        description=f'{author.mention}, я **не могу** найти данного пользователя! Попробуйте ещё раз.',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=author.avatar.url)
                    await msg.edit(embed=emb, components=[])
            except asyncio.TimeoutError:
                emb = disnake.Embed(
                    title='Кик Пользователя из Комнаты',
                    description=f'{author.mention}, время **вышло**!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=author.avatar.url)
                await msg.edit(embed=emb, components=[], delete_after=45)
        elif inter.component.custom_id == 'l_rooms_4':
            emb = disnake.Embed(
                title='Открытие Комнаты для Всех Пользователей Сервера',
                description=f'{author.mention}, комната была успешно **открыта** для всех участников сервера`(которые не имели в неё доступ ранее)`',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)
            await msg.edit(embed=emb, components=[])
            everyone = inter.guild.get_role(inter.guild.id)
            await channel.set_permissions(everyone, connect=True, view_channel=True)
        elif inter.component.custom_id == 'l_rooms_5':
            emb = disnake.Embed(
                title='Закрытие Комнаты от Всех Пользователей Сервера',
                description=f'{author.mention}, комната была успешно **закрыта** от всех участников сервера`(которые не имели в неё доступ ранее)`',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)
            await msg.edit(embed=emb, components=[])
            everyone = inter.guild.get_role(inter.guild.id)
            await channel.set_permissions(everyone, connect=False)
        elif inter.component.custom_id == 'l_rooms_6':
            emb = disnake.Embed(
                title='Права на Перемещение и Мут',
                description=f'{author.mention}, **упомяните** пользователя.',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)
            emb.set_footer(text=f'Для этого у вас есть 60 секунд.')
            await msg.edit(embed=emb, components=[])
            try:
                res = await self.bot.wait_for("message", check=lambda i: i.author == author, timeout=60)
                await res.delete()
                id_mem = res.content \
                    .replace("<", "") \
                    .replace("@", "") \
                    .replace("!", "") \
                    .replace(">", "")
                member = await inter.guild.fetch_member(id_mem)
                if member:
                    emb = disnake.Embed(
                        title='Права на Перемещение и Мут',
                        description=f'{author.mention}, вы **выдали** пользователю {member.mention} права на **перемещение и мут** в комнате <#{channel.id}>',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=author.avatar.url)
                    await msg.edit(embed=emb, components=[], delete_after=60)
                    await channel.set_permissions(member, move_members=True, mute_members=True,
                                                  deafen_members=True)
                else:
                    emb = disnake.Embed(
                        title='Ошибка!',
                        description=f'{author.mention}, я **не могу** найти данного пользователя! Попробуйте ещё раз.',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=author.avatar.url)
                    await msg.edit(embed=emb, components=[])
            except asyncio.TimeoutError:
                emb = disnake.Embed(
                    title='Права на Перемещение и Мут',
                    description=f'{author.mention}, время **вышло**!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=author.avatar.url)
                await msg.edit(embed=emb, components=[], delete_after=45)
        elif inter.component.custom_id == 'l_rooms_9':
            emb = disnake.Embed(
                title='Смена Названия Комнаты и Роли',
                description=f'{author.mention}, **введите** новое название.',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)
            await msg.edit(embed=emb, components=[])
            try:
                res = await self.bot.wait_for("message", check=lambda i: i.author == author, timeout=60)
                await res.delete()
                name = res.content
                role = inter.guild.get_role(num1['role'])
                await role.edit(name=name)
                await channel.edit(name=f'· {name}')
                emb = disnake.Embed(
                    title='Смена Названия Комнаты и Роли',
                    description=f'{author.mention}, название комнаты и роли было изменено на **{name}**',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=author.avatar.url)
                await msg.edit(embed=emb, components=[])
            except asyncio.TimeoutError:
                emb = disnake.Embed(
                    title='Смена Названия Комнаты и Роли',
                    description=f'{author.mention}, время **вышло**!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=author.avatar.url)
                await msg.edit(embed=emb, components=[], delete_after=45)
        elif inter.component.custom_id == 'l_rooms_10':
            emb = disnake.Embed(
                title='Смена Цвета Роли',
                description=f'{author.mention}, **введите** новый цвет.',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)
            await msg.edit(embed=emb, components=[])
            try:
                res = await self.bot.wait_for("message", check=lambda i: i.author == author, timeout=60)
                await res.delete()
                col = res.content
                colors = col \
                    .replace("#", "")
                role = inter.guild.get_role(num1['role'])
                color = int(f"{colors}", 16)
                await role.edit(colour=disnake.Colour(color))
                emb = disnake.Embed(
                    title='Смена цвета роли',
                    description=f'{author.mention}, цвет роли комнаты <#{channel.id}> был установлен на **{role.color}**',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=author.avatar.url)
                await msg.edit(embed=emb, components=[])
            except asyncio.TimeoutError:
                emb = disnake.Embed(
                    title='Смена цвета роли',
                    description=f'{author.mention}, время **вышло**!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=author.avatar.url)
                await msg.edit(embed=emb, components=[], delete_after=45)
        elif inter.component.custom_id == 'l_rooms_11':
            emb = disnake.Embed(
                title='Отображение комнаты',
                description=f'{author.mention}, вы **отобрали** комнату для всего сервера.',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)
            await msg.edit(embed=emb, components=[])
            everyone = inter.guild.get_role(inter.guild.id)
            await channel.set_permissions(everyone, view_channel=True)
        elif inter.component.custom_id == 'l_rooms_12':
            emb = disnake.Embed(
                title='Скрытие комнаты',
                description=f'{author.mention}, вы **скрыли** комнату от всего сервера.',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=author.avatar.url)

            await msg.edit(embed=emb, components=[])
            everyone = inter.guild.get_role(inter.guild.id)
            await channel.set_permissions(everyone, view_channel=False)

class L_room(commands.Cog, name="l_room"):
    def __init__(self, bot):
        self.bot: disnake.Client = bot

        self.cluster = self.bot.cluster
        self.l_room:  pymongo.collection.Collection = self.cluster.infinity.L_rooms
        self.g_count:  pymongo.collection.Collection = self.cluster.infinity.guilds

    @commands.slash_command(
        dm_permission=False,
        guild_ids=test_guild
    )
    async def lroom(self, ctx):
        pass

    @lroom.sub_command(
        name='edit',
        description=f'Удалить/Продлить личную комнату пользователю',
        options=[
            disnake.Option(
                name='channel',
                description='Укажите канал',
                required=True,
                type=disnake.OptionType.channel
            ),
            disnake.Option(
                name='status',
                description='Выберите что хотите сделать. Продлить/Удалить?',
                required=True,
                type=disnake.OptionType.integer,
                choices=[
                    disnake.OptionChoice(
                        name='Продлить',
                        value=1
                    ),
                    disnake.OptionChoice(
                        name='Удалить',
                        value=2
                    ),
                ]
            )
        ],
        guild_ids=test_guild
    )
    async def lroom_edit(self, ctx: disnake.ApplicationCommandInteraction, channel, status):
        finds = self.l_room.find_one({"channel": channel.id})
        if finds:
            if status == 1:
                emb = disnake.Embed(
                    title='Продление комнаты',
                    description=f'{ctx.author.mention}, вы **продлили** личную комнату <#{channel.id}> на месяц!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.send(embed=emb)
                self.l_room.update_one({"channel": channel.id}, {"$inc": {"time_end": 2592000}})
            elif status == 2:
                role = ctx.guild.get_role(finds['role'])
                emb = disnake.Embed(
                    title='Удаление Комнаты',
                    description=f'{ctx.author.mention}, вы **удалили** личную комнату <#{channel.id}> и её роль {role.mention}',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.send(embed=emb)
                await role.delete()
                await channel.delete()
                self.l_room.delete_one(finds)
        else:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, данная комната **не является личной**!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=emb)

    @lroom.sub_command(
        name='create',
        description=f'Создать личную комнату пользователю',
        options=[
            disnake.Option(
                name='member',
                description='Укажите пользователя',
                required=True,
                type=disnake.OptionType.user
            ),
            disnake.Option(
                name='name',
                description=f'Укажите название роли',
                required=True,
                type=disnake.OptionType.string
            ),
            disnake.Option(
                name='color',
                description=f'Укажите цвет роли',
                required=True,
                type=disnake.OptionType.string
            )
        ],
        guild_ids=test_guild

    )
    async def create_lroom(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, name, color):
        okey = list(self.l_room.find({"manage_id": ctx.author.id, "guild_id": ctx.guild.id}))
        if len(okey) < 10:
            finds = self.g_count.find_one({"_id": ctx.guild.id})
            category = disnake.utils.get(
                member.guild.categories, id=1090355578779484322)
            channel2 = await ctx.guild.create_voice_channel(name=f'· {name}', category=category,
                                                            reason='Личные Комнаты')
            color = color \
                .replace("#", "")
            try:
                color = int(f"{color}", 16)
            except ValueError:
                await ctx.send(f'Это не правильный цвет!', ephemeral=True)
            role = await ctx.guild.create_role(name=name, colour=disnake.Colour(color))
            emb = disnake.Embed(
                title='Создание личной комнаты',
                description=f'{ctx.author.mention}, вы **создали** личную комнату <#{channel2.id}> с ролью {role.mention} для пользователя {member.mention}',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=emb)
            await member.add_roles(role)
            everyone = ctx.guild.get_role(ctx.guild.id)
            await channel2.set_permissions(role, connect=True, view_channel=True, speak=True)
            await channel2.set_permissions(everyone, connect=False, view_channel=False)
            post = {
                "owner_id": member.id,
                "manage_id": member.id,
                "prava": 2,
                "channel": channel2.id,
                "role": role.id,
                "time_create": int(time.time()),
                "time_end": int(time.time()) + 2592000,
                "room_name": name,
                "counte": len(okey) + 1,
                "guild_id": ctx.guild.id,
                "voice": 0
            }
            self.l_room.insert_one(post)
            emb = disnake.Embed(
                title='Личная Комната',
                description=f'{member.mention}, администратор {ctx.author.mention} создал для вас личную комнату `{channel2}` с ролью `{role}`',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=member.avatar.url)
            await member.send(embed=emb)
        else:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, пользователь **достиг лимита** в **10** комнат.'
            )
            emb.set_footer(
                text='Пояснение: Можно быть Владельцем/СоВладельцем только в 10 личных комнатах')
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=emb, ephemeral=True)

    @commands.slash_command(
        dm_permission=False,
        guild_ids=test_guild
    )
    async def room(self, ctx):
        pass

    @room.sub_command(
        name='manage',
        description=f'Управление личной комнатой',
    )
    async def room_manage(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        finds = list(self.l_room.find({"manage_id": ctx.author.id, "guild_id": ctx.guild.id}))
        if not finds:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, у вас **нет** личных комнат!'
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.edit_original_message(embed=emb)
        else:
            emb2 = disnake.Embed(
                title='Меню Личных комнат',
                description=f'{ctx.author.mention}, **выберите** комнату, с которой хотите взаимодействовать, ниже!',
                color=0x2b2d31
            )
            emb2.set_thumbnail(url=ctx.author.avatar.url)
            optioons = []
            names = []
            for index, r in enumerate(finds):
                if r['prava'] == 2:
                    own = 'Владелец'
                else:
                    own = 'Участник'
                channel: disnake.VoiceChannel = self.bot.get_channel(r['channel'])
                if not channel:
                    self.l_room.delete_one(r)
                    continue
                names.append({"name": r['room_name']})
                optioons.append(disnake.SelectOption(
                    label=f'{channel.name}', value=f"select_l_room_{r['counte']}",
                    description=f"Вы: {own} данной комнаты"))
            row = Drop_Room(opt=optioons, msg=ctx, user=ctx.author, names=names, db=self.l_room, bot=self.bot)
            await ctx.edit_original_message(embed=emb2, view=row)


def setup(bot):
    bot.add_cog(L_room(bot))
    print('Ког: "Личные Комнаты" загрузился!')
