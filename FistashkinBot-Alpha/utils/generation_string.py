import random


class Generation:
    async def generation(self, string: str):
        chars = list(string)

        for i in range(len(chars) - 1, 0, -1):
            random_number = random.random()

            if chars[i] == " " or chars[i] == "-":
                continue

            if random_number < 0.7:
                chars[i] = "#"

        new_string = "".join(chars)
        return new_string
