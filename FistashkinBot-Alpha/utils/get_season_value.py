import datetime


class Season:
    def get_seasonal():
        now = datetime.datetime.now()
        if (now.month == 10 and now.day >= 31) or (now.month == 11 and now.day <= 2):
            return {
                "footer": f"Риверька © {now.year} Все права защищены 🎃",
                "economy": {
                    "exp": 5 * 4.0,
                    "balance": 0.50 * 4.0,
                    "multiplier": 4.0,
                    "commission": 3,
                },
                "color": {
                    "main": 0xE95230,
                    "gray": 0xE95230,
                    "green": 0x00FF00,
                    "red": 0xFF0000,
                    "dark_gray": 0x2B2D31,
                    "rank_card_main": 0xE39E7E,
                    "rank_card_back": 0x7A5544,
                },
                "emoji": {
                    "slot": [
                        "👹",
                        "👻",
                        "☠️",
                        "🕷️",
                        "🦇",
                        "🦉",
                        "🕸️",
                        "🎃",
                        "🧛",
                        "🩸",
                        "🎩",
                        "🔮",
                    ],
                    "currency": "🎃",
                },
            }

        elif (
            25 <= now.day <= 31
            and now.month == 12
            or (1 <= now.day <= 15 and now.month == 1)
        ):
            return {
                "footer": f"Риверька © {now.year} Все права защищены ❄️",
                "economy": {
                    "exp": 5 * 8.0,
                    "balance": 0.50 * 8.0,
                    "multiplier": 8.0,
                    "commission": 2,
                },
                "color": {
                    "main": 0xFFFFFF,
                    "gray": 0xE95230,
                    "green": 0x00FF00,
                    "red": 0xFF0000,
                    "dark_gray": 0x2B2D31,
                    "rank_card_main": 0xE39E7E,
                    "rank_card_back": 0x7A5544,
                },
                "emoji": {
                    "slot": [
                        "🎀",
                        "🎉",
                        "🍾",
                        "🎄",
                        "🔔",
                        "❄️",
                        "🎅",
                        "🍨",
                        "☃️",
                        "🏂",
                        "🌨️",
                        "🧊",
                    ],
                    "currency": "❄️",
                },
            }

        else:
            return {
                "footer": f"Риверька © {now.year} Все права защищены 🍪",
                "economy": {
                    "exp": 5,
                    "balance": 0.50,
                    "multiplier": 2.0,
                    "commission": 4,
                },
                "color": {
                    "main": 0xC0694E,
                    "gray": 0xE95230,
                    "green": 0x00FF00,
                    "red": 0xFF0000,
                    "dark_gray": 0x2B2D31,
                    "rank_card_main": 0xE39E7E,
                    "rank_card_back": 0x7A5544,
                },
                "emoji": {
                    "slot": [
                        "🍒",
                        "🍊",
                        "🍋",
                        "🍇",
                        "🔔",
                        "💎",
                        "🍀",
                        "🍎",
                        "🫐",
                        "🍍",
                        "🥭",
                        "🍆",
                    ],
                    "currency": "🍪",
                },
            }
