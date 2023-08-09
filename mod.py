from disnake.ext import commands
import time
from config import *
import disnake
from disnake import ButtonStyle
from disnake.ui import ActionRow
from typing import List
import asyncio


def return_avatar_url(member: disnake.Member):
    if member.display_avatar:
        return member.display_avatar.url
    elif member.avatar:
        return member.avatar.url
    else:
        return member.default_avatar.url

def group_list(
        array: (list, tuple, set),
        group_len: int = 2,
        space: int = 0,
        *,
        limit: int = None,
        add_lost: bool = True,
        reverse_groups: bool = True
) -> (list, tuple, set):
    length = len(array)
    group_len = int(group_len)
    space = int(space)
    if limit is None:
        limit = length

    if group_len == 0:
        raise ValueError('You can\'t group using Zero size group!')
    elif space < 0:
        raise ValueError('You can\'t use spaces which are less than Zero!')
    elif limit < 0:
        raise ValueError('You can\'t use limit which is less than Zero')
    elif limit == 0:
        return []
    elif length <= group_len:
        return [array]

    new_array = []

    def dry_appending(p, h):
        if group_len > 0:
            appending = array[p:h]
        else:
            if not position:
                appending = array[h:]
            else:
                appending = array[h:p]
            if reverse_groups:
                appending = appending[::-1]
        if appending:
            new_array.append(appending)

    k = 1 if group_len >= 0 else -1
    position = 0

    while abs(hold := position + group_len) <= length and limit:
        dry_appending(position, hold)
        position = hold + space * k

        if abs(position) >= length:
            position -= space * k
        limit -= 1
    else:
        if add_lost and limit:
            dry_appending(position, position + group_len)
    return new_array


class Pages_Standart(disnake.ui.View):
    def __init__(self, embeds: List[disnake.Embed], time_end):
        super().__init__(timeout=time_end)
        self.embeds = embeds
        self.embed_count = 0

        self.prev_page.disabled = True

        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Страница: {i + 1}/{len(self.embeds)}")

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count -= 1
        embed = self.embeds[self.embed_count]
        self.next_page.disabled = False
        if self.embed_count == 0:
            self.prev_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="❌", style=disnake.ButtonStyle.red)
    async def remove(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(view=None)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count += 1
        embed = self.embeds[self.embed_count]
        self.prev_page.disabled = False
        if self.embed_count == len(self.embeds) - 1:
            self.next_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)


class Pages_Max(disnake.ui.View):
    def __init__(self, embeds: List[disnake.Embed], time_end):
        super().__init__(timeout=time_end)
        self.embeds = embeds
        self.embed_count = 0

        self.first_page.disabled = True
        self.prev_page.disabled = True

        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Страница: {i + 1}/{len(self.embeds)}")

    @disnake.ui.button(emoji="⏪", style=disnake.ButtonStyle.blurple)
    async def first_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count = 0
        embed = self.embeds[self.embed_count]
        embed.set_footer(text=f"Страница: 1/{len(self.embeds)}")
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count -= 1
        embed = self.embeds[self.embed_count]
        self.next_page.disabled = False
        self.last_page.disabled = False
        if self.embed_count == 0:
            self.first_page.disabled = True
            self.prev_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="❌", style=disnake.ButtonStyle.red)
    async def remove(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(view=None)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count += 1
        embed = self.embeds[self.embed_count]
        self.first_page.disabled = False
        self.prev_page.disabled = False
        if self.embed_count == len(self.embeds) - 1:
            self.next_page.disabled = True
            self.last_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple)
    async def last_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count = len(self.embeds) - 1
        embed = self.embeds[self.embed_count]
        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.next_page.disabled = True
        self.last_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)


async def get_activate_button(len_arr, index):
    if len_arr >= index:
        return False
    else:
        return True


async def buy_role(r, money, msg, response, ctx, lshop, l_buys_roles):
    price = r["price"]
    member_ball = money.find_one({"member_id": response.author.id, "guild_id": response.author.guild.id})
    if member_ball['balance'] < price:
        emb = disnake.Embed(
            title='Ошибка Покупки',
            description=f'{ctx.author.mention}, ваш баланс **меньше** стоимости роли!'
        )
        emb.set_thumbnail(url=ctx.author.avatar.url)
        return await response.response.edit_message(embed=emb, delete_after=45, components=[])
    role = ctx.guild.get_role(r['_id'])
    if role in ctx.author.roles:
        emb = disnake.Embed(
            title='Ошибка Покупки',
            description=f'{ctx.author.mention}, у вас уже **есть** данная роль!'
        )
        emb.set_thumbnail(url=ctx.author.avatar.url)
        return await response.response.edit_message(embed=emb, delete_after=45, components=[])
    else:
        role_owner = ctx.guild.get_member(r['role_owner'])
        emb = disnake.Embed(
            title='Покупка Роли',
            description=f'{ctx.author.mention}, вы **купили** роль {role.mention} у {role_owner.mention} за `{price}`'
        )
        emb.set_thumbnail(url=ctx.author.avatar.url)
        await response.response.edit_message(embed=emb, components=[])
        await ctx.author.add_roles(role)
        money.update_one({"member_id": response.author.id, "guild_id": ctx.guild.id},
                               {"$inc": {"balance": -price}})
        money.update_one({"member_id": role_owner.id, "guild_id": ctx.guild.id},
                               {"$inc": {"balance": (price // 100) * 15}})
        lshop.update_one({"_id": role.id}, {"$inc": {"buy_raz": 1}})
        l_buys_roles.insert_one(
            {"member_id": response.author.id, "role_id": role.id, "time_end": int(time.time()) + 2592000})


async def Shop_Button(ctx: disnake.ApplicationCommandInteraction, pages, bot, timeout_time, group_okey, money,
                      group_len, lshop, l_buys_roles):
    row = disnake.ui.ActionRow()
    row.add_button(style=ButtonStyle.blurple, emoji='◀',
                   custom_id='bunt_page_1', disabled=True)
    row.add_button(style=ButtonStyle.red, emoji='🗑',
                   custom_id='bunt_page_3')
    row.add_button(style=ButtonStyle.blurple, emoji='▶',
                   custom_id='bunt_page_2', disabled=len(pages) <= 1)
    row.add_button(style=ButtonStyle.gray, label='Включить',
                   custom_id='on_buy_switch', disabled=False)
    el = 1
    on_buy = 0
    emb = pages[0]
    emb.set_footer(text='❌ Режим покупки выключен')
    emb.set_image(
        url="https://media.disnakeapp.net/attachments/967410375186350161/967863866954514432/polosochkA_1.png")
    msg = await ctx.edit_original_message(embed=emb, components=[row])
    while True:
        try:
            def check_a(i: disnake.MessageInteraction):
                if i.author.id == ctx.author.id and i.message.id == msg.id:
                    return True
                return False

            inter: disnake.MessageInteraction = await bot.wait_for("button_click", timeout=timeout_time,
                                                                        check=lambda i: check_a(i))
        except asyncio.TimeoutError:
            await ctx.edit_original_message(components=[])
            return
        if inter.component.custom_id == 'bunt_page_1':
            el -= 1
            if el > 1:
                dis_back = False
                dis_top = False
            else:
                dis_back = True
                dis_top = False
            row = disnake.ui.ActionRow()
            emb = pages[el - 1]
            emb.set_image(
                url="https://media.disnakeapp.net/attachments/967410375186350161/967863866954514432/polosochkA_1.png")
            if on_buy == 1:
                row.add_button(style=ButtonStyle.blurple, emoji='◀',
                               custom_id='bunt_page_1', disabled=dis_back)
                row.add_button(style=ButtonStyle.red, emoji='🗑',
                               custom_id='bunt_page_3')
                row.add_button(style=ButtonStyle.blurple, emoji='▶',
                               custom_id='bunt_page_2', disabled=dis_top)
                row.add_button(style=ButtonStyle.gray, label='Выключить',
                               custom_id='on_buy_switch', disabled=False)
                row_buy = ActionRow()
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 1}', custom_id='shop_1',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 1))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 2}', custom_id='shop_2',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 2))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 3}', custom_id='shop_3',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 3))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 4}', custom_id='shop_4',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 4))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 5}', custom_id='shop_5',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 5))
                emb.set_footer(text='✅ Режим покупки включен')
                await inter.response.edit_message(embed=emb, components=[row_buy, row])
            else:
                row.add_button(style=ButtonStyle.blurple, emoji='◀',
                               custom_id='bunt_page_1', disabled=dis_back)
                row.add_button(style=ButtonStyle.red, emoji='🗑',
                               custom_id='bunt_page_3')
                row.add_button(style=ButtonStyle.blurple, emoji='▶',
                               custom_id='bunt_page_2', disabled=dis_top)
                row.add_button(style=ButtonStyle.gray, label='Включить',
                               custom_id='on_buy_switch', disabled=False)
                emb.set_footer(text='❌ Режим покупки выключен')
                await inter.response.edit_message(embed=emb, components=[row])
        elif inter.component.custom_id == 'bunt_page_2':
            el += 1
            if len(pages) > el:
                dis_back = False
                dis_top = False
            else:
                dis_back = False
                dis_top = True
            row = disnake.ui.ActionRow()
            emb = pages[el - 1]
            emb.set_image(
                url="https://media.disnakeapp.net/attachments/967410375186350161/967863866954514432/polosochkA_1.png")
            if on_buy == 1:
                row.add_button(style=ButtonStyle.blurple, emoji='◀',
                               custom_id='bunt_page_1', disabled=dis_back)
                row.add_button(style=ButtonStyle.red, emoji='🗑',
                               custom_id='bunt_page_3')
                row.add_button(style=ButtonStyle.blurple, emoji='▶',
                               custom_id='bunt_page_2', disabled=dis_top)
                row.add_button(style=ButtonStyle.gray, label='Выключить',
                               custom_id='on_buy_switch', disabled=False)
                row_buy = ActionRow()
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 1}', custom_id='shop_1',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 1))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 2}', custom_id='shop_2',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 2))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 3}', custom_id='shop_3',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 3))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 4}', custom_id='shop_4',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 4))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 5}', custom_id='shop_5',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 5))
                emb.set_footer(text='✅ Режим покупки включен')
                await inter.response.edit_message(embed=emb, components=[row_buy, row])
            else:
                row.add_button(style=ButtonStyle.blurple, emoji='◀',
                               custom_id='bunt_page_1', disabled=dis_back)
                row.add_button(style=ButtonStyle.red, emoji='🗑',
                               custom_id='bunt_page_3')
                row.add_button(style=ButtonStyle.blurple, emoji='▶',
                               custom_id='bunt_page_2', disabled=dis_top)
                row.add_button(style=ButtonStyle.gray, label='Включить',
                               custom_id='on_buy_switch', disabled=False)
                emb.set_footer(text='❌ Режим покупки выключен')
                await inter.response.edit_message(embed=emb, components=[row])
        elif inter.component.custom_id == 'bunt_page_3':
            await msg.delete()
        elif inter.component.custom_id == 'shop_1':
            for index, r in enumerate(group_okey):
                if index + 1 == (5 * (el - 1)) + 1:
                    await buy_role(r, money, msg, inter, ctx, lshop, l_buys_roles)
                    break
        elif inter.component.custom_id == 'shop_2':
            for index, r in enumerate(group_okey):
                if index + 1 == (5 * (el - 1)) + 2:
                    await buy_role(r, money, msg, inter, ctx, lshop, l_buys_roles)
                    break
        elif inter.component.custom_id == 'shop_3':
            for index, r in enumerate(group_okey):
                if index + 1 == (5 * (el - 1)) + 3:
                    await buy_role(r, money, msg, inter, ctx, lshop, l_buys_roles)
                    break
        elif inter.component.custom_id == 'shop_4':
            for index, r in enumerate(group_okey):
                if index + 1 == (5 * (el - 1)) + 4:
                    await buy_role(r, money, msg, inter, ctx, lshop, l_buys_roles)
                    break
        elif inter.component.custom_id == 'shop_5':
            for index, r in enumerate(group_okey):
                if index + 1 == (5 * (el - 1)) + 5:
                    await buy_role(r, money, msg, inter, ctx, lshop, l_buys_roles)
                    break
        elif inter.component.custom_id == "on_buy_switch":
            if len(pages) > el and el > 1:
                dis_back = False
                dis_top = False
            elif len(pages) <= el and el <= 1:
                dis_back = True
                dis_top = True
            elif len(pages) <= el:
                dis_back = False
                dis_top = True
            elif el <= 1:
                dis_back = True
                dis_top = False
            else:
                dis_back = True
                dis_top = True
            emb = pages[el - 1]
            emb.set_image(
                url="https://media.disnakeapp.net/attachments/967410375186350161/967863866954514432/polosochkA_1.png")
            row = ActionRow()
            row.add_button(style=ButtonStyle.blurple, emoji='◀',
                           custom_id='bunt_page_1', disabled=dis_back)
            row.add_button(style=ButtonStyle.red, emoji='🗑',
                           custom_id='bunt_page_3')
            row.add_button(style=ButtonStyle.blurple, emoji='▶',
                           custom_id='bunt_page_2', disabled=dis_top)
            if on_buy == 0:
                on_buy = 1
                row.add_button(style=ButtonStyle.gray, label='Выключить',
                               custom_id='on_buy_switch', disabled=False)
                row_buy = ActionRow()
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 1}', custom_id='shop_1',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 1))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 2}', custom_id='shop_2',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 2))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 3}', custom_id='shop_3',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 3))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 4}', custom_id='shop_4',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 4))
                row_buy.add_button(style=ButtonStyle.green, label=f'{5 * (el - 1) + 5}', custom_id='shop_5',
                                   disabled=await get_activate_button(group_len, (5 * (el - 1)) + 5))
                emb.set_footer(text='✅ Режим покупки включен')
                await inter.response.edit_message(embed=emb, components=[row_buy, row])
            elif on_buy == 1:
                on_buy = 0
                row.add_button(style=ButtonStyle.gray, label='Включить',
                               custom_id='on_buy_switch', disabled=False)
                emb.set_footer(text='✅ Режим покупки выключен')
                await inter.response.edit_message(embed=emb, components=[row])


"""async def inventory_open(ctx, pages, bot, timeout_time, find, group_len, inventory):
    if len(pages) > 1:
        dis_top = False
    else:
        dis_top = True
    el = 1
    bunts_shop = [
        create_button(style=ButtonStyle.green, label=(
                                                             5 * (el - 1)) + 1, custom_id='inv_1',
                      disabled=await get_activate_button(group_len, (5 * (el - 1)) + 1)),
        create_button(style=ButtonStyle.green, label=(
                                                             5 * (el - 1)) + 2, custom_id='inv_2',
                      disabled=await get_activate_button(group_len, (5 * (el - 1)) + 2)),
        create_button(style=ButtonStyle.green, label=(
                                                             5 * (el - 1)) + 3, custom_id='inv_3',
                      disabled=await get_activate_button(group_len, (5 * (el - 1)) + 3)),
        create_button(style=ButtonStyle.green, label=(
                                                             5 * (el - 1)) + 4, custom_id='inv_4',
                      disabled=await get_activate_button(group_len, (5 * (el - 1)) + 4)),
        create_button(style=ButtonStyle.green, label=(
                                                             5 * (el - 1)) + 5, custom_id='inv_5',
                      disabled=await get_activate_button(group_len, (5 * (el - 1)) + 5))
    ]
    butns = [
        create_button(style=ButtonStyle.blue, emoji='◀',
                      custom_id='inv_page_1', disabled=True),
        create_button(style=ButtonStyle.red, emoji='🗑',
                      custom_id='inv_page_2'),
        create_button(style=ButtonStyle.blue, emoji='▶',
                      custom_id='inv_page_3', disabled=dis_top)
    ]
    row_shop = create_actionrow(*bunts_shop)
    row = create_actionrow(*butns)
    emb = pages[0]
    emb.set_image(
        url="https://media.disnakeapp.net/attachments/967410375186350161/967863866954514432/polosochkA_1.png")
    msg = await ctx.send(embed=emb, components=[row_shop, row])
    while True:
        try:
            response: ComponentContext = await wait_for_component(bot, components=[row_shop, row],
                                                                  check=lambda i: i.author == ctx.author,
                                                                  timeout=timeout_time, messages=msg)
        except asyncio.TimeoutError:
            await msg.edit(components=[], delete_after=20)
        if response.custom_id == 'inv_page_1':
            await response.edit_origin()
            el -= 1
            if el > 1:
                dis_back = False
                dis_top = False
            else:
                dis_back = True
                dis_top = False
            butns = [
                create_button(style=ButtonStyle.blue, emoji='◀',
                              custom_id='inv_page_1', disabled=dis_back),
                create_button(style=ButtonStyle.red, emoji='🗑',
                              custom_id='inv_page_2'),
                create_button(style=ButtonStyle.blue, emoji='▶',
                              custom_id='inv_page_3', disabled=dis_top)
            ]
            bunts_shop = [
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 1, custom_id='inv_1',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 1)),
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 2, custom_id='inv_2',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 2)),
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 3, custom_id='inv_3',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 3)),
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 4, custom_id='inv_4',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 4)),
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 5, custom_id='inv_5',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 5))
            ]
            row_shop = create_actionrow(*bunts_shop)
            row = create_actionrow(*butns)
            emb = pages[el - 1]
            emb.set_image(
                url="https://media.disnakeapp.net/attachments/967410375186350161/967863866954514432/polosochkA_1.png")
            await msg.edit(embed=emb, components=[row_shop, row])
        elif response.custom_id == 'inv_page_3':
            await response.edit_origin()
            el += 1
            if len(pages) > el:
                dis_back = False
                dis_top = False
            else:
                dis_back = False
                dis_top = True
            butns = [
                create_button(style=ButtonStyle.blue, emoji='◀',
                              custom_id='inv_page_1', disabled=dis_back),
                create_button(style=ButtonStyle.red, emoji='🗑',
                              custom_id='inv_page_2'),
                create_button(style=ButtonStyle.blue, emoji='▶',
                              custom_id='inv_page_3', disabled=dis_top)
            ]
            bunts_shop = [
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 1, custom_id='inv_1',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 1)),
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 2, custom_id='inv_2',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 2)),
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 3, custom_id='inv_3',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 3)),
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 4, custom_id='inv_4',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 4)),
                create_button(style=ButtonStyle.green, label=(
                                                                     5 * (el - 1)) + 5, custom_id='inv_5',
                              disabled=await get_activate_button(group_len, (5 * (el - 1)) + 5))
            ]
            row_shop = create_actionrow(*bunts_shop)
            row = create_actionrow(*butns)
            emb = pages[el - 1]
            emb.set_image(
                url="https://media.disnakeapp.net/attachments/967410375186350161/967863866954514432/polosochkA_1.png")
            await msg.edit(embed=emb, components=[row_shop, row])
        elif response.custom_id == 'inv_page_2':
            await msg.delete()
        elif response.custom_id == 'inv_1':
            await response.edit_origin()
            for index, r in enumerate(find):
                if index + 1 == (5 * (el - 1)) + 1:
                    await inventory.delete_one(r)
                    role = ctx.guild.get_role(r['role_id'])
                    await ctx.author.add_roles(role)
                    emb = disnake.Embed(
                        title='Инвентарь',
                        description=f'{ctx.author.mention}, вы **достали** роль {role.mention} из инвенторя!'
                    )
                    emb.set_thumbnail(url=ctx.author.avatar_url)
                    await msg.edit(embed=emb, components=[])
                    break
        elif response.custom_id == 'inv_2':
            await response.edit_origin()
            for index, r in enumerate(find):
                if index + 1 == (5 * (el - 1)) + 2:
                    await inventory.delete_one(r)
                    role = ctx.guild.get_role(r['role_id'])
                    await ctx.author.add_roles(role)
                    emb = disnake.Embed(
                        title='Инвентарь',
                        description=f'{ctx.author.mention}, вы **достали** роль {role.mention} из инвенторя!'
                    )
                    emb.set_thumbnail(url=ctx.author.avatar_url)
                    await msg.edit(embed=emb, components=[])
                    break
        elif response.custom_id == 'inv_3':
            await response.edit_origin()
            for index, r in enumerate(find):
                if index + 1 == (5 * (el - 1)) + 3:
                    await inventory.delete_one(r)
                    role = ctx.guild.get_role(r['role_id'])
                    await ctx.author.add_roles(role)
                    emb = disnake.Embed(
                        title='Инвентарь',
                        description=f'{ctx.author.mention}, вы **достали** роль {role.mention} из инвенторя!'
                    )
                    emb.set_thumbnail(url=ctx.author.avatar_url)
                    await msg.edit(embed=emb, components=[])
                    break
        elif response.custom_id == 'inv_4':
            await response.edit_origin()
            for index, r in enumerate(find):
                if index + 1 == (5 * (el - 1)) + 4:
                    await inventory.delete_one(r)
                    role = ctx.guild.get_role(r['role_id'])
                    await ctx.author.add_roles(role)
                    emb = disnake.Embed(
                        title='Инвентарь',
                        description=f'{ctx.author.mention}, вы **достали** роль {role.mention} из инвенторя!'
                    )
                    emb.set_thumbnail(url=ctx.author.avatar_url)
                    await msg.edit(embed=emb, components=[])
                    break
        elif response.custom_id == 'inv_5':
            await response.edit_origin()
            for index, r in enumerate(find):
                if index + 1 == (5 * (el - 1)) + 5:
                    await inventory.delete_one(r)
                    role = ctx.guild.get_role(r['role_id'])
                    await ctx.author.add_roles(role)
                    emb = disnake.Embed(
                        title='Инвентарь',
                        description=f'{ctx.author.mention}, вы **достали** роль {role.mention} из инвентаря!'
                    )
                    emb.set_thumbnail(url=ctx.author.avatar_url)
                    await msg.edit(embed=emb, components=[])
                    break"""
