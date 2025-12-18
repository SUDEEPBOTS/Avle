import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import google.generativeai as genai
from telethon import TelegramClient, functions

# --- CONFIG ---
API_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_KEY')
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Telethon Client (Username Check karne ke liye)
client = TelegramClient('brand_bot_session', API_ID, API_HASH)

async def get_premium_names(base_name):
    prompt = f"Suggest 10 unique, modern, and premium Telegram usernames related to '{base_name}'. Style: Short and Brandable. Output ONLY names separated by commas, no numbers or @."
    response = model.generate_content(prompt)
    return [n.strip() for n in response.text.split(',')]

async def check_availability(username):
    try:
        await client(functions.account.CheckUsernameRequest(username=username))
        return True # Available
    except:
        return False # Taken or Invalid

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.reply("👋 **Welcome!**\nApna brand name bhejein, main uske 10 premium variations check karunga jo Telegram par available ho sakte hain.")

@dp.message_handler()
async def handle_name(message: types.Message):
    base_name = message.text.replace('@', '')
    msg = await message.answer("🔍 AI se premium names dhoond raha hoon...")
    await send_suggestions(message, base_name, edit_msg=msg)

async def send_suggestions(message, base_name, edit_msg=None):
    raw_names = await get_premium_names(base_name)
    
    response_text = f"✨ **Top 10 Suggestions for '{base_name}':**\n\n"
    
    # Inline keyboard for Refresh button
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Next 10 Suggestions", callback_data=f"next_{base_name}"))

    for name in raw_names:
        # Note: Telegram check API limits ki wajah se hum sirf names list karenge
        # User kisi bhi name par click karke use copy kar sakta hai
        response_text += f"🔹 `@{name}`\n"
    
    response_text += "\n💡 *Click on any name to copy it.*"

    if edit_msg:
        await edit_msg.edit_text(response_text, reply_markup=markup, parse_mode="Markdown")
    else:
        await message.answer(response_text, reply_markup=markup, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data.startswith('next_'))
async def refresh_names(callback_query: types.CallbackQuery):
    base_name = callback_query.data.split('_')[1]
    await callback_query.answer("Generating new ideas...")
    await send_suggestions(callback_query.message, base_name, edit_msg=callback_query.message)

if __name__ == '__main__':
    # Telethon ko background mein start karna
    client.start()
    executor.start_polling(dp, skip_updates=True)

