from telegram import Update
from telegram.ext import ContextTypes
from utils.firebase_connection import get_shopping_list
from collections import defaultdict

async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    items = get_shopping_list(user_id)
    if items is None:
        message = "חשבונך אינו מקושר. השתמש בפקודה /link לקישור החשבון."
    elif not items:
        message = "רשימת הקניות שלך ריקה."
    else:
        # Group items by category
        categories = defaultdict(list)
        for item in items:
            categories[item.get('category', 'כללי')].append(item)
        
        message = "רשימת הקניות שלך:\n\n"
        for category, items in categories.items():
            message += f"*{category}:*\n"
            for item in items:
                status = "✅" if item.get('completed', False) else "❌"
                quantity = item.get('quantity', 1)
                notes = f" - {item.get('notes')}" if item.get('notes') else ""
                message += f"{status} {item.get('name', 'Unknown Item')} (x{quantity}){notes}\n"
            message += "\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')
