import os
from firebase_admin import credentials, firestore, initialize_app, auth
import requests

# עדכן את הנתיב לקובץ החדש
firebase_sdk_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'shop-449e4-firebase-adminsdk-p5bza-42321375db.json')

# בדיקת קיום הקובץ
if not os.path.exists(firebase_sdk_path):
    raise FileNotFoundError(f"Firebase Admin SDK file not found at: {firebase_sdk_path}")

try:
    cred = credentials.Certificate(firebase_sdk_path)
    initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    raise

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
    try:
        website_user_id = get_website_user_id(telegram_id)
        print(f"Getting shopping list for Telegram ID: {telegram_id}, Website User ID: {website_user_id}")
        if website_user_id:
            items = db.collection('shoppingLists').where('userId', '==', website_user_id).stream()
            item_list = [{**item.to_dict(), 'id': item.id} for item in items]
            print(f"Retrieved {len(item_list)} items for user {website_user_id}")
            print(f"Items: {item_list}")
            return item_list
        else:
            print(f"No linked website user found for Telegram ID: {telegram_id}")
            return None
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
