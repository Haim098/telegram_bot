import os
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, auth
import requests
import logging
from functools import wraps
import threading
import _thread
import json

# הגדרת logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Current working directory: {os.getcwd()}")

def load_firebase_config():
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        firebase_sdk_path = os.path.join(BASE_DIR, 'config', 'firebase-config.json')
        
        logger.debug(f"Base directory: {BASE_DIR}")
        logger.debug(f"Looking for Firebase SDK file at: {firebase_sdk_path}")
        
        with open(firebase_sdk_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
            # טיפול במפתח הפרטי - הפעם בצורה פשוטה יותר
            if 'private_key' in config_data:
                # רק מחליף \n במעברי שורה אמיתיים
                config_data['private_key'] = config_data['private_key'].replace('\\n', '\n')
            
            # הדפסת תוכן הקובץ לבדיקה (ללא ה-private key)
            safe_config = config_data.copy()
            if 'private_key' in safe_config:
                safe_config['private_key'] = 'REDACTED'
            logger.debug(f"Loaded config: {json.dumps(safe_config, indent=2)}")
            
            # הדפסת מידע נוסף לדיבוג
            logger.debug(f"Private key starts with: {config_data['private_key'][:50]}...")
            logger.debug(f"Private key ends with: ...{config_data['private_key'][-50:]}")
            
        return config_data
            
    except Exception as e:
        logger.error(f"Error loading Firebase config: {e}")
        raise

def initialize_firebase():
    try:
        # קביעת הנתיב לקובץ הconfig עם השם העדכני ביותר
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cred_path = os.path.join(BASE_DIR, 'config', 'shop-449e4-firebase-adminsdk-p5bza-e5bf82b86a.json')
        
        logger.info(f"Initializing Firebase with credentials from: {cred_path}")
        
        # אתחול Firebase עם הקובץ החדש
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        
        # בדיקת חיבור בסיסית
        db = firestore.client()
        test_ref = db.collection('test').document('test')
        test_ref.set({'test': True})
        test_ref.delete()
        
        logger.info("Firebase initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}", exc_info=True)
        return False

# אתחול Firebase בתחילת הריצה
if not firebase_admin._apps:
    if not initialize_firebase():
        raise Exception("Could not initialize Firebase")

# יצירת client
db = firestore.client()

def add_item_to_list(user_id, item, quantity=1, category='כללי', notes=''):
    try:
        website_user_id = get_website_user_id(user_id)
        print(f"Adding item for Telegram ID: {user_id}, Website User ID: {website_user_id}")
        if website_user_id:
            doc_ref = db.collection('shoppingLists').document()
            doc_ref.set({
                'name': item,
                'completed': False,
                'userId': website_user_id,
                'quantity': quantity,
                'notes': notes,
                'category': category,
                'createdAt': firestore.SERVER_TIMESTAMP
            })
            print(f"Item '{item}' added successfully for user {website_user_id}")
            print(f"Verifying item addition: {doc_ref.get().to_dict()}")
            return True
        else:
            print(f"No linked website user found for Telegram ID: {user_id}")
            return False
    except Exception as e:
        print(f"Error adding item: {e}")
        return False

def get_shopping_list(telegram_id):
    if not check_connection():
        print("Firebase connection is not available")
        return None
    try:
        website_user_id = get_website_user_id(telegram_id)
        if not website_user_id:
            return None
            
        # שימוש בשורה אחת ללא המשכיות שורה
        items = (db.collection('shoppingLists')
                .where('userId', '==', website_user_id)
                .limit(100)
                .get())
        
        item_list = []
        for item in items:
            item_data = item.to_dict()
            item_data['id'] = item.id
            item_list.append(item_data)
            
        return item_list
    except Exception as e:
        print(f"Error getting shopping list: {e}")
        return None

def remove_item_from_list(user_id, item_id):
    try:
        website_user_id = get_website_user_id(user_id)
        if website_user_id:
            db.collection('shoppingLists').document(item_id).delete()
            return True
        return False
    except Exception as e:
        print(f"Error removing item: {e}")
        return False

def link_telegram_to_website_user(telegram_id, website_user_id):
    try:
        db.collection('user_links').document(str(telegram_id)).set({
            'website_user_id': website_user_id
        })
        return True
    except Exception as e:
        print(f"Error linking user: {e}")
        return False

def get_website_user_id(telegram_id):
    try:
        doc = db.collection('user_links').document(str(telegram_id)).get()
        if doc.exists:
            return doc.to_dict().get('website_user_id')
        return None
    except Exception as e:
        print(f"Error getting website user ID: {e}")
        return None

def authenticate_user(email, password):
    try:
        firebase_web_api_key = "AIzaSyAtfIrQTp3rc50H-Um7JSOtW1osbH5diYs"
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_web_api_key}",
            data={"email": email, "password": password, "returnSecureToken": True}
        )
        if response.status_code == 200:
            user_data = response.json()
            print(f"המשת אומת בהצלחה: {user_data['localId']}")
            return user_data['localId']
        else:
            print(f"האימות נכשל: {response.text}")
            return None
    except Exception as e:
        print(f"שגיאה באימות המשתמש: {e}")
        return None

def unlink_telegram_from_website_user(telegram_id):
    try:
        doc_ref = db.collection('user_links').document(str(telegram_id))
        if doc_ref.get().exists:
            doc_ref.delete()
            print(f"Unlinked Telegram ID: {telegram_id}")
            return True
        else:
            print(f"No link found for Telegram ID: {telegram_id}")
            return False
    except Exception as e:
        print(f"Error unlinking user: {e}")
        return False

def mark_item_as_done(telegram_id, item_name):
    try:
        website_user_id = get_website_user_id(telegram_id)
        if not website_user_id:
            return False

        items_ref = db.collection('shoppingLists').where('userId', '==', website_user_id)
        docs = items_ref.get()
        
        for doc in docs:
            if item_name.lower() in doc.to_dict()['name'].lower():
                doc.reference.update({'completed': True})
                return True
        
        return False  # אם הפריט לא נמצא
    except Exception as e:
        print(f"Error marking item as done: {e}")
        return False

def check_connection():
    try:
        # בדיקה פשוטה שהחיבור עובד
        test_ref = db.collection('test').document('test')
        test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP}, timeout=5)
        result = test_ref.get(timeout=5)
        test_ref.delete()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [TimeoutError('Function call timed out')]
            def worker():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    result[0] = e
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            if isinstance(result[0], Exception):
                raise result[0]
            return result[0]
        return wrapper
    return decorator

# שימוש בדקורטור על הפונקציות הקריטיות
@timeout(10)
def get_shopping_list(telegram_id):
    if not check_connection():
        print("Firebase connection is not available")
        return None
    try:
        website_user_id = get_website_user_id(telegram_id)
        if not website_user_id:
            return None
            
        # שימוש בשורה אחת ללא המשכיות שורה
        items = (db.collection('shoppingLists')
                .where('userId', '==', website_user_id)
                .limit(100)
                .get())
        
        item_list = []
        for item in items:
            item_data = item.to_dict()
            item_data['id'] = item.id
            item_list.append(item_data)
            
        return item_list
    except Exception as e:
        print(f"Error getting shopping list: {e}")
        return None

def verify_firebase_connection():
    try:
        # בדיקת חיבור בסיסית
        test_ref = db.collection('test').document('test')
        test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
        result = test_ref.get()
        test_ref.delete()
        
        # בדיקת ימות
        auth.get_user('test_uid')  # זה אמור להיכשל, אבל בצורה ספציפית
        
    except auth.UserNotFoundError:
        # זה בסדר - זה אומר שהאמות עובד
        logger.info("Firebase authentication is working")
        return True
    except Exception as e:
        logger.error(f"Firebase connection test failed: {e}")
        return False

# קרא לפונקציה בזמן האתחול
if verify_firebase_connection():
    logger.info("Firebase connection fully verified")
else:
    logger.error("Failed to verify Firebase connection")
