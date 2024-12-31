import jishaku
from disnake.ext import commands
from jishaku.cog import Jishaku


class FBJishaku(
    Jishaku, name="икэс бокэс икэс", description="Команды моих папиков, хд."
):
    hidden = True


def setup(bot: commands.Bot):
    jishaku.Flags.HIDE = True
    jishaku.Flags.NO_UNDERSCORE = True
    jishaku.Flags.FORCE_PAGINATOR = True
    jishaku.Flags.NO_DM_TRACEBACK = True
    bot.add_cog(FBJishaku(bot=bot))
