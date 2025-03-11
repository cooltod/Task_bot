import os
import json
from pyrogram import Client, filters

# Load Bot Token from Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize Bot in Bot API Mode
bot = Client("CryptoBot", bot_token=BOT_TOKEN, api_id=1, api_hash="abc", no_updates=True)

# File to store user balances
DATA_FILE = "users.json"

# Load user data
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save user data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Start Command
@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    if user_id not in data:
        data[user_id] = {"balance": 0}
        save_data(data)
        await message.reply_text("🎉 Welcome! Start earning by completing tasks.")
    else:
        await message.reply_text("🔄 Welcome back!")

# Check Balance
@bot.on_message(filters.command("balance"))
async def balance(client, message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    balance = data.get(user_id, {}).get("balance", 0)
    await message.reply_text(f"💰 Your balance: {balance} Coins")

# Run the bot
bot.run()
