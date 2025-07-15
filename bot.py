import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from db import init_db, add_user, get_user, update_user_field, get_candidates, add_like, check_match, get_likes, get_matches, get_top_users
from keyboards import main_menu, gender_kb
from ai_chat import generate_ai_reply
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    if not get_user(user_id):
        add_user(user_id, username)
        await message.answer("Բարի գալուստ Dating Bot 🧡\nԳրեք Ձեր անունը:")
        await update_user_field(user_id, "step", "name")
    else:
        await message.answer("Բարի վերադարձ 🧡", reply_markup=main_menu)

@dp.message_handler()
async def handle_messages(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if not user:
        await message.answer("Գրեք /start чтобы начать")
        return

    step = user[8]
    if step == "name":
        await update_user_field(user_id, "name", message.text)
        await update_user_field(user_id, "step", "age")
        await message.answer("Գրեք Ձեր տարիք:")
    elif step == "age":
        if not message.text.isdigit():
            await message.answer("Տարիքը պետք է լինի թիվ։")
            return
        await update_user_field(user_id, "age", int(message.text))
        await update_user_field(user_id, "step", "gender")
        await message.answer("Ընտրեք Ձեր սեռը:", reply_markup=gender_kb)
    elif step == "city":
        await update_user_field(user_id, "city", message.text)
        await update_user_field(user_id, "step", "photo")
        await message.answer("Ուղարկեք Ձեր լուսանկարը:")
    else:
        await message.answer("Օգտագործեք մենյու:", reply_markup=main_menu)

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if user[8] == "photo":
        photo_id = message.photo[-1].file_id
        await update_user_field(user_id, "photo_id", photo_id)
        await update_user_field(user_id, "step", None)
        await message.answer("Գրանցումն ավարտված է ✅", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data in ["boy", "girl"])
async def gender_select(call: types.CallbackQuery):
    gender = "Տղա" if call.data == "boy" else "Աղջիկ"
    user_id = call.from_user.id
    await update_user_field(user_id, "gender", gender)
    await update_user_field(user_id, "step", "city")
    await call.message.answer("Գրեք Ձեր քաղաքը:")
    await call.answer()

@dp.message_handler(lambda m: m.text == "Դիտել օգտատերեր")
async def browse_users(message: types.Message):
    user_id = message.from_user.id
    candidates = get_candidates(user_id)
    if not candidates:
        await message.answer("Այս պահին չկա համապատասխան օգտատեր։")
        return
    for c in candidates:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("❤️ Լայք", callback_data=f"like_{c[0]}"))
        caption = f"Անուն: {c[2]}\nՏարիք: {c[3]}\nՔաղաք: {c[5]}"
        await bot.send_photo(user_id, c[6], caption=caption, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("like_"))
async def like_user(call: types.CallbackQuery):
    to_id = int(call.data.split("_")[1])
    from_id = call.from_user.id
    add_like(from_id, to_id)
    if check_match(from_id, to_id):
        await bot.send_message(from_id, "Դուք համընկաք ❤️")
        await bot.send_message(to_id, "Դուք համընկաք ❤️")
    await call.answer("Լայքը պահպանված է!")

@dp.message_handler(lambda m: m.text == "Իմ լայքերը")
async def my_likes(message: types.Message):
    likes = get_likes(message.from_user.id)
    if not likes:
        await message.answer("Ձեզ դեռ չեն լայքել 😔")
    else:
        await message.answer("Ձեզ լայքել են:\n" + "\n".join(likes))

@dp.message_handler(lambda m: m.text == "Իմ ՄԱՉ-երը")
async def my_matches(message: types.Message):
    matches = get_matches(message.from_user.id)
    if not matches:
        await message.answer("Դեռ համընկումներ չկան։")
    else:
        await message.answer("Ձեր համընկումները:\n" + "\n".join(matches))

@dp.message_handler(lambda m: m.text == "TOP 10")
async def top_users(message: types.Message):
    top = get_top_users()
    text = "TOP 10 ամենահայտնի օգտատերերը:\n"
    for i, t in enumerate(top, start=1):
        text += f"{i}. {t[0]} ({t[1]} լայք)\n"
    await message.answer(text)

@dp.message_handler(commands=['ai'])
async def ai_chat(message: types.Message):
    question = message.get_args()
    if not question:
        await message.answer("Գրեք հարց:\nՕրինակ: /ai Ինչպե՞ս է եղանակը Երևանում")
        return
    answer = await generate_ai_reply(question, OPENAI_KEY)
    await message.answer(answer)

if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)
