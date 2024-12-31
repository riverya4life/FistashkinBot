import disnake

from classes import database as db


class Rating:
    def __init__(self):
        self.db = db

    async def rating_rank(self, member: disnake.Member):
        rank_data = await self.db.get_data(
            member=member.guild.id,
            all_data=True,
            filters="ORDER BY level DESC, xp DESC",
        )

        user_rank_position = 0
        for i in range(len(rank_data)):
            member = member.guild.get_member(rank_data[i][0])
            if member is not None and not member.bot:
                user_rank_position = user_rank_position + 1
                if rank_data[i][0] == member.id:
                    break

        users_rank_len = 0
        for row in rank_data:
            member = member.guild.get_member(row["member_id"])
            if member is not member.bot:
                users_rank_len = users_rank_len + 1

        return user_rank_position, users_rank_len

    async def rating_balance(self, member: disnake.Member):
        balance_data = await self.db.get_data(
            member=member.guild.id, all_data=True, filters="ORDER BY balance DESC"
        )

        user_balance_position = 0
        for i in range(len(balance_data)):
            member = member.guild.get_member(balance_data[i][0])
            if member is not None and not member.bot:
                user_balance_position = user_balance_position + 1
                if balance_data[i][0] == member.id:
                    break

        users_balance_len = 0
        for row in balance_data:
            member = member.guild.get_member(row["member_id"])
            if member is not member.bot:
                users_balance_len = users_balance_len + 1

        return user_balance_position, users_balance_len
