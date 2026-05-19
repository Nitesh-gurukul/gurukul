import sqlite3
from database import get_connection

def register_user(username, password, name, role, assigned_class=None, subjects="", mobile=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # स्टूडेंट हमेशा 'pending' रहेगा, नया एडमिन सीधे 'active' हो जाएगा
        status = 'pending' if role == 'student' else 'active'
        
        cursor.execute('''
            INSERT INTO users (username, password, name, role, assigned_class, allowed_subjects, status, mobile)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, name, role, assigned_class, subjects, status, mobile))
        conn.commit()
        return True, "Registration successful! Waiting for Super Admin approval."
    except sqlite3.IntegrityError:
        return False, "Username already exists! कृपया दूसरा यूजरनेम चुनें।"
    finally:
        conn.close()

# auth.py में login_user फंक्शन को इससे बदलें:

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, name, role, status, assigned_class, allowed_subjects 
        FROM users 
        WHERE username = ? AND password = ?
    ''', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        status = user[3]
        if status == 'pending':
            return None, "आपका अकाउंट अभी पेंडिंग है। Super Admin के अप्रूवल का इंतजार करें।"
        elif status == 'blocked':
            return None, "आपका अकाउंट ब्लॉक कर दिया गया है। कृपया सुपर एडमिन से संपर्क करें।"
        else:
            # यहाँ सुधार किया गया है: अगर क्लास या सब्जेक्ट None हैं तो खाली स्ट्रिंग सेट हो जाएगी
            return {
                "username": user[0],
                "name": user[1],
                "role": user[2],
                "class": user[4] if user[4] else "",
                "subjects": user[5] if user[5] else ""
            }, "Login Successful!"
    return None, "गलत यूजरनेम या पासवर्ड!"