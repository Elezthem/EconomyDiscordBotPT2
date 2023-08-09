import disnake
import pymongo.collection
from disnake.ext import commands, tasks
from pymongo import MongoClient
from config import *
from mod import *
import time
import re
import random
import asyncio


test_guild = [1084577336340512889]

"""
member.voice.deaf - Мут наушников сервер
member.voice.mute - Мут микро сервер
member.voice.self_deaf - Мут наушников
member.voice.self_mute - Мут микро
member.voice.self_video - Видео сервер
member.voice.self_stream - Сервер сервер
member.voice.session_id - Сессия
"""


class Activity(commands.Cog, name="active"):
    def __init__(self, bot):
        self.bot: disnake.Client = bot

        self.cluster = self.bot.cluster
        self.profile: pymongo.collection.Collection = self.cluster.infinity.profile
        self.g_count: pymongo.collection.Collection = self.cluster.infinity.guilds
        self.lovess: pymongo.collection.Collection = self.cluster.infinity.loves
        self.l_room: pymongo.collection.Collection = self.cluster.infinity.L_rooms

        self.member_voice_online.start()
        self.member_voice_online_brack.start()
        self.member_voice_online_private_room.start()

    async def get_member(self, member1: str, guild: disnake.Guild) -> disnake.Member:
        id_mem = str(member1) \
            .replace("<", "") \
            .replace("@", "") \
            .replace("!", "") \
            .replace(">", "")
        member = guild.get_member(int(id_mem))
        return member

    def return_key(self, find: tuple, info):
        for key in find.keys():
            if find[key] == info:
                return key

    @tasks.loop(seconds=60)
    async def member_voice_online_brack(self):
        async def checks(channel: disnake.VoiceChannel):
            find = self.lovess.find_one({"channel_id": channel.id})
            if find:
                self.lovess.update_one(find, {"$inc": {"voice": 1}}, True)
        await self.bot.wait_until_ready()
        guild: disnake.Guild = self.bot.get_guild(1084577336340512889)
        maincategory: disnake.CategoryChannel = disnake.utils.get(
            guild.categories, id=1090999787312136284)
        for channel in maincategory.voice_channels:
            if len(channel.members) >= 2:
                asyncio.create_task(checks(channel))

    @tasks.loop(seconds=60)
    async def member_voice_online_private_room(self):
        async def checks(channel: disnake.VoiceChannel):
            for member in channel.members:
                if not member.voice.deaf and not member.voice.mute and not member.voice.self_deaf:
                    self.l_room.update_one({"channel": channel.id}, {"$inc": {"voice": 1}}, True)
        await self.bot.wait_until_ready()
        guild: disnake.Guild = self.bot.get_guild(1084577336340512889)
        maincategory: disnake.CategoryChannel = disnake.utils.get(
            guild.categories, id=1090999717426638908)# войсы где добавляется монетка 
        for channel in maincategory.voice_channels:
            if len(channel.members) >= 2:
                asyncio.create_task(checks(channel))

    @tasks.loop(seconds=60)
    async def member_voice_online(self):
        async def checks(member: disnake.Member, guild_id: int):
            self.profile.update_one({"member_id": member.id, "guild_id": guild_id}, {"$inc": {'balance': 1, "voice": 1}}, True)
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(test_guild[0])
        for channel in guild.voice_channels:
            if channel != guild.afk_channel:
                for member in channel.members:
                    if not member.voice.deaf and not member.voice.mute and not member.voice.self_deaf and not member.voice.self_mute:
                        asyncio.create_task(checks(member, guild.id))
        for channel in guild.stage_channels:
            for member in channel.members:
                if not member.voice.deaf and not member.voice.self_deaf:
                    asyncio.create_task(checks(member, guild.id))

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        member = message.author
        mes = message.content.lower()
        if mes[0:1:1] != PREFIX and len(mes) > 15 and not member.bot:
            self.profile.update_one({"member_id": member.id, "guild_id": message.guild.id}, {"$inc": {'balance': 1, 'message': 1}}, True)


def setup(bot):
    bot.add_cog(Activity(bot))
    print('Ког: "Активность" загрузился!')
