import disnake
import random
import datetime

from disnake.ext import commands
from utils import (
    main,
    enums,
    constant,
    paginator,
    discord_card,
    rating,
    CustomError,
)
from helpers import (
    CoinButtons,
    FightButtons,
    CaseButtons,
    SlotMachineButtons,
)
from classes.cooldown import default_cooldown
from classes import database as db


class Economy(commands.Cog, name="🍪 Экономика"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.main = main.MainSettings()
        self.economy = main.EconomySystem()
        self.color = enums.Color()
        self.otheremojis = constant.OtherEmojis()
        self.profile = constant.ProfileEmojis()
        self.enum = enums.Enum()
        self.rating = rating.Rating()

    @commands.slash_command(
        name=disnake.Localized("balance", key="USER_BALANCE_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows the balance of the mentioned user or the user who called the command.",
            key="USER_BALANCE_COMMAND_DESCRIPTION",
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def user_balance(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            lambda inter: inter.author,
            name=disnake.Localized("user", key="TARGET_USER_NAME"),
            description=disnake.Localized(
                "Select a user.", key="TARGET_USER_DESCRIPTION"
            ),
        ),
    ):
        if member.bot:
            raise CustomError("❌ Ты не можешь взаимодействовать с ботами!")

        await inter.response.defer(ephemeral=False)

        if not member:
            member = inter.author

        data = await db.get_data(member)
        balance = self.enum.format_large_number(data["balance"])
        level = self.enum.format_large_number(data["level"])
        xp = self.enum.format_large_number(data["xp"])
        total_xp = self.enum.format_large_number(data["total_xp"])
        xp_to_lvl = self.enum.format_large_number(
            5 * (data["level"] ** 2) + 50 * data["level"] + 100
        )

        user_rank_position, members_rank_len = await self.rating.rating_rank(
            member=member
        )
        (
            user_balance_position,
            members_balance_len,
        ) = await self.rating.rating_balance(member=member)
        bonuses = [
            f"- Ежедневный - **каждые 12 часов.**",
            f"{'- **x2** множитель опыта и баланса.' if self.economy.MULTIPLIER == 2.0 else ('- **x4** множитель опыта и баланса.' if self.economy.MULTIPLIER == 4.0 else ('- **x8** множитель опыта и баланса.' if self.economy.MULTIPLIER == 8.0 else ''))}",
        ]
        embed = (
            disnake.Embed(color=self.color.MAIN)
            .add_field(
                name="💰 Баланс:",
                value=f"**```{balance} {self.economy.CURRENCY_NAME}```**",
                inline=True,
            )
            .add_field(
                name=f"🧸 Рейтинг {self.economy.CURRENCY_NAME}:",
                value=f"**```# {user_balance_position}/{members_balance_len}```**",
                inline=True,
            )
            .add_field(
                name=f"🎁 Бонусы:",
                value="\n".join(bonuses),
                inline=False,
            )
            .set_author(
                name=f"💳 Отчётность о балансе {member}",
                icon_url=member.display_avatar.url,
            )
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("rank", key="USER_RANK_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows the rank of the mentioned user or the user who called the command.",
            key="USER_RANK_COMMAND_DESCRIPTION",
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def user_rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            lambda inter: inter.author,
            name=disnake.Localized("user", key="TARGET_USER_NAME"),
            description=disnake.Localized(
                "Select a user.", key="TARGET_USER_DESCRIPTION"
            ),
        ),
    ):
        if member.bot:
            raise CustomError("❌ Ты не можешь взаимодействовать с ботами!")
        else:
            await inter.response.defer(ephemeral=False)

            if not member:
                member = inter.author

            rank_rating_pos = await self.rating.rating_rank(member=member)
            user_rank_position = rank_rating_pos[0]
            data = await db.get_data(member)
            user = await self.bot.fetch_user(member.id)

            levelcard = (
                discord_card.LevelCard()
                .avatar == member.display_avatar.url
                .path == (
                    user.banner.url
                    if user.banner
                    else "https://raw.githubusercontent.com/mario1842/mariocard/main/bg.png"
                )
                .name == member
                .xp == data["xp"]
                .required_xp == (
                    5 * (data["level"] ** 2) + 50 * data["level"] + 100
                )
                .level == data["level"]
                .rank_pos == user_rank_position
                .is_rounded == True
            )
            await inter.edit_original_message(file=await levelcard.create())

    @commands.slash_command(
        name=disnake.Localized("pay", key="PAY_COMMAND_NAME"),
        description=disnake.Localized(
            "Transfers money to the user.", key="PAY_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def pay_cash(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            name=disnake.Localized("user", key="TARGET_USER_NAME"),
            description=disnake.Localized(
                "Select a user.", key="TARGET_USER_DESCRIPTION"
            ),
        ),
        amount: int = commands.Param(
            name=disnake.Localized("amount", key="PAY_AMOUNT_NAME"),
            description=disnake.Localized(
                "The amount you want to transfer to the user.",
                key="PAY_AMOUNT_DESCRIPTION",
            ),
        ),
    ):
        data = await db.get_data(inter.author)
        if amount is None:
            raise CustomError(
                f"❌ Укажите сумму **{self.economy.CURRENCY_NAME}**, которую желаете начислить на счет участника!"
            )

        elif member == inter.author:
            raise CustomError(
                f"❌ Ты не можешь **перевести {self.economy.CURRENCY_NAME}** самому себе!"
            )

        elif amount > data["balance"]:
            raise CustomError(
                f"❌ У вас недостаточно **{self.economy.CURRENCY_NAME}** для перевода!"
            )

        elif amount <= 0:
            raise CustomError(
                f"❌ Укажите сумму больше **0 {self.economy.CURRENCY_NAME}**!"
            )

        elif member.bot:
            raise CustomError("❌ Ты не можешь взаимодействовать с ботами!")
        else:
            await inter.response.defer(ephemeral=False)
            await db.update_member(
                "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
                [amount, inter.author.id, inter.guild.id],
            )
            await db.update_member(
                "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                [amount, member.id, inter.guild.id],
            )
            pay_amount = self.enum.format_large_number(amount)
            comm_amount = self.enum.format_large_number(amount)
            commission = 0
            if amount > 100:
                commission = amount * (self.economy.COMMISSION / 100)
                amount -= commission
                comm_amount = self.enum.format_large_number(amount)

            description = [
                f"[`💱`] **Перевод успешно выполнен!**\n\n",
                # f"=======================================\n",
                f"[`📉`] **Отправитель:** {inter.author.mention}\n",
                f"[`🔴`] **Списано:** - `{pay_amount}` {self.economy.CURRENCY_NAME}\n",
                f"[`📈`] **Получатель:** {member.mention}\n",
                f"[`🟢`] **Получено:** + `{comm_amount}` {self.economy.CURRENCY_NAME}\n",
                f"=======================================\n",
                f"[`⚠️`] **Комиссия:** `{commission}` (**{self.economy.COMMISSION}%**)\n"
                f"[`📃`] **Итого переведено:** `{comm_amount}` {self.economy.CURRENCY_NAME}",
            ]
            embed = (
                disnake.Embed(
                    description=f"".join(description),
                    color=self.color.MAIN,
                )
                .set_author(
                    name="💳 Отчётность о банковской операции",
                    icon_url=member.display_avatar.url,
                )
            )
            await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("leaderboard", key="LEADERBOARD_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows the top ranking of users for something.",
            key="LEADERBOARD_COMMAND_DESCRIPTION",
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        ...

    @leaderboard.sub_command(
        name=disnake.Localized("balance", key="LEADERBOARD_BALANCE_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows the top rating of users by balance.",
            key="LEADERBOARD_BALANCE_COMMAND_DESCRIPTION",
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def server_leaderboard_balance(
        self, inter: disnake.ApplicationCommandInteraction
    ):
        await inter.response.defer(ephemeral=False)

        data = await db.get_data(
            member=inter.guild.id, all_data=True, filters="ORDER BY balance DESC"
        )
        embeds = []
        counter = 0
        current_embed = (
            disnake.Embed(
                description=f"[`👑`] **Список лидеров по балансу на сервере **`{inter.guild.name}`**!**",
                color=self.color.MAIN,
            )
            .set_author(
                name=f"👑 Топ лидеров сервера",
                icon_url=inter.guild.icon.url if inter.guild.icon else None,
            )
            .set_thumbnail(
                url=inter.guild.icon.url if inter.guild.icon else None
            )
        )

        for row in data:
            user = self.bot.get_user(row["member_id"])
            member = inter.guild.get_member(row["member_id"])
            if member is not None and not member.bot:
                if counter != 0 and counter % 5 == 0:
                    embeds.append(current_embed)

                counter += 1
                balance = self.enum.format_large_number(row["balance"])
                current_embed.add_field(
                    name=f"#{counter} | `{self.bot.get_user(row['member_id'])}`",
                    value=f"**Баланс:** {balance} {self.economy.CURRENCY_NAME}",
                    inline=False,
                )

        if counter % 5 != 0:
            embeds.append(current_embed)

        view = paginator.Paginator(inter, embeds=embeds)
        message = await inter.edit_original_message(embed=embeds[0], view=view)
        view.message = message

    @leaderboard.sub_command(
        name=disnake.Localized("rank", key="LEADERBOARD_RANK_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows the top ranking of users by experience.",
            key="LEADERBOARD_RANK_COMMAND_DESCRIPTION",
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def server_leaderboard_level(
        self, inter: disnake.ApplicationCommandInteraction
    ):
        await inter.response.defer(ephemeral=False)

        data = await db.get_data(
            inter.guild.id, all_data=True, filters="ORDER BY level DESC, xp DESC"
        )
        embeds = []
        counter = 0
        current_embed = (
            disnake.Embed(
                description=f"[`👑`] **Список лидеров по опыту на сервере **`{inter.guild.name}`**!**",
                color=self.color.MAIN,
            )
            .set_author(
                name=f"👑 Топ лидеров сервера",
                icon_url=inter.guild.icon.url if inter.guild.icon else None,
            )
            .set_thumbnail(
                url=inter.guild.icon.url if inter.guild.icon else None
            )
        )

        for row in data:
            user = self.bot.get_user(row["member_id"])
            member = inter.guild.get_member(row["member_id"])
            if member is not None and not member.bot:
                if counter != 0 and counter % 5 == 0:
                    embeds.append(current_embed)

                counter += 1
                level = self.enum.format_large_number(row["level"])
                xp = self.enum.format_large_number(row["xp"])
                total_xp = self.enum.format_large_number(500 + 100 * row["level"])
                current_embed.add_field(
                    name=f"#{counter} | `{self.bot.get_user(row['member_id'])}`",
                    value=f"**Уровень:** {level} | **Опыт:** {xp}/{total_xp}",
                    inline=False,
                )

        if counter % 5 != 0:
            embeds.append(current_embed)

        view = paginator.Paginator(inter, embeds=embeds)
        message = await inter.edit_original_message(embed=embeds[0], view=view)
        view.message = message

    @commands.slash_command(
        name=disnake.Localized("shop", key="SHOP_COMMAND_NAME"),
        description=disnake.Localized(
            "A store where you can buy roles.", key="SHOP_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def view_shop(self, inter):
        await inter.response.defer(ephemeral=False)

        data = await db.get_shop_data(inter.guild.id, all_data=True)
        role_buttons = []
        role_pages = []

        for i, row in enumerate(data):
            if i % 6 == 0:
                page = (
                    disnake.Embed(color=self.color.MAIN)
                    .set_thumbnail(
                        url=inter.guild.icon.url if inter.guild.icon else None
                    )
                    .set_author(
                        name=f"Магазин ролей сервера {inter.guild.name}",
                        icon_url=inter.guild.icon.url if inter.guild.icon else None,
                    )
                )

            if inter.guild.get_role(row["role_id"]) is not None:
                counter = i + 1
                role_cost = self.enum.format_large_number(row["cost"])
                page.add_field(
                    name=f"`Товар #{counter}`",
                    value=f"**Роль:** {inter.guild.get_role(row['role_id']).mention}\n"
                    f"**Стоимость:** `{role_cost}` {self.economy.CURRENCY_NAME}",
                    inline=True,
                )

                # Создаем кнопку для каждой роли
                button_label = f"Товар #{str(counter)}"
                role_button = disnake.ui.Button(
                    style=disnake.ButtonStyle.blurple,
                    label=button_label,
                    custom_id=f"buy_role_{row['role_id']}",
                    row=1,
                )
                role_buttons.append(role_button)

            if i % 6 == 5 or i == len(data) - 1:
                role_pages.append(page)

        if not role_pages:
            embed = (
                disnake.Embed(
                    description="😶‍🌫️ Извините, но... магазин пуст.",
                    color=self.color.MAIN,
                )
                .set_thumbnail(
                    url=inter.guild.icon.url if inter.guild.icon else None
                )
                .set_author(
                    name=f"Магазин ролей сервера {inter.guild.name}",
                    icon_url=inter.guild.icon.url if inter.guild.icon else None,
                )
            )
            return await inter.edit_original_message(embed=embed)

        view = paginator.Paginator(inter, embeds=role_pages)
        # Добавляем кнопки к представлению
        for role_button in role_buttons:
            view.add_item(role_button)

        message = await inter.edit_original_message(embed=role_pages[0], view=view)
        view.message = message

    @commands.Cog.listener("on_button_click")
    async def shop_buttons_callback(self, inter: disnake.MessageInteraction):
        data = await db.get_shop_data(inter.guild.id, all_data=True)
        balance = await db.get_data(inter.author)
        if inter.component.custom_id.startswith("buy_role_"):
            role_id = int(inter.component.custom_id.split("_")[2])
            role = disnake.utils.get(inter.guild.roles, id=role_id)
            role_data = next(
                (item for item in data if item["role_id"] == role_id), None
            )

            if role_data:
                if balance["balance"] < role_data["cost"]:
                    embed = disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ У вас недостаточно {self.economy.CURRENCY_NAME} для покупки роли!",
                        color=self.color.RED,
                    )
                    await inter.response.send_message(embed=embed, ephemeral=True)

                elif role in inter.author.roles:
                    embed = disnake.Embed(
                        description=f"❌ У вас имеется данная роль!",
                        color=self.color.RED,
                    )
                    await inter.response.send_message(embed=embed, ephemeral=True)

                elif balance["balance"] <= 0:
                    embed = disnake.Embed(
                        description=f"❌ Недостаточно {self.economy.CURRENCY_NAME}!",
                        color=self.color.RED,
                    )
                    await inter.response.send_message(embed=embed, ephemeral=True)

                else:
                    embed = (
                        disnake.Embed(
                            description=f"✅ Вы успешно купили роль {role.mention} за {role_data['cost']} {self.economy.CURRENCY_NAME}!",
                            color=self.color.MAIN,
                        )
                        .set_author(
                            name="Покупка роли", icon_url=inter.author.display_avatar.url
                        )
                    )
                    await db.update_member(
                        "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
                        [role_data["cost"], inter.author.id, inter.guild.id],
                    )
                    await db.update_member(
                        "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                        [role_data["cost"], self.bot.user.id, inter.guild.id],
                    )
                    await inter.author.add_roles(role)
                    await inter.response.send_message(embed=embed)

            else:
                await inter.response.send_message("❌ Такой роли не существует.")

    @commands.slash_command(
        name=disnake.Localized("slot", key="SLOT_MACHINE_COMMAND_NAME"),
        description=disnake.Localized(
            "Slot machine game.", key="SLOT_MACHINE_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def slot(
        self,
        inter: disnake.ApplicationCommandInteraction,
        amount: int = commands.Param(
            name=disnake.Localized("amount", key="SLOT_MACHINE_COMMAND_TEXT_NAME"),
            description=disnake.Localized(
                "Specify the amount you are going to play for.",
                key="SLOT_MACHINE_COMMAND_TEXT_DESCRIPTION",
            ),
        ),
    ):
        data = await db.get_data(inter.author)
        slot_amount = self.enum.format_large_number(amount)
        if amount > data["balance"]:
            raise CustomError("❌ У вас недостаточно денег для игры!")

        elif amount < 10:
            raise CustomError(
                f"❌ Укажите сумму больше 10 {self.economy.CURRENCY_NAME}!"
            )

        elif amount > 500:
            raise CustomError(
                f"❌ Укажите сумму меньше чем 500 {self.economy.CURRENCY_NAME}!"
            )

        else:
            await inter.response.defer(ephemeral=False)
            description = [
                f"**Приветствуем, {inter.author.mention}!**",
                f"**Вы внесли в слот {slot_amount} {self.economy.CURRENCY_NAME}**",
                f"Вы уверены, что хотите прокрутить данный слот?",
            ]
            embed = (
                disnake.Embed(
                    description="\n".join(description), color=self.color.MAIN
                )
                .set_author(
                    name="Азартная игра «Слот-машина»",
                    icon_url=inter.author.display_avatar.url,
                )
            )
            view = SlotMachineButtons(inter, amount)
            message = await inter.edit_original_message(embed=embed, view=view)
            view.message = message

    @commands.slash_command(
        name=disnake.Localized("bonus", key="BONUS_COMMAND_NAME"),
        description=disnake.Localized(
            "Issues a bonus to the user.", key="BONUS_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.cooldown(1, 43200, commands.BucketType.user)
    async def bonus(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        random_amount = random.randint(10, 100)
        cooldown_time = datetime.datetime.now() + datetime.timedelta(hours=int(12))
        dynamic_time = disnake.utils.format_dt(cooldown_time, style="R")
        embed = (
            disnake.Embed(
                description=f"[`🎉`] **Вы получили** `{random_amount*8}` {self.economy.CURRENCY_NAME}\n\n"
                f"[`🕘`] **В следующий раз бонус можно получить {dynamic_time}.**",
                color=self.color.MAIN,
            )
            .set_author(
                name="🧸 Бонус успешно активирован!",
                icon_url=inter.author.display_avatar.url,
            )
        )
        await db.update_member(
            "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
            [random_amount * 8, inter.author.id, inter.guild.id],
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("coin", key="COIN_COMMAND_NAME"),
        description=disnake.Localized(
            "Cool game of heads or tails.", key="COIN_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def coin_game(
        self,
        inter: disnake.ApplicationCommandInteraction,
        amount: int = commands.Param(
            name=disnake.Localized("amount", key="COIN_COMMAND_TEXT_NAME"),
            description=disnake.Localized(
                "Specify the amount you are going to play for.",
                key="COIN_COMMAND_TEXT_DESCRIPTION",
            ),
        ),
    ):
        data = await db.get_data(inter.author)
        if amount > data["balance"]:
            raise CustomError(
                f"❌ У вас недостаточно {self.economy.CURRENCY_NAME} для игры в монетку! (Не хватает ещё {amount - data['balance']} {self.economy.CURRENCY_NAME})"
            )

        elif amount < 10:
            raise CustomError(
                f"❌ Укажите сумму больше 10 {self.economy.CURRENCY_NAME}!"
            )

        elif amount > 500:
            raise CustomError(
                f"❌ Укажите сумму меньше чем 500 {self.economy.CURRENCY_NAME}!"
            )

        else:
            await inter.response.defer(ephemeral=False)
            coin_embed = (
                disnake.Embed(
                    description=f"Множитель: **{self.economy.MULTIPLIER}** \n Твоя задача выбрать одну из сторон монетки, если угадываешь - умножаешь свою ставку на множитель!",
                    color=self.color.MAIN,
                )
                .add_field(value=amount, name="Ставка")
                .set_thumbnail(
                    url="https://cdn-icons-png.flaticon.com/512/272/272525.png"
                )
                .set_author(
                    name="Монетка", icon_url=inter.author.display_avatar.url
                )
            )
            view = CoinButtons(inter)
            message = await inter.edit_original_message(embed=coin_embed, view=view)
            view.message = message

    @commands.slash_command(
        name=disnake.Localized("fight_club", key="FIGHT_CLUB_COMMAND_NAME"),
        description=disnake.Localized(
            "The first rule of Fight Club...", key="FIGHT_CLUB_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def fight_club_game(
        self,
        inter: disnake.ApplicationCommandInteraction,
        amount: int = commands.Param(
            name=disnake.Localized("amount", key="FIGHT_CLUB_COMMAND_TEXT_NAME"),
            description=disnake.Localized(
                "Specify the amount you are going to play for.",
                key="FIGHT_CLUB_COMMAND_TEXT_DESCRIPTION",
            ),
        ),
    ):
        data = await db.get_data(inter.author)
        if amount > data["balance"]:
            raise CustomError(
                f"❌ У вас недостаточно {self.economy.CURRENCY_NAME} для битвы в бойцовском клубе! (Не хватает ещё {amount - data['balance']} {self.economy.CURRENCY_NAME})"
            )

        elif amount < 10:
            raise CustomError(
                f"❌ Укажите сумму больше 10 {self.economy.CURRENCY_NAME}!"
            )

        elif amount > 500:
            raise CustomError(
                f"❌ Укажите сумму меньше чем 500 {self.economy.CURRENCY_NAME}!"
            )
        else:
            await inter.response.defer(ephemeral=False)
            fight_embed = (
                disnake.Embed(
                    description=f"*Первое правило бойцовского клуба - никому не рассказывай про бойцовский клуб...* \n "
                    f"**Стоимость вступления в поединок - {amount} {self.economy.CURRENCY_NAME}. ** \n "
                    f"Тебе дают возможность сделать удар первым, если ты хорошо реализуешь его, то получишь {amount * self.economy.MULTIPLIER} {self.economy.CURRENCY_NAME}, если противник защитится, соболезную тебе...",
                    color=self.color.MAIN,
                )
                .add_field(value=amount, name="Ставка")
                .set_thumbnail(
                    url="https://cdn-icons-png.flaticon.com/512/6264/6264793.png"
                )
                .set_author(
                    name="Бойцовский клуб", icon_url=inter.author.display_avatar.url
                )
            )
            view = FightButtons(inter)
            message = await inter.edit_original_message(
                embed=fight_embed, view=view
            )
            view.message = message

    @commands.slash_command(
        name=disnake.Localized("case", key="CASE_COMMAND_NAME"),
        description=disnake.Localized(
            "Open cases with pleasant bonuses.", key="CASE_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def open_case(self, inter: disnake.ApplicationCommandInteraction):
        data = await db.get_data(inter.author)
        if 100 > data["balance"]:
            raise CustomError(
                f"❌ У вас недостаточно **{self.economy.CURRENCY_NAME}** для открытия кейса!"
            )
        else:
            await inter.response.defer(ephemeral=False)

            case_embed = (
                disnake.Embed(
                    description=f'Для открытия кейса нажми на "Открыть кейс" \n **В кейсах большие шансы на выигрыш!**',
                    color=self.color.MAIN,
                )
                .set_thumbnail(
                    url="https://cdn-icons-png.flaticon.com/512/10348/10348893.png"
                )
                .set_author(
                    name="Кейсы", icon_url=inter.author.display_avatar.url
                )
            )
            view = CaseButtons(inter)
            message = await inter.edit_original_message(embed=case_embed, view=view)
            view.message = message

    @commands.slash_command(
        name=disnake.Localized("work", key="WORK_COMMAND_NAME"),
        description=disnake.Localized(
            "Cool game of heads or tails.", key="WORK_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        WORKS_LIST = {
            "📦 Грузчик": 1500,
            "🧑‍🏫 Учитель": 500,
            "💻 Разработчик": 2000,
            "🎨 Художник": 1750,
            "🧹 Дворник": 200,
            "👨‍⚕️ Врач": 1800,
            "🧱 Строитель": 2100,
            "👩‍⚕️ Мед. сестра": 500,
            "🪓 Лесник": 2000,
        }
        work = random.choice(list(WORKS_LIST))
        embed = (
            disnake.Embed(
                description="[`🎉`] **Ты сегодня потненько поработал, так держать!**\n"
                "**Держи свои печеньки и отдохни, заслужил :)**",
                color=self.color.MAIN,
            )
            .add_field(name="Профессия", value=f"**{work}**")
            .add_field(
                name="Заработок",
                value=f"`{str(WORKS_LIST[work])}` {self.economy.CURRENCY_NAME}",
            )
            .set_author(name="Работа", icon_url=inter.author.display_avatar.url)
        )
        await db.update_member(
            "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
            [WORKS_LIST[work], inter.author.id, inter.guild.id],
        )
        await inter.edit_original_message(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))
