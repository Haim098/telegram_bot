from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
הנה רשימת הפקודות הזמינות:

/start - התחל את השיחה עם הבוט
/add - הוסף פריט או רשימת פריטים לרשימת הקניות
/list - הצג את רשימת הקניות הנוכחית
/remove - הסר פריט מרשימת הקניות
/done - סמן פריט כבוצע
/link - קשר את חשבון הטלגרם שלך לחשבון באתר
/unlink - בטל את הקישור בין חשבון הטלגרם לחשבון באתר
/help - הצג את רשימת הפקודות הזמינות

לשימוש בפקודות:
- הוסף פריט: /add חלב
- הוסף מספר פריטים: /add 2 תפוחים, לחם, 3 ביצים
- הסר פריט: /remove חלב
- סמן פריט כבוצע: /done חלב

אם יש לך שאלות נוספות, אל תהסס לשאול!
    """
    await update.message.reply_text(help_text)
