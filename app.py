import streamlit as st
import database
import pandas as pd
from datetime import datetime

# --- 🌐 वेबसाइट कॉन्फ़िगरेशन ---
st.set_page_config(page_title="Digital Pathshala", page_icon="🎓", layout="wide")

# 📱 1. साइडबार (Sidebar) में लोगो और नाम दिखाने के लिए:
try:
    st.sidebar.image("logo.png", use_container_width=True)
except:
    # अगर किसी वजह से इमेज लोड न हो, तो टेक्स्ट नाम दिखेगा एरर नहीं आएगा
    st.sidebar.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🎓 डिजिटल पाठशाला</h2>", unsafe_allow_html=True)

# --- 🎨 प्रीमियम लुक CSS ---
st.markdown("""
<style>
    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display:none;}
    .main-title { font-size: 38px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 18px; color: #6B7280; text-align: center; margin-bottom: 25px; }
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = None

# ==========================================
# केस 1: लॉगिन के बाद का डैशबोर्ड व्यू
# ==========================================
if st.session_state.logged_in:
    user_info = st.session_state.user_info
    
    col_head, col_logout = st.columns([8, 2])
    col_head.markdown(f"### 🎯 स्वागत है, {user_info['name']} (`{user_info['role'].upper()}`)")
    if col_logout.button("🚪 लॉगआउट (Sign Out)", key="top_log", width='stretch', type="primary"):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.rerun()
            
    st.markdown("---")

    # 🛠️ [A] सुपर एडमिन का मुख्य पैनल
    if user_info['role'].lower() in ['super_admin', 'admin', 'main owner']:
        st.title("🛠️ मास्टर एडमिन डैशबोर्ड")
        
        # 🎯 यहाँ '🔐 सुरक्षा' नाम का नया टैब जोड़ दिया गया है
        t_not, t_stu, t_tea, t_mat, t_lnk, t_ana, t_pwd = st.tabs([
            "📢 नोटिस", "👥 छात्र", "👨‍🏫 टीचर", "📚 नोट्स", "🔗 लिंक्स", "📊 एनालिटिक्स", "🔐 सुरक्षा"
        ])
        
        with t_not:
            st.subheader("📝 मुख्य नियम और स्टडी प्लान")
            curr_rules, curr_plan = database.get_portal_info()
            u_rules = st.text_area("📋 नियम:", value=curr_rules, height=100)
            u_plan = st.text_area("📅 स्टडी प्लान:", value=curr_plan, height=100)
            if st.button("📢 जानकारी लाइव करें"):
                database.update_portal_info(u_rules, u_plan)
                st.success("अपडेट सफल!")
        
        with t_stu:
            st.subheader("👥 छात्रों की सूची")
            s_list = database.get_all_users_by_role('student')
            if s_list:
                for u_data in s_list:
                    username, name, _, a_class, a_subs, status, mobile, s_board, s_school = u_data[:9]
                    st.markdown(f"""
                    <div style='background-color:#f9f9f9; padding:12px; border-radius:8px; border:1px solid #eee; margin-bottom:10px;'>
                        <b>छात्र:</b> {name} (<code>{username}</code>) | 📞 <b>मोबाइल:</b> {mobile} <br>
                        🏫 <b>स्कूल:</b> {s_school} | 🏛️ <b>बोर्ड:</b> {s_board} | 📖 <b>कक्षा:</b> {a_class} | 🎯 <b>विषय:</b> {a_subs} | 🟢 <b>स्टेटस:</b> {status.upper()}
                    </div>
                    """, unsafe_allow_html=True)
                    b1, b2, b3, _ = st.columns([2, 2, 2, 4])
                    if status in ['pending', 'blocked'] and b1.button("✅ Approve", key=f"ap_{username}"):
                        database.update_user_status(username, 'active'); st.rerun()
                    if status == 'active' and b2.button("🚫 Block", key=f"bl_{username}"):
                        database.update_user_status(username, 'blocked'); st.rerun()
                    if b3.button("🗑️ Delete", key=f"dl_{username}"):
                        database.delete_user(username); st.rerun()
            else: st.write("कोई छात्र डेटा नहीं है।")
                
        with t_tea:
            st.subheader("➕ नए शिक्षक को क्लास और विषय अलॉट करें")
            t_user = st.text_input("टीचर यूजरनेम (Unique Code)")
            t_fullname_input = st.text_input("शिक्षक का पूरा नाम")
            t_pass = st.text_input("लॉगिन पासवर्ड", type="password")
            t_class = st.selectbox("टीचर को कौन सी क्लास अलॉट करनी है?", ["Class 9", "Class 10", "Class 11", "Class 12"])
            t_subjects_input = st.multiselect("टीचर के विषय चुनें (एक से ज़्यादा चुन सकते हैं)", ["Physics", "Chemistry", "Biology", "Maths", "Social Science", "English", "Hindi"])
            t_mob = st.text_input("टीचर का मोबाइल नंबर")
            
            if st.button("➕ शिक्षक को रजिस्टर और अलॉट करें", width='stretch'):
                if t_user.strip() and t_fullname_input.strip() and t_pass.strip():
                    if t_subjects_input:
                        subs_str = ", ".join(t_subjects_input)
                        success, msg = database.add_user(username=t_user.strip(), name=t_fullname_input.strip(), password=t_pass.strip(), role='teacher', student_class=t_class, mobile=t_mob.strip(), subject=subs_str)
                        if success:
                            database.update_user_status(t_user.strip(), 'active')
                            st.success(f"🎉 शिक्षक {t_fullname_input} पंजीकृत हो गए!")
                            st.rerun()
                        else: st.error(msg)
                    else: st.error("कृपया कम से कम एक विषय चुनें!")
                else: st.warning("सभी अनिवार्य बॉक्स भरें!")
            
            st.markdown("---")
            st.subheader("👥 वर्तमान में एक्टिव शिक्षकों की सूची")
            tea_list = database.get_all_users_by_role('teacher')
            if tea_list:
                for t_data in tea_list:
                    st.markdown(f"""
                    <div style='background-color:#f0f7ff; padding:12px; border-radius:8px; border:1px solid #d0e3ff; margin-bottom:10px;'>
                        👨‍🏫 <b>शिक्षक:</b> {t_data[1]} (<code>{t_data[0]}</code>) | 📞 <b>मोबाइल:</b> <span style='color:#1E3A8A; font-weight:bold;'>{t_data[6] if t_data[6] else 'N/A'}</span> <br>
                        📖 <b>अलॉटेड कक्षा:</b> {t_data[3] if t_data[3] else 'Not Assigned'} | 🎯 <b>विषय:</b> <span style='color:#b25900; font-weight:bold;'>{t_data[4] if t_data[4] else 'Not Selected'}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🗑️ शिक्षक {t_data[1]} को पद से हटाएं", key=f"del_t_{t_data[0]}"):
                        database.delete_user(t_data[0]); st.rerun()
            else: st.write("अभी तक कोई शिक्षक नहीं जोड़ा गया है।")

        with t_mat:
            st.subheader("📚 पर अपलोड किया गया कुल स्टडी मटेरियल")
            m_cls = st.selectbox("कक्षा चुनें:", ["Class 9", "Class 10", "Class 11", "Class 12"], key="m_c")
            m_sub = st.selectbox("विषय चुनें:", ["Physics", "Chemistry", "Biology", "Maths", "Social Science", "English", "Hindi"], key="m_s")
            mat_data = database.get_materials_by_class_subject(m_cls, m_sub)
            if mat_data:
                for mid, title, p_name, _, v_url, up_by in mat_data:
                    st.write(f"📝 **{title}** (द्वारा अपलोड: `{up_by}`)")
                    if st.button(f"🗑️ डिलीट मटेरियल (ID: {mid})", key=f"del_m_{mid}"):
                        database.delete_material(mid); st.success("डिलीट सफल!"); st.rerun()
            else: st.info("इस क्लास/सब्जेक्ट में अभी कोई नोट्स नहीं हैं।")

        with t_lnk:
            st.subheader("🔗 WhatsApp / लाइव क्लास लिंक सेट करें")
            link_title = st.text_input("लिंक हेडलाइन")
            actual_url = st.text_input("URL लिंक")
            if st.button("🔗 लिंक लाइव करें"):
                database.add_portal_notice("Urgent Link", link_title, actual_url, datetime.today().strftime('%d-%b-%Y'))
                st.success("लिंक लाइव हो गया!")
                
        with t_ana:
            st.subheader("📊 लाइव康复报告")
            df_city, df_school, df_month, df_daily = database.get_analytics_data()
            if not df_city.empty or not df_school.empty:
                c1, c2 = st.columns(2)
                with c1: st.markdown("#### 🏛️ टॉप शहर"); st.bar_chart(df_city.set_index('city'))
                with c2: st.markdown("#### 🏫 टॉप स्कूल"); st.bar_chart(df_school.set_index('school'))
                st.markdown("---"); st.markdown("#### 📈 पिछले 7 दिनों का ट्रैफिक")
                st.dataframe(df_daily, use_container_width=True)
            else: st.info("💡 जैसे ही छात्र लॉगिन करेंगे, ग्राफ लाइव हो जाएगा!")

        # ==========================================
        # 🔐 [नया टैब]: सुपर एडमिन पासवर्ड चेंज सिस्टम
        # ==========================================
        with t_pwd:
            st.subheader("🔐 सुपर एडमिन पासवर्ड बदलें")
            st.write("पोर्टल को सुरक्षित रखने के लिए आप यहाँ से अपना मास्टर पासवर्ड बदल सकते हैं।")
            
            # डेटाबेस से एडमिन की करंट जानकारी उठाना
            admin_data = database.get_user_by_username('admin')
            current_db_password = admin_data[2] if admin_data else "admin123"
            
            old_pwd = st.text_input("वर्तमान (पुराना) पासवर्ड दर्ज करें", type="password", key="adm_old_pwd")
            new_pwd = st.text_input("नया मजबूत पासवर्ड बनाएं", type="password", key="adm_new_pwd")
            confirm_new_pwd = st.text_input("नया पासवर्ड दोबारा टाइप करें", type="password", key="adm_conf_pwd")
            
            if st.button("🔄 मास्टर पासवर्ड अपडेट करें", type="primary", width='stretch'):
                if old_pwd.strip() == current_db_password:
                    if new_pwd.strip() and confirm_new_pwd.strip():
                        if new_pwd.strip() == confirm_new_pwd.strip():
                            # डेटाबेस में पासवर्ड अपडेट करना
                            database.reset_user_password('admin', new_pwd.strip())
                            st.success("🎉 सुपर एडमिन का पासवर्ड सफलतापूर्वक बदल गया है! अगली बार से नए पासवर्ड का उपयोग करें।")
                        else:
                            st.error("❌ दोनों नए पासवर्ड आपस में मैच नहीं कर रहे हैं!")
                    else:
                        st.warning("⚠️ कृपया नया पासवर्ड खाली न छोड़ें!")
                else:
                    st.error("❌ आपका पुराना पासवर्ड गलत है! सुरक्षा कारणों से बदलाव रिजेक्ट किया गया।")

    # 👨‍🏫 [B] शिक्षक (Teacher) पैनल
    elif user_info['role'].lower() == 'teacher':
        st.title(f"👨‍🏫 शिक्षक कंट्रोल पैनल - डिजिटल पाठशाला")
        t_info = database.get_user_by_username(user_info['username'])
        t_class, t_sub_list = t_info[4], t_info[5]
        st.info(f"📋 जिम्मेदारी: {t_class} | विषय: {t_sub_list}")
        
        t_upload, t_doubts = st.tabs(["📚 स्टडी मटेरियल (Upload/Delete)", "❓ छात्रों के डाउट्स (Doubt Solver)"])
        with t_upload:
            available_subs = [s.strip() for s in t_sub_list.split(",")]
            m_subject = st.selectbox("विषय चुनें", available_subs)
            m_title = st.text_input("चैप्टर का नाम")
            m_video = st.text_input("वीडियो लिंक", value="https://")
            m_file = st.file_uploader("PDF नोट्स", type=["pdf"])
            if st.button("🚀 मटेरियल लाइव करें", width='stretch'):
                if m_title:
                    p_name = m_file.name if m_file else None
                    p_data = m_file.read() if m_file else None
                    database.add_material(t_class, m_subject, m_title, p_name, p_data, m_video, uploaded_by=user_info['name'])
                    st.success("🎉 मटेरियल लाइव हो गया!"); st.rerun()
            st.markdown("---")
            for sub in available_subs:
                st.markdown(f"**📚 विषय: {sub}**")
                my_mats = database.get_materials_by_class_subject(t_class, sub)
                if my_mats:
                    for mid, title, p_name, _, _, _ in my_mats:
                        col_m1, col_m2 = st.columns([8, 2])
                        col_m1.write(f"📝 चैप्टर: **{title}** | File: {p_name if p_name else 'No PDF'}")
                        if col_m2.button("🗑️ हटाएँ", key=f"t_del_{mid}"):
                            database.delete_material(mid); st.rerun()

        with t_doubts:
            st.subheader("❓ छात्रों द्वारा पूछे गए सवाल")
            class_doubts = database.get_doubts_by_class(t_class)
            if class_doubts:
                for d_id, s_name, _, d_text, r_text, i_name, i_data in class_doubts:
                    st.markdown(f"<div style='background-color:#fffbf0; padding:10px; border-left:4px solid #f59e0b; margin-bottom:5px;'><b>{s_name}:</b> {d_text}</div>", unsafe_allow_html=True)
                    if i_data:
                        st.image(i_data, caption=f"🖼️ {s_name} द्वारा भेजी गई फोटो", width=400)
                    if r_text: st.success(f"✍️ **जवाब:** {r_text}")
                    else:
                        reply_input = st.text_area("जवाब लिखें...", key=f"rep_in_{d_id}")
                        if st.button("🚀 जवाब भेजें", key=f"rep_btn_{d_id}"):
                            database.reply_to_doubt(d_id, reply_input.strip(), user_info['name'])
                            st.rerun()
            else: st.info("कोई नया सवाल नहीं है।")
            
    # --- 📚 [C] छात्र डैशबोर्ड ---
    # ==========================================
    # 📚 [C] छात्र डैशबोर्ड (7-Days Free Trial & Payment System)
    # ==========================================
    else:
        st.title(f"👋 डिजिटल पाठशाला स्टूडेंट ज़ोन")
        
        # 🔍 डेटाबेस से छात्र की पूरी जानकारी और जुड़ने की तारीख निकालना
        s_info = database.get_user_by_username(user_info['username'])
        s_class, s_sub = user_info['assigned_class'], user_info['allowed_subjects']
        
        # 📅 ट्रायल के दिनों की गणना करना
        join_date_str = s_info[10] if (s_info and len(s_info) > 10 and s_info[10]) else datetime.today().strftime('%d-%b-%Y')
        
        try:
            join_date = datetime.strptime(join_date_str, '%d-%b-%Y')
            today_date = datetime.today()
            days_used = (today_date - join_date).days
        except:
            days_used = 0 # अगर कोई गड़बड़ हो तो डिफ़ॉल्ट 0 दिन
            
        days_left = 7 - days_used

        # 🚨 केस 1: अगर 7 दिन का ट्रायल खत्म हो चुका है (8वां दिन या उससे ज़्यादा)
        if days_left < 0:
            st.error("⚠️ आपका 7 दिनों का फ्री ट्रायल पीरियड समाप्त हो चुका है!")
            
            pay_col1, pay_col2 = st.columns([6, 4])
            
            with pay_col1:
                st.markdown("""
                <div style='background-color:#FEF2F2; padding:20px; border-radius:10px; border-left:6px solid #DC2626;'>
                    <h3 style='color:#991B1B; margin-top:0;'>🔒 पढ़ाई जारी रखने के लिए मासिक फीस जमा करें</h3>
                    <p style='color:#7F1D1D; font-size:16px;'>डिजिटल पाठशाला का उद्देश्य हर घर तक सस्ती और बेहतरीन शिक्षा पहुँचाना है। माता-पिता पर एक बार में बोझ न पड़े, इसलिए हमारी फीस केवल मंथली ली जाती है।</p>
                    <hr style='border-color:#FCA5A5;'>
                    <p style='font-size:18px; color:#DC2626;'><b>💵 मासिक फीस:</b> <span style='font-size:24px; font-weight:bold;'>₹99</span> / प्रति महीना</p>
                    <p style='font-size:15px;'><b>📞 सहायता एवं एक्टिवेशन के लिए:</b> +91 7903088647 (नितेश सर)</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.info("💡 भुगतान (₹99) करने के बाद अपने पेमेंट का स्क्रीनशॉट ऊपर दिए गए नंबर पर WhatsApp करें। एडमिन तुरंत आपकी क्लास अगले 1 महीने के लिए एक्टिव कर देंगे।")
            
            with pay_col2:
                st.markdown("<div style='text-align:center; font-weight:bold;'>📱 किसी भी UPI ऐप से ₹99 स्कैन करें</div>", unsafe_allow_html=True)
                
                # 🎯 ⬇️ यहाँ नीचे 'NITESHSIR@upi' को अपनी असली UPI ID से बदल लीजिएगा ⬇️
                my_real_upi = "9304768496@ybl" 
                
                # 📸 यह कोड अपने आप ₹99 और आपका नाम स्कैन करते ही छात्र के मोबाइल में भर देगा
                qr_link = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa={my_real_upi}&pn=Nitesh%20Sir&am=99&cu=INR"
                st.image(qr_link, caption="📸 डिजिटल पाठशाला मर्चेंट QR कोड", use_container_width=True)
                
        # 🟢 केस 2: अगर छात्र अभी ट्रायल पीरियड के अंदर है (1 से 7 दिन)
        else:
            # ऊपर एक सुंदर सा अलर्ट बार दिखेगा कि कितने दिन बचे हैं
            if days_left == 0:
                st.warning(f"⏰ ध्यान दें: आज आपके फ्री ट्रायल का **आखरी दिन** है! कल से कोर्स लॉक हो जाएगा।")
            else:
                st.success(f"🎉 आपका फ्री ट्रायल एक्टिव है! आपके पास अपनी पढ़ाई के लिए **{days_left} दिन** और बचे हैं।")
                
            col_info1, col_info2 = st.columns(2)
            col_info1.metric(label="आपकी कक्षा", value=s_class)
            col_info2.metric(label="आपके विषय", value=s_sub)
            
            s_study, s_doubts = st.tabs(["📖 आपके क्लास नोट्स & वीडियो", "❓ डाउट कॉर्नर (Ask Teacher)"])
            
            with s_study:
                if s_sub:
                    student_subs = [s.strip() for s in s_sub.split(",")]
                    st.markdown("### 📖 आपके विषयों के अनुसार नोट्स और वीडियो लेक्चर्स")
                    subs_tabs = st.tabs(student_subs)
                    
                    for index, each_sub in enumerate(student_subs):
                        with subs_tabs[index]:
                            st.markdown(f"#### 📚 {each_sub} स्टडी ज़ोन")
                            materials = database.get_materials_by_class_subject(s_class, each_sub)
                            if materials:
                                for mid, title, pdf_name, pdf_data, video_url, up_by in materials:
                                    st.markdown(f"""
                                    <div style='background-color:#f9f9f9; padding:10px; border-left:4px solid #1E3A8A; margin-top:15px; margin-bottom:5px;'>
                                        <b style='font-size:16px; color:#1E3A8A;'>📝 टॉपिक/चैप्टर: {title}</b> <span style='color:#6B7280; font-size:12px;'>(शिक्षक: {up_by})</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    v_col, p_col = st.columns(2)
                                    with v_col:
                                        if video_url and video_url.startswith("http") and ("youtube.com" in video_url or "youtu.be" in video_url):
                                            st.video(video_url)
                                        elif video_url and video_url != "https://": st.warning("⚠️ वीडियो लिंक सही नहीं है।")
                                        else: st.info("📺 वीडियो उपलब्ध नहीं है।")
                                    with p_col:
                                        if pdf_name and pdf_data:
                                            st.success(f"📄 नोट्स: {pdf_name}")
                                            st.download_button(label=f"📥 डाउनलोड: {pdf_name}", data=pdf_data, file_name=pdf_name, mime="application/pdf", key=f"sd_btn_{mid}")
                                        else: st.info("📄 पीडीएफ उपलब्ध नहीं है।")
                            else: st.info(f"✨ इस विषय में कोई मटीरियल नहीं है।")
                else: st.warning("⚠️ कोई विषय अलॉट नहीं हुआ है।")
                
            with s_doubts:
                st.subheader("❓ अपने शिक्षक से कोई भी सवाल पूछें")
                s_doubt_text = st.text_area("अपना सवाल यहाँ विस्तार से लिखिए...", key="st_doubt_box")
                uploaded_img = st.file_uploader("📷 सवाल का फोटो खींचें या इमेज अपलोड करें", type=["png", "jpg", "jpeg"], key="st_doubt_img")
                
                if st.button("🚀 शिक्षक के पास भेजें", key="st_send_doubt_btn", width='stretch'):
                    if s_doubt_text.strip() or uploaded_img:
                        img_name = uploaded_img.name if uploaded_img else None
                        img_data = uploaded_img.read() if uploaded_img else None
                        database.add_doubt(user_info['username'], user_info['name'], s_class, s_doubt_text.strip(), img_name, img_data)
                        st.success("🎉 सवाल और फोटो सफलतापूर्वक भेज दी गई!"); st.rerun()
                    else: st.warning("⚠️ कृपया सवाल लिखें या इमेज अपलोड करें!")
                        
                st.markdown("---")
                st.subheader("📜 आपके द्वारा पहले पूछे गए सवालों के जवाब")
                my_doubts = database.get_doubts_by_student(user_info['username'])
                if my_doubts:
                    for d_id, d_txt, r_txt, r_by, i_name, i_data in my_doubts:
                        st.markdown(f"<div style='background-color:#F3F4F6; padding:12px; border-radius:6px; margin-top:10px;'><b>❓ आपका सवाल:</b> {d_txt}</div>", unsafe_allow_html=True)
                        if i_data:
                            st.image(i_data, caption="🖼️ आपके द्वारा अपलोड की गई इमेज", width=300)
                        if r_txt: st.markdown(f"<div style='background-color:#ECFDF5; padding:12px; border-radius:6px; border-left:4px solid #10B981; margin-top:5px;'><b>✍️ जवाब (द्वारा {r_by}):</b> {r_txt}</div>", unsafe_allow_html=True)
                        else: st.markdown("<div style='background-color:#FFFBEB; padding:12px; border-radius:6px; border-left:4px solid #F59E0B; margin-top:5px;'>⏳ शिक्षक जल्द ही जवाब देंगे।</div>", unsafe_allow_html=True)
                else: st.info("✨ आपने अभी तक कोई सवाल नहीं पूछा है।")
                
# ==========================================
# केस 2: मुख्य वेबसाइट होमपेज (लॉगिन/रजिस्ट्रेशन)
# ==========================================
else:
    st.markdown("<div class='main-title'>🎓 DIGITAL PATHSHALA</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>बिहार का सबसे आधुनिक ऑनलाइन लर्निंग वेब पोर्टल</div>", unsafe_allow_html=True)
    
    left_content, right_login = st.columns([7, 3])
    with left_content:
        rules, planning = database.get_portal_info()
        t1, t2 = st.tabs(["📋 नियम", "📅 स्टडी प्लान"])
        with t1: st.markdown(rules)
        with t2: st.markdown(planning)
        st.markdown("---"); st.subheader("📢 लेटेस्ट अपडेट्स")
        raw_notices = database.get_all_notices()
        table_data = []
        for nid, ntype, title, link, date in raw_notices:
            if ntype != "Urgent Link":
                clickable_title = f'<a href="{link}" target="_blank">{title} 🔗</a>' if link and link != "https://" else title
                table_data.append({"तारीख": date, "कैटेगरी": ntype, "विषय / लिंक": clickable_title})
        if table_data: st.write(pd.DataFrame(table_data).to_html(escape=False, index=False), unsafe_allow_html=True)

    with right_login:
        st.markdown("<div style='background-color:#1E3A8A; padding:10px; text-align:center; color:white; border-radius:8px 8px 0 0;'><b>🔐 छात्र / शिक्षक प्रवेश द्वार</b></div>", unsafe_allow_html=True)
        choice = st.radio("चुनें:", ["लॉगिन", "साइनअप (रजिस्टर)", "पासवर्ड रीसेट"], horizontal=True)
        st.markdown("---")
        
        if choice == "लॉगिन":
            username = st.text_input("यूजरनेम")
            password = st.text_input("पासवर्ड", type="password")
            city_input = st.text_input("आपका शहर", value="Patna")
            
            if st.button("पोर्टल में प्रवेश करें 🚀", width='stretch'):
                u_strip, p_strip = username.strip(), password.strip()
                
                # 🔍 बिना किसी शॉर्टकट के सीधे डेटाबेस से वेरिफिकेशन
                user = database.get_user_by_username(u_strip)
                
                if user and user[2] == p_strip:
                    if user[6] == 'blocked': 
                        st.error("🚫 आप ब्लॉक हैं!")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_info = {
                            'username': user[0], 
                            'name': user[1], 
                            'role': user[3], 
                            'assigned_class': user[4], 
                            'allowed_subjects': user[5]
                        }
                        if user[3] == 'student': 
                            database.log_user_activity(user[0], city=city_input.strip(), school=user[9])
                        st.success("लॉगिन सफल!"); st.rerun()
                        
                # 🛠️ बैकअप क्रेडेंशियल (केवल तब काम करेगा जब आपने नया पासवर्ड न बदला हो या DB फ्रेश हो)
                elif u_strip == 'admin' and p_strip == 'admin123':
                    st.session_state.logged_in = True
                    st.session_state.user_info = {'username': 'admin', 'name': 'Main Owner', 'role': 'super_admin'}
                    st.success("लॉगिन सफल!"); st.rerun()
                else: 
                    st.error("गलत जानकारी!")
                    
        elif choice == "साइनअप (रजिस्टर)":
            new_username = st.text_input("यूजरनेम बनाएं (बिना स्पेस के)", key="su_user")
            new_name = st.text_input("अपना पूरा नाम", key="su_name")
            new_password = st.text_input("पासवर्ड सेट करें", type="password", key="su_pass")
            student_school = st.text_input("अपने स्कूल का पूरा नाम", key="su_school")
            student_board = st.selectbox("अपना परीक्षा बोर्ड चुनें", ["BSEB (Bihar Board)", "CBSE Board"], key="su_board")
            student_class = st.selectbox("अपनी कक्षा चुनें", ["Class 9", "Class 10", "Class 11", "Class 12"], key="su_class")
            student_subjects = st.multiselect("अपने मुख्य विषय चुनें", ["Physics", "Chemistry", "Biology", "Maths", "Social Science", "English", "Hindi"], key="su_subs")
            mobile = st.text_input("मोबाइल नंबर", key="su_mob")
            
            if st.button("रजिस्ट्रेशन सबमिट करें 🎉", width='stretch', key="su_submit_btn"):
                if new_username.strip() and new_name.strip() and new_password.strip() and mobile.strip() and student_school.strip() and student_subjects:
                    subs_str = ", ".join(student_subjects)
                    success, msg = database.add_user(username=new_username.strip(), name=new_name.strip(), password=new_password.strip(), role='student', student_class=student_class, mobile=mobile.strip(), subject=subs_str, board=student_board, school=student_school.strip())
                    if success: st.success("🎉 रजिस्ट्रेशन सफल! एडमिन अप्रूवल का इंतज़ार करें।")
                    else: st.error(msg)
                else: st.warning("सभी बॉक्स भरना अनिवार्य है।")

        elif choice == "पासवर्ड रीसेट":
            st.caption("🔒 सुरक्षा जांच: पासवर्ड बदलने के लिए अपना रजिस्टर्ड मोबाइल नंबर और मास्टर सिक्योरिटी कोड डालें।")
            f_username = st.text_input("अपना रजिस्टर्ड यूजरनेम", key="pwd_res_user")
            f_mobile = st.text_input("अपना 10 अंकों का मोबाइल नंबर", key="pwd_res_mob")
            f_master_otp = st.text_input("मास्टर सुरक्षा कोड (OTP कोड)", type="password", key="pwd_res_otp")
            f_new_password = st.text_input("नया मजबूत पासवर्ड सेट करें", type="password", key="pwd_res_pass")
            
            if st.button("🔄 पासवर्ड सुरक्षित बदलें", width='stretch', key="pwd_res_btn"):
                u_res = f_username.strip()
                m_res = f_mobile.strip()
                p_res = f_new_password.strip()
                otp_res = f_master_otp.strip()
                
                if u_res and m_res and p_res and otp_res:
                    if otp_res == "9939":
                        user_data = database.get_user_by_username(u_res)
                        if user_data:
                            db_mobile = user_data[7] if user_data[7] else ""
                            if m_res == db_mobile:
                                database.reset_user_password(u_res, p_res)
                                st.success(f"🎉 यूज़र `{u_res}` का पासवर्ड सुरक्षित रीसेट हो गया है! अब नए पासवर्ड से लॉगिन करें।")
                            else: st.error("❌ मोबाइल नंबर मैच नहीं हुआ! कृपया वही नंबर डालें जो रजिस्ट्रेशन के वक्त दिया था।")
                        else: st.error("❌ यह यूजरनेम डेटाबेस में नहीं मिला!")
                    else: st.error("❌ गलत मास्टर सुरक्षा कोड! आप इस पोर्टल के मुख्य ओनर नहीं हैं।")
                else: st.warning("⚠️ कृपया चारों इनपुट बॉक्स को ठीक से भरें!")
