import os
import json
from firebase_admin import credentials, firestore, initialize_app, auth
import requests

# הגדרת ה-credentials ישירות כ-dictionary
FIREBASE_ADMIN_SDK = {
    "type": "service_account",
    "project_id": "shop-449e4",
    "private_key_id": "71f4c1f6f22b48c523ce808d99deb124dc7febff",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCMuxapGRtZqfBi\nqU02azt0nzdSBu5x6WUqVJ9WCmNCe5l6fYWvDruatLuKG3i6ODehZJsbpHP/HNTX\n5ZFrC6zbuXvJuF52lheURvizVqtfmruwFm8fJl4JGxtakDMBoJKWVBv4cLRKuQMm\nTsQ4s3vPzGjGhC6XNdsV9UCL1fmHPsxLaDqw+Mozud9uz808ACZ7AYt90qHxdrDh\nbOFA6FQvcd0wzDQPtArwDr2jdq7qv7QnD5KQd/Ex9O7X9ZCLkMTdMG0Vln9qyso1\nG3gx3F/kKpu/nn7P5aMlSBhKuu73PDW/7iPTEn1mVQDLwNh/92j2r7SiUMJ/ovWk\nZB5m0qZdAgMBAAECggEAFM9Zg3nF9JVPiZdVZpWmvhEJIiUKP2fu4LqQsS1qDhuu\nz1EeYouALFlLXhm/2XGUsFXrJcRErtW5l49H2JdqYTdlWafcuBZruC5iekp3nvSH\nintWxTlsMFaEzfiCwlvXMUmQtUUdM+t1zsVY+LV5unmUiL5lEVESa4XPnJ3wfxIP\nCtPxdcSg19VS+udR5bT19jOcA8dkCgl4fQVHpOr1wPTx51lEkHEHj6lXUZCM54mU\nyUmqx9qO0ai07WEYj2S/Xux/eDzBYz79uv/KzvD5kQCZ7pXA6kxaysd3wx6l/Hff\no7/4cod5qi+l+/eyvdUhFTbjavft6qJ57UYRRt6CoQKBgQC+5fJwoFE8u9SRUbcx\nnHbxrJnfo6sszSWnxNZidDSvHWmEKIFfNZucuB+zXyX33AEvW88DXoRlAa5lTW8a\nS1Dm8oEg+Mg06mjhFeknh0yjYHVaMNcojHwbTBptO6Cctb67q36Lm3i4HzVJMlEX\n8i66HjBnrWmtVuwsedYNU05CBQKBgQC8uVvJwXTKc4hZ6mv7noJtEZEBzOirwmeH\nQ0R0i32Nj+n/yl45KYNxWAFz6HFn8EX/yqH0TYVfwC1tJDAimqoKQHz9h/h82dFj\nTB3mgZ86tKBjk7NM25bVCHupP0Z1yFlPZq4XG5M22axMzv2dfEX6QUqVXg5/rlEs\njQItlMBKeQKBgQC9o8+ppQmu7OVpi6USit36jb261mvJMO8UcE2NNuXThMN6v4Zt\n3+J72MndNkuQpCUlN+456Z5afUYTas5Rb7qqAwTWjW7OaoPP/yVE2HsA3mUWOOi1\nZoIv1/V0yERxCXe2FdK7u7I8LvyPf4Xh5PwYdr8db79IrM4oDMzhJf3bRQKBgHkT\nPeThHQlpN3fgIijKV4ibtXj/OeI/lWW87SUL/J+eTZRSA0MO9An6WOxAmskA6Bej\nq2VtenykcUBM8CizKxXqq4WH/w4yO9hFlAU28a2bBi78KhLL6ieACr3ZH14fC9UZ\n3eRrR3XwDk80mJa5jLdxveS38/tMHT3EtToC7Z6ZAoGBAL7Wf1Bk7MpHyp05KYjs\nz+TaPtML7JvOW7SJvT3l1m+p4iMdFMdOs/e5PnAEqRBzV4TIxHw4HDfXECMzls9i\n7Jpbydv7S4OfVGIR24wN+OBDvHgguUB79auxHiABm3UVhoG/zYTEDmOtldpB+FGZ\ng8XyL/NzMFGmngXLTVO1Y57L\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-p5bza@shop-449e4.iam.gserviceaccount.com",
    "client_id": "110062122686906541008",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-p5bza%40shop-449e4.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# אתחול Firebase עם ה-credentials
cred = credentials.Certificate(FIREBASE_ADMIN_SDK)
initialize_app(cred)

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
        if website_user_id:
            items = db.collection('shoppingLists').where('userId', '==', website_user_id).stream()
            return [{**item.to_dict(), 'id': item.id} for item in items]
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
            print(f"המשתמש אומת בהצלחה: {user_data['localId']}")
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
        return False
    except Exception as e:
        print(f"Error marking item as done: {e}")
        return False