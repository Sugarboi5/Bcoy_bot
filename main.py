import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive  # Keeps bot online

# ========================================================
# 1️⃣  Define your TOKEN first (before using it)
# ========================================================
TOKEN = "7230688408:AAFepfma6tYPuVc3guaZxgbWo1p4PXILdgg"  # Replace with your actual bot token
# ⚠️ Tip: Later move this to Replit Secrets (key: BOT_TOKEN)

# ========================================================
# 2️⃣  Main menu generator (used multiple times)
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
# 3️⃣  Define your command functions
# ========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Choose an item from the menu:",
        reply_markup=main_menu_keyboard()
    )

# ========================================================
# 4️⃣  Define button responses
# ========================================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # If user presses "menu", reload main menu
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

    # Add a "Back to Menu" button
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
# 5️⃣  Run the bot
# ========================================================
def main():
    # Start the Flask keep-alive server
    keep_alive()

    # Create and start the Telegram bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot is now running...")
    application.run_polling()

if __name__ == "__main__":
    main()
