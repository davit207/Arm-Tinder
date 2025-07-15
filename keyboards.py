from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Դիտել օգտատերեր"))
main_menu.add(KeyboardButton("Իմ լայքերը"), KeyboardButton("Իմ ՄԱՉ-երը"))
main_menu.add(KeyboardButton("TOP 10"))

gender_kb = InlineKeyboardMarkup()
gender_kb.add(InlineKeyboardButton("Տղա", callback_data="boy"), InlineKeyboardButton("Աղջիկ", callback_data="girl"))
