import streamlit as st
import pandas as pd
import os
from datetime import datetime

# إعدادات الصفحة والشكل العام
st.set_page_config(page_title="نظام معرض الكبير لإدارة المخازن", layout="wide")

# أسماء ملفات البيانات
INVENTORY_FILE = "inventory_data.csv"
USERS_FILE = "users_data.csv"
SALES_FILE = "sales_data.csv"
PURCHASES_FILE = "purchases_data.csv"
EXPENSES_FILE = "expenses_data.csv"
ATTENDANCE_FILE = "attendance_data.csv"
CONTACTS_FILE = "contacts_data.csv"

# دالة تهيئة الملفات للتأكد من وجود الحسابات الافتراضية
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([
            {"username": "admin", "password": "123", "role": "مدير"},
            {"username": "sharaf", "password": "456", "role": "مشرف"},
            {"username": "user1", "password": "111", "role": "موظف"}
        ]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "الكمية", "سعر الشراء", "سعر البيع"]).to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "اسم العميل", "العنوان", "نوع البيع", "الصنف", "الكمية", "الخصم %", "إجمالي البيع", "المسؤول"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(PURCHASES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "المورد", "الصنف", "الكمية", "إجمالي الشراء", "المسؤول"]).to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(EXPENSES_FILE):
        pd.DataFrame(columns=["التاريخ", "البيان", "المبلغ", "المسؤول"]).to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(ATTENDANCE_FILE):
        pd.DataFrame(columns=["الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف"]).to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(CONTACTS_FILE):
        pd.DataFrame(columns=["النوع", "الاسم", "الهاتف", "العنوان"]).to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')

init_files()

# إدارة الجلسة والمستخدمين
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'role' not in st.session_state: st.session_state.role = "موظف"

# --- واجهة تسجيل الدخول ---
if not st.session_state.auth:
    st.title(" 🏢 نظام معرض الكبير - تسجيل الدخول")
    user_input = st.text_input("اسم المستخدم", key="login_user").strip()
    pw_input = st.text_input("كلمة المرور", type="password", key="login_pw").strip()
    
    if st.button("دخول للنظام", use_container_width=True):
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        match = u_df[(u_df['username'] == user_input) & (u_df['password'] == pw_input)]
        if not match.empty:
            st.session_state.auth = True
            st.session_state.user = user_input
            st.session_state.role = match.iloc[0]['role']
            st.success(f"مرحباً بك يا {user_input} ({st.session_state.role})")
            st.rerun()
        else:
            st.error("بيانات الدخول خاطئة.")
else:
    # --- بناء القائمة الجانبية والصلاحيات حسب الرتبة ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    st.sidebar.write(f"الرتبة: **{st.session_state.role}**")
    
    if st.session_state.role == "مدير":
        menu = [" 📦 تكويد الأصناف", " 📊 رصيد أول المدة Excel", " 🔍 حالة المخزن", " 🤝 العملاء والموردين", " 📥 فاتورة شراء جديدة", " 📤 فاتورة بيع جديدة", " 📈 تقارير البيع والشراء", " 💸 المصاريف", " ⏰ الحضور والانصراف", " ⚙️ إدارة الصلاحيات"]
    elif st.session_state.role == "مشرف":
        menu = [" 🔍 حالة المخزن", " 📥 فاتورة شراء جديدة", " 📤 فاتورة بيع جديدة", " ⏰ الحضور والانصراف"]
    else: # موظف عادي
        menu = [" 🔍 حالة المخزن", " 📤 فاتورة بيع جديدة", " ⏰ الحضور والانصراف"]
        
    choice = st.sidebar.selectbox("الانتقال إلى", menu)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    # قراءة البيانات بشكل فوري ومحدث مع معالجة الأنواع وتجنب الأخطاء
    inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
    sales_df = pd.read_csv(SALES_FILE, dtype={"رقم الفاتورة": str, "الصنف": str})
    purchases_df = pd.read_csv(PURCHASES_FILE, dtype={"رقم الفاتورة": str})
    exp_df = pd.read_csv(EXPENSES_FILE)
    att_df = pd.read_csv(ATTENDANCE_FILE)
    contacts_df = pd.read_csv(CONTACTS_FILE, dtype=str)

    # --- 1. صفحة تكويد الأصناف (لمدير فقط) ---
    if "تكويد الأصناف" in choice:
        st.header("📦 تكويد وتسجيل أصناف جديدة")
        st.dataframe(inv_df, use_container_width=True)
        
        st.subheader("➕ إضافة صنف جديد")
        c1, c2, c3, c4 = st.columns(4)
        iid = c1.text_input("كود الصنف (الباركود / ID)")
        iname = c2.text_input("اسم المنتج")
        ipurchase = c3.number_input("سعر الشراء الافتراضي", min_value=0.0, step=1.0)
        isale = c4.number_input("سعر البيع الافتراضي", min_value=0.0, step=1.0)
        
        if st.button("تكويد وحفظ"):
            if iid and iname:
                if iid in inv_df["كود الصنف"].values:
                    st.warning("⚠️ هذا الكود مسجل مسبقاً!")
                else:
                    new_item = pd.DataFrame([{"كود الصنف": iid, "اسم الصنف": iname, "الكمية": 0, "سعر الشراء": ipurchase, "سعر البيع": isale}])
                    inv_df = pd.concat([inv_df, new_item], ignore_index=True)
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("🎉 تم تكويد المنتج بنجاح!")
                    st.rerun()
            else:
                st.error("الرجاء إدخال كود الصنف واسم المنتج.")

    # --- 2. صفحة رفع رصيد أول المدة عبر شيت Excel (للمدير فقط) ---
    elif "رصيد أول المدة" in choice:
        st.header("📊 رفع بضائع ورصيد أول المدة عبر ملف Excel")
        st.write("ارفع ملف Excel يحتوي على الأعمدة التالية تماماً: `كود الصنف`, `اسم الصنف`, `الكمية`, `سعر الشراء`, `سعر البيع`")
        
        uploaded_file = st.file_uploader("اختر شيت الاكسل الخاص بالبضائع", type=["xlsx", "xls"])
        if uploaded_file is not None:
            try:
                excel_df = pd.read_excel(uploaded_file, dtype={"كود الصنف": str})
                st.subheader("👀 معاينة البيانات المرفوعة من الشيت:")
                st.dataframe(excel_df)
                
                if st.button("تأكيد ودمج الملف في رصيد أول المدة"):
                    combined_df = pd.concat([inv_df, excel_df]).drop_duplicates(subset=['كود الصنف'], keep='last')
                    combined_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("🚀 تم رفع وحفظ رصيد أول المدة بنجاح وتحديث المخزن!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء قراءة الملف، يرجى التأكد من أسماء الأعمدة. الخطأ: {e}")

    # --- 3. صفحة حالة المخزن ---
    elif "حالة المخزن" in choice:
        st.header("🔍 جرد بضائع المخزن الحالية")
        st.dataframe(inv_df, use_container_width=True)

    # --- 4. صفحة العملاء والموردين ---
    elif "العملاء والموردين" in choice:
        st.header("🤝 إدارة بيانات العملاء والموردين")
        st.dataframe(contacts_df, use_container_width=True)
        
        c1, c2, c3, c4 = st.columns(4)
        ctype = c1.selectbox("النوع", ["عميل", "مورد"])
        cname = c2.text_input("الاسم")
        cphone = c3.text_input("الهاتف")
        caddress = c4.text_input("العنوان")
        
        if st.button("حفظ الجهة"):
            if cname:
                new_c = pd.DataFrame([{"النوع": ctype, "الاسم": cname, "الهاتف": cphone, "العنوان": caddress}])
                contacts_df = pd.concat([contacts_df, new_c], ignore_index=True)
                contacts_df.to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم الحفظ بنجاح!")
                st.rerun()
            else:
                st.error("الرجاء كتابة الاسم أولاً.")

    # --- 5. صفحة المشتريات ---
    elif "فاتورة شراء جديدة" in choice:
        st.header("📥 تسجيل فاتورة مشتريات جديدة")
        if inv_df.empty: 
            st.warning("⚠️ قم بتكويد بضائع أو رفع رصيد أول مدة أولاً.")
        else:
            m_list = contacts_df[contacts_df['النوع'] == 'مورد']['الاسم'].unique()
            if len(m_list) == 0: m_list = ["مورد عام"]
            
            c1, c2, c3 = st.columns(3)
            vendor = c1.selectbox("المورد", m_list)
            item = c2.selectbox("الصنف المشترى", inv_df['اسم الصنف'].unique())
            qty = c3.number_input("الكمية", min_value=1, step=1)
            
            item_row = inv_df[inv_df['اسم الصنف'] == item].iloc[0]
            total = float(item_row['سعر الشراء']) * qty
            
            if st.button("حفظ المشتريات"):
                idx = inv_df[inv_df['اسم الصنف'] == item].index[0]
                inv_df.at[idx, 'الكمية'] = int(inv_df.at[idx, 'الكمية']) + qty
                inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                
                pur_id = "PUR-" + str(int(datetime.now().timestamp()))
                new_p = pd.DataFrame([{"رقم الفاتورة": pur_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "المورد": vendor, "الصنف": item, "الكمية": qty, "إجمالي الشراء": total, "المسؤول": st.session_state.user}])
                purchases_df = pd.concat([purchases_df, new_p], ignore_index=True)
                purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم تسجيل الوارد للمخزن بنجاح!")
                st.rerun()

    # --- 6. صفحة فاتورة بيع جديدة ---
    elif "فاتورة بيع جديدة" in choice:
        st.header("📤 إنشاء فاتورة مبيعات جديدة - معرض الكبير")
        if inv_df.empty: 
            st.warning("⚠️ المخزن فارغ تماماً.")
        else:
            c_list = contacts_df[contacts_df['النوع'] == 'عميل']['الاسم'].unique()
            
            c1, c2, c3, c4 = st.columns(4)
            cust_type = c1.radio("نوع العميل", ["سريع / غير مسجل", "مسجل مسبقاً"])
            if cust_type == "مسجل مسبقاً" and len(c_list) > 0:
                c_name = c2.selectbox("اختر العميل", c_list)
                c_address = contacts_df[contacts_df['الاسم'] == c_name]['العنوان'].values[0]
            else:
                c_name = c2.text_input("اسم العميل")
                c_address = c3.text_input("عنوان العميل")
                
            sale_type = c4.selectbox("طبيعة البيع", ["نقدي (كاش)", "آجل (على الحساب)"])
            
            st.markdown("---")
            c5, c6, c7 = st.columns(3)
            selected_item = c5.selectbox("اختر المنتج للبيع", inv_df['اسم الصنف'].unique())
            qty = c6.number_input("الكمية المطلوبة", min_value=1, step=1)
            
            discount = 0.0
            if st.session_state.role in ["مدير", "مشرف"]:
                discount = c7.number_input("نسبة الخصم الممنوحة (%)", min_value=0.0, max_value=100.0, step=0.5)
            else:
                c7.write("🔒 *صلاحية الخصم مغلقة للموظفين*")
                
            item_row = inv_df[inv_df['اسم الصنف'] == selected_item].iloc[0]
            subtotal = float(item_row['سعر البيع']) * qty  
            discount_amount = subtotal * (discount / 100)
            final_total = subtotal - discount_amount
            
            st.warning(f"📊 المتوفر بالمخزن: {item_row['الكمية']} قطعة | السعر الأساسي: {subtotal} | الخصم: {discount_amount} | الصافي المطلوب: {final_total}")
            
            if st.button("🧾 إصدار وطباعة الفاتورة الثلاثية", use_container_width=True):
                idx = inv_df[inv_df['اسم الصنف'] == selected_item].index[0]
                if int(inv_df.at[idx, 'الكمية']) < qty:
                    st.error("❌ الكمية المتوفرة في المخزن لا تكفي!")
                elif not c_name:
                    st.error("❌ يرجى كتابة اسم العميل أولاً.")
                else:
                    inv_df.at[idx, 'الكمية'] = int(inv_df.at[idx, 'الكمية']) - qty
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    inv_id = "INV-" + str(int(datetime.now().timestamp()))
                    new_s = pd.DataFrame([{"رقم الفاتورة": inv_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "اسم العميل": c_name, "العنوان": c_address, "نوع البيع": sale_type, "الصنف": selected_item, "الكمية": qty, "الخصم %": discount, "إجمالي البيع": final_total, "المسؤول": st.session_state.user}])
                    sales_df = pd.concat([sales_df, new_s], ignore_index=True)
                    sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    
                    st.success("🎉 تم حفظ الفاتورة بنجاح في السجلات!")
                    
                    copies = ["نسخة العميل", "نسخة الإدارة المالية", "نسخة مسؤول المخازن"]
                    html_invoice = ""
                    
                    for copy in copies:
                        html_invoice += f"""
                        <div style="border: 2px dashed black; padding: 15px; margin-bottom: 30px; direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background: #fff; color: #000; border-radius: 8px;">
                            <div style="text-align: center; font-weight: bold;">
                                <h2 style="margin: 0; color: #111;">📋 {copy}</h2>
                                <h1 style="margin: 5px 0; font-size: 28px; letter-spacing: 1px;">🏢 معرض الكبير</h1>
                                <p style="font-size: 13px; margin: 2px;">العنوان: ابوحماد - قرية العراقي - بجوار مدرسة الشهيد صلاح فتحي</p>
                            </div>
                            <hr style="border: 1px solid #000;">
                            <table style="width: 100%; font-size: 14px;">
                                <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d')}</td></tr>
                                <tr><td><b>اسم العميل:</b> {c_name}</td><td><b>العنوان:</b> {c_address if c_address else 'غير محدد'}</td></tr>
                                <tr><td><b>نوع الدفع:</b> {sale_type}</td><td><b>المسؤول:</b> {st.session_state.user}</td></tr>
                            </table>
                            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid black; font-size: 14px; text-align: center;">
                                <tr style="background: #f2f2f2;">
                                    <th style="border: 1px solid black; padding: 5px;">الصنف والبيان</th>
                                    <th style="border: 1px solid black; padding: 5px;">الكمية</th>
                                    <th style="border: 1px solid black; padding: 5px;">سعر المفرد</th>
                                    <th style="border: 1px solid black; padding: 5px;">الخصم</th>
                                    <th style="border: 1px solid black; padding: 5px;">الصافي الإجمالي</th>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid black; padding: 5px;">{selected_item}</td>
                                    <td style="border: 1px solid black; padding: 5px;">{qty}</td>
                                    <td style="border: 1px solid black; padding: 5px;">{item_row['سعر البيع']}</td>
                                    <td style="border: 1px solid black; padding: 5px;">{discount}%</td>
                                    <td style="border: 1px solid black; padding: 5px; font-weight: bold;">{final_total}</td>
                                </tr>
                            </table>
                            <div style="margin-top: 10px; font-size: 12px; font-weight: bold; text-align: center; border: 1px solid #000; padding: 5px; background: #eee;">
                                ⚠️ تنبيه هام جداً: مدة الاستبدال والارتجاع 15 يوماً لا غير من تاريخ الفاتورة بشرط سلامة البضاعة وغلافها.
                            </div>
                        </div>
                        """
                    st.markdown(html_invoice, unsafe_allow_html=True)

    # --- 7. صفحة التقارير ---
    elif "تقارير البيع والشراء" in choice:
        st.header("📈 التقارير المالية التفصيلية لمعرض الكبير")
        t1, t2 = st.tabs(["📑 حركة الفواتير", "💰 الخزينة والأرباح"])
        with t1:
            st.subheader("🛒 سجل المبيعات")
            st.dataframe(sales_df, use_container_width=True)
            st.subheader("📦 سجل المشتريات")
            st.dataframe(purchases_df, use_container_width=True)
        with t2:
            s_sum = pd.to_numeric(sales_df['إجمالي البيع'], errors='coerce').sum()
            e_sum = pd.to_numeric(exp_df['المبلغ'], errors='coerce').sum()
            
            # حساب تكلفة البضاعة المباعة الفعليّة (سعر الشراء * الكمية المباعة)
            total_cost_of_goods_sold = 0.0
            for _, row in sales_df.dropna(subset=['الصنف', 'الكمية']).iterrows():
                match_inv = inv_df[inv_df['اسم الصنف'] == row['الصنف']]
                if not match_inv.empty:
                    total_cost_of_goods_sold += float(match_inv.iloc[0]['سعر الشراء']) * int(row['الكمية'])
            
            # صافي الربح المحاسبي الدقيق
            net_profit = s_sum - (total_cost_of_goods_sold + e_sum)
            
            c_m1, c_m2, c_m3 = st.columns(3)
            c_m1.metric("إجمالي حجم المبيعات", f"{s_sum:,.2f} جنيه")
            c_m2.metric("إجمالي المصاريف الإدارية", f"{e_sum:,.2f} جنيه")
            c_m3.metric("صافي الأرباح الفعلية (بعد خصم التكلفة)", f"{net_profit:,.2f} جنيه")

    # --- 8. صفحة المصاريف ---
    elif "المصاريف" in choice:
        st.header("💸 تسجيل المصاريف الإدارية والعمومية")
        st.dataframe(exp_df, use_container_width=True)
        b1 = st.text_input("بيان الصرف (مثال: إيجار، كهرباء، ضيافة)")
        b2 = st.number_input("المبلغ المنصرف", min_value=0.0, step=10.0)
        if st.button("حفظ المصروف"):
            if b1 and b2 > 0:
                new_e = pd.DataFrame([{"التاريخ": datetime.now().strftime("%Y-%m-%d"), "البيان": b1, "المبلغ": b2, "المسؤول": st.session_state.user}])
                exp_df = pd.concat([exp_df, new_e], ignore_index=True)
                exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم حفظ المصروف بنجاح!")
                st.rerun()
            else:
                st.error("يرجى ملء بيان الصرف وتحديد مبلغ أكبر من الصفر.")

    # --- 9. الحضور والانصراف ---
    elif "الحضور والانصراف" in choice:
        st.header("⏰ تسجيل حضور وانصراف موظفي المعرض")
        st.dataframe(att_df, use_container_width=True)
        today = datetime.now().strftime("%Y-%m-%d")
        now_t = datetime.now().strftime("%H:%M:%S")
        
        c1, c2 = st.columns(2)
        if c1.button("🟢 تسجيل حضور اليوم", use_container_width=True):
            if not att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today)].empty:
                st.warning("⚠️ تم تسجيل حضورك بالفعل اليوم!")
            else:
                new_a = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": today, "وقت الحضور": now_t, "وقت الانصراف": "لم ينصرف"}])
                att_df = pd.concat([att_df, new_a], ignore_index=True)
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"📌 تم تسجيل الحضور في تمام الساعة: {now_t}")
                st.rerun()
                
        if c2.button("🔴 تسجيل انصراف الآن", use_container_width=True):
            idx = att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today) & (att_df['وقت الانصراف'] == "لم ينصرف")].index
            if not idx.empty:
                att_df.at[idx[0], 'وقت الانصراف'] = now_t
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"📌 تم تسجيل انصرافك في تمام الساعة: {now_t}")
                st.rerun()
            else:
                st.error("❌ لم يتم العثور على حركة حضور مفتوحة لك اليوم أو تم تسجيل الانصراف مسبقاً.")

    # --- 10. صفحة الصلاحيات واليوزرات ---
    elif "إدارة الصلاحيات" in choice:
        st.header("⚙️ إدارة حسابات موظفي ومشرفي معرض الكبير")
        u_df = pd.read_csv(USERS_FILE)
        st.dataframe(u_df, use_container_width=True)
        
        st.subheader("👤 إضافة مستخدم جديد للنظام وتحديد رتبته")
        c1, c2, c3 = st.columns(3)
        nu = c1.text_input("اسم المستخدم الجديد", key="new_username")
        np = c2.text_input("كلمة المرور الجديدة", type="password", key="new_password")
        nr = c3.selectbox("الصلاحية الممنوحة له", ["موظف", "مشرف", "مدير"], key="new_role")
        
        if st.button("اعتماد وإنشاء الحساب"):
            if nu and np:
                if nu in u_df["username"].astype(str).values:
                    st.error("❌ اسم المستخدم هذا موجود بالفعل، اختر اسماً آخر.")
                else:
                    new_u = pd.DataFrame([{"username": nu, "password": np, "role": nr}])
                    u_df = pd.concat([u_df, new_u], ignore_index=True)
                    u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                    st.success(f"🎉 تم إنشاء حساب بنجاح للـ {nr} ({nu})")
                    st.rerun()
            else:
                st.error("يرجى إدخال اسم المستخدم وكلمة المرور معاً.")
