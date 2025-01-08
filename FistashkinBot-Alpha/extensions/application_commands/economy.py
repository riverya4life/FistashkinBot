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
    )
    @commands.contexts(guild=True, private_channel=True)
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

        formatted_data = {
            "balance": self.enum.format_large_number(data["balance"]),
            "level": self.enum.format_large_number(data["level"]),
            "xp": self.enum.format_large_number(data["xp"]),
            "total_xp": self.enum.format_large_number(data["total_xp"]),
            "xp_to_lvl": self.enum.format_large_number(5 * (data["level"] ** 2) + 50 * data["level"] + 100),
        }

        user_rank_position, members_rank_len = await self.rating.rating_rank(member=member)
        user_balance_position, members_balance_len = await self.rating.rating_balance(member=member)

        multipliers = {2.0: "x2", 4.0: "x4", 8.0: "x8"}
        multiplier = multipliers.get(self.economy.MULTIPLIER, "")
        bonuses = [
            f"- Ежедневный - **каждые 12 часов.**",
            f"- **{multiplier}** множитель опыта и баланса." if multiplier else "",
        ]

        bonuses = [bonus for bonus in bonuses if bonus]

        embed = disnake.Embed(color=self.color.MAIN)
        embed.add_field(
            name="💰 Баланс:",
            value=f"**```{formatted_data['balance']} {self.economy.CURRENCY_NAME}```**",
            inline=True,
        )
        embed.add_field(
            name=f"🧸 Рейтинг {self.economy.CURRENCY_NAME}:",
            value=f"**```# {user_balance_position}/{members_balance_len}```**",
            inline=True,
        )
        embed.add_field(
            name=f"🎁 Бонусы:",
            value="\n".join(bonuses),
            inline=False,
        )
        embed.set_author(
            name=f"💳 Отчётность о балансе {member}",
            icon_url=member.display_avatar.url,
        )

        await inter.edit_original_message(embed=embed)


    @commands.slash_command(
        name=disnake.Localized("rank", key="USER_RANK_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows the rank of the mentioned user or the user who called the command.",
            key="USER_RANK_COMMAND_DESCRIPTION",
        ),
    )
    @commands.contexts(guild=True, private_channel=True)
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

            user_rank_position = (await self.rating.rating_rank(member=member))[0]
            data = await db.get_data(member)
            user = await self.bot.fetch_user(member.id)

            levelcard = discord_card.LevelCard()
            levelcard.avatar = member.display_avatar.url
            levelcard.path = user.banner.url if user.banner else "https://cdn.some-random-api.com/JBiRiEZE"
            levelcard.name = str(member)
            levelcard.xp = data["xp"]
            levelcard.required_xp = 5 * (data["level"] ** 2) + 50 * data["level"] + 100
            levelcard.level = data["level"]
            levelcard.rank_pos = user_rank_position
            levelcard.is_rounded = True
            
            await inter.edit_original_message(file=await levelcard.create())

    @commands.slash_command(
        name=disnake.Localized("pay", key="PAY_COMMAND_NAME"),
        description=disnake.Localized(
            "Transfers money to the user.", key="PAY_COMMAND_DESCRIPTION"
        ),
    )
    @commands.contexts(guild=True, private_channel=True)
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

        conditions = [
            (not amount, f"❌ Укажите сумму **{self.economy.CURRENCY_NAME}**, которую желаете начислить на счет участника!"),
            (member == inter.author, f"❌ Ты не можешь **перевести {self.economy.CURRENCY_NAME}** самому себе!"),
            (amount <= 0, f"❌ Укажите сумму больше **0 {self.economy.CURRENCY_NAME}**!"),
            (amount > data["balance"], f"❌ У вас недостаточно **{self.economy.CURRENCY_NAME}** для перевода!"),
            (member.bot, "❌ Ты не можешь взаимодействовать с ботами!")
        ]

        for condition, error_message in conditions:
            if condition:
                raise CustomError(error_message)

        await inter.response.defer(ephemeral=False)

        commission = amount * (self.economy.COMMISSION / 100) if amount > 100 else 0
        amount_after_commission = amount - commission

        pay_amount = self.enum.format_large_number(amount)
        comm_amount = self.enum.format_large_number(amount_after_commission)
        comm_amount_display = self.enum.format_large_number(amount_after_commission)

        await db.update_member(
            """
            UPDATE users 
            SET balance = CASE 
                WHEN member_id = ? THEN balance - ? 
                WHEN member_id = ? THEN balance + ? 
            END
            WHERE (member_id = ? OR member_id = ?) 
            AND guild_id = ?
            """,
            [inter.author.id, amount, member.id, amount_after_commission, inter.author.id, member.id, inter.guild.id],
        )

        description = [
            f"[`💱`] **Перевод успешно выполнен!**\n\n",
            f"[`📉`] **Отправитель:** {inter.author.mention}\n",
            f"[`🔴`] **Списано:** - `{pay_amount}` {self.economy.CURRENCY_NAME}\n",
            f"[`📈`] **Получатель:** {member.mention}\n",
            f"[`🟢`] **Получено:** + `{comm_amount_display}` {self.economy.CURRENCY_NAME}\n",
            f"=======================================\n",
            f"[`⚠️`] **Комиссия:** `{self.enum.format_large_number(commission)}` (**{self.economy.COMMISSION}%**)\n",
            f"[`📃`] **Итого переведено:** `{comm_amount_display}` {self.economy.CURRENCY_NAME}",
        ]

        embed = disnake.Embed(description="".join(description), color=self.color.MAIN)
        embed.set_author(name="💳 Отчётность о банковской операции", icon_url=member.display_avatar.url)

        await inter.edit_original_message(embed=embed)


    @commands.slash_command(
        name=disnake.Localized("leaderboard", key="LEADERBOARD_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows the top ranking of users for something.",
            key="LEADERBOARD_COMMAND_DESCRIPTION",
        ),
    )
    @commands.contexts(guild=True, private_channel=True)
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
        current_embed = disnake.Embed(
            description=f"[`👑`] **Список лидеров по балансу на сервере **`{inter.guild.name}`**!**",
            color=self.color.MAIN,
        ).set_author(
            name=f"👑 Топ лидеров сервера",
            icon_url=inter.guild.icon.url if inter.guild.icon else None,
        ).set_thumbnail(
            url=inter.guild.icon.url if inter.guild.icon else None
        )

        for row in data:
            user = self.bot.get_user(row["member_id"])
            member = inter.guild.get_member(row["member_id"])
            if member is not None and not member.bot:
                balance = self.enum.format_large_number(row["balance"])
                
                if counter > 0 and counter % 10 == 0:
                    embeds.append(current_embed)
                    current_embed = disnake.Embed(
                        description=f"[`👑`] **Список лидеров по балансу на сервере **`{inter.guild.name}`**!**",
                        color=self.color.MAIN,
                    ).set_author(
                        name=f"👑 Топ лидеров сервера",
                        icon_url=inter.guild.icon.url if inter.guild.icon else None,
                    ).set_thumbnail(
                        url=inter.guild.icon.url if inter.guild.icon else None
                    )

                counter += 1
                current_embed.add_field(
                    name=f"#{counter} | `{user}`",
                    value=f"**Баланс:** {balance} {self.economy.CURRENCY_NAME}",
                    inline=False,
                )

        if counter % 10 != 0:
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
        current_embed = disnake.Embed(
            description=f"[`👑`] **Список лидеров по опыту на сервере **`{inter.guild.name}`**!**",
            color=self.color.MAIN,
        ).set_author(
            name=f"👑 Топ лидеров сервера",
            icon_url=inter.guild.icon.url if inter.guild.icon else None,
        ).set_thumbnail(
            url=inter.guild.icon.url if inter.guild.icon else None
        )

        for row in data:
            user = self.bot.get_user(row["member_id"])
            member = inter.guild.get_member(row["member_id"])
            if member is not None and not member.bot:
                level = self.enum.format_large_number(row["level"])
                xp = self.enum.format_large_number(row["xp"])

                if counter > 0 and counter % 10 == 0:
                    embeds.append(current_embed)
                    current_embed = disnake.Embed(
                        description=f"[`👑`] **Список лидеров по опыту на сервере **`{inter.guild.name}`**!**",
                        color=self.color.MAIN,
                    ).set_author(
                        name=f"👑 Топ лидеров сервера",
                        icon_url=inter.guild.icon.url if inter.guild.icon else None,
                    ).set_thumbnail(
                        url=inter.guild.icon.url if inter.guild.icon else None
                    )

                counter += 1
                current_embed.add_field(
                    name=f"#{counter} | `{user}`",
                    value=f"**Уровень:** {level} | **Опыт:** {xp}",
                    inline=False,
                )

        if counter % 10 != 0:
            embeds.append(current_embed)

        view = paginator.Paginator(inter, embeds=embeds)
        message = await inter.edit_original_message(embed=embeds[0], view=view)
        view.message = message


    @commands.slash_command(
        name=disnake.Localized("shop", key="SHOP_COMMAND_NAME"),
        description=disnake.Localized(
            "A store where you can buy roles.", key="SHOP_COMMAND_DESCRIPTION"
        ),
    )
    @commands.contexts(guild=True, private_channel=True)
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def view_shop(self, inter):
        await inter.response.defer(ephemeral=False)

        data = await db.get_shop_data(inter.guild.id, all_data=True)
        role_buttons = []
        role_pages = []
        page = None

        roles_cache = {role.id: role for role in inter.guild.roles}

        for i, row in enumerate(data):
            if i % 6 == 0:
                if page:
                    role_pages.append(page)
                page = disnake.Embed(color=self.color.MAIN).set_thumbnail(
                    url=inter.guild.icon.url if inter.guild.icon else None
                ).set_author(
                    name=f"Магазин ролей сервера {inter.guild.name}",
                    icon_url=inter.guild.icon.url if inter.guild.icon else None,
                )

            role = roles_cache.get(row["role_id"])
            if role:
                counter = i + 1
                role_cost = self.enum.format_large_number(row["cost"])
                page.add_field(
                    name=f"`Товар #{counter}`",
                    value=f"**Роль:** {role.mention}\n"
                    f"**Стоимость:** `{role_cost}` {self.economy.CURRENCY_NAME}",
                    inline=True,
                )

                button_label = f"Товар #{str(counter)}"
                role_button = disnake.ui.Button(
                    style=disnake.ButtonStyle.blurple,
                    label=button_label,
                    custom_id=f"buy_role_{row['role_id']}",
                    row=1,
                )
                role_buttons.append(role_button)

        if page:
            role_pages.append(page)

        if not role_pages:
            embed = disnake.Embed(
                description="😶‍🌫️ Извините, но... магазин пуст.",
                color=self.color.MAIN,
            ).set_thumbnail(
                url=inter.guild.icon.url if inter.guild.icon else None
            ).set_author(
                name=f"Магазин ролей сервера {inter.guild.name}",
                icon_url=inter.guild.icon.url if inter.guild.icon else None,
            )
            return await inter.edit_original_message(embed=embed)

        view = paginator.Paginator(inter, embeds=role_pages)
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
            role_data = next((item for item in data if item["role_id"] == role_id), None)

            if not role_data:
                return await inter.response.send_message("❌ Такой роли не существует.", ephemeral=True)

            if balance["balance"] <= 0:
                error_message = f"❌ Недостаточно {self.economy.CURRENCY_NAME}!"
            elif balance["balance"] < role_data["cost"]:
                error_message = f"❌ У вас недостаточно {self.economy.CURRENCY_NAME} для покупки роли!"
            elif role in inter.author.roles:
                error_message = f"❌ У вас уже есть эта роль!"
            else:
                embed = disnake.Embed(
                    description=f"✅ Вы успешно купили роль {role.mention} за {role_data['cost']} {self.economy.CURRENCY_NAME}!",
                    color=self.color.MAIN,
                ).set_author(
                    name="Покупка роли", icon_url=inter.author.display_avatar.url
                )
                await db.update_member(
                    "UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?",
                    [role_data["cost"], inter.author.id, inter.guild.id],
                )
                await inter.author.add_roles(role)
                return await inter.response.send_message(embed=embed)

            embed = disnake.Embed(description=error_message, color=self.color.RED)
            return await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        name=disnake.Localized("slot", key="SLOT_MACHINE_COMMAND_NAME"),
        description=disnake.Localized(
            "Slot machine game.", key="SLOT_MACHINE_COMMAND_DESCRIPTION"
        ),
    )
    @commands.contexts(guild=True, private_channel=True)
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

        conditions = [
            (amount < 10, f"❌ Укажите сумму больше 10 {self.economy.CURRENCY_NAME}!"),
            (amount > 500, f"❌ Укажите сумму меньше чем 500 {self.economy.CURRENCY_NAME}!"),
            (amount > data["balance"], "❌ У вас недостаточно денег для игры!")
        ]

        for condition, error_message in conditions:
            if condition:
                raise CustomError(error_message)

        await inter.response.defer(ephemeral=False)

        description = [
            f"**Приветствуем, {inter.author.mention}!**",
            f"**Вы внесли в слот {slot_amount} {self.economy.CURRENCY_NAME}**",
            f"Вы уверены, что хотите прокрутить данный слот?",
        ]
        embed = disnake.Embed(
            description="\n".join(description), color=self.color.MAIN
        ).set_author(
            name="Азартная игра «Слот-машина»", icon_url=inter.author.display_avatar.url
        )

        view = SlotMachineButtons(inter, amount)
        message = await inter.edit_original_message(embed=embed, view=view)
        view.message = message

    @commands.slash_command(
        name=disnake.Localized("bonus", key="BONUS_COMMAND_NAME"),
        description=disnake.Localized(
            "Issues a bonus to the user.", key="BONUS_COMMAND_DESCRIPTION"
        ),
    )
    @commands.contexts(guild=True, private_channel=True)
    @commands.cooldown(1, 43200, commands.BucketType.user)
    async def bonus(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        random_amount = random.randint(10, 100)

        multipliers = {2.0: "x2", 4.0: "x4", 8.0: "x8"}
        multiplier = multipliers.get(self.economy.MULTIPLIER, "")
        bonus_amount = random_amount * self.economy.MULTIPLIER

        cooldown_time = disnake.utils.format_dt(
            datetime.datetime.now() + datetime.timedelta(hours=12), style="R"
        )

        embed = disnake.Embed(
            description=f"[`🎉`] **Вы получили** `{bonus_amount}` {self.economy.CURRENCY_NAME}\n\n"
            f"[`🕘`] **В следующий раз бонус можно получить {cooldown_time}.**",
            color=self.color.MAIN,
        ).set_author(
            name="🧸 Бонус успешно активирован!",
            icon_url=inter.author.display_avatar.url,
        )

        await db.update_member(
            "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
            [bonus_amount, inter.author.id, inter.guild.id],
        )

        await inter.edit_original_message(embed=embed)


    @commands.slash_command(
        name=disnake.Localized("coin", key="COIN_COMMAND_NAME"),
        description=disnake.Localized(
            "Cool game of heads or tails.", key="COIN_COMMAND_DESCRIPTION"
        ),
    )
    @commands.contexts(guild=True, private_channel=True)
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
        conditions = [
            (amount > data["balance"], f"❌ У вас недостаточно {self.economy.CURRENCY_NAME} для игры в монетку! (Не хватает ещё {amount - data['balance']} {self.economy.CURRENCY_NAME})"),
            (amount < 10, f"❌ Укажите сумму больше 10 {self.economy.CURRENCY_NAME}!"),
            (amount > 500, f"❌ Укажите сумму меньше чем 500 {self.economy.CURRENCY_NAME}!")
        ]

        for condition, error_message in conditions:
            if condition:
                raise CustomError(error_message)

        await inter.response.defer(ephemeral=False)

        coin_embed = disnake.Embed(
            description=f"Множитель: **{self.economy.MULTIPLIER}** \nТвоя задача выбрать одну из сторон монетки, если угадываешь - умножаешь свою ставку на множитель!",
            color=self.color.MAIN,
        ).add_field(value=amount, name="Ставка").set_thumbnail(
            url="https://cdn-icons-png.flaticon.com/512/272/272525.png"
        ).set_author(
            name="Монетка", icon_url=inter.author.display_avatar.url
        )

        view = CoinButtons(inter)
        message = await inter.edit_original_message(embed=coin_embed, view=view)
        view.message = message


    @commands.slash_command(
        name=disnake.Localized("fight_club", key="FIGHT_CLUB_COMMAND_NAME"),
        description=disnake.Localized(
            "The first rule of Fight Club...", key="FIGHT_CLUB_COMMAND_DESCRIPTION"
        ),
    )
    @commands.contexts(guild=True, private_channel=True)
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
        conditions = [
            (amount < 10, f"❌ Укажите сумму больше 10 {self.economy.CURRENCY_NAME}!"),
            (amount > 500, f"❌ Укажите сумму меньше чем 500 {self.economy.CURRENCY_NAME}!"),
            (amount > data["balance"], "❌ У вас недостаточно денег для игры!")
        ]

        for condition, error_message in conditions:
            if condition:
                raise CustomError(error_message)

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
    )
    @commands.contexts(guild=True, private_channel=True)
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
    )
    @commands.contexts(guild=True, private_channel=True)
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

        work, salary = random.choice(list(WORKS_LIST.items()))
        embed = (
            disnake.Embed(
                description="[`🎉`] **Ты сегодня потненько поработал, так держать!**\n"
                            "**Держи свои печеньки и отдохни, заслужил :)**",
                color=self.color.MAIN,
            )
            .add_field(name="Профессия", value=f"**{work}**")
            .add_field(name="Заработок", value=f"`{salary}` {self.economy.CURRENCY_NAME}")
            .set_author(name="Работа", icon_url=inter.author.display_avatar.url)
        )

        await db.update_member(
            "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
            [salary, inter.author.id, inter.guild.id],
        )

        await inter.edit_original_message(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))
