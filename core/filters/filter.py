from typing import Any
from aiogram.filters import Filter
from aiogram.types import Message
from core.db_api.db import all_channels, get_checkbox
from aiogram import Bot
from core.settings import settings


class CheckSubChannel(Filter):
    async def __call__(self, message: Message, bot: Bot):
        is_true = get_checkbox()
        if is_true['is_true']:
            channel_list = []
            channels = all_channels()
            
            if channels:
                for channel in channels:
                    links = str(channel['link']).replace('https://t.me/', '@')

                    try:
                        user_status = await bot.get_chat_member(str(links), message.from_user.id)

                        if user_status.status in ['member', 'administrator', "creator"]:
                            channel_list.append(False)
                        else:
                            channel_list.append(True)
                    except Exception as e:
                        print("Error channel link: ", e)        
            
            if True not in channel_list:
                return False
            else:
                return True
        else:
            return False


class CheckText(Filter):
    async def __call__(self, message: Message, bot: Bot):
        text = ((message.text).strip()).split()
        if len(text) == 1 and text[0].isdigit():
            return True
        else:
            return False

class Checktext_two(Filter):
    async def __call__(self, message: Message, bot: Bot):
        text = (message.text).split()
        
        if len(text) == 2:
            return True
        else:
            return False