import disnake
import datetime
import asyncio

from disnake.ext import commands
from utils import enums

from classes import database as db


class Logs(commands.Cog):

    hidden = True
    
    def __init__(self, bot):
        self.bot = bot
        self.color = enums.Color()

    @commands.Cog.listener(disnake.Event.member_join)
    async def on_member_join(self, member: disnake.Member):
        log_channel_data = await db.get_log_channel(guild=member.guild)
        if not log_channel_data:
            return

        channel = member.guild.get_channel(log_channel_data["log_channel_id"])
        if not channel:
            return

        webhook = disnake.utils.find(lambda hook: hook.name == "FistashkinLog", await channel.webhooks())
        if not webhook:
            webhook = await channel.create_webhook(name="FistashkinLog")

        register_f = disnake.utils.format_dt(member.created_at, style="f")
        register_r = disnake.utils.format_dt(member.created_at, style="R")

        embed = disnake.Embed(
            description=f"{'Бот' if member.bot else 'Участник'} **{member}** ({member.mention}) присоединился к серверу",
            color=self.color.MAIN,
            timestamp=datetime.datetime.utcnow(),
        ).add_field(
            name="Дата регистрации",
            value=f"{register_f} ({register_r})",
            inline=True,
        ).set_footer(
            text=f"ID {'бота' if member.bot else 'участника'}: {member.id}"
        ).set_thumbnail(
            url=member.display_avatar.url
        )

        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )


    @commands.Cog.listener(disnake.Event.member_remove)
    async def on_member_remove(self, member: disnake.Member):
        log_channel_data = await db.get_log_channel(guild=member.guild)
        if not log_channel_data:
            return

        channel = member.guild.get_channel(log_channel_data["log_channel_id"])
        if not channel:
            return

        webhook = disnake.utils.find(lambda hook: hook.name == "FistashkinLog", await channel.webhooks())
        if not webhook:
            webhook = await channel.create_webhook(name="FistashkinLog")

        roles = [r.mention for r in member.roles if r != member.guild.default_role]
        roles.reverse()
        role_string = " | ".join(roles)

        embed = disnake.Embed(
            description=f"{'Бот' if member.bot else 'Участник'} **{member}** ({member.mention}) покинул сервер",
            color=self.color.MAIN,
            timestamp=datetime.datetime.utcnow(),
        )
        if roles:
            embed.add_field(
                name=f"{'Роли' if len(roles) > 1 else 'Роль'} при выходе",
                value=role_string,
                inline=False,
            )
        embed.set_footer(
            text=f"ID {'бота' if member.bot else 'участника'}: {member.id}"
        ).set_thumbnail(url=member.display_avatar.url)

        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )

    @commands.Cog.listener(disnake.Event.message_delete)
    async def on_message_delete(self, message: disnake.Member):
        log_channel_data = await db.get_log_channel(guild=message.guild)
        if not log_channel_data:
            return

        channel = message.guild.get_channel(log_channel_data["log_channel_id"])
        if not channel:
            return

        webhook = disnake.utils.find(lambda hook: hook.name == "FistashkinLog", await channel.webhooks())
        if not webhook:
            webhook = await channel.create_webhook(name="FistashkinLog")

        if message.author.bot:
            return

        embed = disnake.Embed(
            description="Сообщение было удалено",
            color=self.color.MAIN,
            timestamp=datetime.datetime.utcnow(),
        )

        if message.content and len(message.content) < 1024:
            embed.add_field(name="Сообщение", value=f"```{message.content}```", inline=False)

        embed.add_field(
            name="Автор", 
            value=f"**{message.author.name}** ({message.author.mention})", 
            inline=True,
        )
        embed.add_field(
            name="Канал", 
            value=f"**{message.channel.name}** ({message.channel.mention})", 
            inline=True,
        )

        if message.attachments:
            embed.add_field(
                name="Изображение", 
                value=f"[Тык]({message.attachments[0].proxy_url})", 
                inline=False,
            )
            embed.set_image(url=message.attachments[0].proxy_url)

        embed.set_footer(text=f"ID сообщения: {message.id}")
        embed.set_thumbnail(url=message.author.display_avatar.url)

        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )


    @commands.Cog.listener(disnake.Event.message_edit)
    async def on_message_edit(self, before, after):
        log_channel_data = await db.get_log_channel(guild=after.guild)
        if not log_channel_data:
            return

        channel = after.guild.get_channel(log_channel_data["log_channel_id"])
        if not channel:
            return

        webhook = disnake.utils.find(lambda hook: hook.name == "FistashkinLog", await channel.webhooks())
        if not webhook:
            webhook = await channel.create_webhook(name="FistashkinLog")

        if (
            after.content == before.content
            or len(after.content) > 4096
            or len(before.content) > 4096
            or after.author.bot
        ):
            return

        embed = disnake.Embed(
            description=f"[Сообщение]({after.jump_url}) было отредактировано",
            color=self.color.MAIN,
            timestamp=datetime.datetime.utcnow(),
        )

        embed.add_field(name="Старое содержимое:", value=f"```{before.content}```", inline=False)
        embed.add_field(name="Новое содержимое:", value=f"```{after.content}```", inline=False)
        embed.add_field(name="Автор", value=f"**{after.author.name}** ({after.author.mention})", inline=True)
        embed.add_field(name="Канал", value=f"**{after.channel.name}** ({after.channel.mention})", inline=True)

        if after.attachments:
            embed.set_image(url=after.attachments[0].proxy_url)

        embed.set_footer(text=f"ID сообщения: {after.id}")
        embed.set_thumbnail(url=after.author.display_avatar.url)

        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )


    @commands.Cog.listener(disnake.Event.member_update)
    async def on_member_update(self, before, after):
        log_channel_data = await db.get_log_channel(guild=after.guild)
        if not log_channel_data:
            return

        channel = after.guild.get_channel(log_channel_data["log_channel_id"])
        if not channel:
            return

        webhook = disnake.utils.find(lambda hook: hook.name == "FistashkinLog", await channel.webhooks())
        if not webhook:
            webhook = await channel.create_webhook(name="FistashkinLog")

        embed = disnake.Embed(
            color=self.color.MAIN,
            timestamp=datetime.datetime.utcnow(),
        ).set_footer(
            text=f"ID {'бота' if after.bot else 'участника'}: {after.id}"
        ).set_thumbnail(
            url=after.display_avatar.url
        )

        if before.display_name != after.display_name:
            embed.description = f"Никнейм {'бота' if after.bot else 'участника'} **{after}** ({after.mention}) был изменён"
            embed.add_field(name="Старый никнейм:", value=before.display_name, inline=True)
            embed.add_field(name="Новый никнейм:", value=after.display_name, inline=True)
            await webhook.send(
                embed=embed,
                username="FistashkinLog",
                avatar_url=self.bot.user.display_avatar.url,
                allowed_mentions=disnake.AllowedMentions.none(),
            )

        if before.roles != after.roles:
            added_roles = [f"<@&{role.id}>" for role in after.roles if role not in before.roles]
            removed_roles = [f"<@&{role.id}>" for role in before.roles if role not in after.roles]

            embed.description = f"Роли {'бота' if after.bot else 'участника'} **{after}** ({after.mention}) были изменены"

            if added_roles:
                embed.add_field(
                    name="Добавленные роли:" if len(added_roles) > 1 else "Добавленная роль:",
                    value=", ".join(added_roles),
                    inline=True,
                )
            if removed_roles:
                embed.add_field(
                    name="Убранные роли:" if len(removed_roles) > 1 else "Убранная роль:",
                    value=", ".join(removed_roles),
                    inline=True,
                )
            await webhook.send(
                embed=embed,
                username="FistashkinLog",
                avatar_url=self.bot.user.display_avatar.url,
                allowed_mentions=disnake.AllowedMentions.none(),
            )


    @commands.Cog.listener(disnake.Event.voice_state_update)
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        log_channel_data = await db.get_log_channel(guild=member.guild)
        if not log_channel_data:
            return

        channel = member.guild.get_channel(log_channel_data["log_channel_id"])
        if not channel:
            return

        webhook = disnake.utils.find(lambda hook: hook.name == "FistashkinLog", await channel.webhooks())
        if not webhook:
            webhook = await channel.create_webhook(name="FistashkinLog")

        embed = disnake.Embed(
            color=self.color.MAIN,
            timestamp=datetime.datetime.utcnow(),
        ).set_footer(
            text=f"ID {'бота' if member.bot else 'участника'}: {member.id}"
        ).set_thumbnail(
            url=member.display_avatar.url
        )

        if before.channel is None and after.channel is not None:
            embed.description = f"**{member}** ({member.mention}) присоединился к голосовому каналу"
            embed.add_field(
                name="Канал:",
                value=f"**{after.channel.name}** ({after.channel.mention})",
                inline=True,
            )
        elif before.channel is not None and after.channel is None:
            embed.description = f"**{member}** ({member.mention}) покинул голосовой канал"
            embed.add_field(
                name="Канал:",
                value=f"**{before.channel.name}** ({before.channel.mention})",
                inline=True,
            )
        elif before.channel != after.channel:
            embed.description = f"**{member}** ({member.mention}) перешёл в голосовой канал"
            embed.add_field(
                name="До:",
                value=f"**{before.channel.name}** ({before.channel.mention})",
                inline=True,
            )
            embed.add_field(
                name="После:",
                value=f"**{after.channel.name}** ({after.channel.mention})",
                inline=True,
            )

        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )



def setup(bot):
    bot.add_cog(Logs(bot))
