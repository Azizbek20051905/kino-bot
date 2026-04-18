from aiogram import Dispatcher, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.keyboards.inline import adminpanel_btn, get_back_btn, users_btn, sub_channel_keyboard, client_user_btn
from aiogram.types import ReplyKeyboardRemove 
from core.states.states import GetChannel_data, MoviesData, GetAds_data
from core.db_api.db import (insert_channel, insert_movie, insert_ads, update_movies, get_movie_details,
                            all_channels, get_checkbox, get_admin, insert_movie_part, get_movie_parts)
from core.config import set_global_var, global_var
# from core.filters.filter import check_subscription
from datetime import datetime, timedelta


from core.settings import settings

user_views = {}
answer_users = {}

async def admin_panel(message: types.Message, bot: Bot):
    admin = get_admin(message.from_user.id)
    if admin:
        btn = adminpanel_btn(model='xabar')
        await message.answer(text="Admin panel", reply_markup=btn)

# Channels ------ start
async def select_add_channel(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    admin = get_admin(call.from_user.id)
    if not admin or not admin['can_manage_channels']:
        await call.answer("Sizda kanallarni boshqarish ruxsati yo'q!", show_alert=True)
        return
    btn = get_back_btn(model="channels")
    await bot.edit_message_text(text="Kanal nomini kiriting:", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=btn)
    # await call.message.answer(text="Kanal nomini kiriting:", reply_markup=btn)
    await state.set_state(GetChannel_data.name)

async def answer_channel_name(message: types.Message, bot: Bot, state: FSMContext):
    await state.update_data(name=message.text)
    btn = get_back_btn(model="channels")
    await message.answer(text="Kanal linkini kiriting:", reply_markup=btn)
    # await bot.edit_message_text(text="Kanal linkini kiriting:", chat_id=message.from_user.id, message_id=message.message_id, reply_markup=btn)
    await state.set_state(GetChannel_data.link)

async def answer_channel_link(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    print(data)
    
    answer = insert_channel(data['name'], data['link'])

    btn = get_back_btn(model="channels")
    if answer:
        await message.answer(text="Kanal qo'shildi!", reply_markup=btn)
    else:
        await message.answer(text="Bunday kanal oldindan mavjud!", reply_markup=btn)

    await state.clear()
# Channels ------ end


# Movie --------- start
async def get_movie_name(message: types.Message, bot: Bot, state: FSMContext):
    admin = get_admin(message.from_user.id)
    if not admin or not admin['can_add_movie']:
        await message.answer("Sizda kino qo'shish ruxsati yo'q!")
        await state.clear()
        return
    await state.update_data(name=message.text)
    await message.answer("Kino tavsifini (description) kiriting:", reply_markup=get_back_btn("movies"))
    await state.set_state(MoviesData.description)

async def get_movie_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Kino qaysi davlatda ishlab chiqarilgan?", reply_markup=get_back_btn("movies"))
    await state.set_state(MoviesData.country)

async def get_movie_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("Kino tilini kiriting:", reply_markup=get_back_btn("movies"))
    await state.set_state(MoviesData.language)

async def get_movie_language(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer("Kino yilini kiriting:", reply_markup=get_back_btn("movies"))
    await state.set_state(MoviesData.year)

async def get_movie_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer("Kino janrini kiriting:", reply_markup=get_back_btn("movies"))
    await state.set_state(MoviesData.genre)

async def get_movie_genre(message: types.Message, state: FSMContext):
    await state.update_data(genre=message.text)
    kb = InlineKeyboardBuilder()
    kb.button(text="🎬 Bitta qismli", callback_data="single")
    kb.button(text="🎞 Ko'p qismli (Serial)", callback_data="series")
    await message.answer("Bu kino qismlimi yoki bitta videomi?", reply_markup=kb.as_markup())
    await state.set_state(MoviesData.is_series)

async def get_movie_is_series(call: types.CallbackQuery, state: FSMContext):
    if call.data == "single":
        await state.update_data(is_series=False, parts_count=1, current_part=1)
        await call.message.edit_text("Kino videosini yuboring:")
        await state.set_state(MoviesData.video)
    else:
        await state.update_data(is_series=True, current_part=1)
        await call.message.edit_text("Qismlar sonini kiriting:")
        await state.set_state(MoviesData.parts_count)

async def get_movie_parts_count(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(parts_count=int(message.text))
        await message.answer(f"1-qism videosini yuboring:")
        await state.set_state(MoviesData.video)
    else:
        await message.answer("Iltimos, faqat raqam kiriting:")

async def get_movie_video(message: types.Message, bot: Bot, state: FSMContext):
    if not message.video:
        await message.answer("Iltimos, video fayl yuboring!")
        return
        
    data = await state.get_data()
    video_file = message.video.file_id
    video_size = message.video.file_size
    mb_size = round(video_size / (1024 * 1024), 1)
    
    current_part = data.get('current_part', 1)
    parts_count = data.get('parts_count', 1)
    
    caption = f"🎬 {data['name']}"
    if parts_count > 1:
        caption += f" | {current_part}-qism"
        
    send_message = await bot.send_video(chat_id=settings.bots.base_channel, video=video_file, caption=caption)
    pers_video_id = send_message.video.file_id
    
    parts = data.get('parts_list', [])
    parts.append({'part': current_part, 'video': pers_video_id, 'size': mb_size})
    await state.update_data(parts_list=parts)
    
    if current_part < parts_count:
        await state.update_data(current_part=current_part + 1)
        await message.answer(f"{current_part + 1}-qism videosini yuboring:")
    else:
        movie_id = insert_movie(data)
        for p in parts:
            insert_movie_part(movie_id, p['part'], p['video'], p['size'])
            
        await message.answer(f"Kino muvaffaqiyatli qo'shildi!\nkino Id si: {movie_id}", reply_markup=get_back_btn("movies"))
        await state.clear()
# Movie ---------- end

async def get_ads_name(message: types.Message, bot: Bot, state: FSMContext):
    admin = get_admin(message.from_user.id)
    if not admin or not admin['can_manage_ads']:
        await message.answer("Sizda reklamalarni boshqarish ruxsati yo'q!")
        await state.clear()
        return
    await state.update_data(name=message.text)
    btn = get_back_btn(model="admin_panel")
    await message.answer(text="Reklama linkini kiriting:", reply_markup=btn)
    await state.set_state(GetAds_data.link)

async def get_ads_link(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    print(data)
    
    answer = insert_ads(data['name'], data['link'])

    btn = get_back_btn(model="admin_panel")
    if answer:
        await message.answer(text="Reklama qo'shildi!", reply_markup=btn)
    else:
        await message.answer(text="Bunday reklama oldindan mavjud!", reply_markup=btn)

    await state.clear()

def generate_movie_caption(movie, part):
    parts = get_movie_parts(movie['id'])
    parts_count = len(parts)
    
    text = f"🎬 Kino nomi: {movie['name']}\n"
    if parts_count > 1:
        text += f"🎞 Qismlar soni: {parts_count}\n"
    
    text += f"🌍 Davlati: {movie.get('country') or 'Noma''lum'}\n"
    text += f"🇺🇿 Tili: {movie.get('language') or 'Noma''lum'}\n"
    text += f"📅 Yili: {movie.get('year') or 'Noma''lum'}\n"
    text += f"🎭 Janri: {movie.get('genre') or 'Noma''lum'}\n"
    
    if movie.get('description'):
        text += f"\n📝 Tavsif: {movie['description']}\n"
    
    text += f"\n📀 Hajmi: {part[2]} MB\n"
    text += f"👁 Ko'rishlar: {movie['views']}\n"
    text += "\n👌 @KodliKinola_robot"
    return text

async def send_movies(message: types.Message, bot: Bot):
    global user_views
    set_global_var(message.from_user.id, datetime.now().isoformat())

    text = (message.text).split(" ")
    if message.from_user.id not in user_views:
        user_views[message.from_user.id] = {}
    
    movie_id_str = text[1] if len(text) > 1 else text[0]
    movie = get_movie_details(movie_id=int(movie_id_str))

    if movie:
        parts = get_movie_parts(movie['id'])
        if not parts:
            await message.answer("Bu kino uchun video topilmadi!")
            return
            
        part = parts[0]

        if message.from_user.id not in user_views or message.from_user.id in user_views and int(movie['id']) not in user_views[message.from_user.id]:
            user_views[message.from_user.id][int(movie['id'])] = int(movie['id'])
            update_movies(id=movie['id'], view=int(movie['views'])+1)

        btn = users_btn(data=movie, user_id=message.from_user.id, current_part=part[0])
        caption = generate_movie_caption(movie, part)
        
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await bot.send_video(chat_id=message.from_user.id, video=part[1], caption=caption, reply_markup=btn)
    else:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await bot.send_message(chat_id=message.from_user.id, text="Bu kodga mos kino topilmadi!")

async def send_movies_id(message: types.Message, bot: Bot):
    global user_views

    set_global_var(message.from_user.id, datetime.now().isoformat())

    text = message.text
    if message.from_user.id not in user_views:
        user_views[message.from_user.id] = {}

    movie = get_movie_details(movie_id=int(text))
    
    if movie:
        parts = get_movie_parts(movie['id'])
        if not parts:
            await message.answer("Bu kino uchun video topilmadi!")
            return
            
        # Default to part 1
        part = parts[0]
        
        if message.from_user.id not in user_views or message.from_user.id in user_views and int(movie['id']) not in user_views[message.from_user.id]:
            user_views[message.from_user.id][int(movie['id'])] = int(movie['id'])
            update_movies(id=movie['id'], view=int(movie['views'])+1)

        btn = users_btn(data=movie, user_id=message.from_user.id, current_part=part[0])
        caption = generate_movie_caption(movie, part)
        
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await bot.send_video(chat_id=message.from_user.id, video=part[1], caption=caption, reply_markup=btn)
    else:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await bot.send_message(chat_id=message.from_user.id, text="Bu kodga mos kino topilmadi!")

async def sub_channel_answer(message: types.Message):
    await message.answer(f"Iltimos, kanalga obuna bo'ling va qayta urinib ko'ring.", parse_mode="HTML", reply_markup=sub_channel_keyboard())

async def sub_channel(call: types.CallbackQuery, bot: Bot):
    results = None
    user_id = call.from_user.id
    try:
        is_true = get_checkbox()
        if is_true['is_true']:
            channel_list = []
            channels = all_channels()
            
            if channels:
                for channel in channels:
                    links = str(channel['link']).replace('https://t.me/', '@')
                    member = await bot.get_chat_member(chat_id=links, user_id=user_id)
                    if member.status in ['member', 'administrator', "creator"]:
                        channel_list.append(True)
                    else:
                        channel_list.append(False)
            
            if False not in channel_list:
                results = True
            else:
                results = False
        else:
            results = True
    except Exception as e:
        print(e)
        results = None
    
    if results:
        text = f"Tanlang:"
        await call.message.answer(text=text, reply_markup=client_user_btn())
    else:
        # btn = get_back_btn(model="admin_panel")
        await bot.answer_callback_query(call.id, text="Kanalga obuna bo'lmadingiz!", show_alert=False)


