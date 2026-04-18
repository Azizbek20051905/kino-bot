from aiogram.filters.callback_data import CallbackData

class AdminPanel(CallbackData, prefix="admin"):
    model: str

class Statistic(AdminPanel, prefix="statistic"):
    model: str
    id: str

class DeleteChannel(AdminPanel, prefix="delete_channel"):
    model: str
    id: int

class AddSaved(AdminPanel, prefix="add_saved"):
    model: str
    user_id: str
    id: int

class DeleteSaved(AdminPanel, prefix="delete_saved"):
    model: str
    saved_id: int
    movie_id: int

class MoviePage(AdminPanel, prefix="movie_page"):
    movie_id: int = 0
    page: int

class AdminManage(CallbackData, prefix="adm_m"):
    action: str
    user_id: int = 0

class AdminPerm(CallbackData, prefix="adm_p"):
    user_id: int
    perm: str
    value: int # 0 or 1