import disnake

from utils import constant, main


class Links(disnake.ui.View):
    def __init__(self):
        self.otheremoji = constant.OtherEmojis()
        self.main = main.MainSettings()

        super().__init__()
        self.add_item(
            disnake.ui.Button(
                label="Наш Сайт",
                url=self.main.BOT_SITE,
                emoji="🍪",
            )
        )
        self.add_item(
            disnake.ui.Button(
                label="Документация",
                url=self.main.BOT_DOCS,
                emoji="🗃️",
            )
        )


class Support_Link(disnake.ui.View):
    def __init__(self):
        self.otheremoji = constant.OtherEmojis()
        self.main = main.MainSettings()

        super().__init__()
        self.add_item(
            disnake.ui.Button(
                label="Сервер поддержки",
                url=self.main.DISCORD_BOT_SERVER,
                emoji=self.main.BOT_EMOJI,
            )
        )


class BotMonitoring(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(
            disnake.ui.Button(
                label="Top.gg",
                url="https://top.gg/bot/991338113630752928",
            )
        ),
        self.add_item(
            disnake.ui.Button(
                label="BotiCord",
                url="https://boticord.top/bot/991338113630752928",
            )
        )
        self.add_item(
            disnake.ui.Button(
                label="SD.C",
                url="https://bots.server-discord.com/991338113630752928",
            )
        )


class Developer_Link(disnake.ui.View):
    def __init__(self):
        self.otheremoji = constant.OtherEmojis()
        self.main = main.MainSettings()

        super().__init__()
        self.add_item(
            disnake.ui.Button(
                label="Разработчик",
                url="https://discord.com/users/668453200457760786",
                emoji=self.main.BOT_EMOJI,
            )
        )


class Spotify_Link(disnake.ui.View):
    def __init__(self, url):
        self.otheremoji = constant.ProfileEmojis()
        self.url = url

        super().__init__()
        self.add_item(
            disnake.ui.Button(
                label="Открыть Spotify",
                url=self.url,
                emoji=self.otheremoji.SPOTIFY,
            )
        )


class Avatar_Link(disnake.ui.View):
    def __init__(self, url):
        self.otheremoji = constant.ProfileEmojis()
        self.png_url = png_url
        self.jpg_url = jpg_url
        self.webp_url = webp_url
        self.gif_url = gif_url
        self.def_url = def_url

        super().__init__()
        self.add_item(
            disnake.ui.Button(
                label="PNG",
                url=self.png_url,
            )
        ),
        self.add_item(
            disnake.ui.Button(
                label="JPG",
                url=self.jpg_url,
            )
        ),
        self.add_item(
            disnake.ui.Button(
                label="WebP",
                url=self.webp_url,
            )
        ),
        if member.display_avatar.is_animated():
            self.add_item(
                disnake.ui.Button(
                    label="GIF",
                    url=self.gif_url,
                )
            ),
        self.add_item(
            disnake.ui.Button(
                label="Стандартный аватар",
                url=self.def_url,
            )
        ),
