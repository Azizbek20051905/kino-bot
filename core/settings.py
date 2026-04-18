from typing import Any
from environs import Env
from dataclasses import dataclass


# @dataclass
# class CheckSub:
#     def __init__(self, is_checked = False):
#         self.is_checked = is_checked
    
#     def get(self):
#         return self.is_checked

# check = CheckSub()


@dataclass
class Bots:
    bot_token: str
    admin_id: int
    base_channel: str

@dataclass
class Settings:
    bots: Bots

def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str("TOKEN"),
            admin_id=env.str("ADMIN_ID"),
            base_channel=env.str("BASE_CHANNEL_URL")
        )
    )

settings = get_settings('input')
