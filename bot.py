import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
START_TEXT = os.getenv("START_TEXT")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ====== KLAVIATURALAR ======
def subscribe_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")],
            [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
        ]
    )

def anonymous_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Anonim habar yuborish", callback_data="send_anon")]
        ]
    )

# ====== OBUNANI TEKSHIRISH ======
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ====== START ======
@dp.message(CommandStart())
async def start_handler(message: Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer(
            "❗ Botdan foydalanish uchun kanalga obuna bo‘lish majburiy",
            reply_markup=subscribe_kb()
        )
        return

    await message.answer(START_TEXT, reply_markup=anonymous_kb())

# ====== OBUNANI QAYTA TEKSHIRISH ======
@dp.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery):
    if not await is_subscribed(call.from_user.id):
        await call.answer("❌ Hali obuna bo‘lmading", show_alert=True)
        return

    await call.message.edit_text(START_TEXT, reply_markup=anonymous_kb())

# ====== ANONIM HABAR BOSILDI ======
@dp.callback_query(F.data == "send_anon")
async def send_anon(call: CallbackQuery):
    await call.message.answer("✍️ Habaringni yoz, adminга yuboraman:")
    await call.answer()

# ====== USER HABARI ======
@dp.message(F.text)
async def anon_message_handler(message: Message):
    text = message.text

    user = message.from_user
    username = f"@{user.username}" if user.username else "Yo‘q"

    admin_text = (
        "📩 <b>Yangi anonim habar</b>\n\n"
        f"👤 <b>User:</b> {user.full_name}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"🔗 <b>Username:</b> {username}\n\n"
        f"✉️ <b>Habar:</b>\n{text}"
    )

    await bot.send_message(ADMIN_ID, admin_text)
    await message.answer("✅ Habaring yuborildi", reply_markup=anonymous_kb())

# ====== ISHGA TUSHURISH ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
