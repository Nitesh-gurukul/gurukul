# ==========================================
# FILE: database.py (डिजिटल पाठशाला बैकएंड)
# ==========================================
import sqlite3
from datetime import datetime

def init_db():
    """सभी आवश्यक टेबल्स को सही कॉलम्स के साथ शुरू करना और डिफ़ॉल्ट एडमिन बनाना"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # 1. यूज़र्स टेबल
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        name TEXT,
        password TEXT,
        role TEXT,
        assigned_class TEXT,
        allowed_subjects TEXT,
        status TEXT,
        mobile TEXT,
        join_date TEXT,
        enrollment_type TEXT,
        city TEXT,
        school TEXT,
        board TEXT,
        payment_status TEXT,
        unlocked_tests INTEGER DEFAULT 1
    )""")
    
    # 2. स्टडी मटेरियल टेबल
    c.execute("""CREATE TABLE IF NOT EXISTS materials (
        material_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class TEXT,
        subject TEXT,
        board TEXT,
        chapter_name TEXT,
        file_path TEXT,
        video_link TEXT
    )""")
    
    # 3. ऑनलाइन टेस्ट (Question Bank) टेबल
    c.execute("""CREATE TABLE IF NOT EXISTS tests (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class TEXT,
        subject TEXT,
        board TEXT,
        test_number INTEGER,
        question TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_option TEXT
    )""")
    
    # 4. AI और टीचर डाउट टेबल
    c.execute("""CREATE TABLE IF NOT EXISTS doubts (
        doubt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        student_class TEXT,
        question_text TEXT,
        question_image BLOB,
        ai_solution TEXT,
        teacher_solution TEXT,
        status TEXT DEFAULT 'Pending'
    )""")
    
    # सुरक्षा जांच: अगर कोई कॉलम पुराने डेटाबेस में छूट गया हो तो उसे जोड़ना
    columns_to_add = [
        ("users", "board", "TEXT DEFAULT 'BSEB'"),
        ("users", "city", "TEXT DEFAULT ''"),
        ("users", "school", "TEXT DEFAULT ''"),
        ("users", "payment_status", "TEXT DEFAULT 'Trial'"),
        ("users", "unlocked_tests", "INTEGER DEFAULT 1")
    ]
    for table, col, col_type in columns_to_add:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        except:
            pass
            
    # 👑 [ऑटो-एडमिन क्रिएटर] डिफ़ॉल्ट सुपर एडमिन अकाउंट बनाना (मोबाइल नंबर के साथ)
    try:
        today_str = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        # यहाँ हमने 'mobile' वाले कॉलम की जगह पर आपका नंबर (e.g. '9999999999') सेट करने का स्लॉट बना दिया है
        c.execute("""INSERT OR IGNORE INTO users 
            (username, name, password, role, status, mobile, join_date, enrollment_type, payment_status, city, school, board) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            ('admin', 'Super Admin', 'admin123', 'admin', 'Active', '7903088647', today_str, 'None', 'Paid', 'Patna', 'Digital Pathshala', 'None'))
            
        # सुरक्षा चक्र: अगर एडमिन पहले से बना हुआ है, तो उसका मोबाइल नंबर डेटाबेस में अपडेट करना
        c.execute("UPDATE users SET mobile = '7903088647' WHERE username = 'admin'", ())
        
    except Exception as e:
        print("Admin creation log:", e)
        
    conn.commit()
    conn.close()

def add_student_auto(username, name, password, mobile, enrollment_type, city, school, board):
    """नया छात्र रजिस्ट्रेशन - रेज़रपे के बाद सीधे Active स्टेट में जाएगा"""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        today_str = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        
        # 'Active' स्टेटस और 'Trial' पेमेंट स्टेटस के साथ सेव करना
        c.execute("""INSERT INTO users 
            (username, name, password, role, assigned_class, allowed_subjects, status, mobile, join_date, enrollment_type, city, school, board, payment_status) 
            VALUES (?, ?, ?, 'student', '', '', 'Active', ?, ?, ?, ?, ?, ?, 'Trial')""", 
            (username, name, password, mobile, today_str, enrollment_type, city, school, board))
        
        conn.commit()
        conn.close()
        return True, "सफलतापूर्वक रजिस्टर किया गया!"
    except sqlite3.IntegrityError:
        return False, "यह यूज़रनेम पहले से मौजूद है! कृपया दूसरा चुनें।"
    except Exception as e:
        return False, str(e)

def get_user_by_username(username):
    """लॉगिन के समय डिक्शनरी फॉर्मेट में यूज़र का डेटा निकालना ताकि इंडेक्स की गलती न हो"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row # यह डेटा को इंडेक्स के बजाय नाम से ढूँढने में मदद करता है
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_user_payment(username, new_payment_status):
    """मासिक फीस या ट्रायल एक्सपायरी के लिए स्टेटस अपडेट करना"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET payment_status = ? WHERE username = ?", (new_payment_status, username))
    conn.commit()
    conn.close()

# डेटाबेस टेबल्स को तुरंत शुरू कर देना
init_db()

# ========================================================
# 📂 database.py के सबसे नीचे ये एडमिन फंक्शन्स जोड़ें
# ========================================================

def add_teacher(username, name, password, assigned_class, subject):
    """एडमिन द्वारा नया शिक्षक जोड़ने के लिए"""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        today_str = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("""INSERT INTO users 
            (username, name, password, role, assigned_class, allowed_subjects, status, mobile, join_date, enrollment_type, city, school, board, payment_status) 
            VALUES (?, ?, ?, 'teacher', ?, ?, 'Active', '', ?, 'None', '', '', 'None', 'Paid')""", 
            (username, name, password, assigned_class, subject, today_str))
        conn.commit()
        conn.close()
        return True, "शिक्षक को सफलतापूर्वक जोड़ा गया!"
    except sqlite3.IntegrityError:
        return False, "यह यूज़रनेम पहले से मौजूद है!"
    except Exception as e:
        return False, str(e)

def get_all_users_by_role(role):
    """टीचर्स या स्टूडेंट्स की पूरी लिस्ट निकालने के लिए"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role = ?", (role,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_user(username):
    """किसी यूज़र (टीचर/स्टूडेंट) को डेटाबेस से डिलीट करने के लिए"""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ========================================================
# 📂 database.py के सबसे नीचे ये टीचर फंक्शन्स जोड़ें
# ========================================================

def add_study_material(assigned_class, subject, board, chapter_name, file_path, video_link):
    """टीचर द्वारा सब्जेक्ट और बोर्ड वाइज स्टडी मटेरियल अपलोड करने के लिए"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""INSERT INTO materials (class, subject, board, chapter_name, file_path, video_link)
                 VALUES (?, ?, ?, ?, ?, ?)""", (assigned_class, subject, board, chapter_name, file_path, video_link))
    conn.commit()
    conn.close()
    return True

def get_study_materials(assigned_class, board):
    """छात्र या शिक्षक के लिए मटेरियल लिस्ट निकालने के लिए"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM materials WHERE class = ? AND board = ?", (assigned_class, board))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_material(material_id):
    """गलत या पुराने स्टडी मटेरियल को डिलीट करने के लिए"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM materials WHERE material_id = ?", (material_id,))
    conn.commit()
    conn.close()

def add_test_question(assigned_class, subject, board, test_number, question, option_a, option_b, option_c, option_d, correct_option):
    """टेस्ट पेपर में नया प्रश्न जोड़ने के लिए (Manual, Excel या AI द्वारा)"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""INSERT INTO tests (class, subject, board, test_number, question, option_a, option_b, option_c, option_d, correct_option)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
              (assigned_class, subject, board, test_number, question, option_a, option_b, option_c, option_d, correct_option))
    conn.commit()
    conn.close()
    return True

def get_questions_by_test(assigned_class, board, test_number):
    """किसी विशिष्ट टेस्ट के सभी प्रश्न देखने के लिए"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM tests WHERE class = ? AND board = ? AND test_number = ?", (assigned_class, board, test_number))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_doubts_by_class(student_class):
    """क्लास-वाइज छात्रों के डाउट्स फ़िल्टर करने के लिए"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM doubts WHERE student_class = ? ORDER BY status DESC", (student_class,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def answer_student_doubt(doubt_id, teacher_solution):
    """छात्र के डाउट का उत्तर देने के लिए"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE doubts SET teacher_solution = ?, status = 'Resolved' WHERE doubt_id = ?", (teacher_solution, doubt_id))
    conn.commit()
    conn.close()

# ========================================================
# 📂 database.py के सबसे नीचे ये छात्र फंक्शन्स जोड़ें
# ========================================================

def add_student_doubt(username, student_class, question_text, question_image_bytes, ai_solution_text):
    """छात्र द्वारा डाउट पूछने पर डेटाबेस में सेव करना (साथ में AI जवाब)"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""INSERT INTO doubts (username, student_class, question_text, question_image, ai_solution, teacher_solution, status)
                 VALUES (?, ?, ?, ?, ?, '', 'Pending')""", 
              (username, student_class, question_text, question_image_bytes, ai_solution_text))
    conn.commit()
    conn.close()
    return True

def get_student_doubts(username):
    """छात्र को उसके पुराने सभी डाउट्स और उनके सॉल्यूशंस दिखाने के लिए"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM doubts WHERE username = ? ORDER BY doubt_id DESC", (username,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def increment_unlocked_tests(username):
    """₹15 का पेमेंट सफल होने पर छात्र के अनलॉक टेस्ट की संख्या 1 बढ़ाना"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET unlocked_tests = unlocked_tests + 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def get_all_notices():
    """डेटाबेस से सभी नोटिस लाने के लिए (5-वैल्यू परफेक्ट मैच के साथ)"""
    notices = []
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # आपकी app.py के अनुसार 5 कॉलम (id, ntype, title, link, date) होने चाहिए
        cursor.execute("SELECT id, title, content, date, date FROM notices ORDER BY id DESC")
        raw_data = cursor.fetchall()
        conn.close()
        
        # इसे 5 वैल्यू के फॉर्मेट में सेट करना
        for row in raw_data:
            notices.append((row[0], "सामान्य", row[1], row[2], row[3]))
        return notices
    except Exception:
        # अगर लाइव सर्वर पर टेबल नहीं है, तो यह 5 वैल्यू का डिफ़ॉल्ट नोटिस भेजेगा ताकि ऐप तुरंत खुल जाए
        default_notices = [
            (1, "📢 नोटिस", "👋 डिजिटल पाठशाला में आपका स्वागत है!", "https://github.com", "2026-05-29")
        ]
        return default_notices

def get_portal_info():
    """पोर्टल के नियम और प्लानिंग की जानकारी डिफ़ॉल्ट रूप से दिखाने के लिए"""
    rules = """
    ### 📑 डिजिटल पाठशाला के नियम एवं स्टडी充लना
    
    #### 📦 Only Study (केवल पढ़ाई) प्लान:
    * ⏱️ नए छात्रों को 7 दिन का फ्री ट्रायल क्लास मिलेगा।
    * 🎓 विषयवार प्रीमियम वीडियो लेक्चर्स और पीडीएफ नोट्स।
    * 🎁 इस प्लान वाले छात्रों को हर महीने 1 ऑनलाइन मॉक टेस्ट बिल्कुल फ्री मिलेगा।
    * 💳 ट्रायल के बाद आगे जारी रखने के लिए मासिक (Monthly) फीस देय होगी।
    """
    
    planning = """
    #### 📝 Only Test (केवल ऑनलाइन टेस्ट) प्लान:
    * 🏆 सभी छात्रों के लिए पहला मॉक टेस्ट बिल्कुल फ्री (Same Test) रहेगा।
    * ⏱️ लाइव काउंटडाउन टाइमर और ऑटो सबमिट की सुविधा।
    * 💳 पहला फ्री टेस्ट देने के बाद, अगले हर टेस्ट के लिए मात्र ₹15 का ऑनलाइन भुगतान करना होगा।
    """
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT rules, planning FROM portal_info LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0], result[1]
    except Exception:
        pass
        
    return rules, planning
