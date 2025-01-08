import disnake
import os
import json

class Automod:
    def __init__(self, bot):
        self.bot = bot
        self.__base = os.path.join(os.path.dirname(__file__), "json")
        self.ban_words_file = os.path.join(self.__base, "banwords.json")

    async def _load_json(self):
        if not os.path.exists(self.ban_words_file):
            raise FileNotFoundError(f"Файл для запрещённых слов {self.ban_words_file} не найден.")

        with open(self.ban_words_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "ban_words" not in data:
            raise KeyError(f"Ключ 'ban_words' не найден в файле {self.ban_words_file}.")
        
        return data["ban_words"]

    async def _create_or_update_automod_rule(self, guild, name, event_type, trigger, actions, trigger_metadata=None):
        try:
            automod_rules = await guild.fetch_automod_rules()
            existing_rule = next(
                (rule for rule in automod_rules if rule.name == name and rule.creator.id == self.bot.user.id), 
                None
            )

            if existing_rule:
                await existing_rule.delete()
                print(f"Существующее правило '{name}' удалено.")

            automod_rule = await guild.create_automod_rule(
                name=name,
                event_type=event_type,
                trigger_type=trigger,
                actions=actions,
                trigger_metadata=trigger_metadata,
                enabled=True,
                exempt_roles=[],
                exempt_channels=[],
                reason="Automod by FistashkinBot",
            )

            print(f"Automod правило '{automod_rule.name} ({automod_rule.id})' на сервере {guild.name} успешно создано!")
        except disnake.DisnakeException as e:
            print(f"Ошибка: {e}")

    async def mention_spam_filter_automod(self, guild: disnake.Guild):
        name = "Fistashkin Protect (Mention Spam Filter)"
        event_type = disnake.AutoModEventType.message_send
        trigger = disnake.AutoModTriggerType.mention_spam
        actions = [
            disnake.AutoModBlockMessageAction(custom_message="Не спамь ^_^ by FistashkinBot"),
            disnake.AutoModTimeoutAction(int(60)),
        ]
        trigger_metadata = disnake.AutoModTriggerMetadata(
            mention_total_limit=15, mention_raid_protection_enabled=True
        )
        await self._create_or_update_automod_rule(guild, name, event_type, trigger, actions, trigger_metadata)

    async def spam_filter_automod(self, guild: disnake.Guild):
        name = "Fistashkin Protect (Spam Filter)"
        event_type = disnake.AutoModEventType.message_send
        trigger = disnake.AutoModTriggerType.spam
        actions = [disnake.AutoModBlockMessageAction(custom_message="Не спамь ^_^ by FistashkinBot")]
        await self._create_or_update_automod_rule(guild, name, event_type, trigger, actions)

    async def ban_word_filter_automod(self, guild: disnake.Guild):
        name = "Fistashkin Protect (Ban Word Filter)"
        event_type = disnake.AutoModEventType.message_send
        trigger = disnake.AutoModTriggerType.keyword
        actions = [
            disnake.AutoModBlockMessageAction(custom_message="Не используй это слово ^_^ by FistashkinBot"),
            disnake.AutoModTimeoutAction(int(60)),
        ]
        trigger_metadata = disnake.AutoModTriggerMetadata(keyword_filter=await self._load_json())
        await self._create_or_update_automod_rule(guild, name, event_type, trigger, actions, trigger_metadata)