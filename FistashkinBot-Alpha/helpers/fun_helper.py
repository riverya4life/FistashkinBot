import disnake
import random

from random import *
from disnake import *
from utils import enums


class MineswiperButtons(ui.Button):
    def __init__(self, inter, label, custom_id, bombs, board):
        super().__init__(label=label, style=ButtonStyle.grey, custom_id=custom_id)
        self.inter = inter
        self.bombs = bombs
        self.board = board
        self.color = enums.Color()

    async def callback(self, inter):
        assert self.view is not None
        view: MineswiperView = self.view
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        await inter.response.defer()
        b_id = self.custom_id
        if int(b_id[5:]) in view.moves:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ Эта часть уже занята.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        if int(b_id[5:]) in self.bombs:
            await view.RevealBombs(b_id, view.board)
        else:
            count = []
            rawpos = int(b_id[5:])
            pos = view.GetBoardPos(rawpos)

            def checkpos(count, rawpos, pos):
                pos = view.GetBoardPos(rawpos)
                if not rawpos - 1 in self.bombs or pos == 0:
                    count.append(rawpos - 1)
                if not rawpos + 1 in self.bombs or pos == 4:
                    count.append(rawpos + 1)
                if not rawpos - 6 in self.bombs or pos == 0:
                    count.append(rawpos - 6)
                if not rawpos - 4 in self.bombs or pos == 4:
                    count.append(rawpos - 4)
                if not rawpos + 6 in self.bombs or pos == 4:
                    count.append(rawpos + 6)
                if not rawpos + 4 in self.bombs or pos == 0:
                    count.append(rawpos + 4)
                if not rawpos - 5 in self.bombs:
                    count.append(rawpos - 5)
                if not rawpos + 5 in self.bombs:
                    count.append(rawpos + 5)
                return count

            count = checkpos(count, rawpos, pos)
            self.label = f"  {8-len(count)}  "
            self.style = ButtonStyle.green
            pos = int(b_id[5:])
            view.board[view.GetBoardRow(pos)][
                view.GetBoardPos(pos)
            ] = f"  {8-len(count)}  "
            view.moves.append(pos)
            if len(view.moves) + len(self.bombs) == 25:
                await inter.edit_original_message(view=view)
                await view.EndGame()

        await inter.edit_original_message(view=view)


class MineswiperView(ui.View):
    message: disnake.Message

    def __init__(self, inter, options, bombs, board):
        super().__init__(timeout=180.0)
        for i, op in enumerate(options):
            self.add_item(MineswiperButtons(inter, op, f"block{i}", bombs, board))
        self.board = board
        self.bombs = bombs
        self.moves = []
        self.inter = inter
        self.color = enums.Color()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(
            content="Игра окончена, так как вы бездействовали!", view=self
        )
        return await super().on_timeout()

    async def EndGame(self):
        await self.inter.edit_original_message(content=f"🥳 Игра окончена. Ты победил!")
        for button in self.children:
            button.disabled = True
            pos = int(button.custom_id[5:])
            if pos in self.bombs:
                button.label = "💣"
                button.style = ButtonStyle.red
                self.board[self.GetBoardRow(pos)][self.GetBoardPos(pos)] = "💣"
        # self.stop()

    @staticmethod
    def GetBoardRow(pos):
        if pos in [0, 1, 2, 3, 4]:
            return 0
        if pos in [5, 6, 7, 8, 9]:
            return 1
        if pos in [10, 11, 12, 13, 14]:
            return 2
        if pos in [15, 16, 17, 18, 19]:
            return 3
        if pos in [20, 21, 22, 23, 24]:
            return 4
        return False

    @staticmethod
    def GetBoardPos(pos):
        if pos in [0, 1, 2, 3, 4]:
            return pos
        if pos in [5, 6, 7, 8, 9]:
            for i, num in enumerate(range(5, 10)):
                if pos == num:
                    return i
        if pos in [10, 11, 12, 13, 14]:
            for i, num in enumerate(range(10, 15)):
                if pos == num:
                    return i
        if pos in [15, 16, 17, 18, 19]:
            for i, num in enumerate(range(15, 20)):
                if pos == num:
                    return i
        if pos in [20, 21, 22, 23, 24]:
            for i, num in enumerate(range(20, 25)):
                if pos == num:
                    return i
        return False

    async def RevealBombs(self, b_id, board):
        bombemo = "💣"
        for button in self.children:
            button.disabled = True
            if button.custom_id == b_id:
                button.label = bombemo
                button.style = ButtonStyle.red
                pos = int(b_id[5:])
                self.board[self.GetBoardRow(pos)][self.GetBoardPos(pos)] = bombemo

        for button in self.children:
            if int(button.custom_id[5:]) in self.bombs:
                button.label = bombemo
                button.style = ButtonStyle.red
                self.board[self.GetBoardRow(int(b_id[5:]))][
                    self.GetBoardPos(int(b_id[5:]))
                ] = bombemo

        await self.inter.edit_original_message(
            content=f"😒 Игра окончена. Ты проиграл!", view=self
        )
