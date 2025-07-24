from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes

TOKEN = "7985558703:AAEkkhLy5KXBMjWVtYk7bcGUNGscCyuQmYM"

SUM_INPUT, DAYS_INPUT, PARTNER_INPUT = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("$500", callback_data="500"),
         InlineKeyboardButton("$1,000", callback_data="1000")],
        [InlineKeyboardButton("$2,500", callback_data="2500"),
         InlineKeyboardButton("$5,000", callback_data="5000")],
        [InlineKeyboardButton("$10,000", callback_data="10000"),
         InlineKeyboardButton("$50,000", callback_data="50000")],
        [InlineKeyboardButton("$250,000", callback_data="250000"),
         InlineKeyboardButton("$1,000,000", callback_data="1000000")]
    ]
    main_menu = [["💰 Расчёт дохода"], ["👥 Партнёрка"], ["🔙 Назад"]]
    reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    inline_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите сумму или введите вручную:", reply_markup=reply_markup)
    await update.message.reply_text("Или нажмите одну из кнопок ниже:", reply_markup=inline_markup)
    return SUM_INPUT

async def handle_sum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        amount = float(text.replace("$", "").replace(",", ""))
        context.user_data['amount'] = amount
        await update.message.reply_text("Введите количество дней:")
        return DAYS_INPUT
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректную сумму.")
        return SUM_INPUT

async def handle_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text)
        amount = context.user_data.get('amount', 0)
        daily_income = amount * 0.005
        total_income = daily_income * days
        await update.message.reply_text(f"💵 Ваш доход за {days} дней: ${total_income:,.2f}")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите количество дней числом.")
        return DAYS_INPUT

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    amount = float(query.data)
    context.user_data['amount'] = amount
    await query.message.reply_text("Введите количество дней:")
    return DAYS_INPUT

async def partner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сколько у вас партнёров и на какую сумму каждый (например: 3 по 1000)?")
    return PARTNER_INPUT

async def handle_partner_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        num, value = map(int, text.replace("по", "").split())
        total = num * value
        lvl1 = total * 0.15
        lvl2 = total * 0.03
        lvl3 = 10 * num
        await update.message.reply_text(
            f"👥 Партнёрка с {num} партнёрами по ${value}:\n"
            f"— 1-я линия: ${lvl1:.2f}\n"
            f"— 2-я линия: ${lvl2:.2f}\n"
            f"— 3-я линия: ${lvl3:.2f} (фиксировано)"
        )
        return ConversationHandler.END
    except Exception:
        await update.message.reply_text("Введите в формате: 5 по 1000")
        return PARTNER_INPUT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SUM_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sum),
                CallbackQueryHandler(handle_button)
            ],
            DAYS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_days)],
            PARTNER_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_partner_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("💰 Расчёт дохода"), start))
    app.add_handler(MessageHandler(filters.Regex("👥 Партнёрка"), partner_command))
    app.add_handler(MessageHandler(filters.Regex("🔙 Назад"), cancel))

    app.run_polling()

if __name__ == "__main__":
    main()
 