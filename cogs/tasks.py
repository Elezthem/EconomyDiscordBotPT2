import time
import pymongo
import disnake
from disnake.ext import commands, tasks
from pymongo import MongoClient
from config import *
from delorean import Delorean


test_guild = [1084577336340512889]


class Testing(commands.Cog, name="task"):
    def __init__(self, bot):
        self.bot: disnake.Client = bot

        self.cluster = self.bot.cluster
        self.lroles: pymongo.collection.Collection = self.cluster.infinity.L_roles  # личные роли
        self.l_buys_roles: pymongo.collection.Collection = self.cluster.infinity.buys_roles
        self.lshop: pymongo.collection.Collection = self.cluster.infinity.L_roles_shop
        self.lovess: pymongo.collection.Collection = self.cluster.infinity.loves
        self.profile: pymongo.collection.Collection = self.cluster.infinity.profile

        self.l_roles.start()
        self.l_buy_roles.start()
        self.braks_loves.start()
        self.already_timely.start()
        self.love_room_check.start()

    def return_avatar(self, member: disnake.Member):
        if member.display_avatar:
            return member.display_avatar.url
        elif member.avatar:
            return member.avatar.url
        else:
            return member.default_avatar.url

    @tasks.loop(seconds=2)
    async def love_room_check(self):
        await self.bot.wait_until_ready()
        guild: disnake.Guild = self.bot.get_guild(1084577336340512889)
        category = disnake.utils.get(guild.categories, id=1090999787312136284)
        if category:
            for channel in category.voice_channels:
                if len(channel.members) == 0 and channel.id != 1091991748152139876:
                    await channel.delete(reason=f'Пустая любовная комната. Очистка каналов!')
                    self.lovess.update_one({"channel_id": channel.id}, {"$set": {"channel_id": 0}}, True)




    @tasks.loop(seconds=15)
    async def l_buy_roles(self):
        await self.bot.wait_until_ready()
        for x in list(self.l_buys_roles.find()):
            if x:
                y = int(x['time_end'])
                if y < int(time.time()):
                    guild = self.bot.get_guild(1090999787312136284)
                    member = guild.get_member(x['member_id'])
                    if member:
                        role = guild.get_role(x['role_id'])
                        emb = disnake.Embed(
                            title='Магазин ролей',
                            description=f'{member.mention}, срок действия роли `{role}` из магазина был окончен. Роль была забрана у вас!',
                            color=0x2b2d31
                        )
                        emb.set_thumbnail(url=self.return_avatar(member))
                        try:
                            await member.send(embed=emb)
                        except (disnake.HTTPException, disnake.Forbidden):
                            pass
                        if role:
                            try:
                                await member.remove_roles(role)
                            except (disnake.HTTPException, disnake.Forbidden):
                                pass
                    self.l_buys_roles.delete_one(x)

    @tasks.loop(seconds=3)
    async def already_timely(self):
        await self.bot.wait_until_ready()
        for x in list(self.profile.find()):
            if x and "next_timely" in x.keys():
                y = int(x['next_timely'])
                if y < int(time.time()):
                    self.profile.update_one(x, {"$unset": {"next_timely": x["next_timely"]}})

    @tasks.loop(seconds=30)
    async def l_roles(self):
        await self.bot.wait_until_ready()
        for x in list(self.lroles.find()):
            if x:
                y = int(x['role_time'])
                if y < int(time.time()):
                    main_guild = self.bot.get_guild(x['guild_id'])
                    member = main_guild.get_member(x["owner_id"])
                    if member:
                        rol_i = x['r_id']
                        role = main_guild.get_role(rol_i)
                        self.lroles.delete_one(x)
                        if role:
                            await member.remove_roles(role)
                            emb = disnake.Embed(
                                title='Личная Роль',
                                description=f'{member.mention}, срок действия вашей личной роли `{role.name}` **закончился**. У вас была **забрана** возможность управления ролью!',
                                color=0x2b2d31
                            )
                            emb.set_thumbnail(url=self.return_avatar(member))
                            try:
                                await member.send(embed=emb)
                            except (disnake.HTTPException, disnake.Forbidden):
                                pass
                            rol_shop = self.lshop.find_one({"_id": role.id})
                            if rol_shop:
                                self.lshop.delete_one(rol_shop)
                            return
                        rol_shop = self.lshop.find_one({"_id": x['r_id']})
                        if rol_shop:
                            self.lshop.delete_one(rol_shop)


    @tasks.loop(minutes=1)
    async def braks_loves(self):
        await self.bot.wait_until_ready()
        for x in list(self.loves.find()):
            if x:
                y = int(x['time_end'])
                if y < int(time.time()):
                    main_guild = self.bot.get_guild(x['guild_id'])
                    balance = x['balance']
                    if balance < 1000:
                        member = main_guild.get_member(x['man'])
                        member1 = main_guild.get_member(x['girl'])
                        love_role = main_guild.get_role(x['love_role'])
                        if member and member1:
                            emb = disnake.Embed(
                                title='Окончание Брака',
                                description=f'{member1}, ваш брак с {member} **закончился**!',
                                color=0x2b2d31
                            )
                            emb.set_thumbnail(url=self.return_avatar(member1))
                            try:
                                await member1.send(embed=emb)
                            except (disnake.HTTPException, disnake.Forbidden):
                                pass
                            # =====
                            emb = disnake.Embed(
                                title='Окончание Брака',
                                description=f'{member}, ваш брак с {member1} **закончился**!',
                                color=0x2b2d31
                            )
                            emb.set_thumbnail(url=self.return_avatar(member))
                            try:
                                await member.send(embed=emb)
                            except (disnake.HTTPException, disnake.Forbidden):
                                pass
                            # =====
                        channel = self.bot.get_channel(x['channel_id'])
                        if channel:
                            try:
                                await channel.delete()
                            except (disnake.HTTPException, disnake.Forbidden):
                                pass
                        if member:
                            try:
                                await member.remove_roles(love_role)
                            except (disnake.HTTPException, disnake.Forbidden):
                                pass
                        if member1:
                            try:
                                await member1.remove_roles(love_role)
                            except (disnake.HTTPException, disnake.Forbidden):
                                pass
                        try:
                            self.lovess.delete_one(x)
                        except (disnake.HTTPException, disnake.Forbidden):
                            pass
                    else:
                        self.lovess.update_one(x, {'$inc': {'balance': -1000, 'time': 60*60*30}}, True)


def setup(bot):
    bot.add_cog(Testing(bot))
    print('Ког: "Таски" загрузился!')
