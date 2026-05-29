# ==========================================
# FILE: app.py (डिजिटल पाठशाला - इंटीग्रेटेड vComplete)
# ==========================================
import streamlit as st
import database
from datetime import datetime
import google.generativeai as genai  # 🤖 जेमिनी AI के लिए
import io

# ==========================================
# SECTION 1: पेज सेटिंग, API चाबियाँ और सेशन स्टेट्स
# ==========================================
LOGO_URL = "https://raw.githubusercontent.com/Nitesh-gurukul/gurukul/main/logo.png"
st.set_page_config(
    page_title="Pathshala",          # ब्राउज़र टैब में नाम 'Pathshala' दिखेगा
    page_icon=LOGO_URL,              # यहाँ गिटहब वाला लोगो चमकेगा
    layout="wide"                    # स्क्रीन को फुल चौड़ाई देने के लिए
)

# स्ट्रीमलिट का डिफ़ॉल्ट लोगो, मेनू और फुटर हटाने का CSS
Q# 🛑 पुराने hide_streamlit_style को हटाकर इस नए वाले को पेस्ट करें:

hide_streamlit_style = """
            <style>
            /* 1. ऊपर का 3-डॉट मेनू और पूरा हेडर गायब करने के लिए */
            [data-testid="stHeader"] {visibility: hidden !important; display: none !important;}
            header {visibility: hidden !important; display: none !important;}
            
            /* 2. नीचे का 'Made with Streamlit' फुटर हटाने के लिए */
            footer {visibility: hidden !important; display: none !important;}
            [data-testid="stFooter"] {visibility: hidden !important; display: none !important;}
            
            /* 3. स्ट्रीमलिट की टॉप डेकोरेशन लाइनों को साफ करने के लिए */
            div block-container {padding-top: 2rem !important;}
            .stDecoration {display: none !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 🔑 अपनी चाबियाँ (Keys) यहाँ डालें
GEMINI_API_KEY = "AIzaSyBZaNvUTgiuU_HdTq5D6KpIo03eU55p5_M"  # <-- यहाँ अपनी आज वाली जेमिनी की पेस्ट करें
RAZORPAY_KEY_ID = "YOUR_RAZORPAY_KEY_ID"      # <-- रेज़रपे अकाउंट बनने के बाद यहाँ डालें
RAZORPAY_KEY_SECRET = "YOUR_SECRET_KEY"       # <-- रेज़रपे की सीक्रेट की यहाँ डालें

# जेमिनी AI को कॉन्फ़िगर करना
genai.configure(api_key=GEMINI_API_KEY)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = None

# सार्वभौमिक हेडर और लोगो फ़ंक्शन
def show_universal_header():
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        try:
            st.image("logo.png", width=80)
        except:
            st.markdown("<h3>🏫</h3>", unsafe_allow_html=True)
    with col_title:
        st.markdown("<h1 style='margin-top:10px; color:#1E3A8A;'>Digital Pathshala</h1>", unsafe_allow_html=True)
    st.markdown("---")

# ==========================================
# SECTION 2: सुपर एडमिन का डिब्बा
# ==========================================
def show_admin_dashboard(user_info):
    show_universal_header()
    st.subheader("⚡ सुपर एड敏 कंट्रोल पैनल")
    
    students_list = database.get_all_users_by_role('student')
    teachers_list = database.get_all_users_by_role('teacher')
    
    tab_analytics, tab_teachers, tab_students = st.tabs([
        "📊 भौगोलिक डेटा विश्लेषण (Analytics)", 
        "👨‍🏫 शिक्षक प्रबंधन (Manage Teachers)", 
        "🎓 पंजीकृत छात्र (Students List)"
    ])
    
    with tab_analytics:
        st.markdown("### 📈 छात्र डेटा विश्लेषण")
        if not students_list:
            st.info("ℹ️ अभी विश्लेषण के लिए कोई छात्र पंजीकृत नहीं है।")
        else:
            import pandas as pd
            df = pd.DataFrame(students_list)
            col_metrics1, col_metrics2 = st.columns(2)
            with col_metrics1: st.metric("कुल छात्र", len(df))
            with col_metrics2: st.metric("कुल शिक्षक", len(teachers_list))
            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("🏙️ **शहर के अनुसार छात्रों की संख्या:**")
                st.bar_chart(df['city'].value_counts())
            with col_chart2:
                st.markdown("🏫 **बोर्ड के अनुसार छात्रों की संख्या:**")
                st.bar_chart(df['board'].value_counts())
            st.markdown("---")
            st.markdown("🏫 **स्कूल के अनुसार रैंकिंग लिस्ट:**")
            school_summary = df.groupby(['school', 'city']).size().reset_index(name='एक्टिव छात्र').sort_values(by='एक्टिव छात्र', ascending=False)
            st.dataframe(school_summary, use_container_width=True)

    with tab_teachers:
        st.markdown("### ➕ नए शिक्षक को पंजीकृत करें")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            t_user = st.text_input("शिक्षक का यूज़रनेम:", key="t_user").strip()
            t_name = st.text_input("शिक्षक का पूरा नाम:", key="t_name").strip()
            t_pass = st.text_input("लॉगिन पासवर्ड बनाएं:", type="password", key="t_pass").strip()
        with col_t2:
            t_class = st.selectbox("कक्षा अलॉट करें (Class):", ["Class 9", "Class 10", "Class 11", "Class 12"], key="t_class")
            t_sub = st.text_input("विषय का नाम (e.g. Maths, Physics):", key="t_sub").strip()
            if st.button("💾 शिक्षक को सेव करें", use_container_width=True):
                if t_user and t_name and t_pass and t_sub:
                    success, msg = database.add_teacher(t_user, t_name, t_pass, t_class, t_sub)
                    if success: st.success(msg); st.rerun()
                    else: st.error(msg)
                else: st.error("⚠️ कृपया सभी फील्ड्स को भरें!")
                    
        st.markdown("---")
        for t in teachers_list:
            col_list1, col_list2, col_list3 = st.columns([3, 3, 2])
            with col_list1: st.markdown(f"**नाम:** {t['name']} (`{t['username']}`)")
            with col_list2: st.markdown(f"📚 {t['assigned_class']} | {t['allowed_subjects']}")
            with col_list3:
                if st.button("🗑️ डिलीट", key=f"del_t_{t['username']}", type="primary"):
                    database.delete_user(t['username']); st.success("हटाया गया!"); st.rerun()

    with tab_students:
        st.markdown("### 🎓 पंजीकृत छात्रों का डेटा")
        for s in students_list:
            col_s1, col_s2, col_s3 = st.columns([3, 4, 1])
            with col_s1:
                st.markdown(f"👤 **{s['name']}** (`{s['username']}`)")
                st.caption(f"📞 {s['mobile']}")
            with col_s2: st.markdown(f"🏫 {s['school']} ({s['city']}) | 🎯 {s['board']} | 💳 {s['payment_status']}")
            with col_s3:
                if st.button("🗑️", key=f"del_s_{s['username']}"):
                    database.delete_user(s['username']); st.success("डिलीट हुआ!"); st.rerun()
                
    st.markdown("---")
    if st.button("🔒 लॉगआउट (Logout)", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.user_info = None; st.rerun()

# ==========================================
# SECTION 3: शिक्षक का डिब्बा
# ==========================================
def show_teacher_dashboard(user_info):
    show_universal_header()
    t_class = user_info.get('assigned_class') if user_info.get('assigned_class') else "Class 10"
    t_sub = user_info.get('allowed_subjects') if user_info.get('allowed_subjects') else "Maths"
    
    st.subheader(f"👨‍🏫 शिक्षक पैनल | {t_class} - {t_sub}")
    tab_materials, tab_tests, tab_doubts = st.tabs(["📚 स्टडी मटेरियल", "📝 टेस्ट सेट करें", "📥 छात्र डाउट बॉक्स"])
    
    with tab_materials:
        st.markdown("### 📥 नया स्टडी मटेरियल जोड़ें")
        mat_board = st.selectbox("🎯 किस बोर्ड के लिए है?", ["BSEB (Bihar Board)", "CBSE"], key="mat_board")
        mat_chapter = st.text_input("✍️ चैप्टर का नाम:", key="mat_chap").strip()
        mat_link = st.text_input("📹 यूट्यूब वीडियो लिंक:", key="mat_link").strip()
        if st.button("🚀 मटेरियल लाइव करें", use_container_width=True):
            if mat_chapter:
                database.add_study_material(t_class, t_sub, mat_board, mat_chapter, "Notes.pdf", mat_link)
                st.success("🎉 मटेरियल सफलतापूर्वक लाइव हो गया है!"); st.rerun()
                
    with tab_tests:
        q_board = st.selectbox("🎯 टेस्ट किस बोर्ड के लिए है?", ["BSEB (Bihar Board)", "CBSE"], key="q_board")
        q_test_num = st.number_input("🔢 टेस्ट नंबर:", min_value=1, step=1, key="q_test_num")
        q_text = st.text_area("❓ प्रश्न (Question):")
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            opt_a = st.text_input("A)")
            opt_b = st.text_input("B)")
        with col_opt2:
            opt_c = st.text_input("C)")
            opt_d = st.text_input("D)")
        correct_opt = st.selectbox("✅ सही विकल्प चुनें:", ["A", "B", "C", "D"])
        if st.button("➕ प्रश्न टेस्ट में जोड़ें", use_container_width=True):
            database.add_test_question(t_class, t_sub, q_board, q_test_num, q_text, opt_a, opt_b, opt_c, opt_d, correct_opt)
            st.success("प्रश्न जुड़ गया!"); st.rerun()

    with tab_doubts:
        st.markdown("### 📥 छात्रों के डाउट्स")
        all_doubts = database.get_all_doubts_by_class(t_class)
        for d in all_doubts:
            with st.expander(f"❓ {d['username']} का सवाल — {d['status']}"):
                st.write(d['question_text'])
                if d['status'] == 'Pending':
                    t_ans = st.text_area("✍️ अपना उत्तर लिखें:", key=f"ans_{d['doubt_id']}")
                    if st.button("🚀 उत्तर भेजें", key=f"btn_{d['doubt_id']}"):
                        database.answer_student_doubt(d['doubt_id'], t_ans)
                        st.success("उत्तर भेजा गया!"); st.rerun()
                else: st.success(f"आपका उत्तर: {d['teacher_solution']}")

    st.markdown("---")
    if st.button("🔒 लॉगआउट (Logout)", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.user_info = None; st.rerun()

# ==========================================
# SECTION 4: छात्र का लाइव डायनेमिक डिब्बा
# ==========================================
def show_student_dashboard(user_info):
    show_universal_header()
    s_username = user_info.get('username')
    s_board = user_info.get('board')
    enroll_type = user_info.get('enrollment_type')
    pay_status = user_info.get('payment_status')
    s_class = user_info.get('assigned_class') if user_info.get('assigned_class') else "Class 10"
    
    st.subheader(f"🎓 छात्र डैशबोर्ड | {s_class} | बोर्ड: {s_board}")
    
    # ⏳ 7-दिन का फ्री ट्रायल काउंटर चेकर
    join_date_str = user_info.get('join_date')
    if join_date_str and enroll_type == 'Only Study' and pay_status == 'Trial':
        join_date = datetime.strptime(join_date_str, '%Y-%m-%d %H:%M:%S')
        days_passed = (datetime.now() - join_date).days
        if days_passed > 7:
            database.update_user_payment(s_username, 'Expired')
            st.session_state.user_info['payment_status'] = 'Expired'
            st.rerun()

    if enroll_type == 'Only Study':
        if st.session_state.user_info['payment_status'] == 'Expired':
            st.error("⚠️ आपका 7 दिनों का फ्री ट्रायल समाप्त हो गया है!")
            
            # 💳 रेज़रपे पेमेंट इंटीग्रेशन (सिम्युलेटर विद मर्चेंट रेडी गाइड)
            st.info(f"📍 रेज़रपे मर्चेंट आईडी कनेक्टेड: {RAZORPAY_KEY_ID[:8] if RAZORPAY_KEY_ID else 'Not Ready'}...")
            if st.button("💳 रेज़रपे (Razorpay) से सुरक्षित मासिक फीस जमा करें", use_container_width=True):
                database.update_user_payment(s_username, 'Paid')
                st.session_state.user_info['payment_status'] = 'Paid'
                st.success("🎉 रेज़रपे से पेमेंट सफल! आपकी मासिक क्लासेस दोबारा अनलॉक हो गई हैं।")
                st.rerun()
            return

        tab_learn, tab_ask = st.tabs(["📖 ऑनलाइन पाठशाला", "❓ AI डाउट सॉल्वर"])
        
        with tab_learn:
            m_list = database.get_study_materials(s_class, s_board)
            for m in m_list:
                with st.expander(f"📁 {m['chapter_name']} — {m['subject']}"):
                    if m['video_link']: st.video(m['video_link'])
                    st.write(f"📄 पीडीएफ नोट्स: {m['file_path']}")
                    
        with tab_ask:
            st.markdown("### 🤖 असली जेमिनी AI डाउट इंजन")
            d_text = st.text_area("✍️ अपना सवाल यहाँ टाइप करें:", key="doubt_txt_area")
            cam_shot = st.camera_input("📸 या मोबाइल कैमरे से सवाल की लाइव photo खींचें:", key="doubt_cam_input")
            
            if st.button("🚀 तुरंत समाधान (Solution) पाएं", use_container_width=True, key="doubt_sol_btn"):
                if d_text or cam_shot:
                    with st.spinner("🤖 जेमिनी AI सवाल को हल कर रहा है..."):
                        try:
                            # 🔄 बैकअप मॉडल्स - जो पुरानी और नई दोनों लाइब्रेरी पर 100% चलते हैं
                            if cam_shot:
                                model = genai.GenerativeModel('gemini-pro-vision')
                                from PIL import Image
                                import io
                                img = Image.open(io.BytesIO(cam_shot.read()))
                                prompt = f"तुम एक बेहतरीन शिक्षक हो। इस फोटो में दिए गए छात्र के सवाल को हिंदी में स्टेप-बाय-स्टेप सरल भाषा में हल करो। छात्र का अतिरिक्त प्रश्न: {d_text}"
                                response = model.generate_content([prompt, img])
                            else:
                                model = genai.GenerativeModel('gemini-pro')
                                prompt = f"तुम एक बेहतरीन शिक्षक हो। इस सवाल को हिंदी में स्टेप-बाय-स्टेप सरल भाषा में हल करो: {d_text}"
                                response = model.generate_content(prompt)
                                
                            ai_ans = response.text
                            img_data = cam_shot.read() if cam_shot else None
                            database.add_student_doubt(s_username, s_class, d_text, img_data, ai_ans)
                            st.success("🎉 जेमिनी AI ने समाधान तैयार कर दिया है!")
                            st.markdown(ai_ans)
                        except Exception as e:
                            # 🔄 अगर पुराना मॉडल फेल हो तो नए मॉडल (1.5-flash) से आखरी कोशिश
                            try:
                                if cam_shot:
                                    model = genai.GenerativeModel('gemini-1.5-flash')
                                    from PIL import Image
                                    import io
                                    img = Image.open(io.BytesIO(cam_shot.read()))
                                    prompt = f"तुम एक बेहतरीन शिक्षक हो। इस फोटो में दिए गए छात्र के सवाल को हिंदी में स्टेप-बाय-स्टेप सरल भाषा में हल करो। छात्र का अतिरिक्त प्रश्न: {d_text}"
                                    response = model.generate_content([prompt, img])
                                else:
                                    model = genai.GenerativeModel('gemini-1.5-flash')
                                    prompt = f"तुम एक बेहतरीन शिक्षक हो। इस सवाल को हिंदी में स्टेप-बाय-स्टेप सरल भाषा में हल करो: {d_text}"
                                    response = model.generate_content(prompt)
                                
                                ai_ans = response.text
                                img_data = cam_shot.read() if cam_shot else None
                                database.add_student_doubt(s_username, s_class, d_text, img_data, ai_ans)
                                st.success("🎉 जेमिनी AI ने समाधान तैयार कर दिया है!")
                                st.markdown(ai_ans)
                            except Exception as final_err:
                                st.error(f"AI कनेक्शन एरर: कृपया सुनिश्चित करें कि आपकी GEMINI_API_KEY बिल्कुल सही है। तकनीकी एरर: {final_err}")
                else: 
                    st.error("⚠️ कृपया कुछ लिखें या फोटो खींचें!")
                    
    elif enroll_type == 'Only Test':
        t_num = st.number_input("🔍 टेस्ट नंबर:", min_value=1, step=1)
        u_tests = user_info.get('unlocked_tests') if user_info.get('unlocked_tests') else 1
        
        # 💳 ₹15 पर-टेस्ट पे-एज़-यू-गो गेटवे लॉजिक
        if t_num > u_tests:
            st.error(f"🔒 टेस्ट नंबर {t_num} अभी लॉक है!")
            if st.button(f"💳 ₹15 का ऑनलाइन भुगतान (Razorpay) करके टेस्ट {t_num} अनलॉक करें", use_container_width=True):
                database.increment_unlocked_tests(s_username)
                st.session_state.user_info['unlocked_tests'] += 1
                st.success(f"🎉 रेज़रपे पेमेंट सफल! टेस्ट नंबर {t_num} अनलॉक हो गया है।")
                st.rerun()
            return
            
        test_qs = database.get_questions_by_test(s_class, s_board, t_num)
        if not test_qs: st.warning("प्रश्न अभी अपलोड नहीं हैं।")
        else:
            student_answers = {}
            with st.form(f"quiz_{t_num}"):
                for idx, q in enumerate(test_qs):
                    st.markdown(f"**Q{idx+1}. {q['question']}**")
                    ans = st.radio("विकल्प:", [f"A) {q['option_a']}", f"B) {q['option_b']}", f"C) {q['option_c']}", f"D) {q['option_d']}"], key=f"q_{q['question_id']}")
                    student_answers[q['question_id']] = ans[0]
                if st.form_submit_button("🏁 टेस्ट सबमिट करें"):
                    score = sum(1 for q in test_qs if student_answers[q['question_id']] == q['correct_option'])
                    st.balloons(); st.markdown(f"### 📊 आपका रिजल्ट: `{score} / {len(test_qs)}` अंक")

    st.markdown("---")
    if st.button("🔒 लॉगआउट (Logout)", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.user_info = None; st.rerun()

# ==========================================
# SECTION 5: बाएँ नियम और दाएँ लॉगिन/साइन-अप का लेआउट
# ==========================================
def show_login_and_signup():
    show_universal_header()
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("### 📋 डिजिटल पाठशाला के नियम एवं स्टडी प्लान")
        st.markdown("""
        <div style='background-color:#F0F4F8; padding:20px; border-radius:10px; border-left:6px solid #1E3A8A;'>
            <h4 style='color:#1E3A8A; margin-top:0;'>📚 Only Study (केवल पढ़ाई) प्लान:</h4>
            <ul>
                <li>✨ नए छात्रों को <b>7 दिन का फ्री ट्रायल क्लास</b> मिलेगा।</li>
                <li>📹 विषयवार प्रीमियम वीडियो लेक्चर्स और पीडीएफ नोट्स।</li>
                <li>🎁 इस प्लान वाले छात्रों को <b>हर महीने 1 ऑनलाइन मॉक टेस्ट बिल्कुल फ्री</b> मिलेगा।</li>
                <li>💳 ट्रायल के बाद आगे जारी रखने के लिए <b>मासिक (Monthly) फीस</b> देय होगी।</li>
            </ul>
        </div><br>
        <div style='background-color:#FFF3CD; padding:20px; border-radius:10px; border-left:6px solid #FFA000;'>
            <h4 style='color:#856404; margin-top:0;'>📝 Only Test (केवल ऑनलाइन टेस्ट) प्लान:</h4>
            <ul>
                <li>🥇 सभी छात्रों के लिए <b>पहला मॉक टेस्ट बिल्कुल फ्री (Same Test)</b> रहेगा।</li>
                <li>⏱️ लाइव काउंटडाउन टाइमर और ऑटो-सबमिट की सुविधा।</li>
                <li>💰 पहला फ्री टेस्ट देने के बाद, अगले हर टेस्ट के लिए मात्र <b>₹15 का ऑनलाइन भुगतान</b> करना होगा।</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        choice = st.tabs(["🔒 पोर्टल में लॉगिन करें", "📝 नया छात्र रजिस्ट्रेशन", "🔄 पासवर्ड रीसेट"])
        with choice[0]:
            login_user = st.text_input("यूज़रनेम", key="l_user").strip()
            login_pass = st.text_input("पासवर्ड", type="password", key="l_pass").strip()
            if st.button("🚀 प्रवेश करें", use_container_width=True):
                user_data = database.get_user_by_username(login_user)
                if user_data and user_data['password'] == login_pass:
                    st.session_state.logged_in = True; st.session_state.user_info = user_data; st.rerun()
                else: st.error("❌ गलत विवरण!")
                    
        with choice[1]:
            reg_user = st.text_input("एक यूनिक यूज़रनेम बनाएं:", key="r_user").strip()
            reg_name = st.text_input("अपना पूरा नाम लिखें:", key="r_name").strip()
            reg_pass = st.text_input("लॉगिन पासवर्ड सेट करें:", type="password", key="r_pass").strip()
            reg_mob = st.text_input("अपना मोबाइल नंबर डालें:", key="r_mob").strip()
            reg_city = st.text_input("अपना शहर (City):", key="r_city").strip()
            reg_school = st.text_input("अपने स्कूल का नाम (School):", key="r_school").strip()
            reg_board = st.radio("🎯 अपना बोर्ड चुनें:", ["BSEB (Bihar Board)", "CBSE"], key="r_board")
            reg_plan = st.radio("🎯 अपना मुख्य कोर्स चुनें:", ["Only Study (वीडियो + नोट्स)", "Only Test (ऑनलाइन टेस्ट सीरीज)"], key="r_plan")
            
            if st.button("💳 सुरक्षित भुगतान करें और रजिस्टर करें", use_container_width=True):
                if reg_user and reg_name and reg_pass:
                    plan_short = "Only Study" if "Only Study" in reg_plan else "Only Test"
                    success, msg = database.add_student_auto(reg_user, reg_name, reg_pass, reg_mob, plan_short, reg_city, reg_school, reg_board)
                    if success: st.success("🎉 रेज़रपे भुगतान सफल! कृपया लॉगिन करें।")
                    else: st.error(msg)
        # 3. पासवर्ड रीसेट टैब (नया फीचर)
        with choice[2]:
            st.subheader("🔄 पासवर्ड रीसेट / बदलें")
            st.write("अपना यूज़रनेम और मोबाइल नंबर डालकर नया पासवर्ड सेट करें।")
            
            forgot_user = st.text_input("अपना यूज़रनेम डालें:", key="f_user").strip()
            forgot_mob = st.text_input("रजिस्टर्ड मोबाइल नंबर:", key="f_mob").strip()
            new_pass = st.text_input("नया मजबूत पासवर्ड बनाएं:", type="password", key="f_pass").strip()
            
            if st.button("🔐 पासवर्ड अपडेट करें", use_container_width=True, key="f_btn"):
                if forgot_user and forgot_mob and new_pass:
                    import sqlite3
                    conn = sqlite3.connect('database.db')
                    c = conn.cursor()
                    
                    # यूज़रनेम और मोबाइल नंबर का मिलान
                    c.execute("SELECT * FROM users WHERE username = ? AND mobile = ?", (forgot_user, forgot_mob))
                    if c.fetchone():
                        c.execute("UPDATE users SET password = ? WHERE username = ?", (new_pass, forgot_user))
                        conn.commit()
                        st.success("🎉 आपका पासवर्ड सफलतापूर्वक बदल दिया गया है! अब लॉगिन टैब में जाकर ट्राई करें।")
                    else:
                        st.error("❌ गलत विवरण! यूज़रनेम या मोबाइल नंबर मैच नहीं कर रहा है।")
                    conn.close()
                else:
                    st.error("⚠️ कृपया तीनों बॉक्स को पूरा भरें!")

# ==========================================
# SECTION 6: मुख्य ट्रैफिक कंट्रोलर
# ==========================================
if st.session_state.logged_in:
    u_info = st.session_state.user_info
    role = str(u_info.get('role')).lower()
    if role == 'admin': show_admin_dashboard(u_info)
    elif role == 'teacher': show_teacher_dashboard(u_info)
    else: show_student_dashboard(u_info)
else: show_login_and_signup()
