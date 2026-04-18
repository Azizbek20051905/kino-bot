import traceback
from aiogram import Bot, types
from core.settings import settings

async def error_handler(event: types.ErrorEvent, bot: Bot):
    admin_id = settings.bots.admin_id
    exception = event.exception
    
    # Get user info if possible
    user_info = "Nomalum"
    if event.update.message:
        u = event.update.message.from_user
        user_info = f"{u.full_name} (@{u.username}) [ID:{u.id}]"
    elif event.update.callback_query:
        u = event.update.callback_query.from_user
        user_info = f"{u.full_name} (@{u.username}) [ID:{u.id}]"

    error_msg = f"❌ <b>BOTDA XATOLIK YUZ BERDI!</b>\n\n"
    error_msg += f"👤 <b>Foydalanuvchi:</b> {user_info}\n"
    error_msg += f"📝 <b>Xato:</b> <code>{str(exception)}</code>\n\n"
    
    # Traceback (limit size to fit in message)
    tb = traceback.format_exc()
    if len(tb) > 3000:
        tb = tb[-3000:]
        
    error_msg += f"📜 <b>Traceback:</b>\n<code>{tb}</code>"
    
    try:
        await bot.send_message(admin_id, text=error_msg)
    except Exception as e:
        print(f"Xatolik hisobotini yuborib bo'lmadi: {e}")
        print(f"Asl xato: {exception}")
    
    return True
