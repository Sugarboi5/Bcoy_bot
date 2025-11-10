import os
import time
import threading
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from keep_alive import keep_alive  # keeps the Render service active

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
        "item1": (
            "**Minimum Force Level (MFL)**\n\n"
            "The MFL must always be maintained, and any changes to the MFL require approval from the Commanding Officer.\n\n"
            "The Chief Operator may delegate tasks but remains responsible for the hunters' assignment."
            " The assignment must be recorded in the designated Ops manning record for accountability and monitoring.\n\n"
            "**MFL Table:**\n\n"
            "| Day         | Day (AM) Shift | Stagger (PM Shift) |\n"
            "|--------------|----------------|--------------------|\n"
            "| Weekday    | 7            | 6                |\n"
            "| Weekend/PH | 8            | 6                |\n"
            "| Flight     | +1           | +2               |\n\n"
            "**If the MFL is not met, the Chief Operator/Deputy Chief Operator must inform:**\n"
            "- CE (for Ops)\n"
            "- Chief Expert (CX) (for manpower resourcing)\n\n"
            "Details to be provided:\n"
            "- Reason for the shortfall\n"
            "- Personnel involved\n"
            "- Current Ops situation\n\n"
            "**Interim Mitigation Measures:**\n"
            "- Reallocate assignments while awaiting late arrivals or activated personnel.\n"
            "- CE/CX may retain personnel from the previous shift if required."
        ),
        "item2": (
            "**PERSONNEL ACTIVATION**\n\n"
            "B Coy personnel may be recalled (activated) from Off-In-Lieu (OIL), OFF, and vacation leave to maintain the MFL caused by unforeseen events and to meet ad-hoc Ops exigencies.\n\n"
            "**Activation Priority for Personnel**\n\n"
            "1. OIL - Back to own shift on their default working day. Includes post-regimental duty rest/OIL.\n"
            "2. Standby (Planned/Pre-arranged) - Last man recalled.\n"
            "3. Working Personnel OFF Shift - Recalled on default working day to another shift.\n"
            "4. OFF Shift - Recalled on default OFF day.\n"
            "5. OFF Shift (if Priority 1-4 exhausted) - Recall personnel from OFF day.\n"
            "6. Full Pay Unrecorded Leave (FPUL) - Recall with OC approval.\n"
            "7. Vacation Leave (Local) - OC approval needed.\n"
            "8. Vacation Leave (Overseas) - CO approval needed.\n"
            "9. VIPER - At discretion of Chief Opr or CX.\n\n"
            "**Reporting Time upon Activation:**\n"
            "Personnel recalled must report to the OPS room within **2 hours** of activation."
        ),
        "item3": (
            "**CONTACTABILITY**\n\n"
            "All personnel must remain contactable at all times, particularly Standby personnel.\n"
            "- Primary Standby personnel must respond before **0630hrs** (for Day shift activation) and **1230hrs** (for Stagger/VIPER shift activation).\n"
            "- Personnel who are uncontactable upon activation will face disciplinary actions.\n\n"
            "**Standby Activation Cut-off Time:**\n"
            "- Default cut-off is **1200hrs**. CX may adjust based on operational needs while ensuring adequate work-rest cycles."
        ),
        "item4": (
            "**ATTENDANCE AND ACCOUNTABILITY**\n\n"
            "**Reporting Time:**\n"
            "- Day Shift: 0745hrs\n"
            "- Stagger Shift: 1445hrs\n"
            "- VIPER Shift: 2145hrs\n\n"
            "Late arrivals (Day: 0746hrs, Stagger: 1446hrs, VIPER: 2146hrs) will face disciplinary actions.\n"
            "Failure to report for duty without official leave is a chargeable offense."
        ),
        "item5": (
            "**LEAVE MANAGEMENT**\n\n"
            "Personnel are encouraged to forecast and plan leave early.\n"
            "- Leave is allocated on a **first-come-first-served basis**.\n"
            "- The last person requesting leave (Last Man) will be recallable to maintain MFL.\n"
            "- Alternatively, personnel may arrange for Standby coverage from the Off shift."
        ),
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
    from keep_alive import keep_alive
    import time
    from telegram.error import NetworkError
    keep_alive()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Cleaning any existing webhooks...")
    try:
        import requests
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    except Exception as e:
        print("⚠️ Could not delete webhook:", e)

    print("🚀 Bot is now running...")

    # Poll forever, even if Render sleeps/restarts
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