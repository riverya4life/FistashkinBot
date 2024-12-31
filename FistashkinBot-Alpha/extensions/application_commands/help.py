import disnake

from disnake.ext import commands
from utils import main, enums

from classes.cooldown import default_cooldown
from classes import database as db


class Slash_Help(commands.Cog):

    hidden = True

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.main = main.MainSettings()
        self.color = enums.Color()

    @staticmethod
    def get_api_command_id(self, name: str):
        command = self.bot.get_global_command_named(name)

        if command:
            return command.id
        else:
            return 0

    @staticmethod
    async def iter_children(self, base, id):
        text = ""

        for sub_command in base.children.values():
            if isinstance(sub_command, commands.SubCommand):
                text += f"</{sub_command.qualified_name}:{id}> "
            else:
                text += await self.iter_children(sub_command, id)

        return text

    @commands.slash_command(
        name=disnake.Localized("help", key="HELP_COMMAND_NAME"),
        description=disnake.Localized(
            "Shows a list of available bot commands.", key="HELP_COMMAND_DESCRIPTION"
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        # debug = [
        #     "OwnerInfo",
        #     "Casino",
        #     "ContextMenu",
        #     "RoleAddToReactionTest",
        #     "Listeners",
        #     "Slash_Help",
        #     "TempVoice",
        #     "DB_Event",
        #     "Logs",
        #     "OnErrors",
        #     "Economy_Event",
        #     "FBJishaku",
        #     "BotLog",
        #     "UpdatePresenceCog",
        #     "UpdateSDCAPI",
        # ]

        embed = (
            disnake.Embed(
                description=f"Бот использует слэш-команды. Для вызова команды введите `/команда`",
                color=self.color.MAIN,
            )
            .set_thumbnail(url=self.bot.user.display_avatar.url)
            .set_author(
                name=f"Доступные команды бота {self.bot.user.name}",
                icon_url=self.bot.user.display_avatar.url,
            )
            .set_footer(text=self.main.FOOTER_TEXT, icon_url=self.main.FOOTER_AVATAR)
        )

        for cog in self.bot.cogs:
            if not isinstance(cog, commands.Cog):
                cog = self.bot.get_cog(cog)

            if cog is None:
                RuntimeError

            if hasattr(cog, 'hidden') and len(cog.get_slash_commands()) > 0 and cog.qualified_name:
                continue

            text = ""

            for slash_command in cog.get_application_commands():
                api_slash_command = self.bot.get_global_command_named(
                    name=slash_command.qualified_name
                )

                if api_slash_command is not None:
                    if isinstance(api_slash_command, commands.SubCommand):
                        return
                    text += f"</{slash_command.qualified_name}:{api_slash_command.id}> "
                    text += await self.iter_children(
                        self,
                        slash_command,
                        self.get_api_command_id(self, slash_command.qualified_name),
                    )

            embed.add_field(
                name=cog.qualified_name,
                value=cog.description + "\n" + text,
                inline=False,
            )

        await inter.edit_original_message(embed=embed)


def setup(bot):
    bot.add_cog(Slash_Help(bot))
