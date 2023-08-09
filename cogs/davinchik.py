import pymongo
import time
from disnake.ext import commands, tasks
from config import *
import disnake

test_guild = [1084577336340512889]


test_channel = 1091016748968456302

class Love_poisk(commands.Cog, name="loves_poisk"):
    def __init__(self, bot):
        self.bot: disnake.Client = bot

        self.cluster = self.bot.cluster
        self.davinchik_db: pymongo.collection.Collection = self.cluster.infinity.davinchik

        self.embed_search: disnake.Embed = disnake.Embed(
            title='Знакомства',
            description=f'Составляя анкету, вы **соглашаетесь** и **обязуетесь** соблюдать следующие пункты:\n'
                        f' Вы достигли совершеннолетия.\n'
                        f' Вы не указали в анкете желаемый возраст человека.\n'
                        f' Строго запрещена мошенническая деятельность, в любых ее проявлениях.\n\n'
                        f'> ***Помните**, мы **не** обязуем вас указывать ваш настоящий возраст, но заявки от пользователей **не** достигших совершеннолетия будут отклонены, а доступ к чату **закрыт**. За более подробной информацией обращайтесь к пользователю в личные сообщения.*\n',
            color=0x2b2d31
        )
        self.embed_search.set_thumbnail(url="")
        self.row_search_buttons: disnake.ui.ActionRow = disnake.ui.ActionRow()
        self.row_search_buttons.add_button(label='Начать общение', emoji='💘', style=disnake.ButtonStyle.blurple, custom_id=f'start_search_love')
        self.row_search_buttons.add_button(label='Моя анкета', emoji='📝', style=disnake.ButtonStyle.blurple,
                                           custom_id=f'my_search_place')

    def return_ava(self, member: disnake.Member):
        if member.display_avatar:
            ava = member.display_avatar.url
        elif member.avatar:
            ava = member.avatar.url
        else:
            ava = member.default_avatar.url
        return ava

    async def send_search(self, member: disnake.Member, name: str, age: str, info: str, inter):
        channel = self.bot.get_channel(test_channel)
        await channel.purge(limit=1, check=lambda i: i.author == self.bot.user)
        emb_to_send: disnake.Embed = disnake.Embed(
            title=f'Анкета — {member}',
            color=0x2b2d31
        )
        emb_to_send.set_thumbnail(url=self.return_ava(member))
        emb_to_send.add_field(name='> Имя', value=f'```fix\n{name}```', inline=True)
        emb_to_send.add_field(name='> Возраст', value=f'```fix\n{age}```', inline=True)
        emb_to_send.add_field(name='> О себе', value=f'```{info}```', inline=False)
        row: disnake.ui.ActionRow = disnake.ui.ActionRow()
        row.add_button(label=' ・ Написать', emoji=f'✏️', style=disnake.ButtonStyle.blurple,
                       custom_id='send_to_user_in_davinchik')
        msg = await channel.send(embed=emb_to_send, components=[row])
        await channel.send(embed=self.embed_search, components=[self.row_search_buttons])
        self.davinchik_db.update_one({"member_id": member.id, "guild_id": inter.guild.id}, {
            "$set": {"name": name, "age": age, "info": info, "next_time": int(time.time()) + (60 * 60 * 12),
                     "msg_id": msg.id}}, True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def start_love_search_embed_send(self, ctx: disnake.MessageInteraction): #КОМАНДА
        await ctx.message.delete()
        await ctx.send(embed=self.embed_search, components=[self.row_search_buttons])

    @commands.Cog.listener("on_modal_submit")
    async def modal_listener(self, inter: disnake.ModalInteraction):
        member: disnake.Member = inter.author
        match inter.custom_id:
            case "search_loves_modal":
                for custom_id, value in inter.text_values.items():
                    match custom_id:
                        case "age":
                            age = value
                        case 'name':
                            name = value
                        case 'info':
                            info = value
                        case _:
                            return
                find = self.davinchik_db.find_one({"member_id": member.id, "guild_id": inter.guild.id})
                if find:
                    self.davinchik_db.delete_one(find)
                    channel_davinchik = self.bot.get_channel(test_channel)
                    if channel_davinchik:
                        try:
                            msg = await channel_davinchik.fetch_message(find['msg_id'])
                            if msg:
                                await msg.delete()
                        except(disnake.Forbidden, disnake.HTTPException, disnake.NotFound):
                            pass
                await self.send_search(member=member, name=name, age=age, info=info, inter=inter)
                emb = disnake.Embed(
                    title='Отправка анкеты',
                    description=f'{member.mention}, ваша анкета была успешно **отправлена**!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=self.return_ava(member))
                await inter.send(embed=emb, ephemeral=True)
            case "search_loves_modal_edit":
                emb = disnake.Embed(
                    title='Изменение Анкеты',
                    description=f'{member.mention}, вы **изменили** свою анкету! Правки вступят в силу со **следующей** отправкой!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=self.return_ava(member))
                await inter.response.edit_message(embed=emb, components=[])
                for custom_id, value in inter.text_values.items():
                    match custom_id:
                        case "age":
                            age = value
                        case 'name':
                            name = value
                        case 'info':
                            info = value
                        case _:
                            return
                self.davinchik_db.update_one({"member_id": member.id, "guild_id": inter.guild.id}, {"$set": {"name": name, "age": age, "info": info}}, True)


    @commands.Cog.listener("on_button_click")
    async def buttons_loves_search(self, inter: disnake.MessageInteraction):
        author: disnake.Member = inter.author
        match inter.component.custom_id:
            case "start_search_love":
                find = self.davinchik_db.find_one({"member_id": author.id, "guild_id": inter.guild.id})
                if find and find['next_time'] >= int(time.time()):
                    times = int((find['next_time'] - int(time.time())) / 60)
                    minutes = times % 60
                    hours = times // 60
                    emb = disnake.Embed(
                        title='Ошибка',
                        description=f'{author.mention}, вы **недавно** отправляли анкету. Повторите попытку через: **{hours} часов, {minutes} минут**',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=self.return_ava(author))
                    await inter.send(embed=emb, ephemeral=True)
                    return
                await inter.response.send_modal(
                    title=f"Знакомства",
                    custom_id=f"search_loves_modal",
                    components=[
                        disnake.ui.TextInput(
                            label="Укажите свой возраст",
                            placeholder=f"Минимальный возраст для подачи анкеты - 18 лет",
                            custom_id="age",
                            style=disnake.TextInputStyle.short,
                            min_length=2,
                            max_length=3,
                            value=f'18'
                        ),
                        disnake.ui.TextInput(
                            label="Укажите имя",
                            placeholder=f"Указывайте исключительно правдивые имена",
                            custom_id="name",
                            style=disnake.TextInputStyle.short,
                            min_length=1,
                            max_length=15,
                        ),
                        disnake.ui.TextInput(
                            label="Расскажите о себе",
                            placeholder=f"Любая информация о вас, не нарушающая правила сервера",
                            custom_id="info",
                            style=disnake.TextInputStyle.paragraph,
                            min_length=10,
                            max_length=350,
                        )
                    ],
                )
            case "my_search_place":
                find = self.davinchik_db.find_one({"member_id": author.id, "guild_id": inter.guild.id})
                if not find:
                    emb = disnake.Embed(
                        title='Ошибка',
                        description=f'{author.mention}, у вас **отсутствует** анкета!',
                        color=0x2b2d31
                    )
                    await inter.send(embed=emb, ephemeral=True)
                    return
                emb = disnake.Embed(
                    title='Ваша активная анкета',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=self.return_ava(author))
                emb.add_field(name='> Имя', value=f'```fix\n{find["name"]}```', inline=True)
                emb.add_field(name='> Возраст', value=f'```fix\n{find["age"]}```', inline=True)
                emb.add_field(name='> О себе', value=f'```{find["info"]}```', inline=False)
                row: disnake.ui.ActionRow = disnake.ui.ActionRow()
                row.add_button(label='Отправить снова', style=disnake.ButtonStyle.blurple,
                               custom_id='send_search_around')
                row.add_button(label='Редактировать анкету', style=disnake.ButtonStyle.blurple,
                               custom_id='edit_search_davinchik')
                row1: disnake.ui.ActionRow = disnake.ui.ActionRow()
                row1.add_button(label='Удалить анкету', style=disnake.ButtonStyle.red,
                               custom_id='delete_search_davinchik')
                await inter.send(embed=emb, ephemeral=True, components=[row, row1])
            case "edit_search_davinchik":
                find = self.davinchik_db.find_one({"member_id": author.id, "guild_id": inter.guild.id})
                await inter.response.send_modal(
                        title=f"Знакомства",
                    custom_id=f"search_loves_modal_edit",
                    components=[
                        disnake.ui.TextInput(
                            label="Укажите свой возраст",
                            placeholder=f"Минимальный возраст для подачи анкеты - 18 лет",
                            custom_id="age",
                            style=disnake.TextInputStyle.short,
                            min_length=2,
                            max_length=3,
                            value=f'{find["age"]}'
                        ),
                        disnake.ui.TextInput(
                            label="Укажите имя/возраст",
                            placeholder=f"Указывайте исключително правдивые имена",
                            custom_id="name",
                            style=disnake.TextInputStyle.short,
                            min_length=1,
                            max_length=15,
                            value=f'{find["name"]}'
                        ),
                        disnake.ui.TextInput(
                            label="Расскажите о себе",
                            placeholder=f"Любая информация о вас, не нарушающая правила сервера",
                            custom_id="info",
                            style=disnake.TextInputStyle.paragraph,
                            min_length=10,
                            max_length=350,
                            value=f'{find["info"]}'
                        )
                    ],
                )

            case "delete_search_davinchik":
                emb = disnake.Embed(
                    title='Удаление Анкеты',
                    description=f'{author.mention}, вы **удалили** свою анкету!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=self.return_ava(author))
                await inter.response.edit_message(embed=emb, components=[])
                find = self.davinchik_db.find_one({"member_id": author.id, "guild_id": inter.guild.id})
                if find:
                    self.davinchik_db.delete_one(find)
                    channel_davinchik = self.bot.get_channel(test_channel)
                    if channel_davinchik:
                        try:
                            msg = await channel_davinchik.fetch_message(find['msg_id'])
                        except (disnake.NotFound, disnake.Forbidden, disnake.HTTPException):
                            return
                        if msg:
                            await msg.delete()
            case "send_search_around":
                find = self.davinchik_db.find_one({"member_id": author.id, "guild_id": inter.guild.id})
                if find['next_time'] >= int(time.time()):
                    times = int((find['next_time'] - int(time.time())) / 60)
                    minutes = times % 60
                    hours = times // 60
                    emb = disnake.Embed(
                        description=f'{author.mention}, вы **недавно** отправляли анкету. Повторите попытку через: **{hours} ч, {minutes} м**',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=self.return_ava(author))
                    await inter.response.edit_message(embed=emb, components=[])
                    return
                emb = disnake.Embed(
                    title='Отправка Анкеты',
                    description=f'{author.mention}, вы **снова** отправили свою анкету!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=self.return_ava(author))
                await inter.response.edit_message(embed=emb, components=[])
                self.davinchik_db.delete_one(find)
                channel_davinchik = self.bot.get_channel(test_channel)
                if channel_davinchik:
                    msg = await channel_davinchik.fetch_message(find['msg_id'])
                    if msg:
                        await msg.delete()
                self.davinchik_db.update_one(find, {"$inc": {"next_time": 60*60*12}}, True)
                await self.send_search(member=author, name=find['name'], age=find['age'], info=find['info'], inter=inter)
            case "send_to_user_in_davinchik":
                find = self.davinchik_db.find_one({"msg_id": inter.message.id})
                if find:
                    user_id = find['member_id']
                    member: disnake.Member = inter.guild.get_member(user_id)
                    if member:
                        user = f'{member.mention}'
                    else:
                        user = f'<@{user_id}>'
                    emb = disnake.Embed(
                        description=f'**Неужели это начало интернет любви?**\nНапишите {user} в личные сообщения,\nили же нажмите на кнопку ниже.',
                        color=0x2b2d31
                    )
                    row_link: disnake.ui.ActionRow = disnake.ui.ActionRow()
                    row_link.add_button(label='Отправить сообщение', url=f"https://discord.com/users/{user_id}", style=disnake.ButtonStyle.url)
                    await inter.send(embed=emb, ephemeral=True, components=[row_link])



def setup(bot):
    bot.add_cog(Love_poisk(bot))
    print('Ког: "Дайвинчик" загрузился!')
