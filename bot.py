from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils import executor

from core.db_api.db import get_book_search
import hashlib
import logging

API_TOKEN = '7283223909:AAHOsh3nNYU2RAOPi1uFhcs3NW4TtecWvGM'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
    text = inline_query.query or 'echo'
    books = get_book_search(text)
    result_id: str = hashlib.md5(text.encode()).hexdigest()

    item = []

    print(text)

    # for book in books:
    #     input_content = InputTextMessageContent(text)
    #     item.append(InlineQueryResultArticle(
    #         input_message_content=input_content,
    #         id=result_id,
    #         title=str(book['name']),
    #     ))
    
    item = InlineQueryResultArticle(
            input_message_content=input_content,
            id=result_id,
            title="Hello test",
            )
    
    await bot.answer_inline_query(inline_query_id=inline_query.id,
                                  results=[item],
                                  cache_time=1, is_personal=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
