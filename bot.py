import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Temporary Storage (User Balances & Tasks)
users = {}
tasks = {}  # Stores tasks (task_id: task_description)
daily_bonus_claimed = {}

# Admin ID (Replace with your Telegram ID)
ADMIN_ID = 123456789  # Change this to your Telegram ID

# Start Command (Fun & Interactive)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.setdefault(user_id, {"balance": 0, "referred_by": None, "completed_tasks": []})

    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
         InlineKeyboardButton("📋 View Tasks", callback_data="view_tasks")],
        [InlineKeyboardButton("🎁 Claim Daily Bonus", callback_data="daily_bonus"),
         InlineKeyboardButton("💼 How to Earn?", callback_data="how_to_earn")],
        [InlineKeyboardButton("📤 Request Withdrawal", callback_data="withdraw")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_animation(
        animation="https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
        caption=f"👋 **Hey {update.effective_user.first_name}!**\n\n"
                f"🎯 Earn ₹1 per task\n"
                f"📢 Refer & earn ₹2 per friend\n"
                f"🎁 Claim a daily bonus!\n\n"
                f"🔽 Choose an option below 👇",
        reply_markup=reply_markup
    )

# Check Balance (Smooth UI)
async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    balance = users.get(user_id, {}).get("balance", 0)

    await query.answer()
    await query.message.edit_text(f"💰 **Your Balance:** ₹{balance} 💸\n\n"
                                  "📋 Keep completing tasks to earn more! 🎯")

# Claim Daily Bonus (With Fun Message)
async def claim_daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in daily_bonus_claimed:
        await query.answer("❌ You've already claimed today's bonus! 🎁")
        return

    users[user_id]["balance"] += 1  # ₹1 Daily Bonus
    daily_bonus_claimed[user_id] = True

    await query.answer()
    await query.message.reply_animation(
        animation="https://media.giphy.com/media/d31w24psGYeekCZy/giphy.gif",
        caption="🎉 **Bonus Claimed!** ₹1 added to your balance!\n"
                "💰 Keep earning more!"
    )

# How to Earn? (Interactive UI)
async def how_to_earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        "💼 **How to Earn Money?** 💸\n\n"
        "✅ Complete tasks (₹1 per task) 📋\n"
        "✅ Refer friends (₹2 per referral) 👥\n"
        "✅ Claim daily bonus (₹1/day) 🎁\n\n"
        "🚀 **Earn more & withdraw at ₹50!**"
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
    await query.message.reply_text("✅ **Withdrawal request sent!** 📤\n"
                                   "👀 Admin will review your request soon!")

# Admin: Add New Task (Now With Confirmation)
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Only the admin can add tasks.")
        return

    try:
        task_description = " ".join(context.args)
        if not task_description:
            await update.message.reply_text("Usage: `/addtask <task description>`")
            return

        task_id = len(tasks) + 1
        tasks[task_id] = task_description

        await update.message.reply_text(f"✅ **New Task Added:**\n📋 {task_description}")

    except Exception as e:
        logger.error(f"Error adding task: {e}")
        await update.message.reply_text("❌ Failed to add task.")

# View Available Tasks (Updated UI)
async def view_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not tasks:
        await query.answer()
        await query.message.edit_text("📋 **No tasks available!**\nCheck back later! ⏳")
        return

    message = "📋 **Available Tasks:**\n\n"
    buttons = []

    for task_id, task_desc in tasks.items():
        if task_id not in users[user_id]["completed_tasks"]:
            message += f"✅ **Task {task_id}:** {task_desc}\n"
            buttons.append([InlineKeyboardButton(f"✔ Complete Task {task_id}", callback_data=f"complete_{task_id}")])

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="start")])
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.answer()
    await query.message.edit_text(message, reply_markup=reply_markup)

# Complete Task (Celebratory Message)
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
    await query.message.reply_animation(
        animation="https://media.giphy.com/media/111ebonMs90YLu/giphy.gif",
        caption=f"🎉 **Task {task_id} Completed!** ₹1 added to your balance! 💰"
    )

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
    elif query.data == "view_tasks":
        await view_tasks(update, context)
    elif query.data.startswith("complete_"):
        await complete_task(update, context)
    elif query.data == "start":
        await start(update, context)

# Main Function
def main():
    BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your Bot Token

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addtask", add_task))  # Admin assigns tasks
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
