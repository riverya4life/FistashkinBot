import disnake

from disnake.ext import commands
from utils import constant, enums, main, automod
from classes import database as db


class TempVoiceButtons(disnake.ui.View):
    message: disnake.Message

    def __init__(self, inter):
        super().__init__(timeout=120.0)
        self.inter = inter
        self.color = enums.Color()

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True
        await self.message.edit(view=self)
        self.stop()

    @disnake.ui.button(label="Добавить триггер", style=disnake.ButtonStyle.green)
    async def add_trigger(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        await inter.response.send_modal(modal=InputVoiceSettingTrigger())

    @disnake.ui.button(
        label="Создать канал и категорию", style=disnake.ButtonStyle.green
    )
    async def add_channel_and_category(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        await inter.response.send_modal(modal=InputVoiceSetting())

    @disnake.ui.button(label="Удалить триггеры", style=disnake.ButtonStyle.red)
    async def delete_trigger(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        await inter.response.send_modal(modal=InputVoiceSettingTriggerDelete())


class RoleShopButtons(disnake.ui.View):
    message: disnake.Message

    def __init__(self, inter):
        super().__init__(timeout=120.0)
        self.inter = inter
        self.color = enums.Color()

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True
        await self.message.edit(view=self)
        self.stop()

    @disnake.ui.button(label="Добавить роли", style=disnake.ButtonStyle.green)
    async def add_role(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        await inter.response.send_modal(modal=InputAddRoleShopSettings())

    @disnake.ui.button(label="Убрать роли", style=disnake.ButtonStyle.red)
    async def delete_role(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        await inter.response.send_modal(modal=InputDeleteRoleShopSettings())


class LogsSetupButtons(disnake.ui.View):
    message: disnake.Message

    def __init__(self, inter):
        super().__init__(timeout=120.0)
        self.inter = inter
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True
        await self.message.edit(view=self)
        self.stop()

    @disnake.ui.button(label="Установить", style=disnake.ButtonStyle.green)
    async def add_logs(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description="❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        if await db.get_log_channel(guild=inter.guild):
            return await inter.response.send_message(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ Система логгирования уже установлена.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        await inter.response.send_modal(modal=InputAddLogsSettings())


    @disnake.ui.button(
        label="Установить текущий канал", style=disnake.ButtonStyle.green
    )
    async def add_logs_channel(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description="❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        try:
            channel = await inter.guild.fetch_channel(inter.channel.id)

            invalid_types = {
                disnake.CategoryChannel: "категорию",
                disnake.VoiceChannel: "голосовой канал",
                disnake.Thread: "ветку",
                disnake.ChannelType.forum: "форум",
            }

            for channel_type, type_name in invalid_types.items():
                if channel.type == channel_type:
                    return await inter.send(
                        embed=disnake.Embed(
                            title=f"{self.otheremojis.WARNING} Ошибка!",
                            description=f"❌ Нельзя использовать {type_name} для логгирования.",
                            color=self.color.RED,
                        ),
                        ephemeral=True,
                    )

            if channel.id == inter.guild.system_channel.id:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description="❌ Нельзя использовать системный канал для логгирования.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            existing_trigger = await db.get_log_channel(guild=inter.guild)
            if existing_trigger:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description="❌ Система логгирования уже установлена.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            await db.insert_log_channel(guild=inter.guild, channel=inter.channel)
            embed = disnake.Embed(
                description=f"✅ Канал для логгирования успешно установлен! {channel.mention}",
                color=self.color.GREEN,
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

        except disnake.errors.Forbidden:
            await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ Бот не имеет доступа к указанному каналу.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )


    @disnake.ui.button(label="Удалить", style=disnake.ButtonStyle.red)
    async def delete_logs(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description="❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        existing_trigger = await db.get_log_channel(guild=inter.guild)
        if not existing_trigger:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ Система логгирования не установлена.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        await db.remove_log_channel(guild=inter.guild)
        await inter.response.send_message(
            embed=disnake.Embed(
                description="✅ Канал для логгирования успешно удалён!",
                color=self.color.GREEN,
            ),
            ephemeral=True,
        )


class InputVoiceSetting(disnake.ui.Modal):
    message: disnake.Message

    def __init__(self):
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()

        components = [
            disnake.ui.TextInput(
                label="Название канала",
                placeholder="Укажите название для канала.",
                custom_id="setup_voice_name_channel",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Название категории",
                placeholder="Укажите название для категории.",
                custom_id="setup_voice_name_category",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
        ]
        super().__init__(
            title="Приватные Голосовые Комнаты",
            components=components,
            custom_id="add_voice",
        )

    async def callback(self, inter: disnake.ModalInteraction):
        try:
            name_voice = inter.text_values["setup_voice_name_channel"]
            name_category_voice = inter.text_values["setup_voice_name_category"]

            category = await inter.guild.create_category(
                name=name_category_voice,
                reason="Создание временных каналов by FistashkinBot",
            )
            channel = await inter.guild.create_voice_channel(
                name=name_voice,
                category=category,
                user_limit=1,
            )

            await db.add_voice_channel_trigger(
                guild=inter.guild, category=category, channel=channel
            )

            embed = disnake.Embed(
                description=(
                    f"✅ Триггер для создания временных каналов успешно установлен!\n"
                    f"Канал: {channel.mention}\nКатегория: {category.mention}"
                ),
                color=self.color.GREEN,
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

        except ValueError:
            return await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ Вы ввели некорректные данные, попробуйте ещё раз.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )


class InputVoiceSettingTrigger(disnake.ui.Modal):
    message: disnake.Message

    def __init__(self):
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()

        components = [
            disnake.ui.TextInput(
                label="ID канала",
                placeholder="Укажите ID канала для которого хотите установить триггер.",
                custom_id="setup_voice_id_channel",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="ID категории",
                placeholder="Укажите ID категории в которой будут созданы каналы.",
                custom_id="setup_voice_id_category",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
        ]
        super().__init__(
            title="Приватные Голосовые Комнаты",
            components=components,
            custom_id="add_voice_trigger",
        )

    async def callback(self, inter: disnake.ModalInteraction):
        try:
            id_voice = int(inter.text_values["setup_voice_id_channel"])
            id_category_voice = int(inter.text_values["setup_voice_id_category"])

            channel = disnake.utils.get(inter.guild.channels, id=id_voice)
            category = disnake.utils.get(inter.guild.categories, id=id_category_voice)

            if not channel or not category:
                raise ValueError("Указаны некорректные ID канала или категории.")

            existing_trigger = await db.get_voice_channel_trigger(
                guild=inter.guild, channel=channel
            )
            if existing_trigger:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=(
                            f"❌ Триггер уже установлен.\n"
                            f"Канал: {channel.mention}\nКатегория: {category.mention}"
                        ),
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            await db.add_voice_channel_trigger(
                guild=inter.guild, category=category, channel=channel
            )

            embed = disnake.Embed(
                description=(
                    f"✅ Триггер для создания временных каналов успешно установлен!\n"
                    f"Канал: {channel.mention}\nКатегория: {category.mention}"
                ),
                color=self.color.GREEN,
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            return await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description=f"❌ {str(e)} Попробуйте ещё раз.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )


class InputVoiceSettingTriggerDelete(disnake.ui.Modal): ############ ОСТАНОВКА ТУТ ############
    message: disnake.Message

    def __init__(self):
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()

        components = [
            disnake.ui.TextInput(
                label="ID канала",
                placeholder="Укажите ID канала для которого хотите удалить триггер.",
                custom_id="setup_voice_id_channel_delete",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="ID категории",
                placeholder="Укажите ID категории в которой будут удалены триггеры для канала.",
                custom_id="setup_voice_id_category_delete",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
        ]
        super().__init__(
            title="Приватные Голосовые Комнаты",
            components=components,
            custom_id="delete_voice_trigger",
        )

    async def callback(self, inter: disnake.ModalInteraction):
        try:
            id_voice = int(inter.text_values["setup_voice_id_channel_delete"])
            id_category_voice = int(inter.text_values["setup_voice_id_category_delete"])

            channel = disnake.utils.get(inter.guild.channels, id=id_voice)
            category = disnake.utils.get(inter.guild.categories, id=id_category_voice)

            trigger_data = await db.get_voice_channel_trigger(
                guild=inter.guild, channel=channel
            )
            if trigger_data is None or trigger_data["category_id"] != id_category_voice:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description="❌ Указанный канал или категория не существует в базе данных.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            await db.remove_voice_channel_trigger(
                guild=inter.guild, category=category, channel=channel
            )
            embed = disnake.Embed(
                description=f"✅ Триггер для создания каналов в {channel.mention} был удалён! (Категория: {category.mention})"
            )
            await inter.send(embed=embed, ephemeral=True)

        except ValueError:
            raise CustomError("❌ Вы ввели некорректные данные, попробуйте ещё раз.")


class InputAddRoleShopSettings(disnake.ui.Modal):
    message: disnake.Message

    def __init__(self):
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()
        self.enum = enums.Enum()

        components = [
            disnake.ui.TextInput(
                label="ID роли",
                placeholder="Укажите ID роли.",
                custom_id="add_role_id",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Стоимость",
                placeholder="Укажите стоимость (от 100 до 100000).",
                custom_id="add_role_cost",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
        ]
        super().__init__(
            title="Настройка магазина", components=components, custom_id="add_role_shop"
        )

    async def callback(self, inter: disnake.ModalInteraction):
        try:
            role_id = int(inter.text_values["add_role_id"])
            role_cost = int(inter.text_values["add_role_cost"])

            # 1. Проверка наличия роли на сервере
            role = disnake.utils.get(inter.guild.roles, id=role_id)
            if role is None:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description="❌ Роль с указанным ID не найдена на сервере. Пожалуйста, укажите корректный ID роли.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            # 2. Проверка на приоритет роли
            if role.position >= inter.author.top_role.position:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description="❌ Вы не можете добавить роль, которая выше вашей.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            if (
                (role.position == 0)
                or (role.is_premium_subscriber())
                or (role.is_integration())
                or (role.is_bot_managed())
            ):
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ Данную роль нельзя выставить в магазин!",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            # 3. Проверка наличия роли в магазине
            existing_role = await db.get_shop_data(role=role)
            if existing_role:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ Роль {role.mention} уже присутствует в магазине.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            # 4. Проверка установки цены
            if not 100 <= role_cost <= 100000:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description="❌ Укажите корректную стоимость для роли. Минимальная цена - 100, максимальная - 100000.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            await db.insert_new_role(role=role, cost=role_cost)
            cost = self.enum.format_large_number(role_cost)

            embed = disnake.Embed(
                description=f"✅ Вы успешно добавили роль {role.mention} в магазин за сумму в **{cost}**!",
                color=self.color.MAIN,
            )
            embed.set_author(
                name="Добавление роли в магазин",
                icon_url=inter.author.display_avatar.url,
            )
            await inter.send(embed=embed, ephemeral=True)

        except ValueError:
            return await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ Вы ввели некорректные данные, попробуйте ещё раз.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )


class InputDeleteRoleShopSettings(disnake.ui.Modal):
    message: disnake.Message

    def __init__(self):
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()

        components = [
            disnake.ui.TextInput(
                label="ID роли",
                placeholder="Укажите ID роли.",
                custom_id="delete_role_id",
                style=disnake.TextInputStyle.short,
                max_length=50,
            )
        ]
        super().__init__(
            title="Настройка магазина",
            components=components,
            custom_id="delete_role_shop",
        )

    async def callback(self, inter: disnake.ModalInteraction):
        try:
            role_id = int(inter.text_values["delete_role_id"])
            role = disnake.utils.get(inter.guild.roles, id=role_id)

            # Проверка на наличие роли на сервере
            if role is None:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description="❌ Указанной роли не существует на сервере.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            if role.position >= inter.author.top_role.position:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description="❌ Вы не можете удалить роль, которая выше вашей.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            # Проверка на наличие роли в магазине
            shop_data = await db.get_shop_data(role=role)
            if shop_data is None:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ Роль {role.mention} отсутствует в магазине.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            await db.delete_role_from_shop(role=role)

            embed = disnake.Embed(
                description=f"✅ Вы успешно удалили роль {role.mention} из магазина!",
                color=self.color.GREEN,
            )
            embed.set_author(
                name="Удаление роли из магазина",
                icon_url=inter.author.display_avatar.url,
            )
            await inter.send(embed=embed, ephemeral=True)

        except ValueError:
            return await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ Вы ввели некорректные данные, попробуйте ещё раз.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )


class InputAddLogsSettings(disnake.ui.Modal):
    message: disnake.Message

    def __init__(self):
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()
        self.enum = enums.Enum()

        components = [
            disnake.ui.TextInput(
                label="ID канала",
                placeholder="Укажите ID канала.",
                custom_id="add_logs_id",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
        ]
        super().__init__(
            title="Настройка системы логов",
            components=components,
            custom_id="add_logs",
        )

    async def callback(self, inter: disnake.ModalInteraction):
        try:
            id_channel_logs = int(inter.text_values["add_logs_id"])

            channel = await inter.guild.fetch_channel(id_channel_logs)
            if not channel:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description="❌ Указанный канал не существует или бот не имеет доступа к нему.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            if isinstance(channel, disnake.CategoryChannel):
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ Нельзя использовать категорию для логгирования.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            if isinstance(channel, disnake.VoiceChannel):
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ Нельзя использовать голосовой канал для логгирования.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            if isinstance(channel, disnake.Thread):
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ Нельзя использовать ветки для логгирования.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            if channel.type == disnake.ChannelType.forum:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ Нельзя использовать форум для логгирования.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            if inter.guild.system_channel.id == channel.id:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ Нельзя использовать системный канал для логгирования.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )

            existing_trigger = await db.get_log_channel(guild=inter.guild)
            if existing_trigger:
                return await inter.send(
                    embed=disnake.Embed(
                        title=f"{self.otheremojis.WARNING} Ошибка!",
                        description=f"❌ Система логгирования уже установлена.",
                        color=self.color.RED,
                    ),
                    ephemeral=True,
                )
            await db.insert_log_channel(guild=inter.guild, channel=channel)
            embed = disnake.Embed(
                description=f"✅ Канал для логгирования успешно установлен! {channel.mention}",
                color=self.color.GREEN,
            )
            await inter.send(embed=embed, ephemeral=True)

        except disnake.errors.Forbidden:
            return await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ Бот не имеет доступа к указанному каналу.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

        except ValueError:
            return await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ Вы ввели некорректные данные, попробуйте ещё раз.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )


class AutomodSetupButtons(disnake.ui.View):
    message: disnake.Message

    def __init__(self, bot, inter):
        super().__init__(timeout=120.0)
        self.bot = bot
        self.inter = inter
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()
        self.main = main.MainSettings()
        self.automod = automod.Automod(self.bot)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True
        await self.message.edit(view=self)
        self.stop()

    @disnake.ui.button(label="Спам упоминаниями", style=disnake.ButtonStyle.green)
    async def add_automod_mention_spam(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        try:
            rule = await self.automod.mention_spam_filter_automod(guild=inter.guild)
            embed = disnake.Embed(
                description="✅ Автомод правило **Спам упоминаниями** было создано!",
                color=self.color.GREEN,
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

        except disnake.errors.Forbidden:
            return await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ У бота нет прав на выполнения этого действия!",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

    @disnake.ui.button(label="Спам", style=disnake.ButtonStyle.green)
    async def add_automod_spam(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        try:
            rule = await self.automod.spam_filter_automod(guild=inter.guild)
            embed = disnake.Embed(
                description="✅ Автомод правило **Спам** было создано!",
                color=self.color.GREEN,
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

        except disnake.errors.Forbidden:
            return await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ У бота нет прав на выполнения этого действия!",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

    @disnake.ui.button(label="Запрещенные слова", style=disnake.ButtonStyle.green)
    async def add_automod_ban_words(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        try:
            rule = await self.automod.ban_word_filter_automod(guild=inter.guild)
            embed = disnake.Embed(
                description="✅ Автомод правило **Запрещенные слова** было создано!",
                color=self.color.GREEN,
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

        except disnake.errors.Forbidden:
            return await inter.send(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description="❌ У бота нет прав на выполнения этого действия!",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )

    @disnake.ui.button(
        label="Удалить все автомод правила", style=disnake.ButtonStyle.red, row=1
    )
    async def delete_all_automod_rules(self, button: disnake.ui.Button, inter):
        if not inter.user == self.inter.author:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    description=f"❌ | Вы не можете этого сделать! Запустите команду самостоятельно, чтобы использовать эти кнопки.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        automod_rules = await inter.guild.fetch_automod_rules()
        rules_to_delete = list(
            filter(lambda rule: rule.creator.id == self.bot.user.id, automod_rules)
        )
        if not rules_to_delete:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    title=f"{self.otheremojis.WARNING} Ошибка!",
                    description=f"❌ Автомод правила, созданные ботом, отсутствуют на сервере.",
                    color=self.color.RED,
                ),
                ephemeral=True,
            )
        for rule in rules_to_delete:
            await rule.delete()

        embed = disnake.Embed(
            description=f"✅ Автомод правила успешно удалены!",
            color=self.color.GREEN,
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
