import os
import json
import random

__all__ = ["fifty_api_fetch_guess"]
__base = f"{os.path.realpath(os.path.dirname(__file__))}/games_src"


async def fifty_api_fetch_guess(category: str):
    paths = {
        "game": f"{__base}/game.json",
        "city": f"{__base}/city.json",
        "logo": f"{__base}/logo.json",
        "country": f"{__base}/country.json",
        "vehicle": f"{__base}/vehicle.json",
    }

    if category not in paths:
        return

    with open(paths[category], "r", encoding="utf-8") as f:
        data = json.load(f)

    item = random.choice(data)
    answers = item["answers"]
    country = item["country"] if category == "city" else None
    text = item["text"] if category == "country" else None
    image = (
        item["image"][0]
        if category == "country"
        else random.choice(item["image"])
        if category == "vehicle"
        else item["image"]
    )

    return item, answers, text, image, country
