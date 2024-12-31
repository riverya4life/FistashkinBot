import disnake

from .get_season_value import Season


class ProfileEmojis():
    ONLINE = "<:online:1193412137272475669>"
    OFFLINE = "<:offline:1193412134902710373>"
    IDLE = "<:idle:1193412141575831582>"
    DND = "<:dnd:1193412139243802736>"

    STATUS = {
        disnake.Status.online: f"{ONLINE}В сети",
        disnake.Status.offline: f"{OFFLINE}Не в сети",
        disnake.Status.idle: f"{IDLE}Неактивен",
        disnake.Status.invisible: f"{OFFLINE}Невидимый",
        disnake.Status.dnd: f"{DND}Не беспокоить",
    }

    BADGES = {
        "staff": "<:staff:1074644138936512532>",
        "partner": "<:partner:1074644131160264764>",
        "hypesquad": "<:hypesquad_events:1074644144179384390>",
        "bug_hunter": "<:bug_hunter:1074644117151289346>",
        "hypesquad_bravery": "<:hypesquad_bravery:1074644134209536112>",
        "hypesquad_brilliance": "<:hypesquad_brilliance:1074644145991335946>",
        "hypesquad_balance": "<:hypesquad_balance:1074644128199090307>",
        "early_supporter": "<:early_supporter:1074644126055792650>",
        "bug_hunter_level_2": "<:golden_bug_hunter:1074644141260156969>",
        "early_verified_bot_developer": "<:verified_bot_developer:1074644136042434631>",
        "verified_bot_developer": "<:verified_bot_developer:1074644136042434631>",
        "moderator_programs_alumni": "<:moderator_programms_alumni:1074644124428423188>",
        "discord_certified_moderator": "<:certified_moderator:1074644119944695808>",
        "verified_developer": "<:verified_bot_developer:1074644136042434631>",
        "active_developer": "<:active_developer:1074646994854879263>",
    }

    SPOTIFY = "<:spotify:1193407822491287652>"
    UPDATED_NICKNAME = "<:originally_known_as:1137162143695900673>"
    BOOSTER_SUBSCRIBER = "<:subscriber_nitro:1074644121714708570>"
    NITRO_BOOSTER = "<a:nitro_boost:1152545187978031147>"
    DEVELOPER = (
        "<:dev:1263785756477095966>"  # "🍪"  # "<:developer:1154073625406750750>"
    )


class ServerEmojis():
    MEMBERS_TOTAL = "<:members_total:1198636744325730314>"
    MEMBERS = "<:members:1198636742148903053>"
    BOT = "<:bot:1198636735660302336>"

    CHANNELS_TOTAL = "<:channels_total:1198636738235600987>"
    TEXT_CHANNEL = "<:text_channel:1198636729914105976>"
    VOICE_CHANNEL = "<:voice_channel:1198636731281440768>"
    STAGE_CHANNEL = "<:stage_channel:1198636726265053255>"
    FORUM_CHANNEL = "<:forum_channel:1198636740156600401>"
    ANNOUNCEMENT_CHANNEL = "<:announce_channel:1198636734116802570>"


class MusicEmojis():
    PLAY = "<:play:1079792261182787634>"
    PAUSE = "<:test:1080223546074218558>"
    STOP = "<:stop:1079792267243569152>"
    QUEUE = "<:queue:1079792263066030213>"
    SKIP = "<:skip:1079792265460994049>"
    COMEBACK = "<:comeback:1079792250055299192>"
    VOLUME_LOW = "<:volume_low:1079792268577349662>"
    VOLUME_UP = "<:volume_up:1079792270913581116>"
    LOOP = "<:loop:1079792253112963173>"
    LOOP_NONE = "<:loop_none:1079792254723567736>"
    LOOP_ONE = "<:loop_one:1079792256749408416>"

    PLAYER_SETTINGS = {"playerEditSeconds": 4, "playerProgressCount": 10, "waiting": 0}

    EMOJIS = {
        "playEmoji": "▶️",
        "stopEmoji": "⏹️",
        "pauseEmoji": "⏸️",
        "skipEmoji": "⏭️",
        "shuffleEmoji": "🔀",
        "loopEmoji": "🔁",
        "onLoopMode": "🔂",
        "backEmoji": "⏮️",
        "volumepEmoji": "🔊",
        "volumemEmoji": "🔉",
        "playlistEmoji": "📋",
        "bassboostEmoji": "🅱️",
    }


class OtherEmojis():
    value = Season.get_seasonal()
    ERROR = "<:error:1129825410109145239>"
    WARNING = "<:warning:1129824531574435902>"
    PAYPAL = "<:paypal:1129821760959828008>"
    GITHUB = "<:github:1129821240610259034>"
    PATREON = "<:patreon:1129822642279559178>"

    REELS = value["emoji"]["slot"]


class RolePlay():
    FIGHT_CLUB_VICTORY_IMAGES = [
        "https://c.tenor.com/cdgZuuTlmcgAAAAC/tyler-edward-norton.gif",
        "https://c.tenor.com/QeOlwQTVuYoAAAAC/fight-club.gif",
        "https://i.gifer.com/fqQ.gif",
        "https://i.gifer.com/2cs2.gif",
        "https://i.gifer.com/BEA.gif",
        "https://i.gifer.com/22bP.gif",
        "https://i.gifer.com/2cro.gif",
    ]

    FIGHT_CLUB_DEFEAT_IMAGES = [
        "https://c.tenor.com/XsBc8PdfavwAAAAC/fighting-unground.gif",
        "https://i.gifer.com/1dsG.gif",
        "https://i.gifer.com/18N1.gif",
    ]

    SAD_ERROR_IMAGES = [
        "https://c.tenor.com/mwNf-HcmrXcAAAAC/cheburashka-sad.gif",
        "https://c.tenor.com/EFBwy6rvcXEAAAAC/sad-anime.gif",
        "https://i.gifer.com/FNm.gif",
        "https://c.tenor.com/P85Hx_Funb0AAAAC/jesse-breaking.gif",
    ]


class EightBall():
    RESPONSES = [
        "Это точно 👌",
        "Очень даже вряд-ли 🤨",
        "Нет ❌",
        "Да, безусловно ✔",
        "Вы можете рассчитывать на это 👌",
        "Вероятно 🤨",
        "Перспектива хорошая 🤔",
        "Да ✔",
        "Знаки указывают да 👍",
        "Ответ туманный, попробуйте еще раз 👀",
        "Спроси позже 👀",
        "Лучше не говорить тебе сейчас 🥵",
        "Не могу предсказать сейчас 👾",
        "Сконцентрируйтесь и спросите снова 🤨",
        "Не рассчитывай на это 🙉",
        "Мой ответ - Нет 😕",
        "Мои источники говорят нет 🤨",
        "Перспективы не очень 🕵️‍♂️",
        "Очень сомнительно 🤔",
    ]


class Faq:
    FAQ = [
        {
            "question": f"Как посмотреть информацию о боте?",
            "answer": f"Достаточно ввести команду косой черты - **/инфо**.",
        },
        {
            "question": f"Как добавить бота на свой сервер?",
            "answer": f"О-о-очень просто! В профиле есть кнопка **Добавить на сервер**, кликаете на неё, выбираете сервер и **готово**!",
        },
        {
            "question": f"Почему я не вижу команды косой черты на сервере?",
            "answer": f"Возможно, что владелец сервера запретил использовать команды косой черты Вам или определённым ролям.",
        },
        {
            "question": f"Как сообщить о наличии багов и недоработок?",
            "answer": f"Перейдите на сервер Discord, найдите канал <#1066328008664813610> и создайте публикацию с обнаруженным багом. Благодаря этому бот будет получать патчи с исправлением багов и прочего.",
        },
        {
            "question": f"Ошибка Forbidden, что делать?",
            "answer": f"Бот не может совершить действие. Убедитесь, что бот имеет право(-а) на совершение действия.",
        },
        {
            "question": f"Ошибка NotFound, что делать?",
            "answer": f"Боту не удалось найти объект (пользователя, сервер и т.д.).",
        },
        {
            "question": f"Ошибка HTTPException, что делать?",
            "answer": f"Бот отправил некорректный запрос на сервера Discord, из-за чего получил ошибку. Убедитесь, что вы ввели всё верно.",
        },
    ]
