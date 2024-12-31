import disnake

from typing import Optional
from disnake.ext import commands
from utils import MainSettings as main


def default_cooldown(
    inter: disnake.Interaction,
) -> Optional[commands.Cooldown]:
    if (
        inter.guild.premium_subscriber_role in inter.author.roles
        or inter.author.premium_since or inter.author.id == main.DEVELOPER_ID
    ):
        return None
    return commands.Cooldown(rate=1, per=3.0)


def hard_cooldown(
    inter: disnake.Interaction,
) -> Optional[commands.Cooldown]:
    if (
        inter.guild.premium_subscriber_role in inter.author.roles
        or inter.author.premium_since or inter.author.id == main.DEVELOPER_ID
    ):
        return commands.Cooldown(rate=1, per=3.0)
    return commands.Cooldown(rate=1, per=10.0)
