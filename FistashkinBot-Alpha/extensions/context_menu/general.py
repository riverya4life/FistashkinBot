import disnake

from disnake.ext import commands
from utils import constant, main, enums, buttons, rating

from classes.cooldown import default_cooldown
from classes import database as db


class ContextMenu(commands.Cog):

    hidden = True

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.main = main.MainSettings()
        self.economy = main.EconomySystem()
        self.profile = constant.ProfileEmojis()
        self.color = enums.Color()
        self.enum = enums.Enum()
        self.rating = rating.Rating()

    @commands.user_command(
        name=disnake.Localized("Avatar", key="CONTEXT_MENU_COMMAND_AVATAR"),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def avatar(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = None,
    ):
        await inter.response.defer(ephemeral=True)
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
                name=f"Аватар {member.display_name}", icon_url=member.display_avatar.url
            )
        )
        await inter.edit_original_message(embed=embed)

    @commands.user_command(
        name=disnake.Localized("UserInfo", key="CONTEXT_MENU_COMMAND_USERINFO"),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def userinfo(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = None,
    ):
        await inter.response.defer(ephemeral=True)

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
            .set_thumbnail(url=member.display_avatar.url)
            .set_image(url=user.banner.url if user.banner else None)
            .set_footer(text=f"ID: {member.id}", icon_url=member.display_avatar.url)
            .set_author(
                name=f"Информация о {'боте' if member.bot else 'участнике'} {member.display_name}",
                icon_url=member.display_avatar.url,
            )
        )

        if (
            not member.bot
            and await db.fetch_rank_system(guild=inter.guild) != False
        ):
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

        await inter.edit_original_message(embed=embed, view=view)


def setup(bot):
    bot.add_cog(ContextMenu(bot))
