import disnake
import datetime
import random

from disnake.ext import commands
from utils import enums, main, CustomError, constant

from classes import database as db


class EconomyHelper:
    def __init__(self):
        self.color = enums.Color()
        self.rp = constant.RolePlay()
        self.economy = main.EconomySystem()
        self.enum = enums.Enum()

    async def hit(
        self, inter: disnake.ApplicationCommandInteraction, body_part: str, amount: int
    ):
        await inter.response.defer(ephemeral=True)
        data = await db.get_data(inter.author)
        if amount > data["balance"]:
            raise CustomError(
                f"❌ У вас недостаточно **{self.economy.CURRENCY_NAME}** для игры!"
            )
        else:
            await db.update_member(
                "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
                [amount, inter.author.id, inter.guild.id],
            )
            if not random.choice(range(0, 4)):
                await db.update_member(
                    "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                    [amount * 2, inter.author.id, inter.guild.id],
                )
                embed = (
                    disnake.Embed(
                        description=f"**Ты сделал {body_part} и отправил своего соперника в нокаут! Так держать, твой ты получаешь {amount * 2} {self.CURRENCY_NAME} на свой баланс!**",
                        color=Color.GREEN,
                    )
                    .set_image(url=random.choice(self.rp.FIGHT_CLUB_VICTORY_IMAGES))
                    .set_author(
                        name="Бойцовский клуб", icon_url=inter.author.display_avatar.url
                    )
                )
                await inter.edit_original_message(embed=embed, view=None)
            else:
                embed = (
                    disnake.Embed(
                        description=f"Ты сделал **{body_part}**, но противник защитился и сделал удар. Ты остался без 5 зубов и **{amount} {self.CURRENCY_NAME}**.",
                        color=Color.RED,
                    )
                    .set_image(url=random.choice(self.rp.FIGHT_CLUB_DEFEAT_IMAGES))
                    .set_author(
                        name="Бойцовский клуб", icon_url=inter.author.display_avatar.url
                    )
                )
                await inter.edit_original_message(embed=embed, view=None)


class CoinButtons(disnake.ui.View):
    message: disnake.Message

    def __init__(self, inter):
        self.inter = inter
        self.economy = main.EconomySystem()
        self.color = enums.Color()
        super().__init__(timeout=120.0)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=None)
        self.stop()

    @disnake.ui.button(label="Орёл", emoji="🪙", style=disnake.ButtonStyle.primary)
    async def orel_button_callback(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        self.stop()
        data = await db.get_data(inter.author)
        await db.update_member(
            "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
            [
                int(inter.message.embeds[0].fields[0].value),
                inter.author.id,
                inter.guild.id,
            ],
        )
        if not random.choice(range(0, 4)):
            await inter.response.defer(ephemeral=True)
            await db.update_member(
                "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                [
                    int(inter.message.embeds[0].fields[0].value)
                    * self.economy.MULTIPLIER,
                    inter.author.id,
                    inter.guild.id,
                ],
            )
            embed = (
                disnake.Embed(
                    title="Успех!",
                    description=f"**Ты успешно выиграл {str(round(int(inter.message.embeds[0].fields[0].value) * self.economy.MULTIPLIER))} {self.economy.CURRENCY_NAME}!**",
                    color=self.color.GREEN,
                )
                .set_thumbnail(
                    url="https://cdn-icons-png.flaticon.com/512/272/272525.png"
                )
                .set_author(name="Монетка", icon_url=inter.author.display_avatar.url)
            )
            await inter.edit_original_message(embed=embed, view=None)
        else:
            await inter.response.defer(ephemeral=True)
            embed = (
                disnake.Embed(
                    title="Промах!",
                    description=f"Ты проиграл **{inter.message.embeds[0].fields[0].value} {self.economy.CURRENCY_NAME}!**",
                    color=self.color.RED,
                )
                .set_thumbnail(
                    url="https://cdn-icons-png.flaticon.com/512/272/272525.png"
                )
                .set_author(name="Монетка", icon_url=inter.author.display_avatar.url)
            )
            await inter.edit_original_message(embed=embed, view=None)

    @disnake.ui.button(label="Решка", emoji="🪙", style=disnake.ButtonStyle.primary)
    async def reshka_button_callback(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        self.stop()
        data = await db.get_data(inter.author)
        await db.update_member(
            "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
            [
                int(inter.message.embeds[0].fields[0].value),
                inter.author.id,
                inter.guild.id,
            ],
        )
        if not random.choice(range(0, 4)):
            await inter.response.defer(ephemeral=True)
            await db.update_member(
                "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                [
                    int(inter.message.embeds[0].fields[0].value)
                    * self.economy.MULTIPLIER,
                    inter.author.id,
                    inter.guild.id,
                ],
            )
            embed = (
                disnake.Embed(
                    title="Успех!",
                    description=f"**Ты успешно выиграл {str(round(int(inter.message.embeds[0].fields[0].value) * self.economy.MULTIPLIER))} {self.economy.CURRENCY_NAME}!**",
                    color=self.color.GREEN,
                )
                .set_thumbnail(
                    url="https://cdn-icons-png.flaticon.com/512/272/272525.png"
                )
                .set_author(name="Монетка", icon_url=inter.author.display_avatar.url)
            )
            await inter.edit_original_message(embed=embed, view=None)
        else:
            await inter.response.defer(ephemeral=True)
            embed = (
                disnake.Embed(
                    title="Промах!",
                    description=f"Ты проиграл **{inter.message.embeds[0].fields[0].value} {self.economy.CURRENCY_NAME}!**",
                    color=self.color.RED,
                )
                .set_thumbnail(
                    url="https://cdn-icons-png.flaticon.com/512/272/272525.png"
                )
                .set_author(name="Монетка", icon_url=inter.author.display_avatar.url)
            )
            await inter.edit_original_message(embed=embed, view=None)


class FightButtons(disnake.ui.View):
    message: disnake.Message

    def __init__(self, inter):
        self.inter = inter
        self.economy = main.EconomySystem()
        self.hit = EconomyHelper()
        self.color = enums.Color()
        super().__init__(timeout=120.0)

    async def on_timeout(self, inter):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=None)
        self.stop()

    @disnake.ui.button(
        label="Удар в ноги",
        emoji="🦵",
        custom_id="legs_hit",
        style=disnake.ButtonStyle.primary,
    )
    async def legs_button_callback(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        self.stop()
        return await self.hit.hit(
            inter,
            body_part="удар в ноги",
            amount=int(inter.message.embeds[0].fields[0].value),
        )

    @disnake.ui.button(
        label="Удар в живот",
        emoji="👊",
        custom_id="torso_hit",
        style=disnake.ButtonStyle.primary,
    )
    async def torso_button_callback(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        self.stop()
        return await self.hit.hit(
            inter,
            body_part="удар в живот",
            amount=int(inter.message.embeds[0].fields[0].value),
        )

    @disnake.ui.button(
        label="Удар в голову",
        emoji="🤕",
        custom_id="head_hit",
        style=disnake.ButtonStyle.primary,
    )
    async def head_button_callback(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        self.stop()
        return await self.hit.hit(
            inter,
            body_part="удар в голову",
            amount=int(inter.message.embeds[0].fields[0].value),
        )


class CaseButtons(disnake.ui.View):
    message: disnake.Message

    def __init__(self, inter):
        self.inter = inter
        self.economy = main.EconomySystem()
        self.color = enums.Color()
        super().__init__(timeout=120.0)

    async def on_timeout(self, inter):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=None)
        self.stop()

    @disnake.ui.button(
        label=f"Открыть кейс (100 FC)",
        emoji="🍪",
        custom_id="open_case",
        style=disnake.ButtonStyle.success,
    )
    async def open_case_button_callback(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        self.stop()
        await inter.response.defer(ephemeral=False)
        data = await db.get_data(inter.author)
        await db.update_member(
            "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
            [100, inter.author.id, inter.guild.id],
        )
        rnd_int_def = random.randint(100, 500)
        rnd_int_max = random.randint(500, 1000)
        rnd_int_min = random.randint(100, 200)
        case = [1.0, 0.1, 0.3]
        random_case = random.choices([rnd_int_def, rnd_int_max, rnd_int_min], case)
        prize = self.enum.format_large_number(random_case)
        embed = (
            disnake.Embed(
                title="Кейс успешно открыт!",
                description=f"**Ваш выигрыш составляет {prize} {self.economy.CURRENCY_NAME}**",
                color=self.color.GREEN,
            )
            .set_thumbnail(
                url="https://cdn-icons-png.flaticon.com/512/10348/10348893.png"
            )
            .set_author(name="Кейсы", icon_url=inter.author.display_avatar.url)
        )
        await db.update_member(
            "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
            [random_case, inter.author.id, inter.guild.id],
        )
        await inter.edit_original_message(embed=embed, view=None)


class SlotMachineButtons(disnake.ui.View):
    message: disnake.Message

    def __init__(self, inter, amount: int):
        super().__init__(timeout=120.0)
        self.inter = inter
        self.amount = amount
        self.economy = main.EconomySystem()
        self.color = enums.Color()
        self.enum = enums.Enum()
        self.otheremojis = constant.OtherEmojis()

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True
        await self.message.edit(view=self)
        self.stop()

    @disnake.ui.button(label="Прокрутить", style=disnake.ButtonStyle.green, emoji="🕹️")
    async def add_role(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        self.stop()
        await inter.response.defer(ephemeral=False)
        reels = self.otheremojis.REELS
        random.shuffle(reels)

        result = []
        for _ in range(3):
            symbol = random.choice(reels)
            result.append(symbol)
        random.shuffle(reels)
        ligne1 = []
        for _ in range(3):
            symbol = random.choice(reels)
            ligne1.append(symbol)
        ligne2 = []
        for _ in range(3):
            symbol = random.choice(reels)
            ligne2.append(symbol)

        slotmachine = [
            f"┏━━━━━━━━━━┓\n"
            f"**| `{ligne1[0]} | {ligne1[1]} | {ligne1[2]}` |**\n"
            f"**>**``{result[0]} | {result[1]} | {result[2]}``**<**\n"
            f"**| `{ligne2[0]} | {ligne2[1]} | {ligne2[2]}` |**\n"
            f"┗━━━━━━━━━━┛\n\n"
        ]

        final = "".join(slotmachine)
        slot_amount = self.enum.format_large_number(self.amount)
        description = [
            f"Сумма, внесенная в лот Вами составила: `{slot_amount}` {self.economy.CURRENCY_NAME}\n\n",
            f"{inter.author.mention}, внеся определенную сумму и запустив «Слот-машину», Вы наблюдаете перед собой следующую выпавшую Вам комбинацию:\n\n",
            f"{final}",
        ]

        if result[0] == result[1] == result[2]:
            slot_final = self.enum.format_large_number(self.amount * 5)
            description.append(
                f"🥳 Поздравляю! Вы сорвали джекпот и преумножили вашу ставку в `5` раз! (Ваш выигрыш составляет `{slot_final}` {self.economy.CURRENCY_NAME})"
            )
            await db.update_member(
                "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                [
                    self.amount * 5,
                    inter.author.id,
                    inter.guild.id,
                ],
            )

        elif (
            (result[0] == result[1])
            or (result[1] == result[2])
            or (result[0] == result[2])
        ):
            slot_final = self.enum.format_large_number(self.amount * 2)
            description.append(
                f"🥳 Поздравляю! Вы выиграли и преумножили вашу ставку в `2` раза! (Ваш выигрыш составляет `{slot_final}` {self.economy.CURRENCY_NAME})"
            )
            await db.update_member(
                "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                [
                    self.amount * 2,
                    inter.author.id,
                    inter.guild.id,
                ],
            )

        else:
            slot_final = self.enum.format_large_number(self.amount)
            description.append(
                f"😢 Увы, но данная комбинация оказалась проигрышной! `{slot_final}` {self.economy.CURRENCY_NAME} были списаны с личного счёта!"
            )
            await db.update_member(
                "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
                [
                    self.amount,
                    inter.author.id,
                    inter.guild.id,
                ],
            )

        embed = disnake.Embed(description=f"".join(description), color=self.color.MAIN)
        embed.set_author(
            name="Азартная игра «Слот-машина»", icon_url=inter.author.display_avatar.url
        )
        await inter.edit_original_message(embed=embed, view=None)

    @disnake.ui.button(label="Отменить", style=disnake.ButtonStyle.red, emoji="❌")
    async def delete_role(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        self.stop()
        await self.message.delete()
