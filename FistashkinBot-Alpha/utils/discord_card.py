import os

from easy_pil import Editor, Canvas, load_image_async, Font
from disnake import File
from pathlib import Path
from utils import enums


class LevelCard:
    def __init__(self):
        self.level: int = 1
        self.xp: int = 0
        self.required_xp: int = 1
        self.total_xp: int = 1
        self.rank_pos: int = 1
        self.name: str = None
        self.avatar: str = None
        self.color: str = "#{0:06x}".format(enums.RankCardColor().RANK_CARD_MAIN)
        self.back_color: str = "#{0:06x}".format(
            enums.RankCardColor().RANK_CARD_BACKGROUND
        )
        self.path: str = (
            "https://raw.githubusercontent.com/mario1842/mariocard/main/bg.png"
        )
        self.is_rounded: bool = False

    async def create(self):
        if self.path.startswith("https://"):
            bgc = await load_image_async(str(self.path))
            background = Editor(bgc).resize((900, 300))
        else:
            background = Editor(self.path).resize((900, 300))
        if self.avatar != None:
            profile = await load_image_async(str(self.avatar))
            if self.is_rounded:
                profile = Editor(profile).resize((150, 150)).circle_image()
            else:
                profile = Editor(profile).resize((150, 150))
            background.paste(profile.image, (30, 40))

        poppins = Font(path="utils/assets/fonts/regular.ttf").poppins(size=40)
        poppins_small = Font(path="utils/assets/fonts/regular.ttf").poppins(size=30)
        background.rectangle(
            (30, 210), width=840, height=50, fill=self.back_color, radius=30
        )
        if self.xp != 0:
            background.bar(
                (30, 210),
                max_width=840,
                height=50,
                percentage=(int(self.xp) / int(self.required_xp)) * 100,
                fill=self.color,
                radius=30,
            )
        background.text((200, 40), str(self.name), font=poppins, color="white")

        background.rectangle((200, 100), width=350, height=10, fill=self.color)
        background.text(
            (200, 130),
            f"Rank : # {self.rank_pos}"
            + f"      Level : {self.level}"
            + f"      XP : {self.xp} / {self.required_xp}      ",
            font=poppins_small,
            color="white",
        )

        file = File(fp=background.image_bytes, filename="card.png")
        return file
