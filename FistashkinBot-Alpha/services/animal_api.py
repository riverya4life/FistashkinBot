import aiohttp

__all__ = ["animal_get_image"]
__base = "https://some-random-api.com"


async def animal_get_image(category: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{__base}/animal/{category}") as response:
            data = await response.json()

    return data.get("image")
