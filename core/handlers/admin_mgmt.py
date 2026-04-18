from aiogram import types, Bot, F
from aiogram.fsm.context import FSMContext
from core.db_api.db import (get_all_admins, add_admin, delete_admin, 
                             get_admin, update_admin_permission)
from core.keyboards.inline import (admin_list_btn, admin_permissions_btn, 
                                   get_back_btn, admin_manage_btn)
from core.utils.callbackdata import AdminManage, AdminPerm
from core.states.states import AdminState
from core.handlers.basic import admin_panel
from core.settings import settings

async def list_admins(call: types.CallbackQuery, bot: Bot):
    if str(call.from_user.id) != str(settings.bots.admin_id):
        await call.answer("Faqat Super Admin bu bo'limni ko'ra oladi!", show_alert=True)
        return
    
    admins = get_all_admins()
    await bot.edit_message_text(
        text="👥 Bot adminlari ro'yxati:",
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=admin_list_btn(admins)
    )

async def add_admin_start(call: types.CallbackQuery, state: FSMContext):
    if str(call.from_user.id) != str(settings.bots.admin_id):
        await call.answer("Faqat Super Admin admin qo'sha oladi!", show_alert=True)
        return
        
    await call.message.edit_text("Yangi adminning Telegram ID sini kiriting:", reply_markup=get_back_btn("admin_panel"))
    await state.set_state(AdminState.user_id)

async def add_admin_finish(message: types.Message, state: FSMContext, bot: Bot):
    if message.text.isdigit():
        user_id = int(message.text)
        add_admin(user_id)
        await message.answer("Admin muvaffaqiyatli qo'shildi! Endi uning ruxsatlarini sozlashingiz mumkin.")
        await state.clear()
        # Refresh list
        admins = get_all_admins()
        await message.answer("👥 Bot adminlari ro'yxati:", reply_markup=admin_list_btn(admins))
    else:
        await message.answer("ID faqat raqamlardan iborat bo'lishi kerak. Qayta urinib ko'ring yoki /admin deb yozing.")

async def edit_admin_permissions(call: types.CallbackQuery, bot: Bot, callback_data: AdminManage):
    if str(call.from_user.id) != str(settings.bots.admin_id):
        await call.answer("Faqat Super Admin ruxsatlarni o'zgartira oladi!", show_alert=True)
        return
        
    admin_data = get_admin(callback_data.user_id)
    if not admin_data:
        await call.answer("Admin topilmadi!")
        return
        
    await bot.edit_message_text(
        text=f"👤 Admin: {callback_data.user_id}\nRuxsatlarni sozlash:",
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=admin_permissions_btn(admin_data)
    )

async def toggle_permission(call: types.CallbackQuery, bot: Bot, callback_data: AdminPerm):
    if str(call.from_user.id) != str(settings.bots.admin_id):
        await call.answer("Faqat Super Admin ruxsatlarni o'zgartira oladi!", show_alert=True)
        return
        
    update_admin_permission(callback_data.user_id, callback_data.perm, callback_data.value)
    
    admin_data = get_admin(callback_data.user_id)
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=admin_permissions_btn(admin_data)
    )

async def remove_admin(call: types.CallbackQuery, bot: Bot, callback_data: AdminManage):
    if str(call.from_user.id) != str(settings.bots.admin_id):
        await call.answer("Faqat Super Admin adminni o'chira oladi!", show_alert=True)
        return
        
    delete_admin(callback_data.user_id)
    await call.answer("Admin o'chirildi!")
    admins = get_all_admins()
    await bot.edit_message_text(
        text="👥 Bot adminlari ro'yxati:",
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=admin_list_btn(admins)
    )
