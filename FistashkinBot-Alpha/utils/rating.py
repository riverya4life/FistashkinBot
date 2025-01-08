import disnake
from classes import database as db


class Rating:
    async def rating_rank(self, member: disnake.Member):
        rank_data = await db.get_data(
            member=member.guild.id,
            all_data=True,
            filters="ORDER BY level DESC, xp DESC"
        )

        rank_data = [
            (data[0], data[1]) for data in rank_data if member.guild.get_member(data[0]) and not member.guild.get_member(data[0]).bot
        ]
        
        user_rank_position = next(
            (i + 1 for i, (user_id, _) in enumerate(rank_data) if user_id == member.id), 
            0
        )

        users_rank_len = len(rank_data)
        return user_rank_position, users_rank_len

    async def rating_balance(self, member: disnake.Member):
        balance_data = await db.get_data(
            member=member.guild.id,
            all_data=True,
            filters="ORDER BY balance DESC"
        )

        balance_data = [
            (data[0], data[1]) for data in balance_data if member.guild.get_member(data[0]) and not member.guild.get_member(data[0]).bot
        ]

        user_balance_position = next(
            (i + 1 for i, (user_id, _) in enumerate(balance_data) if user_id == member.id), 
            0
        )

        users_balance_len = len(balance_data)
        return user_balance_position, users_balance_len