from telegram import Update
from telegram.ext import ContextTypes
from utils.firebase_connection import unlink_telegram_from_website_user

async def unlink_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if unlink_telegram_from_website_user(user_id):
        await update.message.reply_text("החשבון שלך נותק בהצלחה מהאתר.")
    else:
        await update.message.reply_text("לא נמצא חשבון מקושר או שאירעה שגיאה בניתוק החשבון.")