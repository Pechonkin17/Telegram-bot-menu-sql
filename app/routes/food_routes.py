from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold

from ..data import get_foods, get_food_by_name, create_food, update_food, delete_food, find_food, find_foods_by_partial_name
from ..fsm import FoodCreateUpdateForm, FoodDeleteForm, FoodFindForm, FoodUpdateForm
from ..keyboards import build_menu_keyboard, build_details_keyboard

food_router = Router()

async def check_admin_mode(state: FSMContext):
    data = await state.get_data()
    return data.get("admin_mode", False)

async def reset_admin_mode(state: FSMContext):
    await state.update_data(admin_mode=False)

@food_router.message(Command("menu"))
@food_router.message(F.text.casefold().contains("menu"))
async def show_foods_command(message: Message, state: FSMContext):
    await check_commands(message, state)
    foods = get_foods()

    if not foods:
        await message.answer(
            text="No foods in database",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        keyboard = build_menu_keyboard(foods)
        await message.answer(
            text="Choose food",
            reply_markup=keyboard
        )

@food_router.callback_query(F.data.startswith("food_"))
async def show_food_details(callback: CallbackQuery, state: FSMContext) -> None:
    await check_commands(callback.message, state)

    food_name = callback.data.split("_")[-1]
    food = get_food_by_name(food_name)
    text = f"Name: {hbold(food.get('name'))}\nIngredients: {hbold(food.get('ingredients'))}\nRating: {hbold(food.get('rating'))}"
    photo_id = food.get('photo_url')
    await callback.message.answer_photo(photo_id)
    await edit_or_answer(
        callback.message,
        text,
        build_details_keyboard()
    )

async def edit_or_answer(message: Message, text: str, keyboard, **kwargs):
    if message.from_user.is_bot:
        await message.edit_text(text=text, reply_markup=keyboard, **kwargs)
    else:
        await message.answer(text=text, reply_markup=keyboard, **kwargs)

@food_router.message(Command("create_food"))
@food_router.message(F.text.casefold() == "create food")
async def create_food_command(message: Message, state: FSMContext) -> None:
    if not await check_admin_mode(state):
        await message.answer("You do not have permission to execute this command.")
        return

    await check_commands(message, state)
    await state.clear()
    await state.update_data(action="create")
    await state.set_state(FoodCreateUpdateForm.name)
    await edit_or_answer(
        message,
        "Input name",
        ReplyKeyboardRemove()
    )

@food_router.message(Command("update_food"))
@food_router.message(F.text.casefold() == "update food")
async def update_food_command(message: Message, state: FSMContext) -> None:
    if not await check_admin_mode(state):
        await message.answer("You do not have permission to execute this command.")
        return

    await check_commands(message, state)
    await state.clear()
    await state.update_data(action="update")
    await state.set_state(FoodUpdateForm.name)
    await message.answer(
        "Input name of food to update",
        reply_markup=ReplyKeyboardRemove()
    )

@food_router.message(FoodUpdateForm.name)
async def check_food_name(message: Message, state: FSMContext) -> None:
    name = message.text
    food = find_food(name)

    if food:
        await state.update_data(name=name)
        await state.set_state(FoodCreateUpdateForm.ingredients)
        await message.answer(
            f"Food '{name}' found. Input new ingredients:",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "Food not found. Please check the name and try again."
        )
        await state.clear()

@food_router.message(Command("delete_food"))
@food_router.message(F.text.casefold() == "delete food")
async def delete_food_command(message: Message, state: FSMContext) -> None:
    if not await check_admin_mode(state):
        await message.answer("You do not have permission to execute this command.")
        return

    await check_commands(message, state)
    await state.clear()
    await state.update_data(action="delete")
    await state.set_state(FoodDeleteForm.name)
    await edit_or_answer(
        message,
        "Enter name or type 'back' to cancel",
        ReplyKeyboardRemove()
    )

@food_router.message(FoodDeleteForm.name)
async def process_delete_food(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    name = (await state.get_data()).get('name')
    await state.clear()

    if name and delete_food(name):
        await edit_or_answer(
            message,
            "Deleted successfully",
            ReplyKeyboardRemove()
        )
    elif name == 'back':
        return await show_foods_command(message, state)
    else:
        await edit_or_answer(
            message,
            "Food with this name was not found",
            ReplyKeyboardRemove()
        )
    return await show_foods_command(message, state)

@food_router.message(FoodCreateUpdateForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(FoodCreateUpdateForm.ingredients)
    await edit_or_answer(
        message,
        "Input ingredients",
        ReplyKeyboardRemove()
    )

@food_router.message(FoodCreateUpdateForm.ingredients)
async def process_ingredients(message: Message, state: FSMContext) -> None:
    data = await state.update_data(ingredients=message.text)
    await state.set_state(FoodCreateUpdateForm.photo_url)
    await edit_or_answer(
        message,
        f"Enter photo URL of {hbold(data.get('name'))}",
        ReplyKeyboardRemove()
    )

@food_router.message(FoodCreateUpdateForm.photo_url)
@food_router.message(F.photo)
async def process_photo_url(message: Message, state: FSMContext) -> None:
    photo = message.photo[-1]
    photo_id = photo.file_id

    data = await state.update_data(photo_url=photo_id)
    await state.set_state(FoodCreateUpdateForm.rating)
    await edit_or_answer(
        message,
        "Rating 1 to 10",
        ReplyKeyboardRemove()
    )

@food_router.message(FoodCreateUpdateForm.rating)
async def process_rating(message: Message, state: FSMContext) -> None:
    data = await state.update_data(rating=message.text)
    action = (await state.get_data()).get('action')

    filtered_data = {
        "name": data.get("name"),
        "ingredients": data.get("ingredients"),
        "photo_url": data.get("photo_url"),
        "rating": data.get("rating")
    }

    if action == "create":
        create_food(filtered_data)
        await message.answer("Saved successfully.")

    elif action == "update":
        name = data.get('name')
        update_food(name, filtered_data)
        await message.answer("Updated successfully.")

    await state.clear()

    food = find_food(data.get('name'))
    if food:
        text = f"Name: {hbold(food.get('name'))}\nIngredients: {hbold(food.get('ingredients'))}\nRating: {hbold(food.get('rating'))}"
        photo_id = food.get('photo_url')
        await message.answer_photo(photo_id)
        await edit_or_answer(
            message,
            text,
            build_details_keyboard()
        )
    else:
        await message.answer("Food not found. Database ERROR")

@food_router.message(Command("find_food"))
@food_router.message(F.text.casefold() == "find food")
async def find_food_command(message: Message, state: FSMContext) -> None:
    await check_commands(message, state)

    await state.clear()
    await state.update_data(action="find")
    await state.set_state(FoodFindForm.name)
    await edit_or_answer(
        message,
        "Enter name or part of the name",
        ReplyKeyboardRemove()
    )

@food_router.message(FoodFindForm.name)
async def process_find_food(message: Message, state: FSMContext) -> None:
    partial_name = message.text
    matched_foods = find_foods_by_partial_name(partial_name)
    await state.clear()

    if not matched_foods:
        await message.answer("No foods found with that name.")
    elif len(matched_foods) == 1:
        food = matched_foods[0]
        text = f"Name: {hbold(food.get('name'))}\nIngredients: {hbold(food.get('ingredients'))}\nRating: {hbold(food.get('rating'))}"
        photo_id = food.get('photo_url')
        await message.answer_photo(photo_id)
        await edit_or_answer(
            message,
            text,
            build_details_keyboard()
        )
    else:
        keyboard = build_menu_keyboard(matched_foods)
        await message.answer(
            text="Choose a food",
            reply_markup=keyboard
        )

@food_router.callback_query(F.data == 'back')
async def back_handler(callback: CallbackQuery, state) -> None:
    return await show_foods_command(callback.message, state)

async def check_commands(message: Message, state: FSMContext):
    action = (await state.get_data()).get('action')
    if action:
        await state.clear()
        await message.answer(
            text=f"Action {hbold(action)} canceled",
            reply_markup=ReplyKeyboardRemove()
        )

@food_router.message(Command("pass_admin"))
async def pass_admin_command(message: Message, state: FSMContext) -> None:
    await state.update_data(admin_mode=True)
    await message.answer("Admin mode activated. You can now use admin commands.")
