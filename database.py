import sqlite3
import pandas as pd
from datetime import datetime

def get_connection():
    return sqlite3.connect("gurukul.db", check_same_thread=False)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table (छात्र और टीचर दोनों के लिए)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,          
            assigned_class TEXT,         
            allowed_subjects TEXT,       
            status TEXT DEFAULT 'pending', 
            mobile TEXT,                  
            board TEXT,                  
            school TEXT,
	    join_date TEXT                 
        )
    ''')
    
    # 2. Materials Table (स्टडी मटेरियल के लिए)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            topic_title TEXT NOT NULL,
            pdf_name TEXT,
            pdf_data BLOB,              
            video_url TEXT,
            uploaded_by TEXT DEFAULT 'admin'
        )
    ''')
    
    # 3. Portal Info Table (नियम और स्टडी प्लान)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portal_info 
        (id INTEGER PRIMARY KEY, rules TEXT, planning TEXT)
    ''')
    
    # 4. Notices Table (नोटिस बोर्ड)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portal_notices 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, title TEXT, link TEXT, date TEXT)
    ''')
    
    # 5. Activity Logs Table (एनालिटिक्स और ट्रैफिक ट्रैकिंग)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            city TEXT,
            school TEXT,                 
            login_date TEXT,
            login_month TEXT
        )
    ''')
    
    # 🎯 डाउट्स टेबल का बिल्कुल सही और नया स्ट्रक्चर
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doubts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT,
            student_name TEXT,
            student_class TEXT,
            doubt_text TEXT,
            reply_text TEXT,
            replied_by TEXT,
            date_asked TEXT,
            img_name TEXT,       -- ✅ यह नया कॉलम होना जरूरी है
            img_data BLOB        -- ✅ यह नया कॉलम होना जरूरी है
        )
    ''')
    
    # डिफ़ॉल्ट सुपर एडमिन सेटअप
    cursor.execute("SELECT * FROM users WHERE role = 'super_admin'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, password, name, role, status, mobile, school, board)
            VALUES ('admin', 'admin123', 'Main Owner', 'super_admin', 'active', '9999999999', 'Admin HQ', 'All')
        ''')
        
    if cursor.execute("SELECT COUNT(*) FROM portal_info").fetchone()[0] == 0:
        cursor.execute("INSERT INTO portal_info (id, rules, planning) VALUES (1, 'नियमित क्लास में आएं।', 'नया स्टडी प्लान लाइव है।')")
    
    conn.commit()
    conn.close()

def add_user(username, name, password, role='student', student_class='', mobile='', subject='', board='', school=''):
    try:
        conn = get_connection()
        c = conn.cursor()
        # 📅 आज की तारीख (जैसे 24-May-2026)
        today_str = datetime.today().strftime('%d-%b-%Y') 
        
        # 🔍 यहाँ पूरे 11 कॉलम और 11 '?' एकदम परफेक्ट सेट हैं
        c.execute("""INSERT INTO users (username, name, password, role, assigned_class, allowed_subjects, status, mobile, board, school, join_date) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                  (username, name, password, role, student_class, subject, 'pending', mobile, board, school, today_str))
        conn.commit()
        conn.close()
        return True, "सफलतापूर्वक जोड़ा गया!"
    except Exception as e:
        return False, f"त्रुटि: {str(e)}"

def get_user_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT username, name, password, role, assigned_class, allowed_subjects, status, mobile, board, school FROM users WHERE username = ?", (username,))
        return c.fetchone()
    except:
        return None
    finally:
        conn.close()

def get_all_users_by_role(role_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, role, assigned_class, allowed_subjects, status, mobile, board, school FROM users WHERE role = ?", (role_name,))
    users = cursor.fetchall()
    conn.close()
    return users

def update_user_status(username, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE username = ?", (new_status, username))
    conn.commit()
    conn.close()

def delete_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def reset_user_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

def add_material(class_name, subject_name, topic_title, pdf_name=None, pdf_data=None, video_url=None, uploaded_by='admin'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO materials (class_name, subject_name, topic_title, pdf_name, pdf_data, video_url, uploaded_by)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', (class_name, subject_name, topic_title, pdf_name, pdf_data, video_url, uploaded_by))
    conn.commit()
    conn.close()

def get_materials_by_class_subject(class_name, subject_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, topic_title, pdf_name, pdf_data, video_url, uploaded_by FROM materials WHERE class_name = ? AND subject_name = ?', (class_name, subject_name))
    res = cursor.fetchall()
    conn.close()
    return res

def delete_material(material_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
    conn.commit()
    conn.close()

def get_portal_info():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT rules, planning FROM portal_info WHERE id=1")
    data = c.fetchone()
    conn.close()
    return data if data else ("नियम उपलब्ध नहीं हैं", "प्लानिंग उपलब्ध नहीं है")

def update_portal_info(rules, planning):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE portal_info SET rules=?, planning=? WHERE id=1", (rules, planning))
    conn.commit()
    conn.close()

def get_all_notices():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, type, title, link, date FROM portal_notices ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

def add_portal_notice(ntype, title, link, date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO portal_notices (type, title, link, date) VALUES (?, ?, ?, ?)", (ntype, title, link, date))
    conn.commit()
    conn.close()

def add_doubt(student_username, student_name, student_class, doubt_text, img_name=None, img_data=None):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.today().strftime('%d-%b-%Y')
    cursor.execute("""INSERT INTO doubts (student_username, student_name, student_class, doubt_text, date_asked, img_name, img_data) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)""",
                   (student_username, student_name, student_class, doubt_text, today, img_name, img_data))
    conn.commit()
    conn.close()

def get_doubts_by_class(class_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, student_name, student_class, doubt_text, reply_text, img_name, img_data FROM doubts WHERE student_class = ?", (class_name,))
    res = cursor.fetchall()
    conn.close()
    return res

def get_doubts_by_student(student_username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, doubt_text, reply_text, replied_by, img_name, img_data FROM doubts WHERE student_username = ?", (student_username,))
    res = cursor.fetchall()
    conn.close()
    return res

def reply_to_doubt(doubt_id, reply_text, replied_by):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE doubts SET reply_text = ?, replied_by = ? WHERE id = ?", (reply_text, replied_by, doubt_id))
    conn.commit()
    conn.close()

def log_user_activity(username, city='Patna', school='Not Specified'):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.today().strftime('%Y-%m-%d')
    current_month = datetime.today().strftime('%B-%Y')
    cursor.execute("INSERT INTO activity_logs (username, city, school, login_date, login_month) VALUES (?, ?, ?, ?, ?)",
                   (username, city, school, today, current_month))
    conn.commit()
    conn.close()

def get_analytics_data():
    conn = get_connection()
    df_city = pd.read_sql_query("SELECT city, COUNT(*) as active_users FROM activity_logs WHERE city != '' GROUP BY city ORDER BY active_users DESC", conn)
    df_school = pd.read_sql_query("SELECT school, COUNT(*) as student_count FROM activity_logs WHERE school != '' GROUP BY school ORDER BY student_count DESC", conn)
    df_month = pd.read_sql_query("SELECT login_month, COUNT(*) as visits FROM activity_logs GROUP BY login_month", conn)
    df_daily = pd.read_sql_query("SELECT login_date, COUNT(*) as daily_visits FROM activity_logs GROUP BY login_date ORDER BY login_date DESC LIMIT 7", conn)
    conn.close()
    return df_city, df_school, df_month, df_daily

create_tables()
