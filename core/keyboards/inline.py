from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.utils.callbackdata import AdminPanel, DeleteChannel, AddSaved, DeleteSaved, Statistic, MoviePage, AdminManage, AdminPerm, MovieEdit, MainChannel
from core.settings import settings
from core.db_api.db import all_ads, all_channels, get_checkbox, all_movie, get_saveds_movies_id, get_movie_parts, get_admin
import random

def client_user_btn():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='🔎Barcha kinolar',  switch_inline_query_current_chat="")
    keyboard.button(text="📂Saqlangan kinolar", switch_inline_query_current_chat="saved")
    
    ads = all_ads()
    if ads:
        rand = random.choice(ads)
        print()
        print(rand)
        print()
        keyboard.button(text=f"{rand['name']}", url=f"{rand['link']}")
    
    keyboard.adjust(1)
    return keyboard.as_markup()

def adminpanel_btn(model):
    keyboards = InlineKeyboardBuilder()

    keyboards.button(text="📊Statistika", callback_data=AdminPanel(model='statistic'))
    keyboards.button(text="📢Kanallar", callback_data=AdminPanel(model='channels'))
    keyboards.button(text="📝Xabar yuborish", callback_data=AdminPanel(model=model))
    keyboards.button(text="🎞Kino qo'shish", callback_data=AdminPanel(model='movies'))
    keyboards.button(text="➕Reklama qo'shish", callback_data=AdminPanel(model='add_ads'))
    keyboards.button(text="➖Reklama o'chirish", callback_data=AdminPanel(model='del_ads'))
    keyboards.button(text="🎞Kino idsini aniqlash", callback_data=AdminPanel(model='movie_list'))
    keyboards.button(text="👥Adminlarni boshqarish", callback_data=AdminManage(action='list'))
    keyboards.button(text="📢 Asosiy kanal", callback_data=MainChannel(action='view'))
    keyboards.button(text="🔼", callback_data=AdminPanel(model='clear'))

    # keyboards.adjust(1)
    keyboards.adjust(2, 1, 1, 2, 1, 1, 1, 1)

    return keyboards.as_markup()

def channel_btn():
    keyboards = InlineKeyboardBuilder()

    keyboards.button(text="➕Kanal qo'shish", callback_data=AdminPanel(model='add_channel'))
    keyboards.button(text="➖Kanal o'chirish", callback_data=AdminPanel(model='del_channel'))

    # if all_channels():
    is_true = get_checkbox()
    if is_true['is_true']:
        keyboards.button(text="✅Majburiy a'zolik|Yoqilgan", callback_data=AdminPanel(model='off_channel'))
    else:
        keyboards.button(text="❌Majburiy a'zolik|O'chirilgan", callback_data=AdminPanel(model='on_channel'))

    keyboards.button(text="🔙Orqaga", callback_data=AdminPanel(model='admin_panel'))
    keyboards.adjust(2, 1, 1)

    return keyboards.as_markup()

def del_channel_btn():
    keyboards = InlineKeyboardBuilder()

    channels = all_channels()
    if channels:
        for channel in channels:
            keyboards.button(text=channel['name'], callback_data=DeleteChannel(model='delete_channel', id=channel['id']))

    keyboards.button(text="🔙Orqaga", callback_data=AdminPanel(model='channels'))
    keyboards.adjust(2)

    return keyboards.as_markup()

def get_back_btn(model):
    keyboards = InlineKeyboardBuilder()
    keyboards.button(text="🔙Orqaga", callback_data=AdminPanel(model=model))
    keyboards.adjust(1)
    return keyboards.as_markup()

def movies_btn():
    keyboards = InlineKeyboardBuilder()

    keyboards.button(text="➕Kino qo'shish", callback_data=AdminPanel(model='add_movie'))
    keyboards.button(text="➖Kino o'chirish", callback_data=AdminPanel(model='del_movie'))

    keyboards.button(text="🔙Orqaga", callback_data=AdminPanel(model='admin_panel'))
    keyboards.adjust(2, 1)

    return keyboards.as_markup()

def del_movies_btn(data, model, go_back):
    keyboards = InlineKeyboardBuilder()

    movies = data
    print(movies)
    if movies:
        for movie in movies:
            print(movie)
            keyboards.button(text=movie['name'], callback_data=DeleteChannel(model=model, id=movie['id']))

    keyboards.button(text="🔙Orqaga", callback_data=AdminPanel(model=go_back))
    keyboards.adjust(1)

    return keyboards.as_markup()


def users_btn(data, user_id, current_part=1):
    keyboards = InlineKeyboardBuilder()

    parts = get_movie_parts(data['id'])
    rows = []
    
    if parts and len(parts) > 1:
        for part in parts:
            part_num = part[0]
            text = f"✅{part_num}" if part_num == current_part else f"{part_num}"
            keyboards.button(text=text, callback_data=MoviePage(model='part', movie_id=data['id'], page=part_num))
        
        # Adjust parts: 6 per row
        p_rows = len(parts) // 6
        for _ in range(p_rows):
            rows.append(6)
        if len(parts) % 6:
            rows.append(len(parts) % 6)

    keyboards.button(text='🔎Barcha kinolar',  switch_inline_query_current_chat="")
    keyboards.button(text="📂Saqlangan kinolar", switch_inline_query_current_chat="saved")
    results = get_saveds_movies_id(users_id=user_id, movie_id=data['id'])

    if results:
        keyboards.button(text="✅Saqlangan", callback_data=DeleteSaved(model='del_save', saved_id=int(results['id']), movie_id=int(data['id'])))
    else:
        keyboards.button(text="✔️Saqlash", callback_data=AddSaved(model='add_save', id=int(data['id']), user_id=str(user_id)))
    
    ads = all_ads()
    if ads:
        rand = random.choice(ads)
        keyboards.button(text=f"{rand['name']}", url=f"{rand['link']}")
    
    admin = get_admin(user_id)
    if admin:
        keyboards.button(text="⚙️ Tahrirlash", callback_data=MovieEdit(action='menu', movie_id=data['id']))
        rows.append(1)

    rows.extend([2, 1, 1])
    keyboards.adjust(*rows)

    return keyboards.as_markup()

def sub_channel_keyboard():
    keyboards = InlineKeyboardBuilder()
    
    channels = all_channels()
    if channels:
        for channel in channels:
            keyboards.button(text=f"{channel['name']}", url=f"{channel['link']}")

    keyboards.button(text="Tasdiqlash✅", callback_data=AdminPanel(model='checksub'))
    # keyboards.button(text="Tasdiqlash✔", callback_data=DeleteMessage(model='delete'))
    keyboards.adjust(1)
    return keyboards.as_markup()


def status_message_btn(play, model, message_id):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text=play, callback_data=Statistic(model=model, id=message_id))
    keyboard.button(text="Yangilash🔄", callback_data=AdminPanel(model='update'))
    keyboard.button(text="O'chirish🗑", callback_data=AdminPanel(model='delete_status'))
    keyboard.button(text="🔙Orqaga", callback_data=AdminPanel(model='admin_panel'))

    keyboard.adjust(1)

    return keyboard.as_markup()

def movie_pagination_btn(page, total_pages):
    keyboards = InlineKeyboardBuilder()

    if page > 1:
        keyboards.button(text="⬅️", callback_data=MoviePage(model='movie_page', page=page-1))
    
    keyboards.button(text=f"{page}/{total_pages}", callback_data="none_data")

    if page < total_pages:
        keyboards.button(text="➡️", callback_data=MoviePage(model='movie_page', page=page+1))

    keyboards.button(text="🔙Orqaga", callback_data=AdminPanel(model='admin_panel'))
    
    keyboards.adjust(3, 1)
    return keyboards.as_markup()

def admin_manage_btn():
    keyboards = InlineKeyboardBuilder()
    keyboards.button(text="➕Admin qo'shish", callback_data=AdminManage(action='add'))
    keyboards.button(text="🔙Orqaga", callback_data=AdminPanel(model='admin_panel'))
    keyboards.adjust(1)
    return keyboards.as_markup()

def admin_list_btn(admins):
    keyboards = InlineKeyboardBuilder()
    for admin in admins:
        user_id = admin['user_id']
        name = admin.get('full_name') or user_id
        status = "👑" if admin['is_super'] else "👤"
        keyboards.button(text=f"{status} {name}", callback_data=AdminManage(action='edit', user_id=user_id))
    
    keyboards.button(text="➕Yangi admin", callback_data=AdminManage(action='add'))
    keyboards.button(text="🔙Orqaga", callback_data=AdminPanel(model='admin_panel'))
    keyboards.adjust(2)
    return keyboards.as_markup()

def admin_permissions_btn(admin_data):
    keyboards = InlineKeyboardBuilder()
    
    perms = [
        ("Kino qo'shish", "can_add_movie"),
        ("Kino o'chirish", "can_del_movie"),
        ("Kanallarni boshqarish", "can_manage_channels"),
        ("Reklamalarni boshqarish", "can_manage_ads"),
        ("Xabar yuborish", "can_send_message"),
        ("Statistikani ko'rish", "can_view_stats"),
    ]
    
    for label, key in perms:
        value = admin_data[key]
        icon = "✅" if value else "❌"
        keyboards.button(text=f"{icon} {label}", callback_data=AdminPerm(user_id=admin_data['user_id'], perm=key, value=int(not value)))
    
    keyboards.button(text="🗑Adminni o'chirish", callback_data=AdminManage(action='delete', user_id=admin_data['user_id']))
    keyboards.button(text="🔙Orqaga", callback_data=AdminManage(action='list'))
    keyboards.adjust(2)
    return keyboards.as_markup()

