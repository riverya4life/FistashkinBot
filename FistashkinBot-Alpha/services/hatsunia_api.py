import aiohttp

__all__ = ["hatsunia_get_image"]
__base = "https://hmtai.hatsunia.cfd"


async def hatsunia_get_image(category: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{__base}/nsfw/{category}") as response:
            data = await response.json()

    return data.get("url")
