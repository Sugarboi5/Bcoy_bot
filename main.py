import os
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.error import NetworkError, TimedOut, RetryAfter
from keep_alive import keep_alive

# ========================================================
# Configure Logging
# ========================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Suppress httpx logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# ========================================================
# Load BOT_TOKEN safely
# ========================================================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in environment variables!")

# ========================================================
# Inline Keyboard Menu
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
# Start Command
# ========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Choose an item from the menu:",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")

# ========================================================
# Button Handler
# ========================================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        await query.answer()
    except Exception as e:
        logger.error(f"Error answering callback query: {e}")
        return

    if query.data == "menu":
        try:
            await query.edit_message_text(
                text="Choose an item from the menu:",
                reply_markup=main_menu_keyboard()
            )
        except Exception as e:
            logger.error(f"Error showing menu: {e}")
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

    try:
        await query.edit_message_text(
            text=response,
            reply_markup=back_button,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error editing message: {e}")

# ========================================================
# Error Handler
# ========================================================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and handle them gracefully"""
    logger.error(f"Update {update} caused error {context.error}")

# ========================================================
# Post Init - Clean up after application starts
# ========================================================
async def post_init(application: Application):
    """Called after application initialization"""
    logger.info("✅ Bot initialized successfully")

# ========================================================
# Run the bot (Render-Optimized)
# ========================================================
def main():
    # Start Flask keep-alive server
    logger.info("Starting keep-alive server...")
    keep_alive()

    # Build application with proper configuration
    try:
        application = (
            Application.builder()
            .token(TOKEN)
            .read_timeout(30)
            .write_timeout(30)
            .connect_timeout(30)
            .pool_timeout(30)
            .get_updates_read_timeout(30)
            .get_updates_write_timeout(30)
            .get_updates_connect_timeout(30)
            .get_updates_pool_timeout(30)
            .post_init(post_init)
            .build()
        )

        logger.info("✅ Application built successfully")

    except Exception as e:
        logger.error(f"❌ Failed to build application: {e}")
        raise

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)

    logger.info("🚀 Bot handlers registered, starting polling...")

    # Run with proper error handling and retry logic
    max_consecutive_errors = 5
    error_count = 0

    while True:
        try:
            logger.info("Starting polling...")

            # Use run_polling with proper parameters
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                close_loop=False
            )

            # If polling stops cleanly, reset error count
            logger.warning("Polling stopped cleanly, restarting...")
            error_count = 0
            time.sleep(2)

        except RetryAfter as e:
            # Telegram rate limit
            wait_time = int(e.retry_after) + 2
            logger.warning(f"⏳ Rate limited by Telegram. Waiting {wait_time}s...")
            time.sleep(wait_time)
            error_count = 0

        except TimedOut as e:
            logger.warning(f"⏱️ Request timed out: {e}")
            error_count += 1

            if error_count >= max_consecutive_errors:
                logger.error(f"❌ Too many consecutive timeouts ({error_count}), waiting 60s...")
                time.sleep(60)
                error_count = 0
            else:
                time.sleep(5)

        except NetworkError as e:
            logger.error(f"🌐 Network error: {e}")
            error_count += 1

            if error_count >= max_consecutive_errors:
                logger.error(f"❌ Too many consecutive errors ({error_count}), waiting 60s...")
                time.sleep(60)
                error_count = 0
            else:
                time.sleep(10)

        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
            break

        except Exception as e:
            logger.error(f"⚠️ Unexpected error: {e}", exc_info=True)
            error_count += 1

            if error_count >= max_consecutive_errors:
                logger.critical(f"❌ Too many consecutive errors ({error_count}), waiting 120s...")
                time.sleep(120)
                error_count = 0
            else:
                time.sleep(15)

if __name__ == "__main__":
    main()