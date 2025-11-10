import os
import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.error import NetworkError
from keep_alive import keep_alive  # Keeps the Render service active

# ========================================================
# 1️⃣  Load BOT_TOKEN safely
# ========================================================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in environment variables!")

# ========================================================
# 2️⃣  Inline Keyboard Menu
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
        "item1": "**Minimum Force Level (MFL)** — details...",
        "item2": "**PERSONNEL ACTIVATION** — details...",
        "item3": "**CONTACTABILITY** — details...",
        "item4": "**ATTENDANCE AND ACCOUNTABILITY** — details...",
        "item5": "**LEAVE MANAGEMENT** — details...",
        "item6": "Details about Item 6...",
        "item7": "Details about Item 7...",
        "item8": "Details about Item 8...",
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
# 5️⃣  Run the bot (Render-Optimized)
# ========================================================
def main():
    # Start Flask keep-alive server (only once!)
    keep_alive()

    # Clean any old webhook
    print("✅ Cleaning any existing webhooks...")
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    except Exception as e:
        print("⚠️ Could not delete webhook:", e)

    # Start the bot application
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 Bot is now running...")

    # Keep polling forever with auto-restart
    while True:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES)
        except NetworkError:
            print("🌐 Network error, retrying in 10s...")
            time.sleep(10)
        except Exception as e:
            print(f"⚠️ Bot crashed: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
