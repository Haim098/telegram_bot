from telegram import Update
from telegram.ext import ContextTypes
from utils.firebase_connection import add_item_to_list
from utils.llm_parser import parseUnstructuredList

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args:
        text = ' '.join(context.args)
        try:
            parsed_items = parseUnstructuredList(text)
            added_items = []
            for item in parsed_items:
                if add_item_to_list(user_id, item['name'], item['quantity'], item['category'], item['notes']):
                    added_items.append(item['name'])
            
            if added_items:
                await update.message.reply_text(f'הפריטים הבאים נוספו לרשימת הקניות שלך: {", ".join(added_items)}')
            else:
                await update.message.reply_text('לא הצלחתי להוסיף אף פריט לרשימה. אנא נסה שנית.')
        except Exception as e:
            await update.message.reply_text(f'אירעה שגיאה בעיבוד הרשימה: {str(e)}')
    else:
        await update.message.reply_text('אנא ציין את שם הפריט או רשימת פריטים שברצונך להוסיף. לדוגמה: /add חלב, 3 תפוחים')
