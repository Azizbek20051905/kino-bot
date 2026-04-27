from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from core.settings import settings
from core.handlers.basic import (admin_panel, select_add_channel, answer_channel_name, answer_channel_link,
                                 get_movie_name, get_movie_description, get_movie_country, get_movie_language,
                                 get_movie_year, get_movie_genre, get_movie_is_series, get_movie_status, get_movie_image, get_movie_parts_count,
                                 get_movie_video, get_ads_link, get_ads_name,
                                 send_movies, send_movies_id, sub_channel_answer, sub_channel, user_views, generate_movie_caption)
from core.handlers.callback import (deleted_answers, pause_message, selected_channel, selected_admin_panel, selected_del_channel, deleted_channels,
                                     on_channels, movies, add_movies, start_answer_users, start_message, status_all, send_answer_user, answer_forward_id,
                                     delete_movies, del_movies_id, add_ads, del_ads, del_ads_id, 
                                     movie_page_handler, movie_part_switch, movie_list_handler,
                                     add_saved, del_saved, clear_admin, messages_status,
                                     movie_edit_menu, movie_edit_field, movie_add_part_start, movie_edit_value_handler,
                                     movie_finish_edit, main_channel_view, main_channel_edit_start, main_channel_edit_finish)
from core.utils.callbackdata import AdminPanel, DeleteChannel, AddSaved, DeleteSaved, Statistic, MoviePage, AdminManage, AdminPerm, MovieEdit, MainChannel
from core.states.states import GetChannel_data, ForwardMessage, MessageNext, MoviesData, GetAds_data, AdminState, EditMovieState, MainChannelState
from core.handlers.admin_mgmt import list_admins, add_admin_start, add_admin_finish_id, add_admin_finish_name, edit_admin_permissions, toggle_permission, remove_admin
from core.handlers.inlinemode import inline_echo
from core.handlers.error_handler import error_handler
from core.utils.commands import set_commands
from core.config import set_global_var, global_var
from core.filters.filter import CheckSubChannel, CheckText, Checktext_two
from core.db_api.db import get_movie_details, update_movies, add_admin, get_movie_parts
from core.keyboards.inline import client_user_btn, users_btn

from datetime import datetime, timedelta

import asyncio
import logging

# Replaced terminal logging with only ERROR level to reduce noise
logging.basicConfig(level=logging.ERROR)

async def start_bot(bot: Bot):
    add_admin(settings.bots.admin_id, is_super=True)
    await bot.send_message(settings.bots.admin_id, text="Bot ishga tushdi!")
    await set_commands(bot)


async def get_start(message: types.Message, bot: Bot, command: CommandObject):
    set_global_var(message.from_user.id, datetime.now().isoformat())
    
    args = command.args
    if args and args.isdigit():
        movie_id = int(args)
        movie = get_movie_details(movie_id=movie_id)
        
        if movie:
            parts = get_movie_parts(movie['id'])
            if not parts:
                await message.answer("Bu kino uchun video topilmadi!")
                return
                
            part = parts[0]
            
            global user_views
            if message.from_user.id not in user_views:
                user_views[message.from_user.id] = {}
            
            if movie_id not in user_views[message.from_user.id]:
                user_views[message.from_user.id][movie_id] = movie_id
                update_movies(id=movie['id'], view=int(movie['views'])+1)
            
            btn = users_btn(data=movie, user_id=message.from_user.id, current_part=part[0])
            caption = generate_movie_caption(movie, part)
            
            await bot.send_video(
                chat_id=message.from_user.id, 
                video=part[1], 
                caption=caption, 
                reply_markup=btn
            )
            return

    text = f"Tanlang:"
    await message.answer(text=text, reply_markup=client_user_btn())


async def get_help(message: types.Message, bot: Bot):
    set_global_var(message.from_user.id, datetime.now().isoformat())
    text = (
        f"🖐 <b>Assalomu Alaykum,</b> <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>!\n\n"
        f"❓ <b>Botdan qanday foydalanish mumkin?</b>\n\n"
        f"1️⃣ <b>Kino qidirish:</b> Buning uchun pastdagi menyudan Barcha kinolar tugmasini tanlab so'ng kino nomini kiriting.\n"
        f"Yoki taqdim etilgan maxsus kodni yuboring.\n"
        f"2️⃣ <b>ID orqali topish:</b> Agar sizda kinoning ID raqami bo'lsa, uni yozib yuboring va bot sizga videoni taqdim etadi.\n"
        f"3️⃣ <b>Saqlanganlar:</b> O'zingizga yoqqan kinolarni 'Saqlash' tugmasi orqali shaxsiy ro'yxatingizga qo'shib qo'yishingiz mumkin.\n\n"
        f"📢 <b>Eslatma:</b> Kinolarni yuklab olish uchun avval bot ko'rsatgan kanallarga obuna bo'lishingiz shart.\n\n"
        f"💡 <i>Bot doimiy ravishda yangi kinolar bilan boyitib boriladi!</i>"
    )
    await message.answer(text=text, reply_markup=client_user_btn())

async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Bot to'xtadi!")


async def start():
    bot = Bot(token=settings.bots.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    dp = Dispatcher()
    dp.startup.register(start_bot)

    dp.inline_query.register(inline_echo)
    dp.callback_query.register(selected_admin_panel, AdminPanel.filter(F.model =='admin_panel'))
    dp.callback_query.register(selected_channel, AdminPanel.filter(F.model =='channels'))
    dp.callback_query.register(select_add_channel, AdminPanel.filter(F.model =='add_channel'))
    dp.callback_query.register(selected_del_channel, AdminPanel.filter(F.model =='del_channel'))
    dp.callback_query.register(deleted_channels, DeleteChannel.filter(F.model =='delete_channel'))
    dp.callback_query.register(on_channels, AdminPanel.filter(F.model =='on_channel'))
    dp.callback_query.register(on_channels, AdminPanel.filter(F.model =='off_channel'))
    dp.callback_query.register(status_all, AdminPanel.filter(F.model =='statistic'))
    dp.callback_query.register(send_answer_user, AdminPanel.filter(F.model =='xabar'))
    dp.callback_query.register(sub_channel, AdminPanel.filter(F.model =='checksub') )
    dp.message.register(sub_channel_answer, CheckSubChannel())
    dp.message.register(answer_forward_id, ForwardMessage.id)
    dp.callback_query.register(movies, AdminPanel.filter(F.model =='movies'))
    dp.callback_query.register(add_movies, AdminPanel.filter(F.model =='add_movie'))
    dp.callback_query.register(delete_movies, AdminPanel.filter(F.model =='del_movie'))
    dp.callback_query.register(del_movies_id, DeleteChannel.filter(F.model =='delete_movie'))
    dp.callback_query.register(add_ads, AdminPanel.filter(F.model =='add_ads'))
    dp.callback_query.register(del_ads, AdminPanel.filter(F.model =='del_ads'))
    dp.callback_query.register(del_ads_id, DeleteChannel.filter(F.model =='deleted_ads'))
    dp.callback_query.register(add_saved, AddSaved.filter(F.model =='add_save'))
    dp.callback_query.register(del_saved, DeleteSaved.filter(F.model =='del_save'))
    dp.callback_query.register(clear_admin, AdminPanel.filter(F.model =='clear'))
    dp.callback_query.register(messages_status, AdminPanel.filter(F.model =='xabar_status'))
    dp.callback_query.register(messages_status, AdminPanel.filter(F.model =='update'))
    dp.callback_query.register(pause_message, Statistic.filter(F.model =='stop'))
    dp.callback_query.register(start_message, Statistic.filter(F.model =='play'))
    dp.callback_query.register(deleted_answers, AdminPanel.filter(F.model =='delete_status'))
    dp.callback_query.register(movie_page_handler, MoviePage.filter(F.model =='movie_page'))
    dp.callback_query.register(movie_part_switch, MoviePage.filter(F.model =='part'))
    dp.callback_query.register(movie_list_handler, AdminPanel.filter(F.model =='movie_list'))
    
    # Admin management
    dp.callback_query.register(list_admins, AdminManage.filter(F.action == 'list'))
    dp.callback_query.register(add_admin_start, AdminManage.filter(F.action == 'add'))
    dp.message.register(add_admin_finish_id, AdminState.user_id)
    dp.message.register(add_admin_finish_name, AdminState.full_name)
    dp.callback_query.register(edit_admin_permissions, AdminManage.filter(F.action == 'edit'))
    dp.callback_query.register(toggle_permission, AdminPerm.filter())
    dp.callback_query.register(remove_admin, AdminManage.filter(F.action == 'delete'))
    
    # dp.message.register(start_answer_users, MessageNext.model)
    dp.message.register(get_movie_name, MoviesData.name)
    dp.message.register(get_movie_description, MoviesData.description)
    dp.message.register(get_movie_country, MoviesData.country)
    dp.message.register(get_movie_language, MoviesData.language)
    dp.message.register(get_movie_year, MoviesData.year)
    dp.message.register(get_movie_genre, MoviesData.genre)
    dp.callback_query.register(get_movie_status, MoviesData.status)
    dp.message.register(get_movie_image, MoviesData.image)
    dp.callback_query.register(get_movie_is_series, MoviesData.is_series)
    dp.message.register(get_movie_parts_count, MoviesData.parts_count)
    dp.message.register(get_movie_video, MoviesData.video)
    
    dp.message.register(get_ads_name, GetAds_data.name)
    dp.message.register(get_ads_link, GetAds_data.link)
    dp.message.register(answer_channel_name, GetChannel_data.name)
    dp.message.register(answer_channel_link, GetChannel_data.link)
    dp.message.register(send_movies, Checktext_two())
    dp.message.register(send_movies_id, CheckText())
    dp.message.register(get_start, Command(commands='start'))
    dp.message.register(get_help, Command(commands='help'))
    dp.callback_query.register(movie_edit_menu, MovieEdit.filter(F.action == 'menu'))
    dp.callback_query.register(movie_edit_field, MovieEdit.filter(F.action == 'edit_field'))
    dp.callback_query.register(movie_add_part_start, MovieEdit.filter(F.action == 'add_part'))
    dp.callback_query.register(movie_finish_edit, MovieEdit.filter(F.action == 'finish_edit'))
    dp.message.register(movie_edit_value_handler, EditMovieState.value)

    # Main channel management
    dp.callback_query.register(main_channel_view, MainChannel.filter(F.action == 'view'))
    dp.callback_query.register(main_channel_edit_start, MainChannel.filter(F.action == 'edit'))
    dp.message.register(main_channel_edit_finish, MainChannelState.link)

    dp.message.register(admin_panel, Command(commands='admin'))
    
    # Register error handler to send bugs to super admin
    dp.errors.register(error_handler)

    dp.shutdown.register(stop_bot)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())