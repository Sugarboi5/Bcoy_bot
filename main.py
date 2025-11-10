import os
import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from keep_alive import keep_alive  # Keeps the bot alive on Render

# ========================================================
# 1️⃣  Load BOT_TOKEN securely
# ========================================================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in environment variables!")

# ========================================================
# 2️⃣  Main Menu Layout
# ========================================================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Minimum Force Level", callback_data="item1")],
        [InlineKeyboardButton("PERSONNEL ACTIVATION", callback_data="item2")],
        [InlineKeyboardButton("CONTACTABILITY", callback_data="item3")],
        [InlineKeyboardButton("ATTENDANCE AND ACCOUNTABILITY", callback_data="item4")],
        [InlineKeyboardButton("LEAVE MANAGEMENT", callback_data="item5")],
        [InlineKeyboardButton("Item 6", callback_data="item6")],
        [InlineKeyboardButton("Item 7", callback_data="item7")],
        [InlineKeyboardButton("Item 8", callback_data="item8")],
    ])

# ========================================================
# 3️⃣  Start Command
# ========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Choose an item from the menu:",
        reply_markup=main_menu_keyboard()
    )

# ========================================================
# 4️⃣  Button Handler
# ========================================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu":
        await query.edit_message_text(
            text="Choose an item from the menu:",
            reply_markup=main_menu_keyboard()
        )
        return

    responses = {
        "item1": (
            "**Minimum Force Level (MFL)**\n\n"
            "The MFL must always be maintained, and any changes require CO approval.\n\n"
            "The Chief Operator may delegate but remains responsible for assignments.\n\n"
            "**MFL Table:**\n"
            "| Day | AM Shift | PM Shift |\n"
            "|------|-----------|-----------|\n"
            "| Weekday | 7 | 6 |\n"
            "| Weekend/PH | 8 | 6 |\n"
            "| Flight | +1 | +2 |\n\n"
            "**If MFL not met:**\n"
            "- Inform CE (Ops) and CX (Manpower)\n"
            "- Give reason, personnel involved, and Ops situation\n\n"
            "**Mitigation:**\n"
            "- Reallocate duties\n"
            "- Retain personnel if needed"
        ),
        "item2": (
            "**PERSONNEL ACTIVATION**\n\n"
            "Personnel may be recalled from OIL, OFF, or Leave to maintain MFL.\n\n"
            "**Priority Order:**\n"
            "1. OIL → own shift\n"
            "2. Standby → last recalled\n"
            "3. Working OFF shift → working day\n"
            "4. OFF shift → OFF day\n"
            "5. FPUL / Leave → with OC/CO approval\n\n"
            "**Reporting Time:**\n"
            "- Within 2 hours of activation."
        ),
        "item3": (
            "**CONTACTABILITY**\n\n"
            "All personnel must remain contactable.\n"
            "- Primary Standby: respond before **0630hrs** (Day) or **1230hrs** (Stagger/VIPER).\n"
            "- Uncontactable personnel face disciplinary action.\n"
            "- Standby cut-off: **1200hrs** unless adjusted by CX."
        ),
        "item4": (
            "**ATTENDANCE AND ACCOUNTABILITY**\n\n"
            "Report on time:\n"
            "- Day: 0745hrs\n"
            "- Stagger: 1445hrs\n"
            "- VIPER: 2145hrs\n\n"
            "Late arrivals face disciplinary action.\n"
            "Absence without approval is a chargeable offense."
        ),
        "item5": (
            "**LEAVE MANAGEMENT**\n\n"
            "Plan leave early — first-come-first-served.\n"
            "Last man requesting leave can be recalled.\n"
            "Standby coverage from OFF shift allowed."
        ),
        "item6": "Details about Item 6...",
        "item7": "Details about Item 7...",
        "item8": "Details about Item 8..."
    }

    back_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back to Menu", callback_data="menu")]
    ])

    response = responses.get(query.data, "Invalid selection.")
    await query.edit_message_text(
        text=response,
        reply_markup=back_button,
        parse_mode="Markdown"
    )

# ========================================================
# 5️⃣  Run Bot (Async, Safe Restart)
# ========================================================
async def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 Cleaning old webhooks...")
    await application.bot.delete_webhook(drop_pending_updates=True)

    print("✅ Bot is now running...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    keep_alive()
    while True:
        try:
            asyncio.run(run_bot())
        except Exception as e:
            print(f"⚠️ Bot crashed: {e}")
            print("🔁 Restarting in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    main()
