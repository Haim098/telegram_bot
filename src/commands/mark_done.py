from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from utils.firebase_connection import mark_item_as_done, get_shopping_list

async def mark_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args:
        item_to_mark = ' '.join(context.args)
        if mark_item_as_done(user_id, item_to_mark):
            await update.message.reply_text(f'הפריט "{item_to_mark}" סומן כבוצע.')
        else:
            items = get_shopping_list(user_id)
            similar_items = [item['name'] for item in items if item_to_mark.lower() in item['name'].lower()]
            if similar_items:
                keyboard = [[InlineKeyboardButton(item, callback_data=f"mark_done:{item}") for item in similar_items]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f'לא מצאתי פריט בדיוק בשם "{item_to_mark}". האם התכוונת לאחד מאלה?',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(f'לא מצאתי פריט דומה ל-"{item_to_mark}" ברשימה שלך.')
    else:
        await update.message.reply_text('אנא ציין את שם הפריט שברצונך לסמן כבוצע. לדוגמה: /done חלב')

async def mark_done_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(':')
    if data[0] == 'mark_done':
        item_name = data[1]
        user_id = update.effective_user.id
        if mark_item_as_done(user_id, item_name):
            await query.edit_message_text(f'הפריט "{item_name}" סומן כבוצע.')
        else:
            await query.edit_message_text(f'אירעה שגיאה בסימון הפריט "{item_name}" כבוצע.')

def setup(application):
    application.add_handler(CommandHandler("done", mark_done))
    application.add_handler(CallbackQueryHandler(mark_done_button, pattern='^mark_done:'))
