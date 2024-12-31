import disnake

from disnake.ext import commands
from utils import enums


class ButtonRolesFistashkinBot(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_click(
        self, button: disnake.ui.Button, interaction: disnake.Interaction
    ):
        role = interaction.guild.get_role(int(button.custom_id))

        if role in interaction.author.roles:
            text = f"**Вы успешно сняли роль {role.mention}**"
            await interaction.author.remove_roles(role)
        else:
            text = f"**Вы успешно добавили роль {role.mention}**"
            await interaction.author.add_roles(role)

        await interaction.response.send_message(text, ephemeral=True)

    @disnake.ui.button(
        label="Новости",
        custom_id="1082789767122526289",
        emoji=f"<:earlysupporter:1074644126055792650>",
        style=disnake.ButtonStyle.green,
    )
    async def news(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await self.interaction_click(button, interaction)


class RoleAddToReactionTest(commands.Cog):

    hidden = True

    def __init__(self, bot):
        self.bot = bot
        self.color = enums.Color()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ButtonRolesFistashkinBot())


def setup(bot: commands.Bot):
    bot.add_cog(RoleAddToReactionTest(bot))
