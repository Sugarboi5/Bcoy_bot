import os
import sys
import time
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.error import NetworkError, TimedOut, RetryAfter, TelegramError
from keep_alive import keep_alive

# ========================================================
# Configure Logging
# ========================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Suppress noisy logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)

# ========================================================
# Load BOT_TOKEN
# ========================================================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("❌ BOT_TOKEN not found!")
    raise ValueError("BOT_TOKEN not found in environment variables!")

logger.info("✅ BOT_TOKEN loaded successfully")

# ========================================================
# Global variables for health monitoring
# ========================================================
last_update_time = datetime.now()
is_bot_healthy = True

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
# Command Handlers
# ========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    global last_update_time
    last_update_time = datetime.now()

    try:
        await update.message.reply_text(
            "Choose an item from the menu:",
            reply_markup=main_menu_keyboard()
        )
        logger.info(f"✅ User {update.effective_user.id} started the bot")
    except Exception as e:
        logger.error(f"❌ Error in start command: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    global last_update_time
    last_update_time = datetime.now()

    query = update.callback_query

    try:
        await query.answer()
    except Exception as e:
        logger.error(f"❌ Error answering callback: {e}")
        return

    # Back to menu
    if query.data == "menu":
        try:
            await query.edit_message_text(
                text="Choose an item from the menu:",
                reply_markup=main_menu_keyboard()
            )
            logger.info(f"✅ User {update.effective_user.id} returned to menu")
        except Exception as e:
            logger.error(f"❌ Error showing menu: {e}")
        return

    # Response mapping
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
        logger.info(f"✅ User {update.effective_user.id} selected {query.data}")
    except Exception as e:
        logger.error(f"❌ Error editing message: {e}")

# ========================================================
# Error Handler
# ========================================================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"❌ Exception while handling an update: {context.error}")

# ========================================================
# FINAL FIXED Health Watchdog - No More False Recoveries!
# ========================================================
async def health_watchdog(app: Application):
    """
    Monitor bot health and force restart when stalled.
    FIXED: No longer resets timer on connection test!
    """
    global last_update_time, is_bot_healthy

    logger.info("🔍 Health watchdog started (FINAL FIXED VERSION v3)")
    consecutive_stalls = 0

    while True:
        try:
            await asyncio.sleep(180)  # Check every 3 minutes

            # Check if we've received updates recently
            time_since_update = (datetime.now() - last_update_time).total_seconds()

            # Stall threshold: 6 minutes (more aggressive)
            if time_since_update > 360:  # 6 minutes
                consecutive_stalls += 1
                logger.warning(f"⚠️ No updates for {int(time_since_update)}s (stall check #{consecutive_stalls})")

                # Test connection for logging purposes only
                try:
                    bot_info = await app.bot.get_me()
                    logger.info(f"📡 Connection test: @{bot_info.username} reachable")
                except Exception as e:
                    logger.error(f"❌ Connection test failed: {e}")

                # CRITICAL FIX: Force restart after just 1 stall detection!
                # Don't trust connection test - if no updates, something is wrong
                if consecutive_stalls >= 1:
                    logger.error(f"❌ BOT STALLED - No updates for {int(time_since_update)}s - FORCING RESTART NOW!")
                    is_bot_healthy = False
                    raise Exception(f"Forced restart: No updates for {int(time_since_update)}s")

            else:
                # Only reset counter if we ACTUALLY got recent updates
                if consecutive_stalls > 0:
                    logger.info(f"✅ Bot recovered - got update {int(time_since_update)}s ago")
                consecutive_stalls = 0
                logger.info(f"✅ Bot healthy - last update {int(time_since_update)}s ago")

        except Exception as e:
            logger.error(f"🔄 Watchdog triggering restart: {e}")
            is_bot_healthy = False
            return  # Exit watchdog to trigger restart

# ========================================================
# Application Setup
# ========================================================
def create_application():
    """Create and configure the Application"""
    logger.info("📱 Creating application...")

    try:
        # Build application with all necessary timeouts
        app = (
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
            .build()
        )

        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_error_handler(error_handler)

        logger.info("✅ Application created successfully")
        return app

    except Exception as e:
        logger.error(f"❌ Failed to create application: {e}")
        raise

# ========================================================
# Main Bot Loop with Auto-Restart
# ========================================================
async def run_bot():
    """Run the bot with automatic restart on errors"""

    max_consecutive_errors = 5
    error_count = 0
    restart_count = 0

    while True:
        app = None
        watchdog_task = None

        try:
            logger.info(f"🚀 Starting bot (restart #{restart_count})...")

            # Reset health flag
            global is_bot_healthy, last_update_time
            is_bot_healthy = True
            last_update_time = datetime.now()

            # Create application
            app = create_application()

            # Initialize the application
            await app.initialize()
            logger.info("✅ Application initialized")

            # Start the application
            await app.start()
            logger.info("✅ Application started")

            # Start polling
            logger.info("🔄 Starting polling...")
            updater = app.updater
            await updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
                poll_interval=1.0
            )

            logger.info("✅ Bot is now running!")
            error_count = 0  # Reset error count on successful start

            # Start health watchdog in background
            watchdog_task = asyncio.create_task(health_watchdog(app))

            # Keep running - check every second if still healthy
            while is_bot_healthy:
                await asyncio.sleep(1)

            # If we get here, watchdog detected an issue
            logger.warning("⚠️ Watchdog detected issue - restarting bot...")
            raise Exception("Watchdog-triggered restart")

        except RetryAfter as e:
            wait_time = int(e.retry_after) + 2
            logger.warning(f"⏳ Rate limited by Telegram. Waiting {wait_time}s...")
            await asyncio.sleep(wait_time)
            error_count = 0

        except TimedOut:
            logger.warning("⏱️ Request timed out")
            error_count += 1
            if error_count >= max_consecutive_errors:
                logger.error(f"❌ Too many timeouts ({error_count}), waiting 120s...")
                await asyncio.sleep(120)
                error_count = 0
            else:
                await asyncio.sleep(10)

        except NetworkError as e:
            logger.error(f"🌐 Network error: {e}")
            error_count += 1
            if error_count >= max_consecutive_errors:
                logger.error(f"❌ Too many network errors ({error_count}), waiting 120s...")
                await asyncio.sleep(120)
                error_count = 0
            else:
                await asyncio.sleep(15)

        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
            break

        except Exception as e:
            logger.error(f"⚠️ Error: {e}", exc_info=True)
            error_count += 1

            if error_count >= max_consecutive_errors:
                logger.critical(f"❌ Too many errors ({error_count}), waiting 180s...")
                await asyncio.sleep(180)
                error_count = 0
            else:
                await asyncio.sleep(20)

        finally:
            # Cancel watchdog
            if watchdog_task and not watchdog_task.done():
                watchdog_task.cancel()
                try:
                    await watchdog_task
                except asyncio.CancelledError:
                    pass

            # Clean shutdown
            if app:
                try:
                    logger.info("🔄 Shutting down application...")
                    if app.updater and app.updater.running:
                        await app.updater.stop()
                    await app.stop()
                    await app.shutdown()
                    logger.info("✅ Application shut down cleanly")
                except Exception as e:
                    logger.error(f"❌ Error during shutdown: {e}")

            # Increment restart counter
            restart_count += 1

            # Wait before restart
            logger.info("⏳ Waiting 5s before restart...")
            await asyncio.sleep(5)

# ========================================================
# Entry Point
# ========================================================
def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("🤖 Telegram Bot Starting... (FINAL FIXED v3)")
    logger.info("=" * 60)

    # Start keep-alive server
    logger.info("⚡ Starting keep-alive server...")
    keep_alive()

    # Run the bot
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()