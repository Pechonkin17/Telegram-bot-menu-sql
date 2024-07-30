from aiogram.fsm.state import State, StatesGroup


class FoodCreateUpdateForm(StatesGroup):
    name = State()
    ingredients = State()
    photo_url = State()
    rating = State()

class FoodDeleteForm(StatesGroup):
    name = State()

class FoodFindForm(StatesGroup):
    name = State()

class FoodUpdateForm(StatesGroup):
    name = State()