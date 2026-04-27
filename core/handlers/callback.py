import asyncio
from datetime import datetime, timedelta
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from core.settings import settings
from core.utils.callbackdata import AdminPanel, DeleteChannel, AddSaved, DeleteSaved, MoviePage, MovieEdit, MainChannel
from core.keyboards.inline import (channel_btn, adminpanel_btn, del_channel_btn,
                                   get_back_btn, movies_btn, del_movies_btn,
                                   users_btn, status_message_btn, movie_pagination_btn)
from core.db_api.db import (delete_channel, update_channel_details, all_channels, 
                            update_checkbox, all_movie, delete_movies_id, all_ads, 
                            delete_ads, insert_saved, get_movie_details, get_movie_parts, delete_saved, get_admin, update_movie_metadata, insert_movie_part,
                            get_setting, update_setting)
# from core.settings import CheckSub
from core.states.states import ForwardMessage, MoviesData, GetChannel_data, GetAds_data, MessageNext, EditMovieState, MainChannelState
from core.config import set_global_var, global_var
from core.handlers.basic import user_views, answer_users, generate_movie_caption
import uuid

sending_messages = True
send_answer_messages = {}

async def selected_channel(call: CallbackQuery, bot: Bot, state: FSMContext):
    admin = get_admin(call.from_user.id)
    if not admin or not admin['can_manage_channels']:
        await call.answer("Sizda kanallarni boshqarish ruxsati yo'q!", show_alert=True)
        return
    await state.clear()
    await bot.edit_message_text(text="Kanallar", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=channel_btn())
    # await call.message.answer(text="Kanallar", reply_markup=channel_btn())

async def selected_admin_panel(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await bot.edit_message_text(text="Admin panel", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=adminpanel_btn(model='xabar'))

async def selected_del_channel(call: CallbackQuery, bot: Bot, callback_data: AdminPanel):
    await bot.edit_message_text(text="Kanallarni o'chirish uchun ustiga birmarta bosish kifoya:", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=del_channel_btn())
    # await call.message.answer(text="Kanallar", reply_markup=channel_btn())

async def deleted_channels(call: CallbackQuery, bot: Bot, callback_data: DeleteChannel):
    result = delete_channel(channel_id=callback_data.id)
    print(result)
    
    await bot.edit_message_text(text="Kanallarni o'chirish uchun ustiga birmarta bosish kifoya:", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=del_channel_btn())
    await call.message.answer(text="Kanal o'chirildi!")
    # await call.message.answer(text="Kanallar", reply_markup=channel_btn())

async def on_channels(call: CallbackQuery, bot: Bot, callback_data: AdminPanel):
    # await call.answer(text="Kanallar")
    if callback_data.model == 'on_channel':
        update_checkbox(is_true = True)
        print("on_channel")
        
        btn = channel_btn()
        await bot.edit_message_text(text="Kanallar", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=btn)
        # await call.answer(text="Kanallar", reply_markup=btn, show_alert=False)
    elif callback_data.model == 'off_channel':
        update_checkbox(is_true = False)
        print("off_channel")
        
        btn = channel_btn()
        # btn = channel_btn()
        await bot.edit_message_text(text="Kanallar", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=btn)
        # await call.answer(text="Kanallar", reply_markup=btn, show_alert=False)

async def status_all(call: CallbackQuery, bot: Bot, callback_data: AdminPanel):
    admin = get_admin(call.from_user.id)
    if not admin or not admin['can_view_stats']:
        await call.answer("Sizda statistikani ko'rish ruxsati yo'q!", show_alert=True)
        return
    global user_views
    all_user = len(global_var)
    print(all_user)
    active_user = 0
    now = datetime.now()
    one_day_ago = (now - timedelta(hours=24)).isoformat()
    
    if global_var:
        for i in global_var:
            print(global_var[i])
            print(global_var[i])
            if global_var[i] > one_day_ago:
                active_user += 1
    print(active_user)

    movies = all_movie()
    if movies:
        all_movies = len(all_movie())
    else:
        all_movies = 0
    
    active_movies = 0

    if user_views:
        for i in user_views:
            active_movies += len(user_views[i])
    
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    text = f"👥Umumiy foydalanuvchilar soni: <b>{all_user}</b>\n👤Aktiv foydalanuvchilar soni: <b>{active_user}</b>\n🎞Barcha kinolar soni: <b>{all_movies}</b>\n📥Jami yuklab olingan kinolar: {active_movies}\n\n📅{date}"
    await bot.edit_message_text(text=text, chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=get_back_btn(model="admin_panel"))

# Sms xabar -------- start
async def send_answer_user(call: CallbackQuery, bot: Bot, callback_data: AdminPanel, state: FSMContext):
    admin = get_admin(call.from_user.id)
    if not admin or not admin['can_send_message']:
        await call.answer("Sizda xabar yuborish ruxsati yo'q!", show_alert=True)
        return
    await bot.edit_message_text(text="Xabar kiriting: ", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=get_back_btn(model="admin_panel"))
    await state.set_state(ForwardMessage.id)

async def answer_forward_id(message: types.Message, bot: Bot, state: FSMContext):
    global global_var
    global send_answer_messages
    global answer_users
    global sending_messages
    await state.update_data(id=message.text)
    send_answer_messages['chat_id'] = message.chat.id
    send_answer_messages['message_id'] = message.message_id
    send_answer_messages['reply_markup'] = message.reply_markup

    btn = adminpanel_btn(model='xabar_status')
    await bot.send_message(chat_id=message.from_user.id , text="Xabar yuborish boshlandi", reply_markup=btn)
    answer_users = global_var.copy()

    start = True
    
    for i in global_var.keys():
        if sending_messages:
            await bot.copy_message(chat_id=i, from_chat_id=send_answer_messages['chat_id'], message_id=send_answer_messages['message_id'], reply_markup=send_answer_messages['reply_markup'])
            
            del answer_users[i]
            await asyncio.sleep(3)
        else:
            start = False
            break
    
    if start:
        sending_users = len(global_var) - len(answer_users)
        no_sending_users = len(answer_users)
        date = datetime.now().strftime("%d-%m-%Y %H:%M")

        await message.answer(text=f"Xabar yuborish tugadi\n\n✅Yuborilgan: {sending_users}\n❌Yuborilmaganlar: {no_sending_users}\n\n📆{date}")
        answer_users = {}
        send_answer_messages = {}
        sending_messages = True
        await state.clear()
# Sms xabar -------- end

async def messages_status(call: CallbackQuery, bot: Bot):
    global sending_messages, global_var, answer_users, send_answer_messages

    total_users = len(global_var)
    sending_users = len(global_var) - len(answer_users)
    no_sending_users = len(answer_users)


    if sending_messages:
        text = f"Xabar yuborish\n\nYuborilmoqda: 👤Userlarga\n✅Yuborilgan: {sending_users}\n❌Yuborilmaganlar: {no_sending_users}\n👥Umumiy: {sending_users}/{total_users}\n\n📊Status: Davom etmoqda"
        await bot.edit_message_text(text=text, chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=status_message_btn(play="To'xtatish ⏸", model='stop', message_id=str(uuid.uuid4())))
    else:
        text = f"Yuborilmoqda: 👤Userlarga\n✅Yuborilgan: {sending_users}\n❌Yuborilmaganlar: {no_sending_users}\n👥Umumiy: {sending_users}/{total_users}\n\n📊Status: To'xtatilgan"
        await bot.edit_message_text(text=text, chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=status_message_btn(play="Davom etish ▶️", model='play', message_id=str(uuid.uuid4())))

async def pause_message(call: CallbackQuery, bot: Bot):
    global sending_messages
    global global_var
    global answer_users
    global send_answer_messages
    sending_messages = False

    total_users = len(global_var)
    sending_users = len(global_var) - len(answer_users)
    no_sending_users = len(answer_users)

    if sending_messages:
        text = f"Xabar yuborish\n\nYuborilmoqda: 👤Userlarga\n✅Yuborilgan: {sending_users}\n❌Yuborilmaganlar: {no_sending_users}\n👥Umumiy: {sending_users}/{total_users}\n\n📊Status: Davom etmoqda"
        btn = status_message_btn(play="To'xtatish ⏸", model='stop', message_id=str(uuid.uuid4()))
    else:
        text = f"Yuborilmoqda: 👤Userlarga\n✅Yuborilgan: {sending_users}\n❌Yuborilmaganlar: {no_sending_users}\n👥Umumiy: {sending_users}/{total_users}\n\n📊Status: To'xtatilgan"
        btn = status_message_btn(play="Davom etish ▶️", model='play', message_id=str(uuid.uuid4()))
    
    await bot.edit_message_text(text=text, chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=btn)

async def start_message(call: CallbackQuery, bot: Bot, state: FSMContext):
    global sending_messages
    global global_var
    global answer_users
    global send_answer_messages
    sending_messages = True

    total_users = len(global_var)
    sending_users = len(global_var) - len(answer_users)
    no_sending_users = len(answer_users)

    if sending_messages:
        text = f"Xabar yuborish\n\nYuborilmoqda: 👤Userlarga\n✅Yuborilgan: {sending_users}\n❌Yuborilmaganlar: {no_sending_users}\n👥Umumiy: {sending_users}/{total_users}\n\n📊Status: Davom etmoqda"
        btn = status_message_btn(play="To'xtatish ⏸", model='stop', message_id=str(uuid.uuid4()))
    else:
        text = f"Yuborilmoqda: 👤Userlarga\n✅Yuborilgan: {sending_users}\n❌Yuborilmaganlar: {no_sending_users}\n👥Umumiy: {sending_users}/{total_users}\n\n📊Status: To'xtatilgan"
        btn = status_message_btn(play="Davom etish ▶️", model='play', message_id=str(uuid.uuid4()))
    
    await bot.edit_message_text(text=text, chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=btn)
    await start_answer_users(call.message, bot, state)

async def start_answer_users(message: types.Message, bot: Bot, state: FSMContext):
    global send_answer_messages
    global sending_messages
    global global_var
    global answer_users
    
    users = answer_users.copy()
    start = True
    
    for i in users.keys():
        if sending_messages:
            await bot.copy_message(chat_id=i, from_chat_id=send_answer_messages['chat_id'], message_id=send_answer_messages["message_id"], reply_markup=send_answer_messages['reply_markup'])
            send_answer_messages['chat_id'] = message.chat.id
            send_answer_messages['message_id'] = message.message_id
            send_answer_messages['reply_markup'] = message.reply_markup
            del answer_users[i]
            await asyncio.sleep(3)
        else:
            start = False
            break
    
    if start:
        sending_users = len(global_var) - len(answer_users)
        no_sending_users = len(answer_users)
        date = datetime.now().strftime("%d-%m-%Y %H:%M")
        
        await message.answer(text=f"Xabar yuborish tugadi\n\n✅Yuborilgan: {sending_users}\n❌Yuborilmaganlar: {no_sending_users}\n\n📆{date}")
        answer_users = {}
        send_answer_messages = {}
        sending_messages = True
        await state.clear()

async def deleted_answers(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    global global_var, answer_users, send_answer_messages, sending_messages

    sending_users = len(global_var) - len(answer_users)
    no_sending_users = len(answer_users)
    date = datetime.now().strftime("%d-%m-%Y %H:%M")

    await call.message.answer(text=f"Xabar yuborish tugadi\n\n✅Yuborilgan: {sending_users}\n❌Yuborilmaganlar: {no_sending_users}\n\n📆{date}")
    answer_users = {}
    send_answer_messages = {}
    sending_messages = True
    await state.clear()


# all movies ------- start
async def movies(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(text="Kinolar ", chat_id=call.from_user.id, reply_markup=movies_btn())

async def add_movies(call: CallbackQuery, bot: Bot, state: FSMContext):
    admin = get_admin(call.from_user.id)
    if not admin or not admin['can_add_movie']:
        await call.answer("Sizda kino qo'shish ruxsati yo'q!", show_alert=True)
        return
    await bot.edit_message_text(text="Kino nomini kiriting: ", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=get_back_btn(model="movies"))
    await state.set_state(MoviesData.name)

async def delete_movies(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.edit_message_text(text="Kinoni o'chirish uchun ustiga bir marta bosish kifoya: ", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=del_movies_btn(data=all_movie(), model="delete_movie", go_back='movies'))

async def del_movies_id(call: CallbackQuery, bot: Bot, callback_data: DeleteChannel, state: FSMContext):
    admin = get_admin(call.from_user.id)
    if not admin or not admin['can_del_movie']:
        await call.answer("Sizda kinalarni o'chirish ruxsati yo'q!", show_alert=True)
        return
    delete_movies_id(id=callback_data.id)
    await bot.edit_message_text(text="Kinoni o'chirish uchun ustiga bir marta bosish kifoya: ", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=del_movies_btn(data=all_movie(), model="delete_movie", go_back='movies'))
    await bot.send_message(chat_id=settings.bots.admin_id, text="Kino o'chirildi!")
# all movies ------- end


# all Ads ------- start
async def add_ads(call: CallbackQuery, bot: Bot, state: FSMContext):
    admin = get_admin(call.from_user.id)
    if not admin or not admin['can_manage_ads']:
        await call.answer("Sizda reklamalarni boshqarish ruxsati yo'q!", show_alert=True)
        return
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(text="Reklama nomini kiriting: ", chat_id=call.from_user.id, reply_markup=get_back_btn('admin_panel'))

    await state.set_state(GetAds_data.name)

async def del_ads(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.edit_message_text(text="Reklamani o'chirish uchun ustiga bir marta bosish kifoya: ", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=del_movies_btn(data=all_ads(), model="deleted_ads", go_back='admin_panel'))

async def del_ads_id(call: CallbackQuery, bot: Bot, callback_data: DeleteChannel, state: FSMContext):
    admin = get_admin(call.from_user.id)
    if not admin or not admin['can_manage_ads']:
        await call.answer("Sizda reklamalarni o'chirish ruxsati yo'q!", show_alert=True)
        return
    delete_ads(ads_id=callback_data.id)
    await bot.edit_message_text(text="Kinoni o'chirish uchun ustiga bir marta bosish kifoya: ", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=del_movies_btn(data=all_ads(), model="deleted_ads", go_back='admin_panel'))
    await bot.send_message(chat_id=settings.bots.admin_id, text="Reklama o'chirildi!")
# all Ads ------- end

async def add_saved(call: CallbackQuery, bot: Bot, callback_data: AddSaved):
    set_global_var(call.from_user.id, datetime.now().isoformat())

    movie_id = callback_data.id
    user_id = callback_data.user_id

    movie = get_movie_details(movie_id=movie_id)
    
    if insert_saved(movie_id=movie_id, users_id=user_id):
        btn = users_btn(data=movie, user_id=call.from_user.id)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=btn)

async def del_saved(call: CallbackQuery, bot: Bot, callback_data: DeleteSaved):
    set_global_var(call.from_user.id, datetime.now().isoformat())

    saved_id = callback_data.saved_id
    movie_id = callback_data.movie_id
    
    movie = get_movie_details(movie_id=movie_id)
    print(saved_id)

    delete_saved(saved_id=saved_id)
    btn = users_btn(data=movie, user_id=call.from_user.id)
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=btn)

async def clear_admin(call: CallbackQuery, bot: Bot):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)



async def movie_list(call: CallbackQuery, bot: Bot):
    movies = all_movie()
    if not movies:
        await call.answer("Kinolaryo'q!", show_alert=True)
        return

    page = 1
    items_per_page = 10
    total_pages = (len(movies) + items_per_page - 1) // items_per_page
    
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    
    current_movies = movies[start_index:end_index]
    
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    text = "📽 Kinolar ro'yxati:\n\n"
    for movie in current_movies:
        text += f"🎬 {movie['name']} - ID: <code>{movie['id']}</code>\n🔗 Link: <code>t.me/{bot_username}?start={movie['id']}</code>\n\n"
        
    await bot.edit_message_text(
        text=text,
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=movie_pagination_btn(page, total_pages)
    )

async def movie_page_handler(call: CallbackQuery, bot: Bot, callback_data: MoviePage):
    movies = all_movie()
    if not movies:
        await call.answer("Kinolar yo'q!", show_alert=True)
        return

    page = callback_data.page
    items_per_page = 10
    total_pages = (len(movies) + items_per_page - 1) // items_per_page
    
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    
    current_movies = movies[start_index:end_index]
    
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    
    text = "📚 Kinolar ro'yxati:\n\n"
    for movie in current_movies:
        text += f"🎬 {movie['name']} - ID: <code>{movie['id']}</code>\n🔗 Link: <code>t.me/{bot_username}?start={movie['id']}</code>\n\n"
    
    await bot.edit_message_text(
        text=text,
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=movie_pagination_btn(page, total_pages)
    )

async def movie_part_switch(call: CallbackQuery, bot: Bot, callback_data: MoviePage):
    movie_id = callback_data.movie_id
    part_num = callback_data.page
    
    movie = get_movie_details(movie_id=movie_id)
    parts = get_movie_parts(movie_id)
    
    # Find the specific part
    target_part = next((p for p in parts if p[0] == part_num), None)
    
    if movie and target_part:
        caption = generate_movie_caption(movie, target_part)
        btn = users_btn(data=movie, user_id=call.from_user.id, current_part=part_num)
        
        # Use edit_message_media to switch video
        await bot.edit_message_media(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            media=types.InputMediaVideo(media=target_part[1], caption=caption),
            reply_markup=btn
        )
    else:
        await call.answer("Qism topilmadi!", show_alert=True)

async def movie_list_handler(call: CallbackQuery, bot: Bot):
    await movie_page_handler(call, bot, MoviePage(model='movie_page', page=1))

async def movie_edit_menu(call: CallbackQuery, bot: Bot, callback_data: MovieEdit):
    movie = get_movie_details(callback_data.movie_id)
    if not movie:
        await call.answer("Kino topilmadi!")
        return
        
    text = (
        f"⚙️ <b>Kino tahrirlash:</b> {movie['name']}\n\n"
        f"Nimani o'zgartirmoqchisiz?"
    )
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Nomini o'zgartirish", callback_data=MovieEdit(action='edit_field', movie_id=movie['id'], field='name'))
    kb.button(text="📊 Holatini o'zgartirish", callback_data=MovieEdit(action='edit_field', movie_id=movie['id'], field='status'))
    kb.button(text="🎭 Janrini o'zgartirish", callback_data=MovieEdit(action='edit_field', movie_id=movie['id'], field='genre'))
    kb.button(text="➕ Qism qo'shish", callback_data=MovieEdit(action='add_part', movie_id=movie['id']))
    kb.button(text="🔙 Orqaga", callback_data=MoviePage(model='part', movie_id=movie['id'], page=1))
    kb.adjust(1)
    
    try:
        if call.message.text:
            await bot.edit_message_text(
                text=text,
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                reply_markup=kb.as_markup()
            )
        else:
            await call.message.delete()
            await call.message.answer(text=text, reply_markup=kb.as_markup())
    except Exception:
        await call.message.answer(text=text, reply_markup=kb.as_markup())

async def movie_edit_field(call: CallbackQuery, state: FSMContext, callback_data: MovieEdit):
    field_names = {
        'name': "Yangi nomni kiriting:",
        'status': "Yangi holatni kiriting (Davom etmoqda / Tugallangan):",
        'genre': "Yangi janrlarni kiriting:"
    }
    
    await state.update_data(movie_id=callback_data.movie_id, field=callback_data.field)
    text = field_names.get(callback_data.field, "Yangi qiymatni kiriting:")
    
    try:
        if call.message.text:
            await call.message.edit_text(text=text)
        else:
            await call.message.delete()
            await call.message.answer(text=text)
    except Exception:
        await call.message.answer(text=text)
    await state.set_state(EditMovieState.value)

async def movie_add_part_start(call: CallbackQuery, state: FSMContext, callback_data: MovieEdit):
    parts = get_movie_parts(callback_data.movie_id)
    next_part = len(parts) + 1
    
    movie = get_movie_details(callback_data.movie_id)
    if not movie:
        await call.answer("Kino topilmadi!")
        return
        
    await state.update_data(
        movie_id=callback_data.movie_id, 
        name=movie['name'],
        status=movie['status'],
        country=movie.get('country'),
        language=movie.get('language'),
        year=movie.get('year'),
        genre=movie.get('genre'),
        image_id=movie.get('image_id'),
        current_part=next_part, 
        parts_count=next_part, # Update total parts count
        is_editing=True
    )
    text = f"{next_part}-qism videosini yuboring:"
    try:
        if call.message.text:
            await call.message.edit_text(text=text)
        else:
            await call.message.delete()
            await call.message.answer(text=text)
    except Exception:
        await call.message.answer(text=text)
    await state.set_state(MoviesData.video)

async def movie_edit_value_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    movie_id = data['movie_id']
    field = data['field']
    value = message.text
    
    if not value:
        await message.answer("Iltimos, matn kiriting!")
        return
        
    update_movie_metadata(movie_id, field, value)
    await message.answer(f"✅ Muvaffaqiyatli o'zgartirildi: {field} -> {value}")
    await state.clear()
    
    # Return to edit menu
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="⚙️ Tahrirlash menyusi", callback_data=MovieEdit(action='menu', movie_id=movie_id))
    await message.answer("Boshqa narsani o'zgartirasizmi?", reply_markup=kb.as_markup())

async def main_channel_view(call: CallbackQuery, bot: Bot):
    url = get_setting('main_channel_url', '@Kdrama_tv_uz')
    text = f"📢 <b>Asosiy kanal havolasi:</b> {url}\n\nO'zgartirish uchun tugmani bosing:"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 O'zgartirish", callback_data=MainChannel(action='edit'))
    kb.button(text="🔙 Orqaga", callback_data=AdminPanel(model='admin_panel'))
    kb.adjust(1)
    
    await bot.edit_message_text(text=text, chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=kb.as_markup())

async def main_channel_edit_start(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Yangi kanal linkini kiriting (masalan: @Kdrama_tv_uz):")
    await state.set_state(MainChannelState.link)

async def main_channel_edit_finish(message: Message, state: FSMContext):
    url = message.text
    if not url.startswith('@') and not url.startswith('https://'):
        await message.answer("Xato! Link @ bilan yoki https:// bilan boshlanishi kerak.")
        return
        
    update_setting('main_channel_url', url)
    await message.answer(f"✅ Asosiy kanal havolasi yangilandi: {url}")
    await state.clear()
    
    from core.keyboards.inline import adminpanel_btn
    await message.answer("Admin panel", reply_markup=adminpanel_btn(model='xabar'))

async def movie_finish_edit(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if not data:
        await call.answer("Ma'lumot topilmadi!")
        return
        
    # Reuse the logic from get_movie_video to show the summary post
    from core.handlers.basic import get_movie_video
    # We can't easily call get_movie_video because it expects a Message object
    # So we'll manually send the summary post here or refactor
    
    movie = get_movie_details(data['movie_id'])
    parts = get_movie_parts(data['movie_id'])
    
    # Update state data to match what generate summary expects
    await state.update_data(parts_count=len(parts))
    data = await state.get_data()
    
    bot_info = await bot.get_me()
    m_id = data['movie_id']
    download_url = f"https://t.me/{bot_info.username}?start={m_id}"
    channel_link = get_setting('main_channel_url', settings.bots.base_channel)
    
    caption = (
        f"🎬 <b>{data['name']}</b>\n\n"
        f"╭───────────────\n"
        f"├ 🧩 Qism : {len(parts)} ta\n"
        f"├ 📊 Holati : {data.get('status', 'Tugallangan')}\n"
        f"├ 🌍 Davlat : {data.get('country', 'Nomalum')}\n"
        f"├ 🔊 Tili : {data.get('language', 'Nomalum')}\n"
        f"├ 📅 Yili : {data.get('year', 'Nomalum')}\n"
        f"├ 🎭 Janri : {data.get('genre', 'Nomalum')}\n"
        f"╰───────────────\n\n"
        f"📢 Kanal: {channel_link}\n"
        f"🤖 Bot: @{bot_info.username}"
    )
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="📥 Yuklab olish", url=download_url)
    
    if data.get('image_id'):
        await call.message.answer_photo(photo=data['image_id'], caption=caption, reply_markup=kb.as_markup())
    else:
        await call.message.answer(text=caption, reply_markup=kb.as_markup())
        
    await call.message.answer("✅ Tahrirlash yakunlandi!")
    await state.clear()
