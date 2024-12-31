import json

from .get_season_value import Season


class MainSettings:
    _config = json.load(open("package.json"))
    value = Season.get_seasonal()
    DEVELOPER_ID = 668453200457760786
    BOT_ID = 1035205812806754305
    BOT_VERSION = _config["version"]
    BOT_EMOJI = "<:fistashkinbot:1145318360196845649>"

    GITHUB_AUTHOR = "https://github.com/riverya4life"
    DISCORD_BOT_SERVER = "https://discord.gg/H9XCZSReMj"
    DISCORD_BOT_SERVER_ID = 1037792926383747143
    BOT_SITE = "https://fistashkinbot.xyz"
    BOT_DOCS = "https://docs.fistashkinbot.xyz"
    BOT_INVITE = f"https://discord.com/api/oauth2/authorize?client_id={BOT_ID}&permissions=8&scope=bot%20applications.commands"
    GITHUB_REPOSITORY = "https://github.com/fistashkinbot/FistashkinBot-Beta"
    PATREON = "https://www.patreon.com/FistashkinBot"
    TELEGRAM = "https://t.me/riverya4lifeoff"
    FOOTER_TEXT = value["footer"]
    FOOTER_AVATAR = "https://github.com/riverya4life.png"


class EconomySystem:
    value = Season.get_seasonal()
    MULTIPLIER = value["economy"]["multiplier"]
    CURRENCY_NAME = "🍪"
    CURRENCY_EMOJI = value["emoji"]["currency"]
    EXP_ACCRUAL = value["economy"]["exp"]
    BALANCE_ACCRUAL = value["economy"]["balance"]
    COMMISSION = value["economy"]["commission"]
