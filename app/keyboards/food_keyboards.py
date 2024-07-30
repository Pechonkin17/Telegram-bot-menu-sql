from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_menu_keyboard(foods: list):
    builder = InlineKeyboardBuilder()
    for index, food in enumerate(foods):
        builder.button(text=food.get("name"), callback_data=f"food_{index}")
    builder.adjust(1)
    return builder.as_markup()

def build_details_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Back", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()