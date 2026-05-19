import sqlite3

def get_connection():
    # डेटाबेस से कनेक्ट करने के लिए (फाइल अपने आप बन जाएगी)
    conn = sqlite3.connect("study_app.db", check_same_thread=False)
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table (इसमें मोबाइल नंबर और स्टेटस सब शामिल है)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,          -- 'super_admin', 'admin', 'student'
            assigned_class TEXT,         -- 'Class 7', 'Class 8', आदि
            allowed_subjects TEXT,       -- 'Maths,Science'
            status TEXT DEFAULT 'pending', -- 'pending', 'active', 'blocked'
            mobile TEXT                  -- छात्र/अभिभावक का संपर्क नंबर
        )
    ''')
    
    # 2. Materials Table (कोर्स मटेरियल, PDF बाइट्स और वीडियो लिंक्स के लिए)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            topic_title TEXT NOT NULL,
            pdf_name TEXT,
            pdf_data BLOB,              -- PDF फाइल को डेटाबेस में सेव करने के लिए
            video_url TEXT              -- यूट्यूब या वीडियो लिंक
        )
    ''')
    
    # एक डिफॉल्ट Super Admin बनाना (Username: admin, Password: admin123)
    cursor.execute("SELECT * FROM users WHERE role = 'super_admin'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, password, name, role, status, mobile)
            VALUES ('admin', 'admin123', 'Main Owner', 'super_admin', 'active', '9999999999')
        ''')
    
    # पुरानी टेबल में मोबाइल नंबर कॉलम जोड़ने का सेफ्टी कोड
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

# यूजर मैनेजमेंट फंक्शन्स
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, role, assigned_class, allowed_subjects, status, mobile FROM users WHERE role != 'super_admin'")
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

def update_user_access(username, assigned_class, allowed_subjects):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET assigned_class = ?, allowed_subjects = ? 
        WHERE username = ?
    ''', (assigned_class, allowed_subjects, username))
    conn.commit()
    conn.close()

def reset_user_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

# कोर्स मटेरियल वाले फंक्शन्स
def add_material(class_name, subject_name, topic_title, pdf_name=None, pdf_data=None, video_url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO materials (class_name, subject_name, topic_title, pdf_name, pdf_data, video_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (class_name, subject_name, topic_title, pdf_name, pdf_data, video_url))
    conn.commit()
    conn.close()

def get_materials_by_access(class_name, subject_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, topic_title, pdf_name, pdf_data, video_url 
        FROM materials 
        WHERE class_name = ? AND subject_name = ?
    ''', (class_name, subject_name))
    materials = cursor.fetchall()
    conn.close()
    return materials

# फाइल रन होते ही टेबल्स ऑटो-क्रिएट हो जाएं
create_tables()

# database.py के सबसे नीचे इसे पेस्ट करें:

def delete_material(material_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
    conn.commit()
    conn.close()

# database.py के सबसे नीचे इसे पेस्ट करें:

def create_doubt_table():
    conn = get_connection()
    cursor = conn.cursor()
    # डाउट्स टेबल: इसमें छात्र का नाम, सवाल का टेक्स्ट, फोटो (BLOB) और एडमिन का रिप्लाई सेव होगा
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doubts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT NOT NULL,
            student_name TEXT NOT NULL,
            doubt_text TEXT,
            image_name TEXT,
            image_data BLOB,            -- सवाल की फोटो को सुरक्षित रखने के लिए
            reply_text TEXT,            -- एडमिन का जवाब
            status TEXT DEFAULT 'pending' -- 'pending' या 'resolved'
        )
    ''')
    conn.commit()
    conn.close()

def add_doubt(username, name, doubt_text=None, img_name=None, img_bytes=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO doubts (student_username, student_name, doubt_text, image_name, image_data)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, name, doubt_text, img_name, img_bytes))
    conn.commit()
    conn.close()

def get_pending_doubts():
    conn = get_connection()
    cursor = conn.cursor()
    # शिक्षकों को दिखाने के लिए केवल पेंडिंग डाउट्स लाना
    cursor.execute("SELECT id, student_name, doubt_text, image_name, image_data FROM doubts WHERE status = 'pending'")
    doubts = cursor.fetchall()
    conn.close()
    return doubts

def reply_to_doubt(doubt_id, reply_text):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE doubts SET reply_text = ?, status = 'resolved' WHERE id = ?", (reply_text, doubt_id))
    conn.commit()
    conn.close()

def get_student_doubts(username):
    conn = get_connection()
    cursor = conn.cursor()
    # किसी एक छात्र को उसके खुद के पूछे गए सारे सवाल और उनके जवाब दिखाना
    cursor.execute("SELECT doubt_text, image_name, image_data, reply_text, status FROM doubts WHERE student_username = ?", (username,))
    doubts = cursor.fetchall()
    conn.close()
    return doubts

# पक्का करें कि फाइल लोड होते ही टेबल बन जाए
create_doubt_table()