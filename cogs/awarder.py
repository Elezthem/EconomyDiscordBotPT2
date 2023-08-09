import disnake
import pymongo.collection
from disnake.ext import commands, tasks
from disnake import Activity, ActivityType
from PIL import Image, ImageFont, ImageDraw
import requests
import io
from io import BytesIO
import time

test_guild = 1084577336340512889

class Awarded(commands.Cog, name="awarded"):
    def __init__(self, client):
        self.client: disnake.Client = client

        self.cluster = self.client.cluster
        self.collections: pymongo.collection.Collection = self.cluster.infinity.collections
        self.guilds: pymongo.collection.Collection = self.cluster.infinity.guilds
        self.profile: pymongo.collection.Collection = self.cluster.infinity.profile

        self.voice_check.start()
        self.banner.start()
        self.reset_db.start()

    def return_avatar(self, member: disnake.Member):
        if member.display_avatar:
            return member.display_avatar.url
        elif member.avatar:
            return member.avatar.url
        else:
            return member.default_avatar.url

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_restart_banner_time(self, ctx):
        self.guilds.update_one({"_id": ctx.guild.id}, {"$set": {'reset_banner_active_members': int(time.time())}}, True)
        await ctx.send(f'Готово!')

    def get_guild_voice_lenght(self, guild):
        count = 0
        for chan in guild.voice_channels:
            count += len(chan.members)
        for chan in guild.stage_channels:
            count += len(chan.members)
        return count

    def get_guild_stream_lenght(self, guild):
        count = 0
        for chan in guild.voice_channels:
            for member in chan.members:
                if member.voice.self_stream:
                    count += 1
        return count

    def get_guild_online_lenght(self, guild):
        count = 0
        for member in guild.members:
            if member.Status.online:
                count += 1
        return count

    def get_bot_coutner(self, guild):
        botcounter = 0
        for member in guild.members:
            if member.bot:
                botcounter += 1
        return botcounter

    def get_status(self, member: disnake.Member):
        find = self.profile.find_one({'member_id': member.id, "guild_id": member.guild.id})
        if find and "status" in find.keys():
            return find['status']
        else:
            return "Отсутствует"

    def cog_unload(self):
        self.banner.stop()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        unv = member.guild.get_role(1089140831946031144)
        #unvvv = member.guild.get_role(1089140831946031144)
        await member.add_roles(unv)
        #await member.remove_roled(unvvv)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Я запустился как: {self.client.user.name}#{self.client.user.discriminator}')

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        member = message.author
        if len(message.content) > 10 and not member.bot:
            self.collections.update_one({"_id": member.id}, {"$inc": {"score": 2}}, True)

    @tasks.loop(minutes=1)
    async def voice_check(self):
        await self.client.wait_until_ready()
        guild = self.client.get_guild(1084577336340512889)
        for channel in guild.voice_channels:
            if channel != guild.afk_channel:
                for member in channel.members:
                    if not member.voice.deaf and not member.voice.mute and not member.voice.self_deaf and not member.voice.self_mute:
                        self.collections.update_one({"_id": member.id}, {"$inc": {"score": 60}}, True)
        for channel in guild.stage_channels:
            for member in channel.members:
                if not member.voice.deaf and not member.voice.mute and not member.voice.self_deaf and not member.voice.self_mute:
                    self.collections.update_one({"_id": member.id}, {"$inc": {"score": 60}}, True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def new_banner_paint(self, ctx):
        guild = self.client.get_guild(ctx.guild.id)
        voice = self.get_guild_voice_lenght(guild)
        mem = guild.member_count
        member = guild.get_member(ctx.author.id)
        nickname = member.display_name

        status = self.get_status(member=member)
        if guild:
            banner = Image.open('bannerserver.png').convert("RGBA")
            banner = banner.resize((960, 540), Image.Resampling.LANCZOS)
            idraw = ImageDraw.Draw(banner)
            light = ImageFont.truetype("3.ttf", size=45)
            light60 = ImageFont.truetype("3.ttf", size=30)
            medium = ImageFont.truetype("1.ttf", size=40)
            medium100 = ImageFont.truetype("1.ttf", size=65)
            idraw.text((557, 282), str(mem), fill=(253, 253, 253), font=light)  # все участники
            if len(nickname) > 14:
                idraw.text((265, 330), str(f'{nickname[:7]}...'), fill=(255, 255, 255), font=medium)  # ник
            else:
                idraw.text((265, 330), str(f'{nickname}'), fill=(255, 255, 255), font=medium)  # ник
            if len(status) >= 17:
                status = f'{status[:15]}...'
            idraw.text((265, 395), str(status), fill=(253, 253, 253), font=light60)  # статус

            if voice < 10:
                idraw.text((800, 405), str(voice), fill=(255, 255, 255), font=medium100)  # войс
            if 10 <= voice < 100:
                idraw.text((780, 405), str(voice), fill=(255, 255, 255), font=medium100)  # войс
            if voice > 100:
                idraw.text((770, 405), str(voice), fill=(255, 255, 255), font=medium100)  # войс

            avatar = self.return_avatar(member)
            if str(avatar)[-4:] == '.png':
                url1 = requests.get(avatar, stream=True)
            else:
                url1 = requests.get(str(avatar)[:-10], stream=True)
            # =====================================
            avatar = Image.open(io.BytesIO(url1.content))
            avatar = avatar.resize((310, 310), Image.Resampling.LANCZOS)
            # =====================================
            mask = Image.new("L", avatar.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 310, 310), fill=255)

            banner = banner.resize((1920, 1080), Image.Resampling.LANCZOS)
            banner.paste(avatar, (160, 600), mask)

            banner.save('/Economika/src/saved/banner1.png')
            await ctx.send('1')


    @tasks.loop(seconds=30)
    async def banner(self):
        await self.client.wait_until_ready()
        #try:
        find = self.collections.find()
        if not find:
            return
        find = list(find.sort([("score", -1)]))
        if len(find) < 1:
            return
        id = find[:1][0]["_id"]

        guild = self.client.get_guild(1084577336340512889)
        voice = self.get_guild_voice_lenght(guild)
        #   voice = 8
        #voice = 65
        #voice = 213
        mem = guild.member_count
        member = guild.get_member(id)
        nickname = member.display_name

        status = self.get_status(member=member)
        if guild:
            banner = Image.open('bannerserver.png').convert("RGBA")
            idraw = ImageDraw.Draw(banner)
            light = ImageFont.truetype("Economika/src/font/3.ttf", size=55)
            light60 = ImageFont.truetype("Economika/src/font/3.ttf", size=53)
            medium = ImageFont.truetype("Economika/src/font/1.ttf", size=60)
            medium100 = ImageFont.truetype("Economika/src/font/1.ttf", size=75)
            idraw.text((730, 435), str(mem), fill=(253, 253, 253), font=light)  # все участники
            if len(nickname) > 14:
                nickname = f'{nickname[:13]}...'
            idraw.text((370, 510), str(f'{nickname}'), fill=(255, 255, 255), font=medium)  # ник
            if len(status) >= 17:
                status = f'{status[:15]}...'
            idraw.text((370, 570), str(status), fill=(253, 253, 253), font=light60)  # статус

            if voice < 10:
                idraw.text((1100, 520), str(voice), fill=(255, 255, 255), font=medium100)  # войс
            if 10 <= voice < 100:
                idraw.text((1080, 520), str(voice), fill=(255, 255, 255), font=medium100)  # войс
            if voice >= 100:
                idraw.text((1060, 520), str(voice), fill=(255, 255, 255), font=medium100)  # войс

            avatar = self.return_avatar(member)
            if str(avatar)[-4:] == '.png':
                url1 = requests.get(avatar, stream=True)
            else:
                url1 = requests.get(str(avatar)[:-10], stream=True)
            # =====================================
            avatar = Image.open(io.BytesIO(url1.content))
            avatar = avatar.resize((310, 310), Image.Resampling.LANCZOS)
            # =====================================
            mask = Image.new("L", avatar.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 310, 310), fill=255)

            banner = banner.resize((1920, 1080), Image.Resampling.LANCZOS)
            banner.paste(avatar, (180, 620), mask)

            banner.save('Economy/src/saved/banner1.png')
            with open('Economy/src/saved/banner1.png', 'rb') as f:
                banner = f.read()
            await guild.edit(banner=banner)
         #except Exception as e:
        #pass

    @tasks.loop(hours=2)
    async def reset_db(self):
        await self.client.wait_until_ready()
        find = self.guilds.find_one({"_id": 1084577336340512889})
        if int(time.time()) >= find['reset_banner_active_members']:
            self.collections.delete_many({})
            self.guilds.update_one(find, {"$inc": {"reset_banner_active_members": 60 * 60 * 2}}, True)

def setup(bot):
    bot.add_cog(Awarded(bot))
    print('Ког: "Награда" загрузился!')
