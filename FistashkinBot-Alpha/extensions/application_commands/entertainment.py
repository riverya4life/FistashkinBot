import disnake
import random
import asyncio

from disnake.ext import commands
from utils import constant, enums, CustomError, generation_string, main
from helpers import MineswiperView
from itertools import repeat
from services import (
    fifty_api_fetch_guess,
    animal_get_image,
    hatsunia_get_image,
    waifu_get_image,
)
from classes.cooldown import default_cooldown
from classes import database as db


class Entertainment(commands.Cog, name="😄 Развлечение"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.eightball = constant.EightBall()
        self.color = enums.Color()
        self.gen = generation_string.Generation()
        self.main = main.MainSettings

    NSFW_DESCRIPTIONS = {
        "Задницы": "ass",
        "БДСМ": "bdsm",
        "Кам)": "cum",
        "Девушки-доминаторы": "femdom",
        "Хентай": "hentai",
        "Инцест": "incest",
        "Мастурбация": "masturbation",
        "Эротика": "ero",
        "Оргия": "orgy",
        "Юри": "yuri",
        "Трусики": "pantsu",
        "Очко (очки)": "glasses",
        "Работа ручками": "handjob",
        "Блоуджоб": "blowjob",
        "Работа грудью": "boobjob",
        "Просто грудь": "boobs",
        "Ножки": "footjob",
        "Ещё больше хентая": "gif",
        "Ахегао": "ahegao",
        "Школьницы и не только...": "uniform",
        "Щупальца": "tentacles",
        "Бёдра": "thighs",
        "Кошко-девочки": "nsfwNeko",
        "Юбочки": "zettaiRyouiki",
    }

    ANIME_GIRLS = {
        "Мегумин": "megumin",
        "Шинобу": "shinobu",
        "Ававо": "awoo",
        "Неко": "neko",
        "Поке": "poke",
        "Рандом вайфу": "waifu",
    }

    INTERACTION_CHOICE = {
        "Погладить": "pat",
        "Обнять": "hug",
        "Поцеловать": "kiss",
        "Облизнуть": "lick",
        "Прижать": "cuddle",
        "Взять за руку": "handhold",
        "Покормить": "nom",
        "Дать пощечину": "slap",
        "Сделать кусь": "bite",
        "Дать пять": "highfive",
    }

    INTERACTION_DESCRIPTIONS = {
        "pat": "{author} погладил(-а) {user}",
        "hug": "{author} обнял(-а) {user}",
        "kiss": "{author} поцеловал(-а) {user}",
        "lick": "{author} облизнул(-а) {user}",
        "cuddle": "{author} прижал(-а) к себе {user}",
        "handhold": "{author} взял(-а) за руку {user}",
        "nom": "{author} покормил(-а) {user}",
        "slap": "{author} дал(-а) пощечину {user}",
        "bite": "{author} сделал(-а) кусь {user}",
        "highfive": "{author} дал(-а) пять {user}",
    }

    INTERACTION_DESCRIPTIONS_MYSELF = {
        "pat": "{author} погладил(-а) себя",
        "hug": "{author} обнял(-а) себя",
        "kiss": "{author} поцеловал(-а) себя",
        "lick": "{author} облизнул(-а) себя",
        "cuddle": "{author} прижал(-а) себя к себе",
        "handhold": "{author} взял(-а) себя за руку",
        "nom": "{author} покормил(-а) себя",
        "slap": "{author} дал(-а) себе пощёчину",
        "bite": "{author} укусил(-а) себя",
        "highfive": "{author} дал(-а) себе пять",
    }

    INTERACTION_DESCRIPTIONS_FISTASHKIN = {
        "pat": "{author} погладил(-а) {user}",
        "hug": "{author} обнял(-а) {user}",
        "kiss": "{author} поцеловал(-а) {user}",
        "lick": "{author} облизнул(-а) {user}",
        "cuddle": "{author} прижал(-а) к себе {user}",
        "handhold": "{author} взял(-а) за руку {user}",
        "nom": "{author} покормил(-а) {user}",
        "slap": "{author} ну не надо так со мной :(",
        "bite": "{author} ай... За шо ты так со мной?",
        "highfive": "{author} держи пятюню 🖐️",
    }

    ANIMALS_LIST = {
        "Лиса": "fox",
        "Енот": "raccoon",
        "Кошка": "cat",
        "Собака": "dog",
        "Птица": "bird",
        "Панда": "panda",
    }

    GUESS_GAME = {
        "🎮 Игры": "game",
        "🌇 Города": "city",
        "🍃 Логотипы": "logo",
        "🌎 Страны": "country",
        "🚗 Транспорт": "vehicle",
    }

    @commands.slash_command(
        name=disnake.Localized("ball", key="EIGHT_BALL_COMMAND_NAME"),
        description=disnake.Localized(
            "Answers a users question.", key="EIGHT_BALL_COMMAND_DESCRIPTION"
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def ball(
        self,
        inter: disnake.ApplicationCommandInteraction,
        question=commands.Param(
            name=disnake.Localized("question", key="EIGHT_BALL_COMMAND_TEXT_NAME"),
            description=disnake.Localized(
                "Enter your question.", key="EIGHT_BALL_COMMAND_TEXT_DESCRIPTION"
            ),
        ),
    ):
        await inter.response.defer(ephemeral=False)
        embed = (
            disnake.Embed(description=question, color=self.color.MAIN)
            .add_field(
                name="**Ответ: **",
                value=random.choice(self.eightball.RESPONSES),
                inline=False,
            )
            .set_author(name="🎱 Игра 8ball")
            .set_thumbnail(url=inter.author.display_avatar.url)
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("interaction", key="INTERACTION_COMMAND_NAME"),
        description=disnake.Localized(
            "Interact with the user.", key="INTERACTION_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def interact(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            lambda inter: inter.author,
            name=disnake.Localized("user", key="TARGET_USER_NAME"),
            description=disnake.Localized(
                "Select a user.", key="TARGET_USER_DESCRIPTION"
            ),
        ),
        choice: str = commands.Param(
            name=disnake.Localized("choice", key="INTERACTION_COMMAND_CHOICE_NAME"),
            description=disnake.Localized(
                "Choose what interaction you want to do.",
                key="INTERACTION_COMMAND_CHOICE_DESCRIPTION",
            ),
            choices=[disnake.OptionChoice(x, x) for x in INTERACTION_CHOICE.keys()],
        ),
    ):
        try:
            await inter.response.defer(ephemeral=False)
            descriptions = (
                self.INTERACTION_DESCRIPTIONS
                if member != inter.author and member != inter.bot.user
                else self.INTERACTION_DESCRIPTIONS_MYSELF
                if member == inter.author
                else self.INTERACTION_DESCRIPTIONS_FISTASHKIN
            )
            image = await waifu_get_image(
                type="sfw", category=self.INTERACTION_CHOICE.get(choice)
            )
            embed = (
                disnake.Embed(
                    description=f"**{descriptions[self.INTERACTION_CHOICE.get(choice)].format(author=inter.author.display_name, user=member.display_name)}**",
                    color=self.color.MAIN,
                )
                .set_image(url=image)
            )
            await inter.edit_original_message(embed=embed)
        except Exception as e:
            raise CustomError(f"❌ Возникла проблема при отправке запроса на сервер!")

    @commands.slash_command(
        name=disnake.Localized("nsfw", key="NSFW_COMMAND_NAME"),
        description=disnake.Localized(
            "Well... It was not bad.", key="NSFW_COMMAND_DESCRIPTION"
        ),
    )
    @commands.is_nsfw()
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def nsfw(
        self,
        inter: disnake.ApplicationCommandInteraction,
        choice: str = commands.Param(
            name=disnake.Localized("choice", key="NSFW_COMMAND_CHOICE_NAME"),
            description=disnake.Localized(
                "Choose something from the list.",
                key="NSFW_COMMAND_CHOICE_DESCRIPTION",
            ),
            choices=[disnake.OptionChoice(x, x) for x in NSFW_DESCRIPTIONS.keys()],
        ),
    ):
        try:
            await inter.response.defer(ephemeral=False)
            image = await hatsunia_get_image(
                category=self.NSFW_DESCRIPTIONS.get(choice)
            )
            embed = (
                disnake.Embed(color=self.color.MAIN)
                .set_image(url=image)
            )
            await inter.edit_original_message(embed=embed)
        except Exception as e:
            raise CustomError("❌ Возникла проблема при отправке запроса на сервер!")

    @commands.slash_command(
        name=disnake.Localized("anime-chan", key="ANIME_CHAN_COMMAND_NAME"),
        description=disnake.Localized(
            "Anime-chan!", key="ANIME_CHAN_COMMAND_DESCRIPTION"
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def anime_girl(
        self,
        inter: disnake.ApplicationCommandInteraction,
        choice: str = commands.Param(
            name=disnake.Localized("choice", key="ANIME_CHAN_CHOICE_NAME"),
            description=disnake.Localized(
                "Select the tag with anime-chan.", key="ANIME_CHAN_CHOICE_DESCRIPTION"
            ),
            choices=[disnake.OptionChoice(x, x) for x in ANIME_GIRLS.keys()],
        ),
    ):
        try:
            await inter.response.defer(ephemeral=False)
            image = await waifu_get_image(
                type="sfw", category=self.ANIME_GIRLS.get(choice)
            )
            embed = (
                disnake.Embed(
                    description=f"Картинка с **{choice.title()}**", color=self.color.MAIN
                )
                .set_image(url=image)
            )
            await inter.edit_original_message(embed=embed)
        except Exception as e:
            raise CustomError("❌ Возникла проблема при отправке запроса на сервер!")

    @commands.slash_command(
        name=disnake.Localized("minesweeper", key="MINESWEEPER_COMMAND_NAME"),
        description=disnake.Localized(
            "Play minesweeper mini-game.", key="MINESWEEPER_COMMAND_DESCRIPTION"
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def mine(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        board = [["\u200b"] * 5] * 5
        bombs = 0
        bombpositions = []
        for x in repeat(None, random.randint(4, 11)):
            random_index = random.randint(0, 19)
            if random_index not in bombpositions and random_index not in [
                0,
                4,
                20,
                24,
            ]:
                bombpositions.append(random_index)
                bombs += 1

        def ExtractBlocks():
            new_b = []
            for x in board:
                for y in x:
                    new_b.append(y)
            return new_b

        view = MineswiperView(inter, ExtractBlocks(), bombpositions, board)
        message = await inter.edit_original_message(
            f"Всего бомб: `{len(bombpositions)}`",
            view=view,
        )
        view.message = message

    @commands.slash_command(
        name=disnake.Localized("dice", key="ROLLDICE_COMMAND_NAME"),
        description=disnake.Localized(
            "Play a mini-game with rolling a dice.", key="ROLLDICE_COMMAND_DESCRIPTION"
        ),
        dm_permission=False,
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def roll_dice(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=False)
        dice_roll = random.randint(1, 6)

        embed = (
            disnake.Embed(
                description=f"[`🎲`] На кубике выпала цифра: **{dice_roll}**",
                color=self.color.MAIN,
            )
            .set_author(name="🎲 Кости")
            .set_thumbnail(url=inter.author.display_avatar.url)
            .set_footer(text="💝 Оп, оп-ля!")
        )
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name=disnake.Localized("animal", key="ANIMAL_COMMAND_NAME"),
        description=disnake.Localized(
            "It outputs a random photo of the chosen animal.",
            key="ANIMAL_COMMAND_DESCRIPTION",
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def animal(
        self,
        inter: disnake.ApplicationCommandInteraction,
        choice: str = commands.Param(
            name=disnake.Localized("choice", key="ANIMAL_CHOICE_NAME"),
            description=disnake.Localized(
                "Please choose an animal.", key="ANIMAL_CHOICE_DESCRIPTION"
            ),
            choices=[disnake.OptionChoice(x, x) for x in ANIMALS_LIST.keys()],
        ),
    ):
        try:
            await inter.response.defer(ephemeral=False)
            image = await animal_get_image(category=self.ANIMALS_LIST.get(choice))
            embed = (
                disnake.Embed(color=self.color.MAIN)
                .set_image(url=image)
            )
            await inter.edit_original_message(embed=embed)
        except Exception as e:
            raise CustomError("❌ Возникла проблема при отправке запроса на сервер!")

    @commands.slash_command(
        name=disnake.Localized("guess", key="GUESS_GAME_COMMAND_NAME"),
        description=disnake.Localized(
            "Guess what is shown in the picture.", key="GUESS_GAME_COMMAND_DESCRIPTION"
        ),
    )
    @commands.dynamic_cooldown(default_cooldown, type=commands.BucketType.user)
    async def guess_game(
        self,
        inter: disnake.ApplicationCommandInteraction,
        choice: str = commands.Param(
            name=disnake.Localized("choice", key="GUESS_GAME_CHOICE_NAME"),
            description=disnake.Localized(
                "Select a category.", key="GUESS_GAME_CHOICE_DESCRIPTION"
            ),
            choices=[disnake.OptionChoice(x, x) for x in GUESS_GAME.keys()],
        ),
    ):
        try:
            await inter.response.defer(ephemeral=False)
            type = self.GUESS_GAME.get(choice)

            item, answers, text, image, country = await fifty_api_fetch_guess(
                category=type
            )
            lower_answers = [answer.lower() for answer in answers]

            def check(message):
                return (
                    message.content.lower() in lower_answers
                    and message.channel == inter.channel
                )

            guess_title = (
                "игру 🎮"
                if type == "game"
                else (
                    "город 🌇"
                    if type == "city"
                    else (
                        "логотип 🍃"
                        if type == "logo"
                        else (
                            "страну 🌎"
                            if type == "country"
                            else ("название транспорта 🚗" if type == "vehicle" else "")
                        )
                    )
                )
            )
            guess_description = (
                "какая игра изображена"
                if type == "game"
                else (
                    "какой город изображен"
                    if type == "city"
                    else (
                        "какой логотип изображен"
                        if type == "logo"
                        else ("какой транспорт изображен" if type == "vehicle" else "")
                    )
                )
            )
            description = None
            percentage = random.randint(10, 100)
            podsk = f"\nПодсказка: **{await self.gen.generation(answers[0])}**" if percentage < 50 else""
            country_text = f"\nСтрана: **{country}**" if type == "city" else ""

            if type == "country":
                description = f"У вас есть **60 секунд** чтобы назвать страну по **описанию** и **картинке** с Google Maps.\n\n"
            else:
                description = f"У вас есть **30 секунд** чтобы ответить, {guess_description} на картинке ниже.{country_text}{podsk}"

            embed = (
                disnake.Embed(
                    title=f"Угадай {guess_title}", color=disnake.Color.random(),
                    description=description
                )
                .set_image(url=image)
                .add_field(name="Описание", value=f"{text}.") if type == "country" else None
                #.set_footer(text=f"DEBUG ответы: {answers}")  if inter.author.id == self.main.DEVELOPER_ID else None
            )
            await inter.edit_original_message(embed=embed)

            try:
                timeout = 60.0 if type == "country" else 30.0
                message = await self.bot.wait_for(
                    "message", timeout=timeout, check=check
                )
                if message.content.lower() in lower_answers:
                    embed = (
                        disnake.Embed(
                            title=f"Угадай {guess_title}",
                            description=f"Ответ: **{answers[0]}**{country_text}",
                            color=self.color.GREEN,
                        )
                        .set_image(url=image)
                    )
                    return await inter.followup.send(
                        f"Победитель: **{message.author.mention}**", embed=embed
                    )
                else:
                    embed = (
                        disnake.Embed(
                            title=f"Угадай {guess_title}",
                            description=f"Ответ: **{answers[0]}**{country_text}",
                            color=self.color.RED,
                        )
                        .set_image(url=image)
                    )
                    return await inter.followup.send(
                        "**Победители отсувствуют**", embed=embed
                    )
            except asyncio.TimeoutError:
                embed = (
                    disnake.Embed(
                        title=f"Угадай {guess_title}",
                        description=f"Ответ: **{answers[0]}**",
                        color=self.color.RED,
                    )
                    .set_image(url=image)
                )
                return await inter.followup.send(
                    "**Победители отсувствуют**", embed=embed
                )
        except Exception as e:
            raise CustomError(
                f"❌ Категория **{choice}** не поддерживается или не была загружена. {e}"
            )


def setup(bot):
    bot.add_cog(Entertainment(bot))
