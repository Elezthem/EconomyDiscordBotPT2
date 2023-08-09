import random
import time
import disnake
from disnake.ext import commands, tasks
from config import *
from mod import *
import pymongo
import requests
from PIL import Image, ImageFont, ImageDraw
import io

test_guild = [1084577336340512889]

class Commands(commands.Cog, name="commands"):
    def __init__(self, bot):
        self.bot: disnake.Client = bot

        self.cluster = self.bot.cluster
        self.profile: pymongo.collection.Collection = self.cluster.infinity.profile
        self.g_count: pymongo.collection.Collection = self.cluster.infinity.guilds
        self.lovess: pymongo.collection.Collection = self.cluster.infinity.loves
        self.lroles: pymongo.collection.Collection = self.cluster.infinity.L_roles

    async def get_money(self, member_id, guild_id):
        find = self.profile.find_one({"member_id": member_id, "guild_id": guild_id})
        if find and "balance" in find.keys():
            return int(find['balance'])
        else:
            return 0

    async def get_status(self, member_id, guild_id):
        find = self.profile.find_one({"member_id": member_id, "guild_id": guild_id})
        if find and "status" in find.keys():
            return find['status']
        else:
            return "Не установлен"

    async def get_online(self, member_id, guild_id):
        find = self.profile.find_one({"member_id": member_id, "guild_id": guild_id})
        if find and "voice" in find.keys():
            return int(find['voice'])
        else:
            return 0

    async def get_message(self, member_id, guild_id):
        find = self.profile.find_one({"member_id": member_id, "guild_id": guild_id})
        if find and "message" in find.keys():
            return int(find['message'])
        else:
            return 0

    async def return_mesto(self, member_id, guild_id):
        finds = self.profile.find({"guild_id": guild_id}).sort([("voice", -1)])
        finds = list(finds)
        if finds:
            find = self.profile.find_one({"member_id": member_id, "guild_id": guild_id})
            if find:
                index = finds.index(find)+1
                if index > 1000:
                    return "Вне топа"
                else:
                    return index
            else:
                return "Вне топа"
        else:
            return 'Ошибка'

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
            ava = member.display_avatar.url
        elif member.avatar:
            ava = member.avatar.url
        else:
            ava = member.default_avatar.url
        return ava

    @commands.slash_command(
        name='avatar',
        description=f'Посмотреть аватарку',
        dm_permission=False,
        options=[
            disnake.Option(
                name='member',
                description='Укажите пользователя',
                type=disnake.OptionType.user,
                required=True
            )
        ]
    )
    async def avatar_command(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member):
        emb = disnake.Embed(
            title=f'Аватар пользователя — {member}',
            description='',
            color=0x2b2d31
        )
        emb.set_image(url=member.avatar.url)
        await ctx.send(embed=emb)

    @commands.slash_command(
        name='banner',
        description=f'Посмотреть баннер пользователя',
        dm_permission=False,
        options=[
            disnake.Option(
                name='member',
                description='Укажите пользователя',
                type=disnake.OptionType.user,
                required=True
            )
        ]
    )
    async def banner_command(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member):
        try:
            user = await self.bot.fetch_user(member.id)
        except(disnake.HTTPException, disnake.NotFound):
            await ctx.send(f'{ctx.author.mention}, произошла ошибка. Повторите попытку!', ephemeral=True)
            return
        banner = user.banner
        if banner:
            emb = disnake.Embed(
                title=f'Баннер пользователя — {member}',
                color=0x2b2d31
            )
            emb.set_image(url=banner.url)
        else:
            emb = disnake.Embed(
                description=f"{ctx.author.mention}, у {member.mention} **Отсутствует баннер**!"
            )
        await ctx.send(embed=emb)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def all_l_roles(self, ctx):
        await ctx.message.delete()
        okey = list(self.lroles.find({"guild_id": ctx.guild.id}))
        find = group_list(okey, 10)
        if okey:
            embed = disnake.Embed(
                title=f'Все личные роли — {ctx.guild}',
                description=''
            )
            embed.set_thumbnail(url=ctx.author.avatar.url)
            embeds = []
            for page, group in enumerate(find):
                for index, r in enumerate(group):
                    place = page * 10 + index + 1
                    role = ctx.guild.get_role(r['r_id'])
                    member = ctx.guild.get_member(r["owner_id"])
                    if role and member:
                        embed.description += f'**{place})** {role.mention}\n**·** Название: **{role}**\n**·** **Владелец:** {member.mention}\n\n'
                    else:
                        embed.description += f'**{place})** <@&{r["r_id"]}>\n**·** Название: **{r["rol_name"]}**\n**·** **Владелец:** <@{r["owner_id"]}>\n\n'
                embeds.append(embed.copy())
                embed.description = ''
            btns = Pages_Standart(embeds=embeds,  time_end=120)
            await ctx.send(embed=embeds[0], view=btns)

    @commands.slash_command(
        name='profile',
        description=f'Посмотреть серверный профиль',

        dm_permission=False
    )
    async def profile(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member=None):
        if member == None:
            member = ctx.author
        await ctx.response.defer()
        font = ImageFont.truetype("src/font/Roboto-Black.ttf", size=65)
        font_b = ImageFont.truetype("src/font/Roboto-Black.ttf", size=33)
        font_o = ImageFont.truetype("src/font/Roboto-Black.ttf", size=30)
        font_s = ImageFont.truetype("src/font/Montserrat-Medium.otf", size=22)
        avatar_url = self.return_avatar(member)
        if str(avatar_url)[-4:] == '.png':
            url1 = requests.get(avatar_url, stream=True)
        else:
            url1 = requests.get(str(avatar_url)[:-10], stream=True)
        avatar = Image.open(io.BytesIO(url1.content))
        avatar = avatar.resize((150, 150), Image.ANTIALIAS)
        mask = Image.new("L", avatar.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 150, 150), fill=255)
        user_card = Image.open('src/fonlove/fonpro.png')
        user_card = user_card.resize((1081, 608), Image.ANTIALIAS)

        # ==============================

        clan = "Отсутствует"
        nickname = member.display_name
        money = await self.get_money(member.id, ctx.guild.id)
        status = await self.get_status(member.id, ctx.guild.id)
        online = await self.get_online(member.id, ctx.guild.id)
        top = await self.return_mesto(member.id, ctx.guild.id)
        message = await self.get_message(member.id, ctx.guild.id)
        minutes = int(online % 60)
        hour = int(online // 60)
        if hour < 1:
            hour = 0
        if minutes < 1 or minutes >= 60:
            minutes = 0

        idraw = ImageDraw.Draw(user_card)
        idraw.text((150, 505), str(clan), (255, 255, 255), font=font_b)
        if len(nickname) > 15:
            idraw.text((750, 130), str(f'{str(nickname)[:15]}...'), (255, 255, 255), font=font_b)
        else:
            idraw.text((750, 130), str(f'{str(nickname)}'), (255, 255, 255), font=font_b)

        if len(status) > 18:
            idraw.text((750, 165), str(f'{str(status)[:18]}...'), (255, 255, 255), font=font_s)
        else:
            idraw.text((750, 165), str(f'{str(status)}'), (255, 255, 255), font=font_s)

        idraw.text((890, 506), str(f'{hour}ч. {minutes}м.'), (255, 255, 255), font=font_o)
        idraw.text((890, 410), str(message), (255, 255, 255), font=font_o)
        idraw.text((630, 410), str(money), (255, 255, 255), font=font_o)
        idraw.text((630, 505), str(top), (255, 255, 255), font=font_o)

        # ==========================
        lprofiles = self.lovess.find_one({"$or": [{"man": member.id}, {"girl": member.id}]})
        if lprofiles:
            man_id = lprofiles[self.return_partner(lprofiles, member)]
            member: disnake.Member = ctx.guild.get_member(man_id)
            
            avatar1_url = self.return_avatar(member)
            if str(avatar1_url)[-4:] == '.png':
                url1 = requests.get(avatar1_url, stream=True)
            else:
                url1 = requests.get(str(avatar1_url)[:-10], stream=True)
            avatar1 = Image.open(io.BytesIO(url1.content))
            avatar1 = avatar1.resize((110, 110), Image.ANTIALIAS)
            mask1 = Image.new("L", avatar1.size, 0)
            draw_mask1 = ImageDraw.Draw(mask1)
            draw_mask1.ellipse((0, 0, 110, 110), fill=255)

            user_card.paste(avatar, (587, 83), mask)
            user_card.paste(avatar1, (74, 278), mask1)
            memnick = member.display_name
            if len(memnick) > 10:
                idraw.text((210, 312), str(f'{str(memnick)[:14]}...'), (255, 255, 255), font=font_b)
            else:
                idraw.text((210, 312), str(f'{str(memnick)}'), (255, 255, 255), font=font_b)
        else:
            user_card.paste(avatar, (587, 83), mask)

        
        user_card.save('src/templove/fonpro_gotovo.png', quality=95)
        file = disnake.File("src/templove/fonpro_gotovo.png", filename="src/templove/fonpro_gotovo.png")




        # ===============================================================================================================================================



        if member != ctx.author:
            row = disnake.ui.ActionRow()
            row.add_button(style=disnake.ButtonStyle.grey,
                label='Изменить статус', custom_id='lstatus')
            row.add_button(style=disnake.ButtonStyle.red,
                label='Удалить статус', custom_id='dstatus')
            msg = await ctx.edit_original_message(file=file, components = [row])
            try:
                inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=60, check=lambda i: i.author.id == ctx.author.id and i.message.id == msg.id)
            except asyncio.TimeoutError:
                await ctx.edit_original_message(components=[])
                return
            if inter.component.custom_id == 'lstatus':
                await inter.response.send_modal(
                    title=f"Изменение статуса",
                    custom_id=f"status",
                    components=[
                        disnake.ui.TextInput(
                            label="Укажите статус",
                            placeholder=f"Введите текст",
                            custom_id="lstatus",
                            style=disnake.TextInputStyle.short,
                            min_length=1,
                            max_length=30,
                        ),
                    ],
                )
                try:
                    modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                        "modal_submit",
                        check=lambda i: i.custom_id == f"status" and i.author.id == inter.author.id,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return
                for custom_id, value in modal_inter.text_values.items():
                    if custom_id == "lstatus":
                        number = str(value)
                    else:
                        return

                emb = disnake.Embed(
                    title='Смена статуса',
                    description=f'{ctx.author.mention}, вы **изменили** свой статус на: `{number}`',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await modal_inter.send(embed=emb, ephemeral=True)
                self.profile.update_one({"member_id": ctx.author.id, "guild_id": ctx.guild.id}, {"$set": {"status": number}}, True)
            elif inter.component.custom_id == 'dstatus':
                emb = disnake.Embed(
                    title='Сброс статуса',
                    description=f'{ctx.author.mention}, вы **сбросили** свой статус',
                    color=0x2b2d31
                )
                emb.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.edit_original_message(embed=emb)
                self.profile.update_one({"member_id": ctx.author.id,  "guild_id": ctx.guild.id}, {"$set": {"status": "Не установлен"}})
        else:
            msg = await ctx.edit_original_message(file=file)
def setup(bot):
    bot.add_cog(Commands(bot))
    print('Ког: "Команды" загрузился!')
