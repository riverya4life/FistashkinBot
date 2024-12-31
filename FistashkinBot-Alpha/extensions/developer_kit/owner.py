import disnake
from disnake.ext import commands
import datetime
import psutil
import platform

from utils import enums, main, paginator, automod
from utils import discord_card
from asyncio import sleep

from classes.cooldown import default_cooldown
from classes import database as db


class OwnerInfo(commands.Cog):

    hidden = True

    def __init__(self, bot):
        self.bot = bot
        self.color = enums.Color()
        self.enum = enums.Enum()
        self.main = main.MainSettings()
        self.automod = automod.Automod(self.bot)

    @commands.slash_command(name="ruleinfo")
    async def info_rule(self, inter):
        automod_rules = await inter.guild.fetch_automod_rules()

        # Вывод информации о каждом правиле
        for rule in automod_rules:
            if rule is not None:
                print()
                print("Rule ID:", rule.id)
                print("Rule Name:", rule.name)
                print("Enabled:", rule.enabled)
                print("Creator:", rule.creator)
                print("Event Type:", rule.event_type)
                print("Trigger Type:", rule.trigger_type)
                print("Actions:", rule.actions)
                print("Exempt Roles:", rule.exempt_roles)
                print("Exempt Channels:", rule.exempt_channels)
                print("Trigger Metadata:", rule.trigger_metadata)
                print()
            else:
                print("err")

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ButtonRolesRiveryaBrotherhood())
        self.bot.add_view(DropdownRiveryaBrotherhoodView())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.lower() == ("developer_cmd_xp = none"):
            if message.author.id == self.main.DEVELOPER_ID:
                await db.update_member(
                    "UPDATE users SET xp = ? WHERE member_id = ? AND guild_id = ?",
                    [0, message.author.id, message.guild.id],
                )
            else:
                await message.reply(
                    f"{message.author.mention}, ты не являешься владельцем бота, поэтому команда не доступна!",
                    delete_after=15.0,
                )

        if message.content.lower() == ("developer_cmd_welcomer-test"):
            if message.author.id == self.main.DEVELOPER_ID:
                description = [
                    f":flag_gb: :flag_us:\n"
                    f"Hello, {message.author.mention}! Welcome to the FistashkinBot community and support guild!\n"
                    f"Please check the ⁠<#1044628885876260865> channel for useful info and rules.\n\n"
                    f":flag_ru:\n"
                    f"Привет, {message.author.mention}! Добро пожаловать на сервер поддержки и сообщества пользователей FistashkinBot!\n"
                    f"Пожалуйста, ознакомься с информацией и правилами в канале ⁠<#1044628885876260865>\n\n"
                    f":flag_ua:\n"
                    f"Привіт, {message.author.mention}! Ласкаво просимо на сервер підтримки та спільноти користувачів FistashkinBot!\n"
                    f"Будь ласка, ознайомся з інформацією та правилами в каналі <#1044628885876260865>"
                ]
                await message.author.send(
                    embed=disnake.Embed(
                        description="".join(description), color=self.color.MAIN
                    ),
                    components=[
                        disnake.ui.Button(
                            label=f"Отправлено с {message.author.guild.name}",
                            emoji="📨",
                            style=disnake.ButtonStyle.gray,
                            disabled=True,
                        )
                    ],
                )
            else:
                await message.reply(
                    f"{message.author.mention}, ты не являешься владельцем бота, поэтому команда не доступна!",
                    delete_after=15.0,
                )

        if message.content.lower() == ("developer_reset_handled_cmds_1"):
            if message.author.id == self.main.DEVELOPER_ID:
                await db.insert_command_count_debug(amount=10603)
            else:
                await message.reply(
                    f"{message.author.mention}, ты не являешься владельцем бота, поэтому команда не доступна!",
                    delete_after=15.0,
                )

        if message.content.lower() == ("developer_bot_platform_stat1"):
            if message.author.id == self.main.DEVELOPER_ID:
                await message.delete()
                await message.channel.send(
                    f"Операционная система: **{platform.platform()}**\n"
                    f"RAM: **{psutil.virtual_memory().percent}%**\n"
                    f"CPU: **{psutil.cpu_percent()}%**\n"
                    f"Кластеров: **{len(self.bot.shards)}**\n"
                    f"Задержка: **{round(self.bot.latency*1000)}ms**",
                    delete_after=15.0,
                )
            else:
                await message.reply(
                    f"{message.author.mention}, ты не являешься владельцем бота, поэтому команда не доступна!",
                    delete_after=15.0,
                )

        if message.content.lower() == ("developer_bot_automod_test"):
            if message.author.id == self.main.DEVELOPER_ID:
                # automod_rules = await message.guild.fetch_automod_rules()
                # rules = list(
                #    filter(lambda rule: rule.creator.id == self.bot.user.id, automod_rules)
                # )
                # print(rules if rules is not None else "None")

                """automod_rules = await message.guild.fetch_automod_rules()
                # Фильтруем правила, созданные ботом
                rules_to_delete = [rule for rule in automod_rules if rule.creator.id == self.bot.user.id]
                # Удаляем отфильтрованные правила
                for rule in rules_to_delete:
                    await rule.delete()
                    print(f"Deleted rule with ID: {rule.id}")"""
                await self.automod.ban_word_filter_automod(guild=message.guild)
                ban_words = await self.automod._load_json()
                for word in ban_words:
                    print(word)
            else:
                await message.reply(
                    f"{message.author.mention}, ты не являешься владельцем бота, поэтому команда не доступна!",
                    delete_after=15.0,
                )


class ButtonRolesRiveryaBrotherhood(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def inter_click(self, button: disnake.ui.Button, inter):
        role = inter.guild.get_role(int(button.custom_id))

        if role in inter.author.roles:
            text = f"**Вы успешно сняли роль {role.mention}**"
            await inter.author.remove_roles(role)
        else:
            text = f"**Вы успешно добавили роль {role.mention}**"
            await inter.author.add_roles(role)

        await inter.response.send_message(text, ephemeral=True)

    @disnake.ui.button(label="Игроман", custom_id="940996593216258058", emoji="🎲")
    async def gamer(self, button: disnake.ui.Button, inter):
        await self.inter_click(button, inter)

    @disnake.ui.button(
        label="В курсе событий", custom_id="1007187354127183903", emoji="📰"
    )
    async def newsmention(self, button: disnake.ui.Button, inter):
        await self.inter_click(button, inter)

    @disnake.ui.button(label="Значок чата", custom_id="1007184365396172871", emoji="🎓")
    async def badgechat(self, button: disnake.ui.Button, inter):
        await self.inter_click(button, inter)

    @disnake.ui.button(label="NSFW Чат", custom_id="1056532229234372628", emoji="🔞")
    async def nsfwrole(self, button: disnake.ui.Button, inter):
        await self.inter_click(button, inter)


class DropdownRiveryaBrotherhood(disnake.ui.StringSelect):
    def __init__(self):
        self.color = enums.Color()

        options = [
            disnake.SelectOption(
                label="Ответы на часто задаваемые вопросы.", emoji="⁉"
            ),
            disnake.SelectOption(label="Контактная информация.", emoji="📠"),
            disnake.SelectOption(label="Правила Discord.", emoji="📜"),
            disnake.SelectOption(label="Роли за общение.", emoji="🤔"),
            disnake.SelectOption(label="Дополнительные роли.", emoji="😱"),
            disnake.SelectOption(label="Получение ролей.", emoji="🍀"),
            disnake.SelectOption(
                label="Что такое Fistashkin Coins и куда их девать?", emoji="💎"
            ),
        ]

        super().__init__(
            placeholder="🍃 | Выберите интересующий Вас вариант.",
            custom_id="faqdropdown",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter):
        if self.values[0] == "Ответы на часто задаваемые вопросы.":
            embed1 = disnake.Embed(
                description=f"""```🚨Что делать если модератор наказал Вас неверно или же сам нарушает правила сервера?```
                В таком случае рекомендуется собрать все доказательства в руки и обратиться в канал <#1058147813810262186>.
                В случае если наказание было выдано верно и Вы пытаетесь обмануть модерацию ваше наказание может быть удвоено.""",
                colour=self.color.DARK_GRAY,
            )
            embed1.set_footer(
                text=inter.message.guild.name, icon_url=inter.guild.icon.url
            )
            await inter.response.send_message(embed=embed1, ephemeral=True)

        if self.values[0] == "Контактная информация.":
            embed2 = disnake.Embed(
                description=f"""```📌 Контактная информация по модерации нашего сервера : ```
                [`🙋‍♂️`] Создатель - <@668453200457760786>.
                [`🙋‍♂️`] Discord администратор - <@1012493886926630972>.
                [`🙋‍♂️`] Главный модератор - <@649932848379461632>.
                [`🙋‍♂️`] Заместитель главного модератора - Вакантно.\n
                [`📝`] Предложить улучшение нашего дискорд сервера - <#1020770079484432465>.
                [`📝`] Подать жалобу на модератора - [нажмите, чтобы перейти](https://discord.com/channels/809899167282364416/1086332911072059525)
                [`📝`] Магазин Fistashkin Coins - <#1062390882394963978>.""",
                colour=self.color.DARK_GRAY,
            )
            embed2.set_footer(
                text=inter.message.guild.name, icon_url=inter.guild.icon.url
            )
            await inter.response.send_message(embed=embed2, ephemeral=True)

        if self.values[0] == "Правила Discord.":
            embed3 = disnake.Embed(
                description=f"""```📜 Правила сервера:```
                **1.** Соблюдайте:
                    **a.** Условия использования Discord https://discord.com/terms;
                    **b.** Правила сообщества Discord https://discord.com/guidelines (особенно возрастные ограничения допуска с 13 лет);

                **2.** Не проявляйте нацизм, расизм и прочую дискриминацию участников по каким-либо признакам;

                **3.** Не хейтите и не устраивайте междусобойчики (если так приспичило посраться - идите в ЛС);

                **4.** Запрещены спам, пиар и реклама как на сервере, так и по личкам, включая, но не ограничиваясь:
                    **a.** Приглашениями на сторонние серверы;
                    **b.** Сообществами в социальных сетях, YouTube, Twitch и прочих;

                **5.** Не флудите, включая, но не ограничиваясь:
                    **a.** Разного рода бессмысленными сообщениями;
                    **b.** Излишним злоупотреблением командами бота;

                **6.** Взрослому контенту не место на сервере (если вам приспичило - выдадут роль <@&1056532229234372628>);

                **7.** Аватарка, баннер и никнейм не должны:
                    **a.** Нарушать общепринятые моральные и этические нормы;
                    **b.** Быть оскорбительными в какой-либо форме для участников;

                **8.** Ведите себя достойно:
                    **a.** Не злоупотребляйте нецензурными выражениями;
                    **b.** Не ведите себя токсично и не оскорбляйте других участников;
                    **c.** Не упоминайте всех, включая создателя сервера, разработчика бота <@991338113630752928>, модераторов и саппортов без весомой на то причины за исключением случаев, когда они общаются в текстовом канале в текущий момент времени;""",
                colour=self.color.DARK_GRAY,
            )
            embed3.set_footer(
                text=inter.message.guild.name, icon_url=inter.guild.icon.url
            )
            await inter.response.send_message(embed=embed3, ephemeral=True)

        if self.values[0] == "Роли за общение.":
            embed4 = disnake.Embed(
                description=f"""```🗽 Где и за что можно получить опыт? Где проверить свой уровень?```
                >>> Проверить свой уровень можно прописав команду `!ранг` в чат.
                Над количеством ваших EXP отображается количество часов проведенных в voice каналах.
                EXP начисляются за общение в каналах, начисляются раз в минуту.
                Часы в voice каналах начисляются когда в канале **2+** человека и у них включены микрофоны и наушники.\n
                ```💬 Роли выдаваемые за активность в общем чате :```
                <@&1015366236886007809> `[5 уровень]`
                <@&1007178377339338783> `[10 уровень]`
                <@&1015368482839343156> `[20 уровень]`
                <@&1007179756673970276> `[35 уровень]`
                <@&1007179183048376341> `[50 уровень]`
                <@&1007179509725933598> `[75 уровень]`""",
                colour=self.color.DARK_GRAY,
            )
            embed4.set_footer(
                text=inter.message.guild.name, icon_url=inter.guild.icon.url
            )
            await inter.response.send_message(embed=embed4, ephemeral=True)

        if self.values[0] == "Дополнительные роли.":
            embed5 = disnake.Embed(
                description=f"""[`🏆`] <@&1007182161163583548> - выдаётся узнаваемым, активным и старым посетителям сервера, которые с нами больше `7` месяцев.\n
                [`📰`] <@&1007187354127183903> - выдаётся ботом специально для пользователей которые хотят быть в курсе новостей нашего сервера. Получить роль можно в пункте `🍀 Получение ролей`, после получения Вам будут приходить упоминания в канале <#809902527298011136> при выпуске новостей.\n
                [`👼`] <@&1008345238173134849> - выдаётся модерации отстоявшей `9+` месяцев на своей должности [могут быть исключения на усмотрение руководящей модерации].\n
                [`🎨`] <@&1007182615381545004> - выдаётся людям, которые находятся в ТОП-10 сервера по уровню и балансу Fistashkin Coins [Проверить список лидеров по уровню - `/лидеры ранг`, по балансу `/лидеры баланс`].\n
                [`💖`] <@&1006924954362728458> - выдаётся людям, которым можно доверять.\n
                [`💸`] <@&1013436140122034317> - выдаётся определённому кругу лиц, которые ведут аккаунты **Tik Tok** и **YouTube**.\n
                [`🕹`] <@&940996593216258058> - выдаётся игрокам одноименных игр, получить можно в пункте `🍀 Получение ролей`.\n
                [`💩`] <@&1056532229234372628> - даёт доступ к закрытому **NSFW** каналу на нашем сервере.""",
                colour=self.color.DARK_GRAY,
            )
            embed5.set_footer(
                text=inter.message.guild.name, icon_url=inter.guild.icon.url
            )
            await inter.response.send_message(embed=embed5, ephemeral=True)

        if self.values[0] == "Получение ролей.":
            embed6 = disnake.Embed(
                description=f"""**Всем привет!**
                Вы хотите себе роль? Тогда Вам сюда!
                Снизу есть роли на выбор, чтобы выбрать роль, которую хочешь - жми на кнопочку.\n
                **Список ролей доступные для раздачи:**
                <@&940996593216258058>, <@&1007187354127183903>, <@&1007184365396172871> и <@&1056532229234372628>""",
                colour=self.color.DARK_GRAY,
            )
            embed6.set_footer(
                text=inter.message.guild.name, icon_url=inter.guild.icon.url
            )
            await inter.response.send_message(
                embed=embed6, ephemeral=True, view=ButtonRolesRiveryaBrotherhood()
            )

        if self.values[0] == "Что такое Fistashkin Coins и куда их девать?":
            embed7 = disnake.Embed(
                description=f"""> **Fistashkin Coins [FC]** - внутренняя валюта нашего дискорд сервера, получить её можно за общение в общем чате нашего сервера `[0.5 за одно сообщение]`, участвуя в мероприятиях нашего сервера или же выиграв в нашем игровом клубе.\n
                ```🏪 Куда можно потратить накопления Fistashkin Coins?```
                > Магазин можно найти [тут](https://discord.com/channels/809899167282364416/1062390882394963978). В магазине содержится вся необходимая информация о заработке, скидках и товаре. В случае возникновения вопросов обратитесь в <#1058147813810262186>.""",
                colour=self.color.DARK_GRAY,
            )
            embed7.set_footer(
                text=inter.message.guild.name, icon_url=inter.guild.icon.url
            )
            await inter.response.send_message(embed=embed7, ephemeral=True)


class DropdownRiveryaBrotherhoodView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(DropdownRiveryaBrotherhood())


def setup(bot):
    bot.add_cog(OwnerInfo(bot))
