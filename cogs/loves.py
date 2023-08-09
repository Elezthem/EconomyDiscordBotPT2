import disnake
import pymongo
from disnake.ext import commands
from pymongo import MongoClient
from config import *
import time
import os
from time import sleep
import requests
from PIL import Image, ImageFont, ImageDraw
import io
from delorean import Delorean
import asyncio
from disnake import ButtonStyle

test_guild = [1084577336340512889]
emoji_money_id = 1091827829500555286


class Loves(commands.Cog, name="loves"):
    def __init__(self, bot):
        self.bot = bot

        self.cluster = self.bot.cluster
        self.lovess: pymongo.collection.Collection = self.cluster.infinity.loves
        self.profile: pymongo.collection.Collection = self.cluster.infinity.profile
        self.g_count: pymongo.collection.Collection = self.cluster.infinity.guilds

    async def member(self, member1, guild: disnake.Guild):
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

    def return_partner(self, turple, author: disnake.Member):
        for key in turple.keys():
            if turple[key] == author.id:
                if key == 'man':
                    return "girl"
                elif key == 'girl':
                    return 'man'
                else:
                    return None

    def return_avatar(self, member: disnake.Member):
        if member.display_avatar:
            return member.display_avatar.url
        elif member.avatar:
            return member.avatar.url
        else:
            return member.default_avatar.url

    @commands.slash_command(
        name='lprofile',
        description=f'Любовный профиль',
        guild_ids=test_guild
    )

    async def lprofile(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        lprofiles = self.lovess.find_one({"$or": [{"man": ctx.author.id}, {"girl": ctx.author.id}]})
        if lprofiles:
            balls = lprofiles['balance']
            data = int((lprofiles['time_end']-int(time.time()))//60)
            man_id = lprofiles[self.return_partner(lprofiles, ctx.author)]
            member: disnake.Member = ctx.guild.get_member(man_id)
            brak_online = lprofiles['voice']
            # ================
            avatar_url = self.return_avatar(ctx.author)
            if str(avatar_url)[-4:] == '.png':
                url1 = requests.get(avatar_url, stream=True)
            else:
                url1 = requests.get(str(avatar_url)[
                                    :-10], stream=True)
            # ===========
            avatar_url1 = self.return_avatar(member)
            if str(avatar_url1)[-4:] == '.png':
                url2 = requests.get(avatar_url1, stream=True)
            else:
                url2 = requests.get(str(avatar_url1)[:-10], stream=True)
            # ======
            avatar = Image.open(io.BytesIO(url1.content))
            avatar = avatar.resize((375, 375), Image.ANTIALIAS)
            # =====
            avatar2 = Image.open(io.BytesIO(url2.content))
            avatar2 = avatar2.resize((375, 375), Image.ANTIALIAS)
            # ======
            mask = Image.new("L", avatar.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 375, 375), fill=255)
            # ======
            mask2 = Image.new("L", avatar2.size, 0)
            draw_mask2 = ImageDraw.Draw(mask2)
            draw_mask2.ellipse((0, 0, 375, 375), fill=255)
            # =====
            user_card = Image.open('src/fonlove/fon.png')
            user_card = user_card.resize((1572, 1392), Image.ANTIALIAS)
            user_card.paste(avatar, (202, 348), mask)
            user_card.paste(avatar2, (1005, 348), mask2)
            # =====
            idraw = ImageDraw.Draw(user_card)
            font = ImageFont.truetype("src/font/Roboto-Black.ttf", size=65)
            font_b = ImageFont.truetype("src/font/Roboto-Black.ttf", size=75)
            if balls < 10:
                idraw.text((760, 630), str(balls),
                        (255, 255, 255), font=font_b)  # баланс
            if balls >= 10 and balls < 100:
                idraw.text((740, 630), str(balls),
                        (255, 255, 255), font=font_b)  # баланс
            if balls >= 100 and balls < 1000:
                idraw.text((720, 630), str(balls),
                        (255, 255, 255), font=font_b)  # баланс
            if balls >= 1000 and balls < 10000:
                idraw.text((700, 630), str(balls),
                        (255, 255, 255), font=font_b)  # баланс
            if balls >= 10000:
                idraw.text((680, 630), str(balls),
                        (255, 255, 255), font=font_b)  # баланс
            minutes = int(brak_online % 60)
            hour = int(brak_online // 60)
            if hour < 1:
                hour = 0
            if minutes < 1 or minutes >= 60:
                minutes = 0
            brack_online = f"{hour}ч. {minutes}м."
            # ==========================================================================
            idraw.text((690, 440), str(brack_online),
                       (255, 255, 255), font=font)  # онлайн
            # ============================================================================
            user_card.save('src/templove/fon_gotovo.png', quality=95)
            file = disnake.File("src/templove/fon_gotovo.png", filename="src/templove/fon_gotovo.png")
            row = disnake.ui.ActionRow()
            row.add_button(style=disnake.ButtonStyle.grey,
                label='Пополнить баланс', custom_id='lbalance')
            row.add_button(style=disnake.ButtonStyle.grey,
                label='Развод', custom_id='divorce')
            msg = await ctx.edit_original_message(file=file, components = [row])
            try:
                inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=60, check=lambda i: i.author.id == ctx.author.id and i.message.id == msg.id)
            except asyncio.TimeoutError:
                await ctx.edit_original_message(components=[])
                return
            if inter.component.custom_id == 'lbalance':
                emoji_money_id = 1091827829500555286
                emoji_money = self.bot.get_emoji(emoji_money_id)
                embed = disnake.Embed(
                    title = "Пополнение баланса",
                    description = f"```Списание произойдёт через {data//60//24}д, {data//60//60}ч, {data%60}м```",
                    color=0x2b2d31
                )
                embed.set_thumbnail(url=ctx.author.avatar.url)
                await inter.response.send_modal(
                    title=f"Пополнение баланса",
                    custom_id=f"balance",
                    components=[
                        disnake.ui.TextInput(
                            label="Введите сумму",
                            placeholder=f"Введите текст",
                            custom_id="lbalance",
                            style=disnake.TextInputStyle.short,
                            min_length=1,
                            max_length=5,
                        ),
                    ],
                )
                try:
                    modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                        "modal_submit",
                        check=lambda i: i.custom_id == f"balance" and i.author.id == inter.author.id,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return
                for custom_id, value in modal_inter.text_values.items():
                    if custom_id == "lbalance":
                        number = int(value)
                    else:
                        return

                ball = self.profile.find_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id})
                ball = ball['balance']
                emoji = self.bot.get_emoji(emoji_money_id)
                if number <= 0:
                    emb = disnake.Embed(
                        title='Ошибка',
                        description=f'{ctx.author.mention}, сумма пополнения баланса пары **не может** быть **меньше** или __0__ {emoji} !',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    await modal_inter.send(embed=emb)
                elif ball - number < 0:
                    emb = disnake.Embed(
                        title='Ошибка',
                        description=f'{ctx.author.mention}, сумма пополнения баланса пары **не может** быть **больше** вашего баланса!',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    await modal_inter.send(embed=emb)
                else:
                    self.lovess.update_one(lprofiles, {"$inc": {"balance": number}})
                    self.profile.update_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id}, {"$inc": {"balance": -number}}, True)

                    embed1 = disnake.Embed(
                        title = "Успешное пополнение",
                        description = f"Вы успешно пополнили баланс пары на **{number}** {emoji_money}!",
                        color=0x2b2d31
                    )
                    embed1.set_thumbnail(url = ctx.author.avatar.url)
                    await modal_inter.send(embed = embed1)
                    await inter.edit_original_message(embed=embed, components = [row])
                
            elif inter.component.custom_id == 'divorce':
                partner = lprofiles[self.return_partner(lprofiles, ctx.author)]
                '''emb = disnake.Embed(
                    title='Подтверждение',
                    description=f'{ctx.author.mention}, вы **уверены** что хотите **развестить** с <@{partner}>?'
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                row = disnake.ui.ActionRow()
                row.add_button(style=ButtonStyle.green,
                                label='Да', emoji='✔', custom_id='divorce_accept_yes')
                row.add_button(style=ButtonStyle.red, label='Нет',
                                emoji='❌', custom_id='divorce_accept_no')
                msg = await ctx.edit_original_message(embed=emb, components=[row])
                try:
                    inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=60, check=lambda i: i.author.id == ctx.author.id and i.message.id == msg.id)
                except asyncio.TimeoutError:
                    await ctx.edit_original_message(components=[])
                    return
                if inter.component.custom_id == 'divorce_accept_yes':'''
                love_role = ctx.guild.get_role(1084577336340512896)
                channel = self.bot.get_channel(lprofiles['channel_id'])
                member = ctx.guild.get_member(partner)
                if channel:
                    await channel.delete()
                if love_role:
                    await ctx.author.remove_roles(love_role)
                if member and love_role:
                    await member.remove_roles(love_role)
                self.lovess.delete_one(lprofiles)
                # ====
                emb = disnake.Embed(
                    title='Развод',
                    description=f'{ctx.author.mention}, вы **успешно** развелись с {member.mention}!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=member.avatar.url)
                await inter.response.edit_message(embed=emb, components=[])
                emb = disnake.Embed(
                    title='Развод',
                    description=f'{member.mention}, {ctx.author.mention} развёлся с вами!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await member.send(embed=emb, components=[])
                '''elif inter.response.custom_id == 'divorce_accept_no':
                    emb = disnake.Embed(
                        title='Отмена Действия',
                        description=f'{ctx.author.mention}, вы **отменили** ваш развод с <@{partner}>'
                    )
                    emb.set_thumbnail(url=ctx.author.avatar.url)
                    await inter.response.edit_message(embed=emb, components=[])'''
            else:
                emb = disnake.Embed(
                    title='Ошибка',
                    description=f'{ctx.author.mention}, у вас **отсутствует** брак!'
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.edit_original_message(embed=emb)

        else:
            emoji_money_id = 1091827829500555286
            emoji_money = self.bot.get_emoji(emoji_money_id)
            emb = disnake.Embed(
                title='Любовный профиль',
                description=f'{ctx.author.mention}, у вас **отсутсвует** пара! Для её создания используйте команду: `/marry @member`.',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.edit_original_message(embed=emb)





    @commands.slash_command(
        name='marry',
        description=f'Предложить пользователю заключить брак',
        options=[
            disnake.Option(
                name='member',
                description='Укажите пользователя для брака',
                required=True,
                type=disnake.OptionType.user
            )
        ],
        guild_ids=test_guild
    )
    async def marry(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member):
        await ctx.response.defer()
        if member.id == ctx.author.id:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, вы **не можете** создать брак **сами с собой**!'
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.edit_original_message(embed=emb)
            return
        lprofiles = self.lovess.find_one({"$or": [{"man": ctx.author.id}, {"girl": member.id}]})
        if lprofiles:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, вы **не можете** создать брак, т.к. вы **уже состоите** в браке!'
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.edit_original_message(embed=emb)
            return
        lprofile1 = self.lovess.find_one({"$or": [{"man": member.id}, {"girl": member.id}]})
        if lprofile1:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, вы **не можете** создать брак, т.к. пользователь **уже состоит** в браке!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.edit_original_message(embed=emb)
            return
        emoji = self.bot.get_emoji(emoji_money_id)
        balance = self.profile.find_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id})
        balance = balance['balance']
        if balance < 1500:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, у вас **недостаточно** средств для создания брака! Стоимость создания `1500` {emoji}',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.edit_original_message(embed=emb)
            return
        row = disnake.ui.ActionRow()
        row.add_button(style=disnake.ButtonStyle.green,
                          label='Да', emoji='✔', custom_id='marry_yes')
        row.add_button(style=disnake.ButtonStyle.red,
                          label='Нет', emoji='❌', custom_id='marry_no')
        emb = disnake.Embed(
            title='Создание Брака',
            description=f'{ctx.author.mention}, вы **уверены** что хотите создать брак с {member.mention}?',
            color=0x2b2d31
        )
        emb.set_thumbnail(url=ctx.author.avatar.url)
        emb.set_footer(
            text='Стоимость создания брака 1500 коинов!')

        msg = await ctx.edit_original_message(embed=emb, components=[row])
        try:
            inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=60, check=lambda i: i.author.id == ctx.author.id and i.message.id == msg.id)
        except asyncio.TimeoutError:
            await ctx.edit_original_message(components=[])
            return
        if inter.component.custom_id == 'marry_yes':
            emb = disnake.Embed(
                title=f'Создание брака',
                description=f'{ctx.author.mention}, ваше __предложение__ о создании брака была отправлена пользователю {member.mention}!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            emb.set_footer(
                text=f'Если у пользователя закрыто лс, вы получите извещение об этом в лс.')
            await inter.response.edit_message(embed=emb, components=[])
            # =======
            emb = disnake.Embed(
                title='Предложение брака',
                description=f'{member.mention}, пользователь {ctx.author.mention} отправил **вам** предложение о **браке**. Для принятия/отказа используйте кнопки ниже!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=member.avatar.url)
            emb.set_footer(text='Для ответа у вас есть **360** секунд!', icon_url=ctx.guild.icon.url)
            row = disnake.ui.ActionRow()
            row.add_button(style=ButtonStyle.green,
                              label='Принять', emoji='✔', custom_id='marry_accept_yes')
            row.add_button(style=ButtonStyle.red,
                              label='Отказать', emoji='❌', custom_id='marry_accept_deny')
            try:
                msg_mem = await member.send(embed=emb, components=[row])
            except (disnake.Forbidden, disnake.HTTPException):
                try:
                    await ctx.author.send(f'**Не удалось** отправить ваше предложение о браке пользователю {member.mention} в лс! Возможно у него оно закрыто!')
                except (disnake.Forbidden, disnake.HTTPException):
                    return
            # =====
            try:
                inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=360, check=lambda i: i.author.id == member.id and i.message.id == msg_mem.id)
            except asyncio.TimeoutError:
                await ctx.edit_original_message(components=[])
                return
            if inter.component.custom_id == 'marry_accept_yes':
                love_role = ctx.guild.get_role(1084577336340512896)
                self.profile.update_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id}, {"$set": {"balance": balance - 1500}})
                await member.add_roles(love_role)
                await ctx.author.add_roles(love_role)
                # ======
                emb = disnake.Embed(
                    title='Брак',
                    description=f'{member.mention}, вы **создали** брак с пользователем {ctx.author.mention}!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=member.avatar.url)
                await inter.response.edit_message(embed=emb, components=[])
                # =====
                emb = disnake.Embed(
                    title='Брак',
                    description=f'{ctx.author.mention}, вы **создали** брак с пользователем {member.mention}!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.author.send(embed=emb)
                # =====
                # =====
                post = {
                    "man": ctx.author.id,
                    "girl": member.id,
                    "guild_id": ctx.guild.id,
                    "time_end": int(time.time()) + 2591500,
                    "balance": 0,
                    "channel_id": 0,
                    "voice": 0,
                    "love_role": love_role.id
                }
                self.lovess.insert_one(post)
            elif inter.component.custom_id == 'marry_accept_deny':
                emb = disnake.Embed(
                    title='Отказ брака',
                    description=f'{member.mention}, вы **отказались** от брака с пользователем {ctx.author.mention}!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=member.avatar.url)
                await inter.response.edit_message(embed=emb, components=[])
                # ====
                emb = disnake.Embed(
                    title='Отказ брака',
                    description=f'{ctx.author.mention}, пользователь {member.mention} **отказал** вам в браке!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=member.avatar.url)
                await ctx.author.send(embed=emb)
        elif inter.component.custom_id == 'marry_no':
            emb = disnake.Embed(
                title='Создание брака',
                description=f'{ctx.author.mention}, вы **отменили** __создание__ брака с пользователем {member.mention}!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await inter.response.edit_message(embed=emb, components=[])

    '''@commands.slash_command(
        name='ldeposit',
        description=f'Пополнить баланс пары',
        options=[
            disnake.Option(
                name='number',
                description="Укажите сумму пополнения баланса пары",
                type=disnake.OptionType.integer,
                required=True
            )
        ],
        dm_permission=False
    )
    async def ldeposit_command(self, ctx: disnake.ApplicationCommandInteraction, number: int):
        lprofiles = self.lovess.find_one({"$or": [{"man": ctx.author.id}, {"girl": ctx.author.id}]})
        if lprofiles:
            ball = self.profile.find_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id})
            ball = ball['balance']
            emoji = self.bot.get_emoji(emoji_money_id)
            if number <= 0:
                emb = disnake.Embed(
                    title='Ошибка',
                    description=f'{ctx.author.mention}, сумма пополнения баланса пары **не может** быть **меньше** или __0__ {emoji} !'
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.send(embed=emb)
            elif ball - number < 0:
                emb = disnake.Embed(
                    title='Ошибка',
                    description=f'{ctx.author.mention}, сумма пополнения баланса пары **не может** быть **больше** вашего баланса!'
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.send(embed=emb)
            else:
                emb = disnake.Embed(
                    title='Пополнение Баланса Пары',
                    description=f'{ctx.author.mention}, вы **пополнили** баланс пары на `{number}` {emoji}!'
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.send(embed=emb, components=[])
                self.lovess.update_one(lprofiles, {"$inc": {"balance": number}})
                self.profile.update_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id}, {"$inc": {"balance": -number}}, True)
        else:
            emb = disnake.Embed(
                title=f'Ошибка',
                description=f'{ctx.author.mention}, у вас **отсутствует** брак!'
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=emb)'''

    @commands.slash_command(
        name='divorce',
        description=f'Развестись с пользователем',
        dm_permission=False
    )
    async def divorce(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        lprofiles = self.lovess.find_one({"$or": [{"man": ctx.author.id}, {"girl": ctx.author.id}]})
        if lprofiles:
            partner = lprofiles[self.return_partner(lprofiles, ctx.author)]
            emb = disnake.Embed(
                title='Подтверждение',
                description=f'{ctx.author.mention}, вы **уверены** что хотите **развестить** с <@{partner}>?',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            row = disnake.ui.ActionRow()
            row.add_button(style=ButtonStyle.green,
                              label='Да', emoji='✔', custom_id='divorce_accept_yes')
            row.add_button(style=ButtonStyle.red, label='Нет',
                              emoji='❌', custom_id='divorce_accept_no')
            msg = await ctx.edit_original_message(embed=emb, components=[row])
            try:
                inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=60, check=lambda i: i.author.id == ctx.author.id and i.message.id == msg.id)
            except asyncio.TimeoutError:
                await ctx.edit_original_message(components=[])
                return
            if inter.component.custom_id == 'divorce_accept_yes':
                love_role = ctx.guild.get_role(1084577336340512896)
                channel = self.bot.get_channel(lprofiles['channel_id'])
                member = ctx.guild.get_member(partner)
                if channel:
                    await channel.delete()
                if love_role:
                    await ctx.author.remove_roles(love_role)
                if member and love_role:
                    await member.remove_roles(love_role)
                self.lovess.delete_one(lprofiles)
                # ====
                emb = disnake.Embed(
                    title='Развод',
                    description=f'{ctx.author.mention}, вы **успешно** развелись с {member.mention}!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=member.avatar.url)
                await inter.response.edit_message(embed=emb, components=[])
                emb = disnake.Embed(
                    title='Развод',
                    description=f'{member.mention}, {ctx.author.mention} развёлся с вами!',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await member.send(embed=emb, components=[])
            elif inter.response.custom_id == 'divorce_accept_no':
                emb = disnake.Embed(
                    title='Отмена Действия',
                    description=f'{ctx.author.mention}, вы **отменили** ваш развод с <@{partner}>',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await inter.response.edit_message(embed=emb, components=[])
        else:
            emb = disnake.Embed(
                title='Ошибка',
                description=f'{ctx.author.mention}, у вас **отсутствует** брак!',
                color=0x2b2d31
            )
            emb.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.edit_original_message(embed=emb)

    async def create_love_voice(self, member: disnake.Member, db, guild: disnake.Guild, membs_id: int):
        category = disnake.utils.get(guild.categories, id=1090999787312136284)
        if category:
            membs: disnake.Member = guild.get_member(membs_id)
            if membs:
                name = f'{member.display_name} 🖤 {membs.display_name}'
            else:
                name = f'{member.display_name} 🖤 {member.display_name}'
            try:
                channel = await guild.create_voice_channel(name=name, category=category, user_limit=2)
            except (disnake.Forbidden, disnake.HTTPException, disnake.InvalidArgument):
                await member.send(f'{member.mention}, не удалось создать канал! Возможно суточный лимит канав у бота, переполнена категория или лимит каналов сервера. Повторите попытку позже!')
                await member.move_to(None)
                return
            await member.move_to(channel)
            self.lovess.update_one(db, {"$set": {"channel_id": channel.id}})
            return
        else:
            await member.send(f'{member.mention}, Проблема с ботом. Обратитесь к Администрации!')
            await member.move_to(None)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel:
            if after.channel.id == 1090291863589748736: #Канал входа в лав рум
                lprofiles = self.lovess.find_one({"$or": [{"man": member.id}, {"girl": member.id}]})
                if lprofiles:
                    chan_id = lprofiles['channel_id']
                    partner_id = lprofiles[self.return_partner(turple=lprofiles, author=member)]
                    if chan_id != 0:
                        channel = self.bot.get_channel(chan_id)
                        if channel:
                            await member.move_to(channel)
                        else:
                            await self.create_love_voice(member=member, db=lprofiles, guild=member.guild, membs_id=partner_id)
                    else:
                        await self.create_love_voice(member=member, db=lprofiles, guild=member.guild, membs_id=partner_id)
                else:
                    await member.move_to(None)
                    emb = disnake.Embed(
                        title='Ошибка',
                        description=f'{member.mention}, У вас **отсутствует** лаврума! **Обратитесь к Администрации!**',
                        color=0x2b2d31
                    )
                    emb.set_thumbnail(url=member.avatar.url)
                    try:
                        await member.send(embed=emb)
                    except (disnake.Forbidden, disnake.HTTPException):
                        return


def setup(bot):
    bot.add_cog(Loves(bot))
    print('Ког: "Лав Система" загрузился!')
