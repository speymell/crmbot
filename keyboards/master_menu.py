#keyboards/master_menu
import logging

import types

from aiogram import F, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

from db.crud import get_masters_from_db

def masters_list_kb(masters: list[tuple[int, str]]):
    keyboard = []

    for master_id, master_name in masters:
        keyboard.append([
            InlineKeyboardButton(
                text=master_name,
                callback_data=f"master_{master_id}"
            )
        ])

    # keyboard.append([
    #     InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_menu")
    # ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
