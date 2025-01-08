import disnake
import random

from disnake.ext import commands
from utils import constant, enums, main, custom_string

from classes import database as db


class Economy_Event(commands.Cog):

    hidden = True
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()
        self.economy = main.EconomySystem()
        self.enum = enums.Enum()
        self.custom_string = custom_string.LevelUp()

    @commands.Cog.listener(disnake.Event.message)
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.author == self.bot.user:
            return

        if len(message.content) >= 6:
            data = await db.get_data(message.author)
            required_xp = 5 * (data["level"] ** 2) + 50 * data["level"] + 100

            if data["xp"] >= required_xp:
                member_id = message.author.id
                guild_id = message.guild.id

                await db.update_member(
                    """
                    UPDATE users 
                    SET level = level + 1, xp = 0 
                    WHERE member_id = ? AND guild_id = ?
                    """,
                    [member_id, guild_id],
                )

                new_level = self.enum.format_large_number(data["level"] + 1)
                selected_message = random.choice(self.custom_string.LEVEL_UP_TEXT)
                embed = disnake.Embed(
                    description=selected_message.format(member=message.author.mention, level=new_level),
                    color=self.color.MAIN,
                ).set_author(
                    name="Новый уровень!",
                    icon_url=message.author.display_avatar.url,
                ).set_footer(
                    text="Уведомление будет удалено в течение 10 секунд!"
                )
                await message.channel.send(embed=embed, delete_after=10.0)
            else:
                xp_increment = self.economy.EXP_ACCRUAL
                balance_increment = self.economy.BALANCE_ACCRUAL

                if (
                    message.guild.premium_subscriber_role in message.author.roles
                    or message.author.premium_since
                ):
                    multiplier = self.economy.MULTIPLIER
                    xp_increment *= multiplier
                    balance_increment *= multiplier

                await db.update_member(
                    """
                    UPDATE users 
                    SET 
                        xp = xp + ?, 
                        total_xp = total_xp + ?, 
                        balance = balance + ? 
                    WHERE 
                        member_id = ? AND guild_id = ?
                    """,
                    [
                        xp_increment,
                        xp_increment,
                        balance_increment,
                        message.author.id,
                        message.guild.id,
                    ],
                )



def setup(bot):
    bot.add_cog(Economy_Event(bot))
