from aiogram.fsm.state import State, StatesGroup

class GetChannel_data(StatesGroup):
    name = State()
    link = State()

class GetAds_data(StatesGroup):
    name = State()
    link = State()

class ForwardMessage(StatesGroup):
    id = State()

class MoviesData(StatesGroup):
    name = State()
    description = State()
    country = State()
    language = State()
    year = State()
    genre = State()
    status = State()
    image = State()
    is_series = State()
    parts_count = State()
    current_part = State()
    video = State()

class MessageNext(StatesGroup):
    model = State()

class AdminState(StatesGroup):
    user_id = State()
    full_name = State()

class EditMovieState(StatesGroup):
    movie_id = State()
    field = State()
    value = State()

class MainChannelState(StatesGroup):
    link = State()
