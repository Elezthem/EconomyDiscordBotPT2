# -*- coding: utf-8 -*-
import disnake
from disnake.ext import commands
import os
import asyncio
from pymongo import MongoClient
from config import *
import time
from disnake import Activity, ActivityType
import os
import sys

cluster = MongoClient(MONGO_URI)

bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), intents=disnake.Intents.all())
bot.remove_command('help')
bot.cluster = cluster
guilds = [1084577336340512889]


@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f'Ког {extension} успешно загружен!')


@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f'Ког {extension} успешно отключен!')


def cogs_names():
    list_cogs = []
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            list_cogs.append(filename[:-3])
    return list_cogs


list_developers = [559094143440257031]


@bot.slash_command(name='reload', description='Перезагрузка файла бота', options=[
    disnake.Option(name='extension', description="Название кога", type=disnake.OptionType.string, required=True,
                   choices=cogs_names())])
async def reload(ctx: disnake.ApplicationCommandInteraction, extension: str):
    if ctx.author.id not in list_developers:
        await ctx.send(f'У вас недостаточно прав!', ephemeral=True)
        return
    try:
        bot.reload_extension(f"cogs.{extension}")
    except:
        await ctx.send(f'Ког: **{extension}** - **не** загружен!', ephemeral=True)
        return
    await ctx.send(f'Ког: **{extension}** Успешно перезагружен!', ephemeral=True)


@bot.command()
async def check_start(ctx):
    await ctx.send(f'Я тут!')


@bot.event
async def on_ready():
    print("Бот запущен")
    print(f'Вы вошли как {bot.user.name}#{bot.user.discriminator}')


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run('')
