import os
from easy_pil import Editor, load_image_async, Font
from disnake import File
from utils import enums


class LevelCard:
    def __init__(self):
        self.level = 1
        self.xp = 0
        self.required_xp = 1
        self.total_xp = 1
        self.rank_pos = 1
        self.name = None
        self.avatar = None
        self.color = "#{0:06x}".format(enums.RankCardColor().RANK_CARD_MAIN)
        self.back_color = "#{0:06x}".format(enums.RankCardColor().RANK_CARD_BACKGROUND)
        self.path = "https://raw.githubusercontent.com/mario1842/mariocard/main/bg.png"
        self.is_rounded = False
        self.poppins_large = Font(path="utils/assets/fonts/regular.ttf").poppins(size=40)
        self.poppins_small = Font(path="utils/assets/fonts/regular.ttf").poppins(size=30)

    async def create(self):
        background = await self._load_background(self.path)

        if self.avatar:
            profile = await self._load_avatar(self.avatar)
            background.paste(profile.image, (30, 40))

        self._draw_progress_bar(background)
        self._add_text(background)

        return File(fp=background.image_bytes, filename="card.png")

    async def _load_background(self, path: str) -> Editor:
        if path.startswith("https://"):
            bgc = await load_image_async(path)
            return Editor(bgc).resize((900, 300))
        return Editor(path).resize((900, 300))

    async def _load_avatar(self, avatar_path: str) -> Editor:
        profile = await load_image_async(avatar_path)
        if self.is_rounded:
            return Editor(profile).resize((150, 150)).circle_image()
        return Editor(profile).resize((150, 150))

    def _draw_progress_bar(self, background: Editor):
        background.rectangle((30, 210), width=840, height=50, fill=self.back_color, radius=30)
        if self.xp > 0:
            background.bar(
                (30, 210),
                max_width=840,
                height=50,
                percentage=(int(self.xp) / int(self.required_xp)) * 100,
                fill=self.color,
                radius=30,
            )

    def _add_text(self, background: Editor):
        background.text((200, 40), str(self.name), font=self.poppins_large, color="white")
        background.rectangle((200, 100), width=350, height=10, fill=self.color)
        background.text(
            (200, 130),
            f"Rank : # {self.rank_pos}      Level : {self.level}      XP : {self.xp} / {self.required_xp}",
            font=self.poppins_small,
            color="white",
        )
