import os
import disnake

from disnake.ext import commands
from typing import List
from utils import enums


class Paginator(disnake.ui.View):
    def __init__(self, inter: disnake.Interaction, embeds: List[disnake.Embed]):
        super().__init__(timeout=300.0)
        self.inter = inter
        self.embeds = embeds
        self.index = 0
        self.color = enums.Color()

        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Страница {i + 1} из {len(self.embeds)}") if len(
                self.embeds
            ) > 1 else None

        self._update_state()

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)
        return await super().on_timeout()

    def _update_state(self) -> None:
        self.prev_page.disabled = self.index == 0
        self.next_page.disabled = self.index == len(self.embeds) - 1
        self.to_page_button.disabled = len(self.embeds) == 1

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        self.index -= 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="Перейти к странице", style=disnake.ButtonStyle.gray)
    async def to_page_button(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description="❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
            
        await inter.response.send_modal(PageModal(paginator=self))

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        self.index += 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red)
    async def remove(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        self.stop()
        await self.message.delete()


class PageModal(disnake.ui.Modal):
    def __init__(self, paginator: Paginator):
        self.paginator = paginator
        self.color = enums.Color()
        super().__init__(
            title="Перейти к странице",
            custom_id="embed_page_modal",
            timeout=300,
            components=[
                disnake.ui.TextInput(
                    label="Страница",
                    placeholder="Укажите номер страницы",
                    custom_id="embed_page_num",
                    style=disnake.TextInputStyle.short,
                    max_length=3,
                ),
            ],
        )

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        try:
            page_num = int(inter.text_values["embed_page_num"])
            if 1 <= page_num <= len(self.paginator.embeds):
                self.paginator.index = page_num - 1
                self.paginator._update_state()
                await inter.response.edit_message(
                    embed=self.paginator.embeds[self.paginator.index],
                    view=self.paginator,
                )
            else:
                return await inter.response.send_message(
                    embed=disnake.Embed(
                        description=f"❌ | Страница не существует! Укажите число в диапазоне от 1 до {len(self.paginator.embeds)}.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )
        except ValueError:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description="❌ | Неверный формат страницы! Укажите число.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
