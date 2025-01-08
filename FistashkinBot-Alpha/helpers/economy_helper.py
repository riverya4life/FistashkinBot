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

        await db.update_member(
            "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
            [amount, inter.author.id, inter.guild.id],
        )

        is_victory = not random.choice(range(0, 4))
        win_amount = amount * 2

        if is_victory:
            description = (
                f"**Ты сделал {body_part} и отправил своего соперника в нокаут! Так держать, "
                f"ты получаешь {win_amount} {self.economy.CURRENCY_NAME} на свой баланс!**"
            )
            color = self.color.GREEN
            image_url = random.choice(self.rp.FIGHT_CLUB_VICTORY_IMAGES)

            await db.update_member(
                "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                [win_amount, inter.author.id, inter.guild.id],
            )
        else:
            description = (
                f"Ты сделал **{body_part}**, но противник защитился и сделал удар. "
                f"Ты остался без 5 зубов и **{amount} {self.economy.CURRENCY_NAME}**."
            )
            color = self.color.RED
            image_url = random.choice(self.rp.FIGHT_CLUB_DEFEAT_IMAGES)

        embed = (
            disnake.Embed(description=description, color=color)
            .set_image(url=image_url)
            .set_author(name="Бойцовский клуб", icon_url=inter.author.display_avatar.url)
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
                    description="❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        self.stop()

        await inter.response.defer(ephemeral=True)

        bet_amount = int(inter.message.embeds[0].fields[0].value)

        await db.update_member(
            "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
            [bet_amount, inter.author.id, inter.guild.id],
        )

        is_win = not random.choice(range(0, 4))

        if is_win:
            win_amount = bet_amount * self.economy.MULTIPLIER
            await db.update_member(
                "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                [win_amount, inter.author.id, inter.guild.id],
            )
            title = "Успех!"
            description = f"**Ты успешно выиграл {win_amount} {self.economy.CURRENCY_NAME}!**"
            color = self.color.GREEN
        else:
            title = "Промах!"
            description = f"Ты проиграл **{bet_amount} {self.economy.CURRENCY_NAME}!**"
            color = self.color.RED

        embed = (
            disnake.Embed(title=title, description=description, color=color)
            .set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/272/272525.png")
            .set_author(name="Монетка", icon_url=inter.author.display_avatar.url)
        )

        await inter.edit_original_message(embed=embed, view=None)


    @disnake.ui.button(label="Решка", emoji="🪙", style=disnake.ButtonStyle.primary)
    async def reshka_button_callback(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description="❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        self.stop()

        await inter.response.defer(ephemeral=True)

        bet_amount = int(inter.message.embeds[0].fields[0].value)
        
        await db.update_member(
            "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
            [bet_amount, inter.author.id, inter.guild.id],
        )

        is_win = not random.choice(range(0, 4))

        if is_win:
            win_amount = bet_amount * self.economy.MULTIPLIER
            await db.update_member(
                "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                [win_amount, inter.author.id, inter.guild.id],
            )
            title = "Успех!"
            description = f"**Ты успешно выиграл {win_amount} {self.economy.CURRENCY_NAME}!**"
            color = self.color.GREEN
        else:
            title = "Промах!"
            description = f"Ты проиграл **{bet_amount} {self.economy.CURRENCY_NAME}!**"
            color = self.color.RED

        embed = (
            disnake.Embed(title=title, description=description, color=color)
            .set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/272/272525.png")
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
        self.enum = enums.Enum()
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
                    description="❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        self.stop()

        await inter.response.defer(ephemeral=False)

        bet_amount = 100
        await db.update_member(
            "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
            [bet_amount, inter.author.id, inter.guild.id],
        )

        prize_weights = [1.0, 0.1, 0.3]
        prize_values = [
            random.randint(100, 150),
            random.randint(500, 1000),
            random.randint(200, 250),
        ]
        prize = random.choices(prize_values, weights=prize_weights, k=1)[0]

        formatted_prize = self.enum.format_large_number(prize)

        await db.update_member(
            "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
            [prize, inter.author.id, inter.guild.id],
        )

        embed = (
            disnake.Embed(
                title="Кейс успешно открыт!",
                description=f"**Ваш выигрыш составляет {formatted_prize} {self.economy.CURRENCY_NAME}**",
                color=self.color.GREEN,
            )
            .set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/10348/10348893.png")
            .set_author(name="Кейсы", icon_url=inter.author.display_avatar.url)
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
                    description="❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        self.stop()
        await inter.response.defer(ephemeral=False)

        reels = self.otheremojis.REELS
        slot_lines = [[random.choice(reels) for _ in range(3)] for _ in range(3)]

        slot_display = (
            "┏━━━━━━━━━━┓\n"
            f"**| `{slot_lines[0][0]} | {slot_lines[0][1]} | {slot_lines[0][2]}` |**\n"
            f"**>**``{slot_lines[1][0]} | {slot_lines[1][1]} | {slot_lines[1][2]}``**<**\n"
            f"**| `{slot_lines[2][0]} | {slot_lines[2][1]} | {slot_lines[2][2]}` |**\n"
            "┗━━━━━━━━━━┛\n\n"
        )

        slot_amount = self.enum.format_large_number(self.amount)
        description = [
            f"Сумма, внесенная в лот Вами составила: `{slot_amount}` {self.economy.CURRENCY_NAME}\n\n",
            f"{inter.author.mention}, внеся определенную сумму и запустив «Слот-машину», Вы наблюдаете перед собой следующую выпавшую Вам комбинацию:\n\n",
            f"{slot_display}",
        ]

        win_multiplier = 0
        if slot_lines[1][0] == slot_lines[1][1] == slot_lines[1][2]:
            win_multiplier = 5
            description.append(
                f"🥳 **Поздравляю!** Вы сорвали джекпот и преумножили вашу ставку в `5` раз!** "
                f"(Ваш выигрыш составляет `{self.enum.format_large_number(self.amount * 5)}` {self.economy.CURRENCY_NAME})"
            )
        elif (
            slot_lines[1][0] == slot_lines[1][1]
            or slot_lines[1][1] == slot_lines[1][2]
            or slot_lines[1][0] == slot_lines[1][2]
        ):
            win_multiplier = 2
            description.append(
                f"🥳 **Поздравляю! Вы выиграли и преумножили вашу ставку в `2` раза!** "
                f"(Ваш выигрыш составляет `{self.enum.format_large_number(self.amount * 2)}` {self.economy.CURRENCY_NAME})"
            )
        else:
            description.append(
                f"😢 **Увы, но данная комбинация оказалась проигрышной!** "
                f"`{slot_amount}` {self.economy.CURRENCY_NAME} были списаны с личного счёта!"
            )

        balance_update_amount = self.amount * win_multiplier if win_multiplier else -self.amount
        await db.update_member(
            "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
            [balance_update_amount, inter.author.id, inter.guild.id],
        )

        embed = disnake.Embed(description="".join(description), color=self.color.MAIN)
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
