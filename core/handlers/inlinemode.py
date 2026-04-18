from aiogram import Bot, Dispatcher, types
from core.db_api.db import search_movie, get_movie_details, all_movie, get_saveds
import hashlib
import uuid
from core.config import set_global_var, global_var
from datetime import datetime, timedelta


async def inline_echo(inline_query: types.InlineQuery, bot: Bot):
    text = inline_query.query or None
    set_global_var(inline_query.from_user.id, datetime.now().isoformat())

    if text == "saved":
        movies = get_saveds(users_id=int(inline_query.from_user.id))
        results = []

        if movies:
            for movie in movies:
                results.append(types.InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    thumbnail_url="https://st.depositphotos.com/1555678/1276/i/450/depositphotos_12766135-stock-photo-3d-cinema-clapper-film-reel.jpg",
                    title=movie['name'],
                    description=f"📀Hajmi: {movie['size']} MB\n👁:{movie['views']}",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"movie {movie['movie_id']}"
                    ),))
        
        try:
            await bot.answer_inline_query(inline_query_id=inline_query.id,
                                        results=results,
                                        cache_time=1, is_personal=True)
        except Exception as e:
            print()
            print("error: ", e)
            print()
    
    if text == None:
        movies = all_movie()
        results = []

        if movies:
            for movie in movies:
                results.append(types.InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    thumbnail_url="https://st.depositphotos.com/1555678/1276/i/450/depositphotos_12766135-stock-photo-3d-cinema-clapper-film-reel.jpg",
                    title=movie['name'],
                    description=f"📀Hajmi: {movie['size']} MB\n👁:{movie['views']}",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"movie {movie['id']}"
                    ),))
        
        try:
            await inline_query.answer(results=results, cache_time=1)
        except Exception as e:
            print()
            print("error: ", e)
            print()

    else:
        movies = search_movie(text)
        results = []

        if movies:
            
            for movie in movies:
                results.append(types.InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    thumbnail_url="https://st.depositphotos.com/1555678/1276/i/450/depositphotos_12766135-stock-photo-3d-cinema-clapper-film-reel.jpg",
                    title=movie['name'],
                    description=f"📀Hajmi: {movie['size']} MB\n👁:{movie['views']}",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"movie {movie['id']}"
                    ),))
        try:
            await bot.answer_inline_query(inline_query_id=inline_query.id,
                                        results=results,
                                        cache_time=1, is_personal=True)
        except Exception as e:
            print()
            print("error: ", e)
            print()
    