from string import Template


class MyTemplate(Template):
    delimiter = "["
    pattern = r"""\[(?:(?P<escaped>\[) | (?P<named>[_a-z][_a-z0-9]*)\] | (?P<braced>[_a-z][_a-z0-9]*)\] | (?P<invalid>))"""

    def welcome_function(member, message):
        variables = {
            "memberMention": member.mention,
            "guildMembers": str(len(member.guild.members)),
            "guild": member.guild.name,
            "member": member,
        }

        return MyTemplate(message).safe_substitute(variables)


class LevelUp:
    LEVEL_UP_TEXT = [
        "{member}, ты повысил свой уровень на **{level} LVL!**",
        "{member}, ничего себе! Ты апнул свой уровень до **{level} LVL!**",
        "Полегче {member}, ты продвинулся до **{level}** уровня! Поздравляю!",
        "Воу-воу-воу {member}, что ты делаешь? Ты повысил свой уровень до **{level} LVL!**",
        "{member} да ты монстр! Твой уровень был повышен до **{level} LVL!**",
        "{member} Поздравляю! Ты достиг **{level} LVL!**",
        "Ура! {member} только что достиг **{level} LVL!** Мои поздравления ^•^",
    ]
