from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
import os

# Environment Variables (Vercel Settings mein dalne honge)
API_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_KEY')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Vercel Handler (Serverless function)
async def handler(event, context):
    # Webhook logic yahan aayegi
    # Vercel par bot chalane ke liye Webhook set karna padta hai
    pass

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Brand Name likho, main AI se modern ideas nikalunga!")

@dp.message_handler()
async def handle_msg(message: types.Message):
    base = message.text
    # Gemini Logic
    prompt = f"Suggest 10 premium telegram usernames for '{base}'. Only names, comma separated."
    response = model.generate_content(prompt)
    names = response.text.split(',')

    text = f"✨ **Suggestions for {base}:**\n\n"
    for n in names:
        text += f"• `@{n.strip()}`\n"

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Next 10", callback_data=f"next_{base}"))
    await message.answer(text, reply_markup=markup, parse_mode="Markdown")

# Callback handler for 'Next' button
@dp.callback_query_handler(lambda c: c.data.startswith('next_'))
async def next_names(callback: types.CallbackQuery):
    # Same Gemini logic here to update text
    await callback.answer("Fetching new ideas...")
  
