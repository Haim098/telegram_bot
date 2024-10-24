from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.firebase_connection import link_telegram_to_website_user, get_website_user_id, authenticate_user

EMAIL, PASSWORD = range(2)

async def link_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    existing_link = get_website_user_id(user_id)
    if existing_link:
        await update.message.reply_text("החשבון שלך כבר מקושר לחשבון באתר.")
        return ConversationHandler.END
    
    await update.message.reply_text("בבקשה הזן את כתובת האימייל שלך באתר:")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    await update.message.reply_text("תודה. עכשיו הזן את הסיסמה שלך:")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = context.user_data['email']
    password = update.message.text
    
    user_id = authenticate_user(email, password)
    if user_id:
        telegram_id = update.effective_user.id
        if link_telegram_to_website_user(telegram_id, user_id):
            await update.message.reply_text("החשבון שלך קושר בהצלחה!")
        else:
            await update.message.reply_text("אירעה שגיאה בקישור החשבון. אנא נסה שוב מאוחר יותר.")
    else:
        await update.message.reply_text("האימייל או הסיסמה שגויים. אנא נסה שוב.")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("תהליך הקישור בוטל.")
    return ConversationHandler.END

link_account_handler = ConversationHandler(
    entry_points=[CommandHandler('link', link_account)],
    states={
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
