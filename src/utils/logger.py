import logging
import os
from datetime import datetime

def setup_logger():
    # יצירת תיקיית logs אם לא קיימת
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # הגדרת שם הקובץ עם תאריך
    log_filename = f'logs/shopping_bot_{datetime.now().strftime("%Y%m%d")}.log'
    error_log_filename = f'logs/shopping_bot_errors_{datetime.now().strftime("%Y%m%d")}.log'

    # הגדרת הפורמט
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )

    # הגדרת handler לכל הלוגים
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)

    # הגדרת handler ללוגי שגיאות
    error_file_handler = logging.FileHandler(error_log_filename)
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)

    # הגדרת handler לקונסול
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # הגדרת הlogger הראשי
    logger = logging.getLogger('ShoppingBot')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)
    logger.addHandler(console_handler)

    return logger
