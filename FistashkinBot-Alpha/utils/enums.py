from .get_season_value import Season


class Color():
    value = Season.get_seasonal()
    MAIN = value["color"]["main"]
    GRAY = value["color"]["gray"]
    GREEN = value["color"]["green"]
    RED = value["color"]["red"]
    DARK_GRAY = value["color"]["dark_gray"]


class RankCardColor():
    value = Season.get_seasonal()
    RANK_CARD_MAIN = value["color"]["rank_card_main"]
    RANK_CARD_BACKGROUND = value["color"]["rank_card_back"]


class Enum():
    def format_large_number(self, number):
        str_number = str(number)
        parts = str_number.split(".")
        integer_part = parts[0]
        groups = []
        while len(integer_part) > 0:
            groups.insert(0, integer_part[-3:])
            integer_part = integer_part[:-3]
        formatted_number = ",".join(groups)
        if len(parts) == 2:
            formatted_number += "." + parts[1]

        return formatted_number
