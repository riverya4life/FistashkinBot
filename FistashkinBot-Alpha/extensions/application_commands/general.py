import disnake
import random
import datetime
import platform
import aiohttp
import psutil

from disnake.ext import commands
from bs4 import BeautifulSoup
from utils import constant, enums, main, buttons, paginator, rating
from jishaku.modules import package_version
from utils import CustomError
from humanize import naturaldelta, naturalsize
from os import getpid
from helpers import BioButtons
from core import config

from classes.cooldown import default_cooldown
from classes import database as db


class General(commands.Cog, name="🛠️ Утилиты"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.profile = constant.ProfileEmojis()
        self.main = main.MainSettings()
        self.server = constant.ServerEmojis()
        self.color = enums.Color()
        self.economy = main.EconomySystem()
        self.enum = enums.Enum()
        self.rating = rating.Rating()
        self.config = config.Config()

    async def autocomplete_faq(
        inter: disnake.ApplicationCommandInteraction, string: str
    ):
        return list(
            filter(
                lambda question: string in question,
                [i["question"] for i in constant.Faq.FAQ],
            )
        )

    @commands.slash_command(
        name=disnake.Localized("faq", key="FAQ_COMMAND_NAME"),
        description=disnake.Localized(
            "See the most frequently asked questions.", key="FAQ_COMMAND_DESCRIPTION"
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def faq(
        self,
        inter: disnake.ApplicationCommandInteraction,
        question: str = commands.Param(
            name=disnake.Localized("question", key="FAQ_QUESTION_COMMAND_NAME"),
            description=disnake.Localized(
                "Choose your question here.", key="FAQ_QUESTION_COMMAND_DESCRIPTION"
            ),
            autocomplete=autocomplete_faq,
        ),
    ):
        if question in [i["question"] for i in constant.Faq.FAQ]:
            await inter.response.defer(ephemeral=False)
            embed = (
                disnake.Embed(
                    description=[
                        i["answer"] for i in constant.Faq.FAQ if i["question"] == question
                    ][0],
                    color=self.color.MAIN,
                )
                .set_author(
                    name=f"FAQ: {question}", icon_url=self.bot.user.display_avatar.url
                )
                .set_footer(
                    text="В случае, если вашей ошибки нет в списке, обратитесь в поддержку.",
                    icon_url=self.main.FOOTER_AVATAR,
                )
            )
            await inter.edit_original_message(embed=embed, view=buttons.Links())

        else:
            await inter.edit_original_message(
                "Вопрос не найден. Не стесняйтесь задавать свой вопрос на одном из каналов."
            )

    @commands.slash_command(
        name=disnake.Localized("userinfo", key="USER_INFO_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows user information.", key="USER_INFO_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def userinfo(
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
        await inter.response.defer(ephemeral=False)

        if not member:
            member = inter.author

        data = await db.get_data(member)
        user = await self.bot.fetch_user(member.id)
        bio = await db.get_bio(member)

        registerf = disnake.utils.format_dt(member.created_at, style="f")
        registerr = disnake.utils.format_dt(member.created_at, style="R")
        joinedf = disnake.utils.format_dt(member.joined_at, style="f")
        joinedr = disnake.utils.format_dt(member.joined_at, style="R")

        rank_rating_pos = await self.rating.rating_rank(member=member)
        balance_rating_pos = await self.rating.rating_balance(member=member)

        level = self.enum.format_large_number(data["level"])
        xp = self.enum.format_large_number(data["xp"])
        total_xp = self.enum.format_large_number(data["total_xp"])
        xp_to_lvl = self.enum.format_large_number(
            5 * (data["level"] ** 2) + 50 * data["level"] + 100
        )
        balance = self.enum.format_large_number(data["balance"])
        ranking_position = self.enum.format_large_number(rank_rating_pos[0])
        ranking_members = self.enum.format_large_number(rank_rating_pos[1])
        balance_position = self.enum.format_large_number(balance_rating_pos[0])
        balance_members = self.enum.format_large_number(balance_rating_pos[1])

        badges = [
            self.profile.BADGES[badge.name]
            for badge in member.public_flags.all()
            if badge.name in self.profile.BADGES
        ]
        if member.id == self.main.DEVELOPER_ID:
            badges.append(self.profile.DEVELOPER)  # Developer
        if member.premium_since:
            badges.append(self.profile.NITRO_BOOSTER)  # Nitro Booster
        if member.display_avatar.is_animated() or user.banner:
            badges.append(self.profile.BOOSTER_SUBSCRIBER)  # Nitro Subscriber
        if member.discriminator == "0":
            badges.append(self.profile.UPDATED_NICKNAME)  # Updated Nickname

        description = [
            f"**Имя {'бота' if member.bot else 'участника'}:** {member} ({member.mention})",
            f"**Статус:** {self.profile.STATUS[member.status]}",  # **| Устройство:** {'`📱 Mobile`' if member.is_on_mobile() else '`🖥️ Desktop`'}
            f"**Присоединился:** {joinedf} ({joinedr})",
            f"**Дата регистрации:** {registerf} ({registerr})",
        ]

        view = None
        if not member.bot:
            for activity in member.activities:
                if activity.type == disnake.ActivityType.playing:
                    description.append(
                        f"**Играет в:** {activity.name} | <t:{round(activity.created_at.timestamp())}:R>"
                    )
                elif activity.type == disnake.ActivityType.streaming:
                    description.append(f"**Стримит:** {activity.name}")
                elif activity.type == disnake.ActivityType.watching:
                    description.append(f"**Смотрит:** {activity.name}")
                elif activity.type == disnake.ActivityType.listening and isinstance(
                    activity, disnake.Spotify
                ):
                    description.append(
                        f"**Слушает Spotify:** {self.profile.SPOTIFY} **[{activity.title} | {', '.join(activity.artists)}]({activity.track_url})**"
                    )
                    view = buttons.Spotify_Link(url=activity.track_url)
                elif activity.type == disnake.ActivityType.listening:
                    description.append(f"**Слушает:** {activity.name}")

        if (
            member.bot
            or member != inter.author
            and bio
            == "Вы можете добавить сюда какую-нибудь полезную информацию о себе командой `/осебе`"
        ):
            bio = None

        embed = (
            disnake.Embed(
                description=bio,
                color=user.accent_color,
                timestamp=inter.created_at,
            )
            .add_field(
                name="Основная информация",
                value="\n".join(description),
                inline=False,
            )
            .add_field(name="Значки", value=" ".join(badges), inline=True) if badges and not member.bot else None
        )

        if (not member.bot):
            embed.add_field(
                name="Рейтинг",
                value=f"# {ranking_position}/{ranking_members}",
                inline=True,
            )
            embed.add_field(
                name="Уровень",
                value=level,
                inline=True,
            )
            embed.add_field(
                name="Опыт",
                value=f"{xp}/{xp_to_lvl} (всего {total_xp})",
                inline=True,
            )
            embed.add_field(
                name="Экономика",
                value=f"{balance} {self.economy.CURRENCY_NAME} | # {balance_position}/{balance_members}",
                inline=True,
            )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=user.banner.url if user.banner else None)
        embed.set_footer(text=f"ID: {member.id}", icon_url=member.display_avatar.url)
        embed.set_author(
            name=f"Информация о {'боте' if member.bot else 'участнике'} {member.display_name}",
            icon_url=member.display_avatar.url,
        )

        await inter.edit_original_message(embed=embed, view=view)

    @commands.slash_command(
        name=disnake.Localized("serverinfo", key="SERVER_INFO_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows server information.", key="SERVER_INFO_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def serverinfo(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        shard_names = {
            "0": "#1 (Рёмен)",
            "1": "#2 (Аква)",
            "2": "#3 (Дикси)",
            "3": "#4 (Гроув)",
            "4": "#5 (Хакари)",
        }

        total_members = self.enum.format_large_number(len(inter.guild.members))
        members = self.enum.format_large_number(
            len(list(filter(lambda m: m.bot == False, inter.guild.members)))
        )
        bots = self.enum.format_large_number(
            len(list(filter(lambda m: m.bot == True, inter.guild.members)))
        )

        members_online = self.enum.format_large_number(
            len(list(filter(lambda m: str(m.status) == "online", inter.guild.members)))
        )
        members_idle = self.enum.format_large_number(
            len(list(filter(lambda m: str(m.status) == "idle", inter.guild.members)))
        )
        members_dnd = self.enum.format_large_number(
            len(list(filter(lambda m: str(m.status) == "dnd", inter.guild.members)))
        )
        members_offline = self.enum.format_large_number(
            len(list(filter(lambda m: str(m.status) == "offline", inter.guild.members)))
        )

        total_channels = self.enum.format_large_number(len(inter.guild.channels))
        text_channels = self.enum.format_large_number(len(inter.guild.text_channels))
        voice_channels = self.enum.format_large_number(len(inter.guild.voice_channels))

        members_field = [
            f"{self.server.MEMBERS_TOTAL} Всего: **{total_members}**",
            f"{self.server.MEMBERS} Людей: **{members}**",
            f"{self.server.BOT} Ботов: **{bots}**",
        ]
        if inter.guild.premium_subscribers:
            members_field.append(
                f"Бустеров: **{len(inter.guild.premium_subscribers)}**"
            )

        members_field_status = [
            f"{self.profile.ONLINE} В сети: **{members_online}**",
            f"{self.profile.IDLE} Неактивен: **{members_idle}**",
            f"{self.profile.DND} Не беспокоить: **{members_dnd}**",
            f"{self.profile.OFFLINE} Не в сети: **{members_offline}**",
        ]
        channels_field = []
        if inter.guild.channels:
            channels_field.append(
                f"{self.server.CHANNELS_TOTAL} Всего: **{total_channels}**"
            )
        if inter.guild.text_channels:
            channels_field.append(
                f"{self.server.TEXT_CHANNEL} Текстовых: **{text_channels}**"
            )
        if inter.guild.voice_channels:
            channels_field.append(
                f"{self.server.VOICE_CHANNEL} Голосовых: **{voice_channels}**"
            )
        if inter.guild.stage_channels:
            channels_field.append(
                f"{self.server.STAGE_CHANNEL} Трибун: **{len(inter.guild.stage_channels)}**"
            )
        if inter.guild.forum_channels:
            channels_field.append(
                f"{self.server.FORUM_CHANNEL} Форумов: **{len(inter.guild.forum_channels)}**"
            )

        embed = (
            disnake.Embed(
                description=None
                if not inter.guild.description
                else inter.guild.description,
                color=self.color.MAIN,
            )
            .add_field(
                name="Участники:",
                value="\n".join(members_field),
                inline=True,
            )
            .add_field(
                name="По статусам:",
                value="\n".join(members_field_status),
                inline=True,
            )
            .add_field(
                name="Каналы:",
                value="\n".join(channels_field),
                inline=True,
            )
            .add_field(
                name="Владелец:",
                value=f"{inter.guild.owner}\n{inter.guild.owner.mention}",
                inline=True,
            )
            .add_field(
                name="Создан:",
                value=f"<t:{round(inter.guild.created_at.timestamp())}:D>\n"
                f"<t:{round(inter.guild.created_at.timestamp())}:R>",
                inline=True,
            )
            .add_field(
                name="Прочее:",
                value=f"Стикеров: **{len(inter.guild.stickers)}**\n"
                f"Эмодзи: **{len(inter.guild.emojis)}**\n"
                f"Уровень буста: **{inter.guild.premium_tier}**\n"
                f"Количество ролей: **{len(inter.guild.roles[:-1])}**",
                inline=True,
            )
            .set_thumbnail(url=inter.guild.icon.url if inter.guild.icon else None)
            .set_image(url=inter.guild.banner.url if inter.guild.banner else None)
            .set_footer(
                text=f"ID: {inter.guild.id} • Звено: {shard_names[str(inter.guild.shard_id)]}"
            )
            .set_author(
                name=f"Информация о сервере {inter.guild.name}",
                icon_url=inter.guild.icon.url if inter.guild.icon else None,
            )
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("avatar", key="AVATAR_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows the avatar of the mentioned user or the user who called the command.",
            key="AVATAR_COMMAND_DESCRIPTION",
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def avatar(
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
        await inter.response.defer(ephemeral=False)
        if not member:
            member = inter.author

        formats = [
            f"[**[PNG]**]({member.display_avatar.replace(format='png', size=4096).url}) | ",
            f"[**[JPG]**]({member.display_avatar.replace(format='jpg', size=4096).url})",
            f" | [**[WebP]**]({member.display_avatar.replace(format='webp', size=4096).url})",
            f" | [**[GIF]**]({member.display_avatar.replace(format='gif', size=4096).url})"
            if member.display_avatar.is_animated()
            else "",
            f"\n[**[Стандартный аватар]**]({member.default_avatar.url})",
        ]

        description_format = "".join(formats)
        embed = (
            disnake.Embed(
                description=f"Нажмите ниже чтобы скачать аватар\n{description_format}",
                color=self.color.MAIN,
            )
            .set_image(url=member.display_avatar.url)
            .set_author(
                name=f"Аватар {'бота' if member.bot else 'участника'} {member.display_name}",
                icon_url=member.display_avatar.url,
            )
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("roles", key="ROLES_LIST_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows all server roles.", key="ROLES_LIST_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def roles(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        all_roles = []
        guild = inter.guild
        roles = [
            role
            for role in guild.roles
            if role in inter.guild.roles
            if role != inter.guild.default_role
        ]
        roles.reverse()

        items_per_page = 10
        pages = [
            roles[i : i + items_per_page] for i in range(0, len(roles), items_per_page)
        ]

        embed_pages = []
        roles_count = self.enum.format_large_number(len(inter.guild.roles[:-1]))
        for i, page in enumerate(pages):
            embed = (
                disnake.Embed(
                    description="\n".join([role.mention for role in page])
                )
                .set_author(
                    name=f"Роли сервера {inter.guild.name} [{roles_count}]",
                    icon_url=inter.guild.icon.url if inter.guild.icon else None,
                )
            )
            embed_pages.append(embed)

        view = paginator.Paginator(inter, embeds=embed_pages)
        message = await inter.edit_original_message(embed=embed_pages[0], view=view)
        view.message = message

    @commands.slash_command(
        name=disnake.Localized("botinfo", key="BOT_INFO_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows interesting information about the bot.",
            key="BOT_INFO_COMMAND_DESCRIPTION",
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def botinfo(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        developer = await self.bot.fetch_user(self.main.DEVELOPER_ID)
        embed = (
            disnake.Embed(
                description=f"👋 Привет! Меня зовут Фисташкин! Я небольшой бот с кучкой небольших полезностей!\n"
                f"\nМой префикс `/` (слэш), но ты также можешь просто @обратиться ко мне для справки. Взгляни на команду `/хелп` для более детальной информации о моих возможностях 🍪",
                colour=self.color.MAIN,
            )
            .set_author(
                name=f"{self.bot.user.name}",
                icon_url=self.bot.user.display_avatar.url,
                url=self.main.BOT_SITE,
            )
            .add_field(
                name="Сборка:",
                value=self.main.BOT_VERSION,
                inline=True,
            )
            .add_field(
                name="Мой разработчик:",
                value=f"<:riverya4life:1065581416357826560> [{developer}](https://discord.com/users/{developer.id})",
                inline=True,
            )
            .set_thumbnail(url=self.bot.user.display_avatar.url)
            .set_footer(text=self.main.FOOTER_TEXT, icon_url=self.main.FOOTER_AVATAR)
        )
        """embed.add_field(
            name="Дата создания:",
            value=f"<t:{round(self.bot.user.created_at.timestamp())}:D> (<t:{round(self.bot.user.created_at.timestamp())}:R>)",
            inline=False,
        )"""
        await inter.edit_original_message(embed=embed, view=buttons.Links())

    @commands.slash_command(
        name=disnake.Localized("stats", key="BOT_STATS_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows bot statistics.", key="BOT_STATS_COMMAND_DESCRIPTION"
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def stats(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)

        shard_names = {
            "0": "#1 (Рёмен)",
            "1": "#2 (Аква)",
            "2": "#3 (Дикси)",
            "3": "#4 (Гроув)",
            "4": "#5 (Хакари)",
        }

        channels_count = 0
        total_connections = 0
        for guild in self.bot.guilds:
            channels_count += len(guild.channels)
            for voice_channel in guild.voice_channels:
                if voice_channel.members:
                    total_connections += 1

        bot_guilds = self.enum.format_large_number(len(self.bot.guilds))
        bot_guilds_members = self.enum.format_large_number(len(self.bot.users))
        bot_guilds_channels = self.enum.format_large_number(int(channels_count))
        bot_active_voice_connections = self.enum.format_large_number(
            int(total_connections)
        )

        uptimebot = disnake.utils.format_dt(
            round(self.bot.uptime.timestamp()), style="R"
        )
        cpu = psutil.cpu_percent()
        ram = naturalsize(psutil.Process(getpid()).memory_info().rss)
        command_counter = await db.get_used_commands()
        formatted_command_counter_result = self.enum.format_large_number(
            command_counter
        )
        if command_counter >= 100000000:
            formatted_command_counter_result = f"\n{formatted_command_counter_result}"
        else:
            formatted_command_counter_result = f"{formatted_command_counter_result}"

        embed = (
            disnake.Embed(
                description=f"🔧 **Конфигурация**\n"
                f"**Версия бота:** v{self.main.BOT_VERSION}\n"
                f"**Версия Python:** v{platform.python_version()}\n"
                f"**Библиотеки:** disnake v{package_version('disnake')}, disnake-jishaku v{package_version('disnake-jishaku')}\n"
                f"**ОС:** {platform.platform()}",
                colour=self.color.MAIN,
                timestamp=inter.created_at,
            )
            .set_author(
                name=f"Статистика {self.bot.user.name}",
                icon_url=self.bot.user.display_avatar.url,
            )
            .add_field(
                name="✨ Основная",
                value=f"**Серверов:** {bot_guilds}\n"
                f"**Участников:** {bot_guilds_members}\n"
                f"**Каналов:** {bot_guilds_channels}\n"
                f"**Голосовых соединений:** {bot_active_voice_connections}\n"
                f"**Кластер:** # {inter.guild.shard_id + 1} / {len(self.bot.shards)} | {shard_names[str(inter.guild.shard_id)]}",
                inline=True,
            )
            .add_field(
                name="🤖 Платформа",
                value=f"**Обработано команд:** {formatted_command_counter_result}\n"
                f"**Задержка:** {round(self.bot.latency * 1000)} мс\n"
                f"**RAM:** {ram}\n"
                f"**Нагрузка:** {cpu}%\n"
                f"**Запущена**: {uptimebot}\n",
                inline=True,
            )
            .set_thumbnail(url=self.bot.user.display_avatar.url)
            .set_footer(text=self.main.FOOTER_TEXT, icon_url=self.main.FOOTER_AVATAR)
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("ping", key="BOT_PING_COMMAND_NAME"),
        description=disnake.Localized(
            "Testing bot functionality and delays.", key="BOT_PING_COMMAND_DESCRIPTION"
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        embed = disnake.Embed(
            description=f"{inter.author.mention}, я живой и кушаю фисташки! "
            f"Мой пинг: {round(self.bot.latency * 1000)} мс!",
            color=self.color.MAIN,
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("roleinfo", key="ROLEINFO_COMMAND_NAME"),
        description=disnake.Localized(
            "Displays information about any role on the server.",
            key="ROLEINFO_COMMAND_DESCRIPTION",
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def role_info(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role = commands.Param(
            name=disnake.Localized("role", key="TARGET_ROLE_NAME"),
            description=disnake.Localized(
                "Select a role.", key="TARGET_ROLE_DESCRIPTION"
            ),
        ),
    ):
        await inter.response.defer(ephemeral=False)
        role_info_array = [
            f"Цвет роли: **{hex(role.color.value)} ({'#{0:06x}'.format(role.color.value)})**",
            f"Интеграция: **{'Да' if role.is_integration() else 'Нет'}**",
            f"Участников с этой роли: **{len(role.members)}**",
            f"Упоминание роли: {role.mention}",
            f"Позиция: **{role.position}**",
            f"Роль создана: <t:{round(role.created_at.timestamp())}:D>",
        ]
        embed = (
            disnake.Embed(
                description="\n".join(role_info_array),
                color=role.color
            )
            .set_author(
                name=f"Информация о роли {role.name}",
                icon_url=inter.guild.icon.url if inter.guild.icon else None,
            )
            .set_footer(text=f"ID роли: {role.id}")
            .set_thumbnail(url=role.icon.url if role.icon else None)
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("clist", key="CLIST_COMMAND_NAME"),
        description=disnake.Localized(
            "Displays a list of members with a specific role.",
            key="CLIST_COMMAND_DESCRIPTION",
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def clist(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role = commands.Param(
            name=disnake.Localized("role", key="TARGET_ROLE_NAME"),
            description=disnake.Localized(
                "Select a role.", key="TARGET_ROLE_DESCRIPTION"
            ),
        ),
    ):
        await inter.response.defer(ephemeral=False)
        data = [(member.mention or member.nick) for member in role.members]
        member_count = self.enum.format_large_number(len(role.members))

        counter = 0
        paginated_data = []
        for i in range(0, len(data), 10):
            paginated_data.append("\n".join(data[i : i + 10]))

        embeds = []
        for i, page_data in enumerate(paginated_data):
            embed = (
                disnake.Embed(
                    description=f"{page_data}\n",
                    color=role.color
                )
                .set_author(
                    name=f"Все участники с ролью {role} [{member_count}]\n",
                    icon_url=inter.guild.icon.url if inter.guild.icon else None,
                )
                .set_thumbnail(url=role.icon.url if role.icon else None)
            )
            embeds.append(embed)

        view = paginator.Paginator(inter, embeds)
        message = await inter.edit_original_message(embed=embeds[0], view=view)
        view.message = message

    @commands.slash_command(
        name=disnake.Localized("emoji-random", key="EMOJI_RANDOM_COMMAND_NAME"),
        description=disnake.Localized(
            "Finds a random emoji.", key="EMOJI_RANDOM_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.is_nsfw()
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def random_emoji(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        emoji = random.choice(inter.bot.emojis)
        embed = (
            disnake.Embed(
                description=f"[**Скачать эмодзик**]({emoji.url})",
                color=self.color.MAIN
            )
            .set_author(
                name=f"Эмодзи с {emoji.guild.name}",
                icon_url=emoji.guild.icon.url if emoji.guild.icon else None,
            )
            .set_footer(text=f"ID: {emoji.id}")
            .set_image(url=emoji.url)
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("bio", key="USER_BIO_COMMAND_NAME"),
        description=disnake.Localized(
            "Changes the biography of the user.", key="USER_BIO_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def bio(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        await inter.response.defer(ephemeral=False)
        user = await self.bot.fetch_user(inter.author.id)
        bio = await db.get_bio(inter.author)
        if (
            bio
            == "Вы можете добавить сюда какую-нибудь полезную информацию о себе командой `/осебе`"
        ):
            bio = "Биография отсутствует."

        embed = (
            disnake.Embed(
                description=bio,
                color=self.color.MAIN,
            )
            .set_thumbnail(url=inter.author.display_avatar.url)
            .set_image(url=user.banner.url if user.banner else None)
            .set_author(
                name=f"Биография {inter.author}", icon_url=inter.author.display_avatar.url
            )
        )
        view = BioButtons(inter)
        message = await inter.edit_original_message(embed=embed, view=view)
        view.message = message

    @commands.slash_command(
        name=disnake.Localized("monitoring", key="MONITORING_COMMAND_NAME"),
        description=disnake.Localized(
            "Displays the monitors where the bot is present.",
            key="MONITORING_COMMAND_DESCRIPTION",
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def monitoring(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        text = [
            f"**А вот мини-инструкция, как апнуть {self.bot.user.name}:**\n"
            f"1. Заходите поочередно на каждый из мониторингов, далее, авторизуетесь через свой аккаунт.\n"
            f"2. После нажимаете на __**оценить**__, проходите капчу, и всё. Желательно делать так каждые 4 часа (для SD.C)."
        ]
        embed = (
            disnake.Embed(
                description="".join(text),
                color=self.color.MAIN
            )
            .set_author(
                name=f"{self.bot.user.name} на мониторингах!",
                icon_url=self.bot.user.display_avatar.url,
            )
            .set_footer(text="Ну и отзыв по желанию 🥰")
        )
        await inter.edit_original_message(embed=embed, view=buttons.BotMonitoring())

    @commands.slash_command(
        name=disnake.Localized("github", key="GITHUB_COMMAND_NAME"),
        description=disnake.Localized(
            "Github repository information.", key="GITHUB_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def github(
        self,
        inter: disnake.ApplicationCommandInteraction,
        arg: str = commands.Param(
            name=disnake.Localized("repository", key="GITHUB_ARG_NAME"),
            description=disnake.Localized(
                "Specify the name of the repository in the format nick/repository.",
                key="GITHUB_ARG_DESCRIPTION",
            ),
        ),
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.github.com/repos/{arg}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await inter.response.defer(ephemeral=False)
                    embed = (
                        disnake.Embed(color=self.color.DARK_GRAY)
                        .set_author(
                            name=data["owner"]["login"],
                            icon_url=data["owner"]["avatar_url"],
                            url=data["owner"]["html_url"],
                        )
                        .set_thumbnail(url=data["owner"]["avatar_url"])
                        .add_field(
                            name="Репозиторий:",
                            value=f"[{data['name']}]({data['html_url']})",
                            inline=True,
                        )
                        .add_field(name="Язык:", value=data["language"], inline=True)
                    )

                    license_url = "None"
                    if (
                        "license" in data
                        and data["license"]
                        and "url" in data["license"]
                    ):
                        async with session.get(data["license"]["url"]) as license_resp:
                            if license_resp.status == 200:
                                license_data = await license_resp.json()
                                license_url = f"[{license_data.get('spdx_id', 'Unknown')}]({license_data.get('html_url', '')})"

                    embed.add_field(name="Лицензия:", value=license_url, inline=True)
                    if data["stargazers_count"] != 0:
                        embed.add_field(
                            name="Звёзд:", value=data["stargazers_count"], inline=True
                        )
                    if data["forks_count"] != 0:
                        embed.add_field(
                            name="Форков:", value=data["forks_count"], inline=True
                        )
                    if data["open_issues"] != 0:
                        embed.add_field(
                            name="Проблем:", value=data["open_issues"], inline=True
                        )
                    embed.add_field(
                        name="Описание:", value=data["description"], inline=False
                    )

                    async with session.get(data["html_url"]) as html_resp:
                        html_text = await html_resp.text()
                        for meta in BeautifulSoup(
                            html_text, features="html.parser"
                        ).find_all("meta"):
                            try:
                                if meta.attrs["property"] == "og:image":
                                    embed.set_image(url=meta.attrs["content"])
                                    break
                            except:
                                pass

                    await inter.edit_original_message(embed=embed)
                elif resp.status == 404:
                    raise CustomError("❌ Репозиторий не найден!")
                else:
                    raise CustomError(
                        "❌ Неизвестная ошибка при получении информации репозитория!"
                    )


def setup(bot):
    bot.add_cog(General(bot))
