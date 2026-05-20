import streamlit as st
import auth
import database

# 1. Sabse upar Browser Tab ka naam badlein
st.set_page_config(page_title="Gurukul Digital", layout="centered")

# app.py me sabse upar yeh code jodein

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 🎯 ऐप के फ्रंट पेज पर आपका नया लोगो दिखाने के लिए:

# आपके गिटहब से लोगो का डायरेक्ट लिंक
logo_url = "https://raw.githubusercontent.com/Nitesh-gurukul/gurukul/main/logo.png"

# लोगो को स्क्रीन पर दिखाने के लिए (width आप अपने हिसाब से 100, 150 या 200 कर सकते हैं)
st.image(logo_url, width=180)

# 2. Main Screen ki badi Heading ko badlein
st.title("📚 Gurukul Digital (Class 7-10)")
st.subheader("घर बैठे सुरक्षित और आसान पढ़ाई")

# सेशन स्टेट्स ट्रैकिंग
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# --- लॉगिन और साइनअप स्क्रीन ---
if not st.session_state.logged_in:
    choice = st.radio("विकल्प चुनें:", ["लॉगिन (Login)", "नया रजिस्ट्रेशन (Sign Up)"])
    
    if choice == "लॉगिन (Login)":
        st.write("### अपने अकाउंट में लॉगिन करें")
        st.caption("ℹ️ यदि आप पासवर्ड भूल गए हैं, तो रीसेट कराने के लिए एडमिन से संपर्क करें।")
        username = st.text_input("यूजरनेम (Username)", key="log_user")
        password = st.text_input("पासवर्ड (Password)", type="password", key="log_pass")
        
        if st.button("Login", key="log_btn"):
            user, message = auth.login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_info = user
                st.success(message)
                st.rerun()
            else:
                st.error(message)
                
    elif choice == "नया रजिस्ट्रेशन (Sign Up)":
        st.write("### नया छात्र अकाउंट बनाएं")
        name = st.text_input("आपका पूरा नाम (Full Name)", key="reg_name")
        mobile = st.text_input("मोबाइल / व्हाट्सऐप नंबर (10 अंक)", max_chars=10, key="reg_mob")
        username = st.text_input("एक यूनिक यूजरनेम चुनें", key="reg_user")
        password = st.text_input("एक मजबूत पासवर्ड", type="password", key="reg_pass")
        student_class = st.selectbox("अपनी कक्षा चुनें", ["Class 7", "Class 8", "Class 9", "Class 10"], key="reg_cls")
        
        if st.button("Register", key="reg_btn"):
            if name and mobile and username and password:
                success, message = auth.register_user(username, password, name, 'student', student_class, "", mobile)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("कृपया सभी फील्ड्स को भरें!")

else:
    # --- लॉगिन होने के बाद का डैशबोर्ड ---
    user_info = st.session_state.user_info
    st.sidebar.image(logo_url, use_container_width=True)

    st.sidebar.write(f"👋 नमस्ते, **{user_info['name']}**")
    st.sidebar.write(f"रोल: `{user_info['role'].upper()}`")
    
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.rerun()
        
    # ==========================================
    # 1. SUPER ADMIN CONTROL PANEL
    # ==========================================
    if user_info['role'] == 'super_admin':
        st.write("## 👑 Super Admin Control Panel")
        
        tab1, tab2 = st.tabs(["👥 यूजर मैनेजमेंट (Students/Admins)", "➕ नया एडमिन जोड़ें"])
        
        with tab1:
            st.write("### सभी रजिस्टर्ड यूजर्स की सूची")
            all_users = database.get_all_users()
            
            if not all_users:
                st.info("अभी तक कोई नया यूजर रजिस्टर नहीं हुआ है।")
            else:
                for row in all_users:
                    u_username, u_name, u_role, u_class, u_subjects, u_status, u_mobile = row
                    
                    with st.container():
                        st.markdown(f"**नाम:** {u_name} | **📞 मोबाइल:** `{u_mobile if u_mobile else 'N/A'}`")
                        st.markdown(f"**यूजरनेम:** `{u_username}` | **रोल:** `{u_role.upper()}`")
                        st.write(f"कक्षा: {u_class} | विषय एक्सेस: {u_subjects if u_subjects else 'None'}")
                        
                        if u_status == 'pending':
                            st.warning(f"स्टेटस: PENDING (लॉगिन बंद है)")
                        elif u_status == 'active':
                            st.success(f"स्टेटस: ACTIVE (लॉगिन चालू है)")
                        elif u_status == 'blocked':
                            st.error(f"स्टेटस: BLOCKED (अकाउंट ब्लॉक है)")
                            
                        col1, col2, col3 = st.columns(3)
                        
                        if u_status == 'pending' or u_status == 'blocked':
                            if col1.button("✅ Approve / Unblock", key=f"app_{u_username}"):
                                database.update_user_status(u_username, 'active')
                                st.success(f"{u_username} एक्टिव हो गया!")
                                st.rerun()
                                
                        if u_status == 'active':
                            if col1.button("🚫 Temporary Block", key=f"blk_{u_username}"):
                                database.update_user_status(u_username, 'blocked')
                                st.error(f"{u_username} ब्लॉक हो गया!")
                                st.rerun()
                                
                        if col2.button("❌ Remove Permanent", key=f"rem_{u_username}"):
                            database.delete_user(u_username)
                            st.error(f"{u_username} डिलीट हो गया!")
                            st.rerun()
                            
                        with st.expander("📝 क्लास और सब्जेक्ट एक्सेस बदलें"):
                            new_class = st.selectbox("क्लास बदलें", ["Class 7", "Class 8", "Class 9", "Class 10"], index=["Class 7", "Class 8", "Class 9", "Class 10"].index(u_class) if u_class else 0, key=f"cls_sel_{u_username}")
                            
                            available_subjects = ["Maths", "Physics", "Chemistry", "Biology", "English", "Social Science"]
                            default_sub = [s.strip() for s in u_subjects.split(",")] if u_subjects else []
                            default_sub = [s for s in default_sub if s in available_subjects]
                            
                            new_subs = st.multiselect("विषय चुनें", available_subjects, default=default_sub, key=f"sub_sel_{u_username}")
                            
                            if st.button("एक्सेस अपडेट करें", key=f"up_acc_{u_username}"):
                                sub_string = ",".join(new_subs)
                                database.update_user_access(u_username, new_class, sub_string)
                                st.success("एक्सेस अपडेट हो गया!")
                                st.rerun()
                                
                        with st.expander("🔑 पासवर्ड रीसेट करें (Reset Password)"):
                            new_pass = st.text_input("नया पासवर्ड डालें", type="password", key=f"pass_{u_username}")
                            if st.button("पासवर्ड बदलें", key=f"btn_pass_{u_username}"):
                                if new_pass:
                                    database.reset_user_password(u_username, new_pass)
                                    st.success(f"🔑 पासवर्ड सफलतापूर्वक बदल दिया गया है!")
                                else:
                                    st.warning("कृपया पासवर्ड टाइप करें!")
                                    
                    st.markdown("---")
                    
        with tab2:
            st.write("### नया एडमिन (शिक्षक) अकाउंट बनाएं")
            adm_name = st.text_input("एडमिन का नाम", key="new_adm_name")
            adm_username = st.text_input("एडमिन यूजरनेम (यूनिक)", key="new_adm_user")
            adm_password = st.text_input("एडमिन पासवर्ड", type="password", key="new_adm_pass")
            
            # app.py के tab2 के अंदर केवल इस हिस्से को अपडेट करें:

            if st.button("Create Admin", key="new_adm_btn"):
                if adm_name and adm_username and adm_password:
                    # यहाँ हमने क्लास की जगह "" और सब्जेक्ट की जगह "" भेजा है ताकि एरर न आए
                    success, message = auth.register_user(adm_username, adm_password, adm_name, 'admin', "", "", "")
                    if success:
                        st.success(f"🎉 Admin {adm_username} सफलतापूर्वक बन गया और एक्टिव है!")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("कृपया सभी फील्ड्स भरें!")

    # ==========================================
    # 2. ADMIN / TEACHER DASHBOARD (मटीरियल अपलोड और डिलीट पैनल)
    # ==========================================
    elif user_info['role'] == 'admin':
        st.write("## 👨‍🏫 Admin / Teacher Dashboard")
        
        tab_upload, tab_view, tab_doubts = st.tabs(["➕ नया मटीरियल अपलोड करें", "📚 अपलोडेड मटीरियल देखें", "🙋‍♂️ छात्रों के डाउट्स (Doubts)"])
        
        with tab_upload:
            st.write("### स्टडी मटीरियल फॉर्म")
            c_class = st.selectbox("किस क्लास के लिए है?", ["Class 7", "Class 8", "Class 9", "Class 10"], key="adm_cls")
            c_sub = st.selectbox("विषय (Subject) चुनें", ["Maths", "Physics", "Chemistry", "Biology", "English", "Social Science"], key="adm_sub")
            c_title = st.text_input("टॉपिक या चैप्टर का नाम", placeholder="जैसे: Chapter 1 - Number System", key="adm_tit")
            
            uploaded_pdf = st.file_uploader("चैप्टर की PDF फाइल अपलोड करें", type=["pdf"], key="adm_pdf")
            c_video = st.text_input("शॉर्ट वीडियो का URL / Link", placeholder="https://youtube.com/shorts/...", key="adm_vid")
            
            if st.button("🚀 मटीरियल ऐप पर लाइव करें", key="adm_pub_btn"):
                if c_title and (uploaded_pdf or c_video):
                    pdf_name, pdf_bytes = None, None
                    if uploaded_pdf is not None:
                        pdf_name = uploaded_pdf.name
                        pdf_bytes = uploaded_pdf.read()
                        
                    database.add_material(c_class, c_sub, c_title, pdf_name, pdf_bytes, c_video)
                    st.success(f"🎉 मटीरियल सफलतापूर्वक लाइव हो गया!")
                    st.rerun()
                else:
                    st.warning("कृपया टॉपिक का नाम और कम से कम एक चीज़ (PDF या Video Link) ज़रूर डालें!")
                    
        with tab_view:
            st.write("### आपके द्वारा अपलोडेड मटीरियल")
            v_class = st.selectbox("क्浪स चुनें", ["Class 7", "Class 8", "Class 9", "Class 10"], key="v_cls")
            v_sub = st.selectbox("विषय चुनें", ["Maths", "Science", "English", "Social Science"], key="v_sub")
            
        # app.py में Teacher Dashboard के 'with tab_view:' ब्लॉक के ठीक नीचे (उसी की सीध में) इसे पेस्ट करें:

        with tab_doubts:
            st.write("### ❓ छात्रों द्वारा पूछे गए सवाल")
            pending_doubts = database.get_pending_doubts()
            
            if not pending_doubts:
                st.success("🎉 सभी डाउट्स सॉल्व हो चुके हैं! कोई पेंडिंग सवाल नहीं है।")
            else:
                for dbt in pending_doubts:
                    d_id, d_st_name, d_text, d_img_name, d_img_bytes = dbt
                    
                    with st.container():
                        st.markdown(f"**छात्र का नाम:** {d_st_name}")
                        if d_text:
                            st.info(f"💬 सवाल: {d_text}")
                        if d_img_bytes:
                            st.image(d_img_bytes, caption=f"📄 अपलोडेड फोटो: {d_img_name}", use_container_width=True)
                            
                        # रिप्लाई देने के लिए इनपुट बॉक्स
                        t_reply = st.text_area("अपना जवाब यहाँ लिखें (Reply):", key=f"rep_txt_{d_id}")
                        if st.button("🚀 जवाब सबमिट करें", key=f"rep_btn_{d_id}"):
                            if t_reply:
                                database.reply_to_doubt(d_id, t_reply)
                                st.success("जवाब सफलता पूर्वक भेज दिया गया है!")
                                st.rerun()
                            else:
                                st.warning("कृपया जवाब टाइप करें!")
                    st.markdown("---")
            materials_list = database.get_materials_by_access(v_class, v_sub)
            if not materials_list:
                st.info(f"फिलहाल कोई मटीरियल अपलोड नहीं है।")
            else:
                for mat in materials_list:
                    m_id, m_title, m_pdf_name, m_pdf_data, m_video = mat
                    with st.expander(f"📖 {m_title}"):
                        if m_pdf_name:
                            st.write(f"📄 फाइल: {m_pdf_name}")
                            st.download_button(label="📥 Download PDF", data=m_pdf_data, file_name=m_pdf_name, mime="application/pdf", key=f"dl_{m_id}")
                        if m_video:
                            st.write("📺 वीडियो लेक्चर:")
                            try:
                                st.video(m_video)
                            except:
                                st.write(f"🔗 लिंक खोलें: {m_video}")
                        
                        # ---- नया फीचर: गलती से डबल अपलोड हुए मटीरियल को डिलीट करने का बटन ----
                        st.markdown("---")
                        if st.button("🗑️ इस मटीरियल को डिलीट करें", key=f"del_mat_{m_id}"):
                            database.delete_material(m_id)
                            st.error(f"❌ मटीरियल '{m_title}' को डिलीट कर दिया गया है!")
                            st.rerun()

    # ==========================================
    # 3. STUDENT DASHBOARD (छात्र पोर्टल - मटीरियल + डाउट सेक्शन)
    # ==========================================
    elif user_info['role'] == 'student':
        st.write(f"## 🎓 छात्र पोर्टल (Student Dashboard)")
        st.write(f"👋 नमस्ते, **{user_info['name']}** | कक्षा: `{user_info['class']}`")
        
        # यहाँ हमने छात्र के लिए दो अलग टैब बना दिए हैं
        st_tab1, st_tab2 = st.tabs(["📚 पढ़ाई (Study Material)", "🙋‍♂️ मेरा डाउट बॉक्स (Ask Doubt)"])
        
        with st_tab1:
            allowed_subs = [s.strip() for s in user_info['subjects'].split(",") if s.strip()] if user_info['subjects'] else []
            
            if not allowed_subs:
                st.warning("⚠️ आपको अभी तक सुपर एडमिन द्वारा कोई विषय (Subjects) असाइन नहीं किया गया है। कृपया फीस क्लियर करके एडमिन से संपर्क करें।")
            else:
                st.write("### 📚 आपके विषय (Your Assigned Subjects)")
                selected_sub = st.selectbox("पढ़ने के लिए विषय चुनें:", allowed_subs, key="stud_sub_select")
                st.markdown(f"#### 📝 {selected_sub} का स्टडी मटीरियल")
                
                student_materials = database.get_materials_by_access(user_info['class'], selected_sub)
                
                if not student_materials:
                    st.info(f"अभी {user_info['class']} के {selected_sub} विषय में कोई नया मटीरियल अपलोड नहीं हुआ है।")
                else:
                    for mat in student_materials:
                        sm_id, sm_title, sm_pdf_name, sm_pdf_data, sm_video = mat
                        with st.container():
                            st.markdown(f"##### 📖 {sm_title}")
                            col1, col2 = st.columns(2)
                            if sm_pdf_name:
                                with col1:
                                    st.caption(f"📄 नोट्स: {sm_pdf_name}")
                                    st.download_button(label="📥 Download PDF Notes", data=sm_pdf_data, file_name=sm_pdf_name, mime="application/pdf", key=f"st_dl_{sm_id}")
                            if sm_video:
                                with col2:
                                    st.caption("📺 वीडियो लेक्चर देखें:")
                                    try:
                                        st.video(sm_video)
                                    except:
                                        st.write(f"🔗 लिंक: {sm_video}")
                        st.markdown("---")
                        
        with st_tab2:
            st.write("### ❓ अपना सवाल पूछें")
            q_text = st.text_area("अपना सवाल यहाँ टाइप करें:", placeholder="यहाँ अपना प्रश्न लिखें...")
            q_img = st.file_uploader("या अपने सवाल की फोटो अपलोड करें (Optional):", type=["png", "jpg", "jpeg"])
            
            if st.button("🚀 सवाल एडमिन को भेजें", key="ask_dbt_btn"):
                if q_text or q_img:
                    img_name, img_bytes = None, None
                    if q_img is not None:
                        img_name = q_img.name
                        img_bytes = q_img.read()
                        
                    database.add_doubt(user_info['username'], user_info['name'], q_text, img_name, img_bytes)
                    st.success("🎉 आपका सवाल सफलतापूर्वक टीचर के पास भेज दिया गया है!")
                    st.rerun()
                else:
                    st.warning("कृपया कुछ टाइप करें या फोटो अपलोड करें!")
                    
            st.markdown("---")
            st.write("### 📋 आपके पुराने सवाल और उनके जवाब")
            
            my_doubts = database.get_student_doubts(user_info['username'])
            if not my_doubts:
                st.info("आपने अभी तक कोई सवाल नहीं पूछा है।")
            else:
                for d_row in my_doubts:
                    d_txt, d_img_n, d_img_b, d_rep, d_status = d_row
                    with st.expander(f"{'✅ सॉल्व हो गया' if d_status == 'resolved' else '⏳ पेंडिंग है'} - {d_txt[:30] if d_txt else 'फोटो प्रश्न'}"):
                        if d_txt:
                            st.write(f"**आपका सवाल:** {d_txt}")
                        if d_img_b:
                            st.image(d_img_b, caption="आपकी अपलोडेड फोटो", use_container_width=True)
                        
                        st.markdown("---")
                        if d_status == 'resolved':
                            st.success(f"👨‍🏫 **शिक्षक का जवाब:** {d_rep}")
                        else:
                            st.warning("⏳ शिक्षक जल्द ही इस सवाल का जवाब देंगे।")
