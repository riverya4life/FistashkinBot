import disnake

from disnake.ext import commands

from classes import database as db


class TempVoice(commands.Cog):

    hidden = True
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(disnake.Event.voice_state_update)
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        if after.channel is not None:
            trigger_info = await db.get_voice_channel_trigger(
                guild=member.guild, channel=after.channel
            )
            if trigger_info and after.channel.id == trigger_info["channel_id"]:
                guild = self.bot.get_guild(trigger_info["guild_id"])
                category_id = trigger_info["category_id"]
                main_category = disnake.utils.get(guild.categories, id=category_id)

                permissions = {
                    member: disnake.PermissionOverwrite(
                        connect=True,
                        mute_members=True,
                        move_members=True,
                        manage_channels=True,
                    )
                }

                private_voice_channel = await guild.create_voice_channel(
                    name=f"Комната {member.display_name}",
                    category=main_category,
                    bitrate=96000,
                    overwrites=permissions,
                )

                await member.move_to(private_voice_channel)
                await self.bot.wait_for(
                    "voice_state_update",
                    check=lambda x, y, z: len(private_voice_channel.members) == 0,
                )
                await private_voice_channel.delete()


def setup(bot):
    bot.add_cog(TempVoice(bot))
