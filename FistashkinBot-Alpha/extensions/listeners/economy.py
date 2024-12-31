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
            if data["xp"] >= 5 * (data["level"] ** 2) + 50 * data["level"] + 100:
                await db.update_member(
                    "UPDATE users SET level = level + ? WHERE member_id = ? AND guild_id = ?",
                    [1, message.author.id, message.guild.id],
                )
                await db.update_member(
                    "UPDATE users SET xp = ? WHERE member_id = ? AND guild_id = ?",
                    [0, message.author.id, message.guild.id],
                )

                new_level = self.enum.format_large_number(data["level"] + 1)
                selected_message = random.choice(self.custom_string.LEVEL_UP_TEXT)

                embed = (
                    disnake.Embed(
                        description=selected_message.format(
                            member=message.author.mention, level=new_level
                        ),
                        color=self.color.MAIN,
                    )
                    .set_author(
                        name="Новый уровень!",
                        icon_url=message.author.display_avatar.url,
                    )
                    .set_footer(
                        text="Уведомление будет удалено в течении 10 секунд!"
                    )
                )
                await message.channel.send(embed=embed, delete_after=10.0)

            else:
                if (
                    message.guild.premium_subscriber_role in message.author.roles
                    or message.author.premium_since
                ):
                    await db.update_member(
                        "UPDATE users SET xp = xp + ? WHERE member_id = ? AND guild_id = ?",
                        [
                            self.economy.EXP_ACCRUAL * self.economy.MULTIPLIER,
                            message.author.id,
                            message.guild.id,
                        ],
                    )
                    await db.update_member(
                        "UPDATE users SET total_xp = total_xp + ? WHERE member_id = ? AND guild_id = ?",
                        [
                            self.economy.EXP_ACCRUAL * self.economy.MULTIPLIER,
                            message.author.id,
                            message.guild.id,
                        ],
                    )
                    await db.update_member(
                        "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                        [
                            self.economy.BALANCE_ACCRUAL * self.economy.MULTIPLIER,
                            message.author.id,
                            message.guild.id,
                        ],
                    )
                else:
                    await db.update_member(
                        "UPDATE users SET xp = xp + ? WHERE member_id = ? AND guild_id = ?",
                        [
                            self.economy.EXP_ACCRUAL,
                            message.author.id,
                            message.guild.id,
                        ],
                    )
                    await db.update_member(
                        "UPDATE users SET total_xp = total_xp + ? WHERE member_id = ? AND guild_id = ?",
                        [
                            self.economy.EXP_ACCRUAL,
                            message.author.id,
                            message.guild.id,
                        ],
                    )
                    await db.update_member(
                        "UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",
                        [
                            self.economy.BALANCE_ACCRUAL,
                            message.author.id,
                            message.guild.id,
                        ],
                    )


def setup(bot):
    bot.add_cog(Economy_Event(bot))
