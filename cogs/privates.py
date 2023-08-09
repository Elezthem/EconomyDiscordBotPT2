import asyncio
import time
import disnake
import pymongo.collection
from disnake.ext import commands, tasks
from config import *

test_guild = []


class Privates(commands.Cog, name="privatkis"):
    def __init__(self, bot):
        self.bot: disnake.Client = bot

        self.cluster = self.bot.cluster
        self.privatki: pymongo.collection.Collection = self.cluster.infinity.privatki
        self.member_privatki: pymongo.collection.Collection = self.cluster.infinity.member_privatki

    async def members(self, member1: str, guild: disnake.Guild, inter: disnake.MessageInteraction):
        id_mem = str(member1) \
            .replace("<", "") \
            .replace("@", "") \
            .replace("!", "") \
            .replace(">", "")
        try:
            member = await guild.fetch_member(int(id_mem))
        except disnake.Forbidden:
            await inter.edit_original_message(embed=disnake.Embed(description=f'Не нашёл пользователя!'))
            return
        except disnake.HTTPException:
            await inter.edit_original_message(embed=disnake.Embed(description=f'Ошибка! Повторите попытку!'))
            return
        return member

    async def del_chan(self, channel: disnake.VoiceChannel):
        try:
            await channel.delete(reason='Канал приваток')
        except (disnake.Forbidden, disnake.NotFound, disnake.HTTPException):
            pass
        find = self.privatki.find_one({"_id": channel.id})
        if find:
            self.privatki.delete_one(find)
            return


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        if after.channel and after.channel.id == 1084577338920018076: #вход румы
            maincategory = after.channel.category
            finds = self.member_privatki.find_one({"member_id": member.id, "guild_id": member.guild.id})
            if finds:
                abc = finds['name']
                name = f'— {abc}'
            else:
                name = f'— Канал {member.display_name}'
            channel2 = await member.guild.create_voice_channel(name=name, category=maincategory, reason='Приватные комнаты || Создание')
            try:
                await member.move_to(channel2, reason='Приватные комнаты || Перемещение')
            except disnake.HTTPException:
                await channel2.delete(reason='Защита от краша приваток')
                return
            post = {
                "_id": channel2.id,
                "member_id": member.id
            }
            self.privatki.insert_one(post)
            await channel2.set_permissions(member, connect=True, view_channel=True)
        if before.channel and before.channel.category.id == 1084577338920018074 and len(before.channel.members) < 1 and before.channel.id != 1084577338920018076: #хуй
            await self.del_chan(before.channel)


    @commands.command()
    async def create_privates_systems(self, ctx):
        emoji1 = self.bot.get_emoji(1089640770773983333)  # изменить название
        emoji2 = self.bot.get_emoji(1089640776281116743)  # лимит
        emoji3 = self.bot.get_emoji(1089640765220733100)  # закрыть комнату
        emoji4 = self.bot.get_emoji(1089640772426551397)  # открыть комнату
        emoji5 = self.bot.get_emoji(1089640767103975554)  # забрать доступ
        emoji6 = self.bot.get_emoji(1089640774771146893)  # выдать доступ
        emoji7 = self.bot.get_emoji(1089640780060164277)  # выгнать из комнаты
        emoji8 = self.bot.get_emoji(1089640768609718382)  # забрать право говорить
        emoji9 = self.bot.get_emoji(1089640777661022290)  # выдать право говорить
        emoji10 = self.bot.get_emoji(1089640763392012299) # передать право на комнату
        row1 = disnake.ui.ActionRow()
        row1.add_button(style=disnake.ButtonStyle.gray, emoji=emoji1, custom_id='pri1')
        row1.add_button(style=disnake.ButtonStyle.gray, emoji=emoji2, custom_id='pri2')
        row1.add_button(style=disnake.ButtonStyle.gray, emoji=emoji3, custom_id='pri3')
        row1.add_button(style=disnake.ButtonStyle.gray, emoji=emoji4, custom_id='pri4')
        row1.add_button(style=disnake.ButtonStyle.gray, emoji=emoji5, custom_id='pri5')
        row2 = disnake.ui.ActionRow()
        row2.add_button(style=disnake.ButtonStyle.gray, emoji=emoji6, custom_id='pri6')
        row2.add_button(style=disnake.ButtonStyle.gray,
                        emoji=emoji7, custom_id='pri7')
        row2.add_button(style=disnake.ButtonStyle.gray,
                        emoji=emoji8, custom_id='pri8')
        row2.add_button(style=disnake.ButtonStyle.gray,
                        emoji=emoji9, custom_id='pri9')
        row2.add_button(style=disnake.ButtonStyle.gray,
                        emoji=emoji10, custom_id='pri10')
        embed = disnake.Embed(
            title='Управление приватной комнатой',
            description=f'Жми следующие кнопки, чтобы настроить свою комнату\nИспользовать их можно только когда у тебя есть приватный канал\n\n'
                        f'{emoji1} — Изменить **название** комнаты\n'
                        f'{emoji2} — Изменить **лимит** пользователей\n'
                        f'{emoji3} — **Закрыть** комнату для всех\n'
                        f'{emoji4} — **Открыть** комнату для всех\n'
                        f'{emoji5} — **Забрать** доступ у пользователя\n'
                        f'{emoji6} — **Выдать** доступ пользователя\n'
                        f'{emoji7} — **Выгнать** пользователя из комнаты\n'
                        f'{emoji8} — **Забрать** право говорить\n'
                        f'{emoji9} — **Выдать** право говорить\n'
                        f'{emoji10} — Передать **владельца** комнаты\n',
            color=0x2b2d31

        )
        await ctx.send(embed=embed, components=[row1, row2])

    async def check_origin_voice(self, member, inter: disnake.MessageInteraction):
        if member.voice is not None:
            channel = member.voice.channel
            finds = self.privatki.find_one({"member_id": member.id})
            if finds:
                chan_id = finds['_id']
                if chan_id == channel.id:
                    return True
                else:
                    await inter.send(embed=disnake.Embed(colour=0x2b2d31, description=f'Данный приватный канал **не принадлежит** вам!'), ephemeral=True)
                    return False
            else:
                await inter.send(embed=disnake.Embed(colour=0x2b2d31, description=f'Данный канал **не принадлежит** вам!'), ephemeral=True)
                return False
        else:
            await inter.send(embed=disnake.Embed(colour=0x2b2d31, description=f'Вы **не находитесь** в голосовом канале!'), ephemeral=True)
            return False

    async def text_and_voice(self, member, guild_id):
        channel = member.voice.channel
        channel2 = self.bot.get_channel(1084577338920018075) #1
        return channel, channel2

    @commands.Cog.listener("on_button_click")
    async def cool_button_listener(self, inter: disnake.MessageInteraction):
        member: disnake.Member = inter.author
        if inter.component.custom_id == "pri1":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel2.set_permissions(member, send_messages=True)
                await inter.send(embed=disnake.Embed(colour=0x2b2d31, description=f'{member.mention}, укажите **новое** название для канала! Для этого у вас есть **60 секунд**.'),
                    ephemeral=True)
                try:
                    names = await self.bot.wait_for("message", check=lambda i: i.author == member, timeout=60)
                except asyncio.TimeoutError:
                    await inter.edit_original_message(embed=disnake.Embed(description=f'Вы не успели указать!'))
                    await channel2.set_permissions(member, send_messages=False)
                    return
                await channel2.set_permissions(member, send_messages=False)
                await names.delete()
                name = str(names.content)
                await inter.edit_original_message(embed=disnake.Embed(description=f'{member.mention}, вы **изменили** название комнаты на: `{name}`'))
                try:
                    await channel.edit(name=f'— {name}')
                except:
                    pass
                self.member_privatki.update_one({"member_id": member.id, "guild_id": member.guild.id}, {"$set": {"name": name}}, True)
        elif inter.component.custom_id == "pri2":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel2.set_permissions(member, send_messages=True)
                await inter.send(embed=disnake.Embed(description=f'{member.mention}, укажите **новый** лимит пользователей для канала! Для этого у вас есть **60 секунд**.'),
                    ephemeral=True)
                try:
                    names = await self.bot.wait_for("message", check=lambda i: i.author == member, timeout=60)
                except asyncio.TimeoutError:
                    await inter.edit_original_message(embed=disnake.Embed(description=f'Вы не успели указать!'))
                    await channel2.set_permissions(member, send_messages=False)
                    return
                await channel2.set_permissions(member, send_messages=False)
                await names.delete()
                try:
                    name = int(names.content)
                except ValueError:
                    await inter.edit_original_message(embed=disnake.Embed(description=f'Это не является числом!'))
                    return
                await inter.edit_original_message(embed=disnake.Embed(description=f'Вы **изменили** лимит пользователей в  комнате на: `{name}`'))
                await channel.edit(user_limit=name)
        elif inter.component.custom_id == "pri3":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel.set_permissions(inter.guild.default_role, connect=False)
                await inter.send(embed=disnake.Embed(description=f'Вы успешно **закрыли** комнату от всех'), ephemeral=True)
        elif inter.component.custom_id == "pri4":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel.set_permissions(inter.guild.default_role, connect=True)
                await inter.send(embed=disnake.Embed(description=f'Вы успешно **открыли** комнату для всех'), ephemeral=True)
        elif inter.component.custom_id == "pri5":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel2.set_permissions(member, send_messages=True)
                await inter.send(embed=disnake.Embed(
                    description=f'Укажите id или упомяните пользователя у которого хотите **забрать** доступ к комнате! Для этого у вас есть **60 секунд**.'), ephemeral=True)
                try:
                    names = await self.bot.wait_for("message", check=lambda i: i.author == member, timeout=60)
                except asyncio.TimeoutError:
                    await inter.edit_original_message(embed=disnake.Embed(description=f'Вы не успели указать!'))
                    await channel2.set_permissions(member, send_messages=False)
                    return
                await channel2.set_permissions(member, send_messages=False)
                await names.delete()
                abcs = names.content
                user = await self.members(abcs, member.guild, inter)
                await channel.set_permissions(user, connect=False)
                await inter.edit_original_message(embed=disnake.Embed(description=f'{member.mention}, вы **закрыли доступ** в комнату пользователю {user.mention}'))
                if user.voice and member.voice and user.voice.channel.id == member.voice.channel.id:
                    try:
                        await user.move_to(None)
                    except disnake.HTTPException:
                        pass
        elif inter.component.custom_id == "pri6":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel2.set_permissions(member, send_messages=True)
                await inter.send(embed=disnake.Embed(
                    description=f'Укажите id или упомяните пользователя которому хотите **выдать** доступ к комнате!. Для этого у вас есть **60 секунд**.'),
                    ephemeral=True)
                try:
                    names = await self.bot.wait_for("message", check=lambda i: i.author == member, timeout=60)
                except asyncio.TimeoutError:
                    await inter.edit_original_message(embed=disnake.Embed(description=f'Вы не успели указать!'))
                    await channel2.set_permissions(member, send_messages=False)
                    return
                await channel2.set_permissions(member, send_messages=False)
                await names.delete()
                abcs = names.content
                user = await self.members(abcs, member.guild, inter)
                await channel.set_permissions(user, connect=True)
                await inter.edit_original_message(
                    embed=disnake.Embed(description=f'{member.mention}, вы **выдали доступ** в комнату пользователю {user.mention}'))
        elif inter.component.custom_id == "pri7":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel2.set_permissions(member, send_messages=True)
                await inter.send(
                    embed=disnake.Embed(description=f'Укажите id или упомяните пользователя которого хотите **выгнать** из комнаты! Для этого у вас есть **60 секунд**.'),
                    ephemeral=True)
                try:
                    names = await self.bot.wait_for("message", check=lambda i: i.author == member, timeout=60)
                except asyncio.TimeoutError:
                    await inter.edit_original_message(embed=disnake.Embed(description=f'Вы не успели указать!'))
                    await channel2.set_permissions(member, send_messages=False)
                    return
                await channel2.set_permissions(member, send_messages=False)
                await names.delete()
                abcs = names.content
                user: disnake.Member = await self.members(abcs, member.guild, inter)
                if user.voice and member.voice and user.voice.channel.id == member.voice.channel.id:
                    try:
                        await user.move_to(None)
                    except disnake.HTTPException:
                        pass
                    await inter.edit_original_message(embed=disnake.Embed(description=f'{member.mention}, вы **выгнали** из комнаты пользователя {user.mention}'))
                else:
                    await inter.edit_original_message(embed=disnake.Embed(
                        description=f'{member.mention}, пользователя **нет** в вашем голосовом канале!'))
        elif inter.component.custom_id == "pri8":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel2.set_permissions(member, send_messages=True)
                await inter.send(
                    embed=disnake.Embed(description=f'Укажите id или упомяните пользователя у которого хотите **забрать** право говорить в комнате!. Для этого у вас есть **60 секунд**.'),
                    ephemeral=True)
                try:
                    names = await self.bot.wait_for("message", check=lambda i: i.author == member, timeout=60)
                except asyncio.TimeoutError:
                    await inter.edit_original_message(embed=disnake.Embed(description=f'Вы не успели указать!'))
                    await channel2.set_permissions(member, send_messages=False)
                    return
                await channel2.set_permissions(member, send_messages=False)
                await names.delete()
                abcs = names.content
                user: disnake.Member = await self.members(abcs, member.guild, inter)
                channel4 = user.voice.channel
                channel3 = member.guild.afk_channel
                await channel2.set_permissions(user, speak=False)
                try:
                    await user.move_to(channel3)
                except disnake.HTTPException:
                    pass
                try:
                    await user.move_to(channel4)
                except disnake.HTTPException:
                    pass
                await inter.edit_original_message(
                    embed=disnake.Embed(description=f'{member.mention}, вы **забрали** право **разговаривать** в комнате у пользователя {user.mention}'))
        elif inter.component.custom_id == "pri9":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel2.set_permissions(member, send_messages=True)
                await inter.send(
                    embed=disnake.Embed(description=f'Укажите id или упомяните пользователя которому вы хотите **выдать** право говорить в комнате!. Для этого у вас есть **60 секунд**.'),
                    ephemeral=True)
                try:
                    names = await self.bot.wait_for("message", check=lambda i: i.author == member, timeout=60)
                except asyncio.TimeoutError:
                    await inter.edit_original_message(embed=disnake.Embed(description=f'Вы не успели указать!'))
                    await channel2.set_permissions(member, send_messages=False)
                    return
                await channel2.set_permissions(member, send_messages=False)
                await names.delete()
                abcs = names.content
                user = await self.members(abcs, member.guild, inter)
                channel4 = user.voice.channel
                channel3 = member.guild.afk_channel
                await channel2.set_permissions(user, speak=True)
                try:
                    await user.move_to(channel3)
                except disnake.HTTPException:
                    pass
                try:
                    await user.move_to(channel4)
                except disnake.HTTPException:
                    pass
                await inter.edit_original_message(
                    embed=disnake.Embed(description=f'{member.mention}, вы **выдали** право **разговаривать** в комнате пользователю {user.mention}'))
        elif inter.component.custom_id == "pri10":
            origin_message = await self.check_origin_voice(member, inter)
            if origin_message:
                channel, channel2 = await self.text_and_voice(member, member.guild.id)
                await channel2.set_permissions(member, send_messages=True)
                await inter.send(embed=disnake.Embed(
                    description=f'{member.mention}, укажите id или упомяните пользователя которому вы хотите **передать** право владения комнатой!. Для этого у вас есть **60 секунд**.'),
                    ephemeral=True)
                try:
                    names = await self.bot.wait_for("message", check=lambda i: i.author == member, timeout=60)
                except asyncio.TimeoutError:
                    await inter.edit_original_message(embed=disnake.Embed(description=f'Вы не успели указать!'))
                    await channel2.set_permissions(member, send_messages=False)
                    return
                await channel2.set_permissions(member, send_messages=False)
                await names.delete()
                abcs = names.content
                user = await self.members(abcs, member.guild, inter)
                self.privatki.update_one({"_id": channel.id}, {"$set": {"member_id": user.id}}, True)
                await inter.edit_original_message(embed=disnake.Embed(description=f'{member.mention}, вы **передали** права на комнату пользователю {user.mention}!'))


def setup(bot):
    bot.add_cog(Privates(bot))
    print('Ког: "Приватки" загрузился!')
