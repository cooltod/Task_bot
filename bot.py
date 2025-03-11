import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Temporary Storage (User Balances & Referral Tracking)
users = {}
daily_bonus_claimed = {}

# Admin ID (Replace with your Telegram ID)
ADMIN_ID = 123456789  # Change this to your Telegram ID

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.setdefault(user_id, {"balance": 0, "referred_by": None})

    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("🎁 Claim Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton("💼 How to Earn?", callback_data="how_to_earn")],
        [InlineKeyboardButton("📤 Request Withdrawal", callback_data="withdraw")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Welcome {update.effective_user.first_name}!\n"
        f"💸 Earn ₹1 per task!\n"
        f"📢 Refer friends & earn ₹2 per referral!\n\n"
        f"🔽 Use the buttons below:",
        reply_markup=reply_markup
    )

# Check Balance
async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    balance = users.get(user_id, {}).get("balance", 0)

    await query.answer()
    await query.message.edit_text(f"💰 Your current balance: ₹{balance}")

# Claim Daily Bonus
async def claim_daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in daily_bonus_claimed:
        await query.answer("❌ You've already claimed today's bonus!")
        return

    users[user_id]["balance"] += 1  # ₹1 Daily Bonus
    daily_bonus_claimed[user_id] = True

    await query.answer()
    await query.message.edit_text("🎉 Daily bonus claimed! ₹1 added to your balance.")

# How to Earn?
async def how_to_earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()
    await query.message.edit_text(
        "💼 **Ways to Earn Money:**\n"
        "1️⃣ Complete tasks (₹1 per task)\n"
        "2️⃣ Refer friends (₹2 per referral)\n"
        "3️⃣ Claim daily bonus (₹1 per day)\n\n"
        "🚀 Earn more & withdraw when you reach ₹50!"
    )

# Request Withdrawal
async def request_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    balance = users.get(user_id, {}).get("balance", 0)

    if balance < 50:
        await query.answer("❌ Minimum ₹50 required for withdrawal!")
        return

    users[user_id]["balance"] = 0  # Reset balance after withdrawal request
    await query.answer()
    await query.message.edit_text(
        "✅ Withdrawal request sent! Admin will review your request soon."
    )

# Admin: Assign Task (Manually)
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Only the admin can assign tasks.")
        return

    try:
        user_id = int(context.args[0])  # User ID
        if user_id not in users:
            await update.message.reply_text("❌ User not found.")
            return

        users[user_id]["balance"] += 1  # ₹1 per task
        await update.message.reply_text(f"✅ ₹1 added to user {user_id}'s balance.")

    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/addtask <user_id>`")

# Callback Query Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "balance":
        await check_balance(update, context)
    elif query.data == "daily_bonus":
        await claim_daily_bonus(update, context)
    elif query.data == "how_to_earn":
        await how_to_earn(update, context)
    elif query.data == "withdraw":
        await request_withdraw(update, context)

# Error Handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# Main Function
def main():
    BOT_TOKEN = "7856544100:AAEQg6esrMF6Z7mefUAtbwzmqgG-TBuKTU0"  # Replace with your Bot Token

    app = Application.builder().token(BOT_TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addtask", add_task))  # Admin assigns tasks

    # Callback Query Handler (For Inline Buttons)
    app.add_handler(CallbackQueryHandler(button_handler))

    # Error Handler
    app.add_error_handler(error_handler)

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
