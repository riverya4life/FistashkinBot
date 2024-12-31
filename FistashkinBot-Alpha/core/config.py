from environs import Env


class Config:
    env = Env()
    env.read_env()
    TOKEN = env.str("TOKEN")
    MONGODB_LINK = env.str("MONGODB_LINK")
    SPOTIFY_CLIENT_ID = env.str("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = env.str("SPOTIFY_CLIENT_SECRET")
    SDC_TOKEN = env.str("SDC_TOKEN")

    LAVALINK_SETTINGS = {
        "host": "127.0.0.1",
        "port": 2333,
        "identifier": "Sukuna",
        "password": "n1ke02061992",
    }
