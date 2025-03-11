import os
import asyncio
from pyrogram import Client, filters
from pymongo import MongoClient

# Bot Config
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
MONGO_URL = "your_mongo_db_url"

# Initialize bot and database
bot = Client("CryptoBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = MongoClient(MONGO_URL)["CryptoBot"]

# Start Command
@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    user = db.users.find_one({"user_id": user_id})
    
    if not user:
        db.users.insert_one({"user_id": user_id, "balance": 0, "referred_by": None})
        await message.reply_text("🎉 Welcome! Start earning by completing tasks.")
    else:
        await message.reply_text("🔄 Welcome back!")

# Check Balance
@bot.on_message(filters.command("balance"))
async def balance(client, message):
    user = db.users.find_one({"user_id": message.from_user.id})
    balance = user["balance"] if user else 0
    await message.reply_text(f"💰 Your balance: {balance} Coins")

# Add Task (Admin only)
@bot.on_message(filters.command("addtask") & filters.user(123456789))  # Replace with your Telegram ID
async def add_task(client, message):
    task_desc = message.text.split("/addtask ", 1)[-1]
    db.tasks.insert_one({"task": task_desc})
    await message.reply_text("✅ Task added!")

# Request Withdrawal
@bot.on_message(filters.command("withdraw"))
async def withdraw(client, message):
    user = db.users.find_one({"user_id": message.from_user.id})
    if user["balance"] < 10:  # Minimum withdrawal limit
        await message.reply_text("⚠️ Minimum withdrawal is 10 Coins!")
        return
    await message.reply_text("✅ Withdrawal request sent. Admin will review.")

# Run bot
bot.run()
