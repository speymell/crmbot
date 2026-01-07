from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard = [
            [KeyboardButton(text="Записаться")],
            [KeyboardButton(text="Моя история")],
            [KeyboardButton(text="Цены на услуги")],
            [KeyboardButton(text="Мастера")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )