import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
from commands.add_item import add_item
from commands.list_items import list_items
from commands.remove_item import remove_item
from commands.link_account import link_account, link_account_handler
from commands.unlink_account import unlink_account
from commands.help import help_command
# הוסף את השורה הזו בייבוא הפקודות
from commands.mark_done import mark_done, setup as setup_mark_done

# Temporary: Use explicit token
TOKEN = "7850514395:AAHmzx6XAu5c0XRx1p9GIs-H2ZYefis75ZY"

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="ברוכים הבאים לבוט רשימת הקניות! אני כאן כדי לעזור לכם לנהל את רשימת הקניות שלכם.")

async def echo(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"קיבלתי את ההודעה שלך: {update.message.text}")

def main():
    application = Application.builder().token(TOKEN).build()

    print("מוסיף link_account_handler")
    application.add_handler(link_account_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_item))
    application.add_handler(CommandHandler("list", list_items))
    application.add_handler(CommandHandler("remove", remove_item))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler("unlink", unlink_account))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("done", mark_done))

    setup_mark_done(application)

    print("מתחיל את סקירת הבוט")
    application.run_polling()

if __name__ == '__main__':
    main()
