from telegram import Update
from telegram.ext import ContextTypes
from utils.firebase_connection import remove_item_from_list, get_shopping_list

async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args:
        item_to_remove = ' '.join(context.args)
        items = get_shopping_list(user_id)
        for item in items:
            if item['name'].lower() == item_to_remove.lower():
                if remove_item_from_list(user_id, item['id']):
                    await update.message.reply_text(f'הפריט "{item_to_remove}" הוסר מרשימת הקניות שלך.')
                else:
                    await update.message.reply_text('אירעה שגיאה בהסרת הפריט. אנא נסה שוב מאוחר יותר.')
                return
        await update.message.reply_text(f'הפריט "{item_to_remove}" לא נמצא ברשימה שלך.')
    else:
        await update.message.reply_text('אנא ציין את שם הפריט שברצונך להסיר. לדוגמה: /remove חלב')
