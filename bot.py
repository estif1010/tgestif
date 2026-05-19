import random
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

users = {}
pending_deposits = {}
pending_withdraw = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {"balance": 100, "games": 0}
    return users[uid]

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(
        "🎰 FULL KENO SYSTEM\n\n"
        "/bet amount number(1-10)\n"
        "/balance\n"
        "/deposit amount\n"
        "/withdraw amount"
    )

# BALANCE
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 Balance: {u['balance']} ETB")

# BET
async def bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = get_user(uid)

    if len(context.args) != 2:
        return await update.message.reply_text("/bet amount number")

    amount = int(context.args[0])
    number = int(context.args[1])

    if amount > u["balance"]:
        return await update.message.reply_text("Not enough balance")

    lucky = random.randint(1, 10)
    u["games"] += 1

    if number == lucky:
        win = amount * 5
        u["balance"] += win
        msg = f"🎉 WIN! Lucky: {lucky} +{win}"
    else:
        u["balance"] -= amount
        msg = f"❌ Lose! Lucky: {lucky} -{amount}"

    await update.message.reply_text(msg)

# DEPOSIT REQUEST
async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    amount = int(context.args[0])

    pending_deposits[uid] = amount

    await update.message.reply_text(
        f"📥 Deposit Request Sent\nSend {amount} ETB via Telebirr\nThen wait admin approval."
    )

    await context.bot.send_message(
        ADMIN_ID,
        f"📥 Deposit request:\nUser: {uid}\nAmount: {amount}\nApprove: /approve {uid}"
    )

# WITHDRAW REQUEST
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = get_user(uid)

    amount = int(context.args[0])

    if amount > u["balance"]:
        return await update.message.reply_text("Not enough balance")

    pending_withdraw[uid] = amount

    await update.message.reply_text("📤 Withdraw request sent")

    await context.bot.send_message(
        ADMIN_ID,
        f"📤 Withdraw request:\nUser: {uid}\nAmount: {amount}\n/confirmw {uid}"
    )

# ADMIN APPROVE DEPOSIT
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    uid = int(context.args[0])
    amount = pending_deposits.get(uid, 0)

    get_user(uid)["balance"] += amount

    await context.bot.send_message(uid, f"✅ Deposit approved +{amount} ETB")

# ADMIN CONFIRM WITHDRAW
async def confirmw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    uid = int(context.args[0])
    amount = pending_withdraw.get(uid, 0)

    get_user(uid)["balance"] -= amount

    await context.bot.send_message(uid, f"✅ Withdraw approved -{amount} ETB")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("bet", bet))
app.add_handler(CommandHandler("deposit", deposit))
app.add_handler(CommandHandler("withdraw", withdraw))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("confirmw", confirmw))

print("FULL KENO SYSTEM RUNNING...")
app.run_polling()