import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage (Temporary - No DB)
users = {}  # {user_id: {"balance": X, "referrals": [ref_user_ids]}}
tasks = {1: "Share the bot with 3 friends", 2: "Join our Telegram group"}  # Example tasks
joined_users = set()  # Users who passed the channel join check

# Admin ID (Replace with your Telegram ID)
ADMIN_ID = 737758689  # Replace with your Telegram ID

# Bot Configuration
BOT_USERNAME = "duckpolz_bot"  # Replace with your bot's username (without @)
CHANNEL_USERNAME = "MNBLChat "  # Channel username (without @)
CHANNEL_LINK = "https://t.me/MNBLChat"

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.setdefault(user_id, {"balance": 0, "referrals": [], "completed_tasks": []})

    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
         InlineKeyboardButton("📋 View Tasks", callback_data="view_tasks")],
        [InlineKeyboardButton("👥 Referral Info", callback_data="referrals"),
         InlineKeyboardButton("📤 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("💼 How to Earn?", callback_data="earnings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Welcome {update.effective_user.first_name}!\n\n"
        f"💰 Earn ₹2 per referral!\n"
        f"🔗 Your Referral Link:\n"
        f"`https://t.me/{BOT_USERNAME}?start={user_id}`\n\n"
        f"📢 Invite friends & start earning!",
        reply_markup=reply_markup
    )

# Check Balance
async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    balance = users.get(user_id, {}).get("balance", 0)

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()
    await query.message.edit_text(f"💰 **Your Balance:** ₹{balance}\n\n"
                                  "📢 Keep inviting friends to earn more!",
                                  reply_markup=reply_markup)

# View Available Tasks
async def view_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not tasks:
        await query.answer()
        await query.message.edit_text("📋 **No tasks available right now.**\nCheck back later! ⏳")
        return

    message = "📋 **Available Tasks:**\n\n"
    buttons = []

    for task_id, task_desc in tasks.items():
        if task_id not in users[user_id]["completed_tasks"]:
            message += f"✅ **Task {task_id}:** {task_desc}\n"
            buttons.append([InlineKeyboardButton(f"✔ Complete Task {task_id}", callback_data=f"complete_{task_id}")])

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.answer()
    await query.message.edit_text(message, reply_markup=reply_markup)

# Complete Task
async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    task_id = int(query.data.split("_")[1])

    if task_id in users[user_id]["completed_tasks"]:
        await query.answer("❌ You have already completed this task.")
        return

    users[user_id]["completed_tasks"].append(task_id)
    users[user_id]["balance"] += 1  # ₹1 per completed task

    await query.answer()
    await query.message.edit_text(f"🎉 **Task {task_id} Completed!** ₹1 added to your balance! 💰")

# Referral Info
async def referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    referral_count = len(users.get(user_id, {}).get("referrals", []))

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()
    await query.message.edit_text(f"👥 **Total Referrals:** {referral_count}\n\n"
                                  f"🔗 Your Referral Link:\n"
                                  f"`https://t.me/{BOT_USERNAME}?start={user_id}`\n\n"
                                  f"📢 Invite more & earn ₹2 per referral!",
                                  reply_markup=reply_markup)

# Withdrawal Request
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    balance = users.get(user_id, {}).get("balance", 0)

    if balance < 50:
        await query.answer("❌ Minimum ₹50 required for withdrawal!", show_alert=True)
        return

    users[user_id]["balance"] = 0  # Reset balance after withdrawal request

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()
    await query.message.edit_text("📤 **Withdrawal Request Sent!**\n\n"
                                  "✅ The admin will review your request shortly!",
                                  reply_markup=reply_markup)

# How to Earn?
async def earning_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()
    await query.message.edit_text(
        "💼 **How to Earn Money?**\n\n"
        "✅ **Refer Friends:** Earn ₹2 per referral! 👥\n"
        "✅ **Complete Tasks:** Earn ₹1 per task! 📋\n"
        "✅ **Withdraw when you reach ₹50** 📤\n\n"
        "🚀 Start referring & earning now!",
        reply_markup=reply_markup
    )

# Back to Main Menu
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
         InlineKeyboardButton("📋 View Tasks", callback_data="view_tasks")],
        [InlineKeyboardButton("👥 Referral Info", callback_data="referrals"),
         InlineKeyboardButton("📤 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("💼 How to Earn?", callback_data="earnings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        f"💰 Earn ₹2 per referral!\n"
        f"🔗 Your Referral Link:\n"
        f"`https://t.me/{BOT_USERNAME}?start={user_id}`\n\n"
        f"📢 Invite friends & start earning!",
        reply_markup=reply_markup
    )

# Callback Query Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    actions = {
        "balance": check_balance,
        "view_tasks": view_tasks,
        "referrals": referral_info,
        "withdraw": withdraw,
        "earnings": earning_guide,
        "back": back_to_menu
    }
    await actions.get(query.data, back_to_menu)(update, context)

# Main Function
def main():
    BOT_TOKEN = "7856544100:AAEQg6esrMF6Z7mefUAtbwzmqgG-TBuKTU0"  # Replace with your Bot Token

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
