import disnake

async def is_premium(user_id: int) -> str:
    pass


async def is_premium_server(guild: disnake.Guild) -> bool:
    pass


async def is_in_blacklist(resource_id: int) -> bool:
    pass


async def interaction_is_not_in_blacklist(interaction: disnake.Interaction) -> bool:
    pass


async def is_shutted_down(command: str) -> bool:
    pass


async def interaction_is_not_shutted_down(interaction: disnake.Interaction) -> bool:
    pass
