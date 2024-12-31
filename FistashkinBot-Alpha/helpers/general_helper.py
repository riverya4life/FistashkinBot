import disnake

from disnake.ext import commands
from utils import enums, constant
from classes import database as db


class BioButtons(disnake.ui.View):
    message: disnake.Message

    def __init__(self, inter):
        self.inter = inter
        self.color = enums.Color()
        super().__init__(timeout=120.0)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=None)
        self.stop()

    @disnake.ui.button(
        label="Установить биографию", emoji="✨", style=disnake.ButtonStyle.green
    )
    async def set_bio(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        await inter.response.send_modal(modal=InputSetBioUser())

    @disnake.ui.button(
        label="Удалить биографию", emoji="❎", style=disnake.ButtonStyle.red
    )
    async def remove_bio(self, button: disnake.ui.Button, inter):
        bio = await db.get_bio(member=inter.author)
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        elif (
            bio
            == "Вы можете добавить сюда какую-нибудь полезную информацию о себе командой `/осебе`"
        ):
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Как вы можете удалить биографию, если у вас её нету?",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        await db.remove_bio(member=inter.author)
        embed = (
            disnake.Embed(
                description="✅ Информация успешно удалена, проверьте командой `/юзер`, либо опять вызовите эту команду.",
                color=self.color.MAIN,
            )
            .set_author(
                name=f"Биография {inter.author}", icon_url=inter.author.display_avatar.url
            )
        )
        await inter.response.edit_message(embed=embed, view=None)


class InputSetBioUser(disnake.ui.Modal):
    message: disnake.Message

    def __init__(self):
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()

        components = [
            disnake.ui.TextInput(
                label="Текст",
                placeholder="Напишите текст...",
                custom_id="set_bio",
                style=disnake.TextInputStyle.paragraph,
                max_length=2048,
            )
        ]
        super().__init__(
            title="Биография",
            components=components,
            custom_id="set_bio_modal",
        )

    async def callback(self, inter: disnake.ModalInteraction):
        try:
            text_bio = str(inter.text_values["set_bio"])
            await db.set_bio(member=inter.author, bio=text_bio)
            embed = (
                disnake.Embed(
                    description="✅ Информация успешно обновлена, проверьте командой `/юзер`, либо опять вызовите эту команду.",
                    color=self.color.MAIN,
                )
                .set_author(
                    name=f"Биография {inter.author}",
                    icon_url=inter.author.display_avatar.url,
                )
            )
            await inter.response.edit_message(embed=embed, view=None)

        except ValueError:
            raise CustomError("❌ Вы ввели некорректные данные, попробуйте ещё раз.")
