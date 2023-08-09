import time
import disnake
from disnake.ext import commands, tasks
from pymongo import MongoClient
from config import *

test_guild = [1084577336340512889]


class Webhook(commands.Cog, name="webhook"):
    def __init__(self, bot):
        self.bot = bot

        self.cluster = self.bot.cluster

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_select_menu_roles_events_dostyp(self, ctx):
        await ctx.message.delete()

        event = self.bot.get_emoji(1089565281443135518)
        movie = self.bot.get_emoji(1089568392974975016)
        staff = self.bot.get_emoji(1089565271167082609)

        emb1 = disnake.Embed(color=disnake.Color.from_rgb(47, 49, 54))
        emb1.set_image(
            url="https://media.discordapp.net/attachments/996770355752468521/1020154982718242866/b1a5f1457873c4e6.gif?width=540&height=226")
        emb2 = disnake.Embed(
            title='Под этим постом вы можете выбрать себе роль, \nнажав на соответствующую роли кнопку в меню выбора.',
            description=f'\n\n'
                        f'<:event:1089565281443135518> — Предстоящие ивенты.\n'
                        f'<:movie:1089568392974975016> — Предстоящие фильмы.\n'
                        f'<:staff:1089565271167082609> — Наборы в стафф\n',
            color=disnake.Color.from_rgb(47, 49, 54)
        )
        emb2.set_image(
            url="https://cdn.discordapp.com/attachments/877327839022710894/905758031357296690/222.png ")
        emb2.set_footer(
            text='Выбором в меню вы можете взять соответствующую смайлику роль.\nТакже повторным нажатием — роль можно снять.')
        await ctx.send(embed=emb1)
        row = disnake.ui.ActionRow()
        row.add_select(options=[
                disnake.SelectOption(
                    label="Предстоящие ивенты", value="select_events12", emoji=event),
                disnake.SelectOption(
                    label="Предстоящие фильмы", value="select_events13", emoji=movie),
                disnake.SelectOption(
                    label="Наборы в стафф", value="select_events14", emoji=staff),
            ],
            placeholder="Выберите роль!",
            min_values=1,
            max_values=1,
            custom_id='select_roles_dostyp')
        await ctx.send(embed=emb2, components=[row])

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_select_menu_roles_events(self, ctx):
        await ctx.message.delete()

        csgo = self.bot.get_emoji(1089565280147087410)
        dota = self.bot.get_emoji(1089565273792725033)
        lol = self.bot.get_emoji(1089355673151754360)
        gen = self.bot.get_emoji(1089565277555007591)

        emb1 = disnake.Embed(color=disnake.Color.from_rgb(47, 49, 54))
        emb1.set_image(
            url="https://media.discordapp.net/attachments/996770355752468521/1020154982311407616/09e1bb4fc999ea48.gif?width=540&height=226")
        emb2 = disnake.Embed(
            title='Выберите интересующие вас роли со списка ниже.',
            description=f'\n\n'
                        f'<:csgo:1089565280147087410> — CS:GO\n'
                        f'<:dota2:1089565273792725033> — Dota 2\n'
                        f'<:LIGA:1020751607895433319> — League of legends\n'
                        f'<:gen:1089565277555007591> — Genshin Impact\n',
            color=disnake.Color.from_rgb(47, 49, 54)
        )
        emb2.set_image(
            url="https://cdn.discordapp.com/attachments/877327839022710894/905758031357296690/222.png ")
        emb2.set_footer(
            text='Нажав на соответствующую роль в меню — её можно выбрать. Используйте повторное нажатие на ту же роль, что бы снять её.')
        await ctx.send(embed=emb1)
        row = disnake.ui.ActionRow()
        row.add_select(options=[
                disnake.SelectOption(
                    label="CS:GO", value="select_events2", emoji=csgo),
                disnake.SelectOption(
                    label="Dota 2", value="select_events3", emoji=dota),
                disnake.SelectOption(
                    label="League of legends", value="select_events4", emoji=lol),
                disnake.SelectOption(
                    label="Genshin Impact", value="select_events6", emoji=gen),
            ],
            placeholder="Выберите роль!",
            min_values=1,
            max_values=1,
            custom_id='select_roles_game')
        await ctx.send(embed=emb2, components=[row])

    @commands.Cog.listener("on_dropdown")
    async def select_for_game_and_chat(self, inter: disnake.MessageInteraction):
        member: disnake.Member = inter.author
        guild: disnake.Guild = inter.guild
        if inter.component.custom_id == 'select_roles_game':
            match inter.values[0]:
                case 'select_events2':
                    role = guild.get_role(1089365369082359970)  # csgo
                case'select_events3':
                    role = guild.get_role(1089365377445810216)  # dota
                case'select_events4':
                    role = guild.get_role(1089365378813145108)  # lol
                case'select_events6':
                    role = guild.get_role(1089365379786219600)  # gen
                case _:
                    return
            if role not in member.roles:
                try:
                    await member.add_roles(role)
                except disnake.Forbidden:
                    await inter.send(f'Произошла ошибка прав бота! Свяжитесь с администрацией!', ephemeral=True)
                    return
                except disnake.HTTPException:
                    await inter.send(f'Произошла ошибка при выдаче роли, повторите попытку!', ephemeral=True)
                    return
                emb = disnake.Embed(
                    description=f'{member.mention}, вы **получили** роль {role.mention}',
                    color=disnake.Color.from_rgb(47, 49, 54)
                )
                await inter.send(embed=emb, ephemeral=True)
                return
            else:
                try:
                    await member.remove_roles(role)
                except disnake.Forbidden:
                    await inter.send(f'Произошла ошибка прав бота! Свяжитесь с администрацией!', ephemeral=True)
                    return
                except disnake.HTTPException:
                    await inter.send(f'Произошла ошибка при снятии роли, повторите попытку!', ephemeral=True)
                    return
                emb = disnake.Embed(
                    description=f'{member.mention}, вы **сняли** роль {role.mention}',
                    color=disnake.Color.from_rgb(47, 49, 54)
                )
                await inter.send(embed=emb, ephemeral=True)
                return
        elif inter.component.custom_id == 'select_roles_dostyp':
            match inter.values[0]:
                case 'select_events12':
                    role = guild.get_role(1089367888240058389)  # ивенты
                case 'select_events13':
                    role = guild.get_role(1089569011378958456)  # фильм
                case 'select_events14':
                    role = guild.get_role(1089367950588395520)  # staff
                case  _:
                    return
            if role not in member.roles:
                try:
                    await member.add_roles(role)
                except disnake.Forbidden:
                    await inter.send(f'Произошла ошибка прав бота! Свяжитесь с администрацией!', ephemeral=True)
                    return
                except disnake.HTTPException:
                    await inter.send(f'Произошла ошибка при выдаче роли, повторите попытку!', ephemeral=True)
                    return
                emb = disnake.Embed(
                    description=f'{member.mention}, вы **получили** роль {role.mention}',
                    color=disnake.Color.from_rgb(47, 49, 54)
                )
                await inter.send(embed=emb, ephemeral=True)
                return
            else:
                try:
                    await member.remove_roles(role)
                except disnake.Forbidden:
                    await inter.send(f'Произошла ошибка прав бота! Свяжитесь с администрацией!', ephemeral=True)
                    return
                except disnake.HTTPException:
                    await inter.send(f'Произошла ошибка при снятии роли, повторите попытку!', ephemeral=True)
                    return
                emb = disnake.Embed(
                    description=f'{member.mention}, вы **сняли** роль {role.mention}',
                    color=disnake.Color.from_rgb(47, 49, 54)
                )
                await inter.send(embed=emb, ephemeral=True)
                return



def setup(bot):
    bot.add_cog(Webhook(bot))
    print('Ког: "Вебхуки" загрузился!')
